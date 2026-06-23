"""
La Ocasión · Sistema de Inventarios — v3
Streamlit + Supabase
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import json, io

import db
import costos as calc

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="La Ocasión · Inventarios",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta La Ocasión: crema #F5EFE0, café oscuro #3B1A0A, café medio #7C4A1E, acento #C17F3E
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp { background-color: #F5EFE0; }

/* SIDEBAR */
[data-testid="stSidebar"] { background-color: #3B1A0A !important; }
[data-testid="stSidebar"] * { color: #F5EFE0 !important; font-family: 'Nunito', sans-serif !important; }
[data-testid="stSidebar"] .stRadio label { font-size:14px; padding:4px 0; }
[data-testid="stSidebar"] hr { border-color: rgba(245,239,224,0.2) !important; }

/* TOPBAR / TÍTULOS */
h1 { color: #3B1A0A !important; font-weight:800; }
h2, h3 { color: #5C2E0A !important; font-weight:700; }

/* BOTONES */
.stButton > button {
    background-color: #7C4A1E !important; color: #F5EFE0 !important; border:none !important;
    border-radius:8px !important; font-weight:700 !important; font-family:'Nunito',sans-serif !important;
    transition: background .2s; font-size: 13px !important;
}
.stButton > button:hover { background-color: #5C2E0A !important; color:#F5EFE0 !important; }
.stButton > button[kind="primary"]   { background-color: #7C4A1E !important; color: #F5EFE0 !important; }
.stButton > button[kind="secondary"] { background-color: #C17F3E !important; color: #F5EFE0 !important; }
.stButton > button p,
.stButton > button span,
.stButton > button div { color: #F5EFE0 !important; font-size: 13px !important; }
/* Download buttons */
[data-testid="stDownloadButton"] > button {
    background-color: #7C4A1E !important; color: #F5EFE0 !important;
    border:none !important; border-radius:8px !important; font-weight:700 !important;
}
[data-testid="stDownloadButton"] > button p { color: #F5EFE0 !important; }
/* Form submit buttons */
[data-testid="stFormSubmitButton"] > button {
    background-color: #7C4A1E !important; color: #F5EFE0 !important;
    border:none !important; border-radius:8px !important; font-weight:700 !important;
}
[data-testid="stFormSubmitButton"] > button p { color: #F5EFE0 !important; }

/* FORMULARIOS */
.stForm { background: #fff8f0; border-radius:12px; padding:16px; border:1px solid #e8d5b7; }

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background-color: #ede3d0; border-radius:10px; padding:4px;
    flex-wrap: wrap; gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent; color: #7C4A1E !important;
    font-weight: 600; border-radius: 8px;
    font-family: 'Nunito', sans-serif !important;
    font-size: 13px; padding: 6px 14px !important;
    white-space: nowrap;
}
.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] span,
.stTabs [data-baseweb="tab"] div {
    color: #7C4A1E !important;
    font-size: 13px !important;
}
.stTabs [aria-selected="true"] {
    background-color: #7C4A1E !important;
    color: #F5EFE0 !important;
}
.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span,
.stTabs [aria-selected="true"] div {
    color: #F5EFE0 !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background-color: #c9a87a !important;
    color: #3B1A0A !important;
}
.stTabs [data-baseweb="tab-highlight"] { background-color: transparent !important; }
.stTabs [data-baseweb="tab-border"]    { display: none !important; }

/* MÉTRICAS */
[data-testid="metric-container"] {
    background:#fff8f0; border-radius:10px; padding:12px 16px;
    border-left:4px solid #C17F3E; box-shadow:0 1px 4px rgba(59,26,10,.1);
}

/* DATAFRAME */
.stDataFrame { border-radius:10px; overflow:hidden; }
[data-testid="stDataFrame"] > div { background:#fff8f0 !important; border-radius:10px; }

/* DATA EDITOR (tabla editable) */
[data-testid="stDataEditor"] > div { background:#fff8f0 !important; border-radius:10px; }

/* METRIC valores grandes */
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #3B1A0A !important; font-weight:800; }
[data-testid="metric-container"] [data-testid="stMetricLabel"] { color: #7C4A1E !important; font-weight:600; }
[data-testid="metric-container"] [data-testid="stMetricDelta"] { color: #5C2E0A !important; }

/* Texto general en el cuerpo */
p, span, div, li { color: #3B1A0A; }
.stMarkdown p { color: #3B1A0A !important; }
.stMarkdown strong { color: #3B1A0A !important; }

/* CAPTION */
.stCaption { color: #7C4A1E !important; }

/* KPI CARDS */
.kpi-box {
    background:#fff8f0; border-radius:12px; padding:16px 18px;
    border-top:4px solid #C17F3E; box-shadow:0 2px 8px rgba(59,26,10,.10);
    text-align:center;
}
.kpi-box.danger { border-top-color:#c0392b; }
.kpi-box.warn   { border-top-color:#e07b39; }
.kpi-box.ok     { border-top-color:#27ae60; }
.kpi-val { font-size:24px; font-weight:800; color:#3B1A0A; }
.kpi-lbl { font-size:12px; color:#7C4A1E; margin-top:3px; font-weight:600; }

/* EXPANDERS */
[data-testid="stExpander"] summary {
    color: #3B1A0A !important; font-weight:700 !important;
}
[data-testid="stExpander"] summary:hover { color: #7C4A1E !important; }
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span { color: #3B1A0A !important; }
details > summary { color: #3B1A0A !important; }

/* INFO / SUCCESS / WARNING */
.stAlert { border-radius:10px; }

/* INPUTS — texto, número, selectbox, multiselect, date, textarea */
input, textarea {
    background-color: #fff8f0 !important;
    color: #3B1A0A !important;
    border-color: #c9a87a !important;
    font-family: 'Nunito', sans-serif !important;
    pointer-events: all !important;
    cursor: text !important;
    user-select: text !important;
    -webkit-user-select: text !important;
}
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
[data-baseweb="base-input"] input {
    background-color: #fff8f0 !important;
    color: #3B1A0A !important;
    border: none !important;
    pointer-events: all !important;
    cursor: text !important;
}
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="textarea"] {
    background-color: #fff8f0 !important;
    border: 1px solid #c9a87a !important;
    border-radius: 8px !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="base-input"]:focus-within,
[data-baseweb="textarea"]:focus-within {
    border-color: #7C4A1E !important;
    box-shadow: 0 0 0 2px rgba(124,74,30,0.25) !important;
}
/* NUMBER INPUT — asegurar que el campo de texto central sea clickeable */
[data-testid="stNumberInput"] > div {
    background-color: #fff8f0 !important;
    border: 1px solid #c9a87a !important;
    border-radius: 8px !important;
}
[data-testid="stNumberInput"] input {
    background-color: transparent !important;
    color: #3B1A0A !important;
    text-align: center;
    font-size: 15px !important;
    font-weight: 600 !important;
    cursor: text !important;
    pointer-events: all !important;
    -webkit-user-select: text !important;
    user-select: text !important;
}

/* SELECT / DROPDOWN */
[data-baseweb="select"] > div {
    background-color: #fff8f0 !important;
    border-color: #c9a87a !important;
    border-radius: 8px !important;
    color: #3B1A0A !important;
}
[data-baseweb="select"] span,
[data-baseweb="select"] div { color: #3B1A0A !important; }
[data-baseweb="popover"] { background-color: #fff8f0 !important; }
[data-baseweb="menu"] { background-color: #fff8f0 !important; }
[data-baseweb="menu"] li { color: #3B1A0A !important; }
[data-baseweb="menu"] li:hover { background-color: #ede3d0 !important; }
[data-baseweb="option"]:hover { background-color: #ede3d0 !important; }
[aria-selected="true"][data-baseweb="option"] { background-color: #C17F3E !important; color:#F5EFE0 !important; }

/* NUMBER INPUT buttons */
[data-testid="stNumberInput"] button {
    background-color: #ede3d0 !important;
    color: #3B1A0A !important;
    border: none !important;
}
[data-testid="stNumberInput"] button:hover { background-color: #c9a87a !important; }

/* DATE INPUT */
[data-testid="stDateInput"] input { background-color: #fff8f0 !important; color:#3B1A0A !important; }

/* LABELS */
label, .stTextInput label, .stNumberInput label,
.stSelectbox label, .stDateInput label, .stTextArea label {
    color: #5C2E0A !important;
    font-weight: 600 !important;
    font-family: 'Nunito', sans-serif !important;
}

/* MULTISELECT tags */
[data-baseweb="tag"] {
    background-color: #C17F3E !important;
    color: #F5EFE0 !important;
    border-radius: 6px !important;
}

/* LOGO sidebar */
.logo-text {
    font-size:26px; font-weight:800; color:#F5EFE0 !important;
    letter-spacing:-0.5px; line-height:1.1;
}
.logo-sub {
    font-size:11px; color:rgba(245,239,224,0.65) !important;
    letter-spacing:1px; text-transform:uppercase;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────────────────────────────────────
def check_password():
    if st.session_state.get("authenticated"): return True
    st.markdown("""
    <div style='text-align:center;padding:60px 20px 20px'>
      <div style='font-size:48px'>🍽️</div>
      <div style='font-size:36px;font-weight:800;color:#3B1A0A'>la Ocasión</div>
      <div style='font-size:14px;color:#7C4A1E;margin-bottom:32px;letter-spacing:1px'>SISTEMA DE INVENTARIOS</div>
    </div>
    """, unsafe_allow_html=True)
    col = st.columns([1,2,1])[1]
    pwd = col.text_input("Contraseña de acceso", type="password", label_visibility="collapsed",
                          placeholder="Contraseña de acceso")
    if col.button("Ingresar →", use_container_width=True, type="primary"):
        if pwd == st.secrets.get("APP_PASSWORD","laocasion2024"):
            st.session_state.authenticated = True; st.rerun()
        else:
            col.error("Contraseña incorrecta")
    return False

if not check_password(): st.stop()

# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fmt_cop(n):
    if n is None: return "—"
    return f"$ {int(round(float(n))):,}".replace(",",".")
def fmt_n(n):
    if n is None: return "—"
    v=float(n); return f"{v:,.2f}".rstrip("0").rstrip(".")
def hoy(): return str(date.today())

CATEGORIAS = ["Proteínas","Lácteos","Verduras","Frutas","Granos / Harinas",
              "Aceites / Grasas","Condimentos","Bebidas","Pastelería","Panadería","Otros"]
UNIDADES   = ["g","kg","ml","L","unidad","porción","taza","cucharada","cucharadita","manojo","lámina"]
CAUSAS_BAJA= ["Vencimiento","Contaminación","Error de preparación","Sobre-producción",
               "Accidente / caída","Devolución cliente","Error de porción","Otro"]
TURNOS     = ["Mañana","Tarde","Noche"]
CAT_RECETA    = ["Plato Principal","Entrada","Postre","Bebida","Brunch","Panadería","Pastelería","Especial","Sanduches Salados","Sanduches Dulces"]
CAT_SANDUCHE  = ["Sanduches Salados","Sanduches Dulces"]   # recetas que requieren elección de pan
CAT_PAN_SUB   = "Tipo de pan"                              # categoría de sub-recetas que son bases de pan
CAT_LECHE_SUB = "Tipo de leche"                            # categoría de sub-recetas que son opciones de leche

# ─────────────────────────────────────────────────────────────────────────────
#  NAVEGACIÓN
# ─────────────────────────────────────────────────────────────────────────────
PAGES = {
    "📊 Dashboard":             "dashboard",
    "📦 Insumos":               "insumos",
    "📋 Recetas":               "recetas",
    "🧪 Sub-recetas":           "subrecetas",
    "🔄 Movimientos":           "movimientos",
    "📒 Kardex":                "kardex",
    "🗑️ Bajas":                "bajas",
    "🔔 Alertas":               "alertas",
    "📈 Reportes":              "reportes",
    "🏭 Proyección Producción": "produccion",
    "❓ Ayuda":                 "ayuda",
    "⚙️ Configuración":         "config",
}

with st.sidebar:
    st.markdown("""
    <div style='padding:20px 16px 12px'>
      <div class='logo-text'>la Ocasión</div>
      <div class='logo-sub'>perfecta para...</div>
      <div style='font-size:10px;color:rgba(245,239,224,0.4);margin-top:4px;letter-spacing:.5px'>
        SISTEMA DE INVENTARIOS
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    page = st.radio("Módulos", list(PAGES.keys()), label_visibility="collapsed")
    st.divider()
    st.markdown(f"<div style='font-size:11px;color:rgba(245,239,224,0.5);padding:0 4px'>📅 {date.today().strftime('%d/%m/%Y')}</div>",
                unsafe_allow_html=True)
    if st.button("🚪 Cerrar sesión", use_container_width=True):
        st.session_state.authenticated = False; st.rerun()

current = PAGES[page]

# ─────────────────────────────────────────────────────────────────────────────
#  DATOS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=8)
def load_all():
    return {"insumos":db.get_insumos(),"recetas":db.get_recetas(),
            "subrecetas":db.get_subrecetas(),"movs":db.get_movimientos(),
            "bajas":db.get_bajas(),"config":db.get_config(),
            "cf_items":db.get_costos_fijos_items()}

def reload():
    load_all.clear(); st.rerun()

data       = load_all()
insumos    = data["insumos"];   recetas    = data["recetas"]
subrecetas = data["subrecetas"]; movs       = data["movs"]
bajas      = data["bajas"];     cfg        = data["config"]
_cf_raw    = data["cf_items"]
cf_table_ok = _cf_raw is not None      # False = falta correr el SQL en Supabase
cf_items   = _cf_raw or []
umbral_precio    = float(cfg.get("umbral_precio",3))
ventas_esperadas = float(cfg.get("ventas_esperadas",0))
_cf_default = float(cfg.get("costos_fijos",15))

CAT_SIN_CF = ["Bebida"]   # categorías que NO cargan costos fijos (se costean solo con materia prima + margen)

# % global de costos fijos = total rubros activos / ventas esperadas
_cf_total_activos = sum(float(i.get("monto",0)) for i in cf_items if i.get("activo",True))
costos_fijos = round((_cf_total_activos/ventas_esperadas)*100,2) if (cf_items and ventas_esperadas>0) else _cf_default

def cf_cat(cat=""):
    """% de costos fijos a aplicar según la categoría de la receta.
    Las bebidas (CAT_SIN_CF) quedan exentas: se costean solo con materia
    prima + margen, sin cargarles costos fijos. El resto usa el % global."""
    if cat in CAT_SIN_CF:
        return 0.0
    return costos_fijos
panes_sub     = [s for s in subrecetas if s.get("categoria")==CAT_PAN_SUB]
leches_sub    = [s for s in subrecetas if s.get("categoria")==CAT_LECHE_SUB]

def consumo_insumos(ingredientes, mult=1, _prof=0):
    """Devuelve {ins_id: cantidad_bruta} que consume una lista de ingredientes.
    Descompone sub-recetas (sub:) en sus insumos según su rendimiento, de forma
    recursiva (hasta 5 niveles) para que el descuento cubra TODO lo enlazado."""
    need={}
    if _prof>5: return need
    for ing in ingredientes or []:
        ref=ing.get("ref_id",""); cant=ing.get("cantidad",ing.get("cant_neta",0))*mult
        if ref.startswith("ins:"):
            iid=ref[4:]; need[iid]=need.get(iid,0)+calc.cant_bruta(cant,ing.get("merma",0))
        elif ref.startswith("sub:"):
            sub=next((s for s in subrecetas if s["id"]==ref[4:]),None)
            if sub:
                rend=sub.get("rendimiento",1) or 1
                for k,v in consumo_insumos(sub.get("ingredientes",[]),cant/rend,_prof+1).items():
                    need[k]=need.get(k,0)+v
    return need

def kpi(col,val,lbl,t=""):
    col.markdown(f'<div class="kpi-box {t}"><div class="kpi-val">{val}</div><div class="kpi-lbl">{lbl}</div></div>',
                 unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if current == "dashboard":
    st.title("📊 Dashboard")
    bajo       = [i for i in insumos if i.get("minimo",0)>0 and i.get("stock",0)<=i["minimo"]]
    lunes      = date.today()-timedelta(days=date.today().weekday())
    bajas_sem  = sum(b.get("costo_total",0) for b in bajas if (b.get("fecha") or "")>=str(lunes))
    movs_hoy   = sum(1 for m in movs if m.get("fecha")==hoy())
    valor_total= sum(i.get("stock",0)*i.get("costo",0) for i in insumos)

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    kpi(c1,len(insumos),"Insumos registrados")
    kpi(c2,len(bajo),"Stock crítico","danger" if bajo else "ok")
    kpi(c3,len(recetas),"Recetas activas")
    kpi(c4,fmt_cop(round(bajas_sem/1000))+"k","Bajas esta semana","warn")
    kpi(c5,movs_hoy,"Movimientos hoy")
    kpi(c6,fmt_cop(round(valor_total/1000))+"k","Valor inventario")

    st.markdown("---")
    cl,cr = st.columns(2)
    with cl:
        st.subheader("📉 Stock vs Mínimo")
        criticos = sorted([i for i in insumos if i.get("minimo",0)>0],
                          key=lambda i:i.get("stock",0)/max(i["minimo"],0.001))[:12]
        if criticos:
            df_c = pd.DataFrame({"Insumo":[i["nombre"][:20] for i in criticos],
                                  "Stock":[i.get("stock",0) for i in criticos],
                                  "Mínimo":[i.get("minimo",0) for i in criticos]})
            fig = go.Figure()
            colors=["#c0392b" if r["Stock"]<=r["Mínimo"] else "#7C4A1E" for _,r in df_c.iterrows()]
            fig.add_bar(x=df_c["Insumo"],y=df_c["Stock"],name="Stock",marker_color=colors)
            fig.add_scatter(x=df_c["Insumo"],y=df_c["Mínimo"],name="Mínimo",
                            mode="lines+markers",line=dict(color="#C17F3E",width=2))
            fig.update_layout(height=300,margin=dict(t=10,b=10),
                              plot_bgcolor="#fff8f0",paper_bgcolor="#fff8f0",
                              legend=dict(orientation="h"))
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.info("Sin insumos con stock mínimo definido.")

    with cr:
        st.subheader("📅 Movimientos últimos 7 días")
        days=[str(date.today()-timedelta(days=i)) for i in range(6,-1,-1)]
        tipos_c={"Entradas":"entrada","Ventas":"venta","Bajas":"baja"}
        colores={"Entradas":("#7C4A1E","rgba(124,74,30,0.15)"),
                 "Ventas":  ("#C17F3E","rgba(193,127,62,0.15)"),
                 "Bajas":   ("#c0392b","rgba(192,57,43,0.15)")}
        fig2=go.Figure()
        for label,tipo in tipos_c.items():
            counts=[sum(1 for m in movs if m.get("fecha")==d and m.get("tipo")==tipo) for d in days]
            lc,fc=colores[label]
            fig2.add_scatter(x=[d[5:] for d in days],y=counts,name=label,
                             mode="lines+markers",line=dict(color=lc,width=2),
                             fill="tozeroy",fillcolor=fc)
        fig2.update_layout(height=300,margin=dict(t=10,b=10),
                           plot_bgcolor="#fff8f0",paper_bgcolor="#fff8f0",
                           legend=dict(orientation="h"))
        st.plotly_chart(fig2,use_container_width=True)

    cl2,cr2=st.columns(2)
    with cl2:
        st.subheader("⚠️ Alertas de stock")
        if bajo:
            for i in bajo[:8]:
                st.markdown(f"🔴 **{i['nombre']}** — {fmt_n(i.get('stock',0))} / {fmt_n(i.get('minimo',0))} {i.get('unidad','')} *({i.get('categoria','')})*")
        else:
            st.success("✅ Todo el stock sobre el mínimo")
    with cr2:
        st.subheader("🕐 Últimos movimientos")
        if movs:
            df_m=pd.DataFrame([{"Fecha":m.get("fecha"),"Tipo":m.get("tipo"),
                                 "Insumo/Plato":m.get("nombre"),"Cant.":m.get("cantidad")} for m in movs[:8]])
            st.dataframe(df_m,hide_index=True,use_container_width=True)
        else:
            st.info("Sin movimientos aún.")


# ══════════════════════════════════════════════════════════════════════════════
#  INSUMOS
# ══════════════════════════════════════════════════════════════════════════════
elif current == "insumos":
    st.title("📦 Insumos")
    tab_list,tab_stock0,tab_minimos,tab_add,tab_imp,tab_exp = st.tabs([
        "📋 Listado","📊 Stock inicial","🔔 Mínimos / Alertas","➕ Agregar","📥 Importar CSV","📤 Exportar CSV"
    ])

    with tab_list:
        c1,c2,c3=st.columns([3,2,2])
        busq=c1.text_input("🔍 Buscar nombre o proveedor")
        fcat=c2.selectbox("Categoría",["Todas"]+CATEGORIAS,key="fcat")
        fstk=c3.selectbox("Stock",["Todos","Stock bajo","Stock OK"],key="fstk")
        lista=insumos
        if busq: lista=[i for i in lista if busq.lower() in i["nombre"].lower() or busq.lower() in (i.get("proveedor") or "").lower()]
        if fcat!="Todas": lista=[i for i in lista if i.get("categoria")==fcat]
        if fstk=="Stock bajo": lista=[i for i in lista if i.get("minimo",0)>0 and i.get("stock",0)<=i["minimo"]]
        elif fstk=="Stock OK": lista=[i for i in lista if not(i.get("minimo",0)>0 and i.get("stock",0)<=i["minimo"])]
        st.markdown(f"**{len(lista)} insumos** — Haz doble clic en cualquier celda para editar. Luego pulsa **💾 Guardar cambios**.")
        if lista:
            df_edit = pd.DataFrame([{
                "_id":           i["id"],
                "Nombre":        i["nombre"],
                "Categoría":     i.get("categoria",""),
                "Unidad":        i.get("unidad",""),
                "Stock":         float(i.get("stock",0)),
                "Mínimo":        float(i.get("minimo",0)),
                "Costo (COP)":   float(i.get("costo",0)),
                "Proveedor":     i.get("proveedor") or "",
                "Vida útil (d)": int(i.get("vida_util",0)),
                "Valor total":   round(i.get("stock",0)*i.get("costo",0)),
                "Estado":        "⚠️ Bajo" if i.get("minimo",0)>0 and i.get("stock",0)<=i["minimo"] else "✓ OK",
            } for i in lista])

            edited = st.data_editor(
                df_edit,
                hide_index=True,
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "_id":           st.column_config.Column(disabled=True, width="small"),
                    "Nombre":        st.column_config.TextColumn("Nombre", width="large"),
                    "Categoría":     st.column_config.SelectboxColumn("Categoría", options=CATEGORIAS),
                    "Unidad":        st.column_config.SelectboxColumn("Unidad", options=UNIDADES),
                    "Stock":         st.column_config.NumberColumn("Stock", step=0.01, format="%.2f"),
                    "Mínimo":        st.column_config.NumberColumn("Mínimo", step=0.01, format="%.2f"),
                    "Costo (COP)":   st.column_config.NumberColumn("Costo (COP)", step=100, format="%d"),
                    "Proveedor":     st.column_config.TextColumn("Proveedor"),
                    "Vida útil (d)": st.column_config.NumberColumn("Vida útil (d)", step=1, format="%d"),
                    "Valor total":   st.column_config.NumberColumn("Valor total", disabled=True, format="%d"),
                    "Estado":        st.column_config.Column("Estado", disabled=True),
                },
                key="edit_insumos_table",
            )

            if st.button("💾 Guardar cambios", type="primary", use_container_width=True):
                cambios = 0
                for i, (orig, new_row) in enumerate(zip(lista, edited.to_dict("records"))):
                    upd = {}
                    if orig["nombre"]               != new_row["Nombre"]:        upd["nombre"]      = new_row["Nombre"].strip()
                    if orig.get("categoria","")     != new_row["Categoría"]:     upd["categoria"]   = new_row["Categoría"]
                    if orig.get("unidad","")        != new_row["Unidad"]:        upd["unidad"]      = new_row["Unidad"]
                    if float(orig.get("stock",0))   != new_row["Stock"]:         upd["stock"]       = new_row["Stock"]
                    if float(orig.get("minimo",0))  != new_row["Mínimo"]:        upd["minimo"]      = new_row["Mínimo"]
                    if float(orig.get("costo",0))   != new_row["Costo (COP)"]:
                        nuevo_costo = new_row["Costo (COP)"]
                        hist = orig.get("historial_precios") or []
                        hist.append({"fecha":hoy(),"precio":nuevo_costo,"precio_anterior":orig.get("costo",0)})
                        upd["costo"] = nuevo_costo
                        upd["historial_precios"] = hist
                    if (orig.get("proveedor") or "") != new_row["Proveedor"]:    upd["proveedor"]   = new_row["Proveedor"]
                    if int(orig.get("vida_util",0)) != int(new_row["Vida útil (d)"]): upd["vida_util"] = int(new_row["Vida útil (d)"])
                    if upd:
                        db.update_insumo(orig["id"], upd); cambios += 1
                if cambios:
                    st.success(f"✅ {cambios} insumo(s) actualizados"); reload()
                else:
                    st.info("No se detectaron cambios.")

            st.markdown("---"); st.subheader("🗑️ Eliminar insumo")
            sel_del = st.selectbox("Selecciona insumo a eliminar", ["— Selecciona —"] + [i["nombre"] for i in lista], key="del_ins")
            if sel_del != "— Selecciona —":
                ins_del = next(i for i in lista if i["nombre"] == sel_del)
                if st.button(f"🗑️ Eliminar '{sel_del}'", type="secondary"):
                    db.delete_insumo(ins_del["id"]); st.warning("Eliminado"); reload()
        else:
            st.info("Sin insumos. Agrega en ➕ o importa un CSV.")

    # ── STOCK INICIAL ──────────────────────────────────────────────────────────
    with tab_stock0:
        st.subheader("📊 Stock inicial importado")
        st.markdown("Este es el inventario con el que arrancas. Fue importado desde tu archivo Excel.")

        con_stock  = [i for i in insumos if (i.get("stock") or 0) > 0]
        sin_stock  = [i for i in insumos if (i.get("stock") or 0) <= 0]
        valor_total= sum(i.get("stock",0)*i.get("costo",0) for i in insumos)

        k1,k2,k3,k4 = st.columns(4)
        kpi(k1, len(insumos),    "Total insumos")
        kpi(k2, len(con_stock),  "Con stock", "ok")
        kpi(k3, len(sin_stock),  "Sin stock / en 0", "warn" if sin_stock else "ok")
        kpi(k4, fmt_cop(round(valor_total/1000))+"k", "Valor total inventario")

        st.markdown("---")
        cat_s0 = st.selectbox("Filtrar categoría", ["Todas"]+CATEGORIAS, key="s0_cat")
        busq_s0= st.text_input("🔍 Buscar", key="s0_busq")
        mostrar_s0 = st.radio("Mostrar", ["Todos","Con stock","Sin stock / en 0"], horizontal=True, key="s0_filt")

        lista_s0 = insumos
        if cat_s0 != "Todas":    lista_s0 = [i for i in lista_s0 if i.get("categoria")==cat_s0]
        if busq_s0:              lista_s0 = [i for i in lista_s0 if busq_s0.lower() in i["nombre"].lower()]
        if mostrar_s0 == "Con stock":         lista_s0 = [i for i in lista_s0 if (i.get("stock") or 0) > 0]
        elif mostrar_s0 == "Sin stock / en 0":lista_s0 = [i for i in lista_s0 if (i.get("stock") or 0) <= 0]

        df_s0 = pd.DataFrame([{
            "Nombre":      i["nombre"],
            "Categoría":   i.get("categoria",""),
            "Unidad":      i.get("unidad",""),
            "Stock actual":float(i.get("stock",0)),
            "Stock mínimo":float(i.get("minimo",0)),
            "Costo unit.": float(i.get("costo",0)),
            "Valor total": round(i.get("stock",0)*i.get("costo",0)),
            "Estado":      "⚠️ Bajo" if i.get("minimo",0)>0 and i.get("stock",0)<=i.get("minimo",0)
                           else ("📭 Sin stock" if (i.get("stock") or 0)<=0 else "✓ OK"),
        } for i in lista_s0])

        st.markdown(f"**{len(lista_s0)} insumos**")
        st.dataframe(df_s0, hide_index=True, use_container_width=True,
            column_config={
                "Stock actual": st.column_config.NumberColumn(format="%.2f"),
                "Stock mínimo": st.column_config.NumberColumn(format="%.2f"),
                "Costo unit.":  st.column_config.NumberColumn(format="%d"),
                "Valor total":  st.column_config.NumberColumn(format="%d"),
            })
        st.download_button(
            "⬇️ Exportar stock inicial (CSV)",
            df_s0.to_csv(index=False).encode("utf-8"),
            f"stock_inicial_{hoy()}.csv", "text/csv", use_container_width=True
        )

    # ── MÍNIMOS / ALERTAS ─────────────────────────────────────────────────────
    with tab_minimos:
        st.subheader("🔔 Configurar stock mínimo por insumo")
        st.markdown(
            "Define el stock mínimo de cada insumo. Cuando el stock caiga **por debajo** "
            "de ese valor, aparecerá una alerta en el Dashboard y en el módulo Alertas. "
            "**Doble clic en 'Stock mínimo'** para editar. Luego pulsa **💾 Guardar mínimos**."
        )

        # resumen alertas actuales
        bajo_m = [i for i in insumos if i.get("minimo",0)>0 and i.get("stock",0)<=i["minimo"]]
        sin_min= [i for i in insumos if (i.get("minimo") or 0)==0]
        ma1,ma2,ma3 = st.columns(3)
        kpi(ma1, len(bajo_m),  "Insumos bajo mínimo ahora", "danger" if bajo_m else "ok")
        kpi(ma2, len(sin_min), "Sin mínimo definido",       "warn"   if sin_min else "ok")
        kpi(ma3, len(insumos)-len(sin_min), "Con mínimo definido", "ok")

        st.markdown("---")
        fm1,fm2 = st.columns([3,2])
        busq_m2 = fm1.text_input("🔍 Buscar insumo", key="min_busq")
        cat_m2  = fm2.selectbox("Categoría", ["Todas"]+CATEGORIAS, key="min_cat")
        solo_sin= st.checkbox("Mostrar solo insumos SIN mínimo definido", key="min_solo_sin")

        lista_m2 = insumos
        if busq_m2:      lista_m2 = [i for i in lista_m2 if busq_m2.lower() in i["nombre"].lower()]
        if cat_m2 != "Todas": lista_m2 = [i for i in lista_m2 if i.get("categoria")==cat_m2]
        if solo_sin:     lista_m2 = [i for i in lista_m2 if (i.get("minimo") or 0)==0]

        df_min = pd.DataFrame([{
            "_id":          i["id"],
            "Nombre":       i["nombre"],
            "Categoría":    i.get("categoria",""),
            "Unidad":       i.get("unidad",""),
            "Stock actual": float(i.get("stock",0)),
            "Stock mínimo": float(i.get("minimo",0)),
            "Alerta":       "🔴 BAJO" if i.get("minimo",0)>0 and i.get("stock",0)<=i["minimo"]
                            else ("⚪ Sin mínimo" if (i.get("minimo") or 0)==0 else "🟢 OK"),
        } for i in lista_m2])

        edited_min = st.data_editor(
            df_min,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                "_id":          st.column_config.Column(disabled=True, width="small"),
                "Nombre":       st.column_config.Column(disabled=True),
                "Categoría":    st.column_config.Column(disabled=True),
                "Unidad":       st.column_config.Column(disabled=True),
                "Stock actual": st.column_config.NumberColumn(disabled=True, format="%.2f"),
                "Stock mínimo": st.column_config.NumberColumn("Stock mínimo ✏️", step=0.5, format="%.2f",
                                    help="Edita este valor. Si stock actual ≤ mínimo → alerta roja."),
                "Alerta":       st.column_config.Column(disabled=True),
            },
            key="edit_minimos_table",
        )

        if st.button("💾 Guardar mínimos", type="primary", use_container_width=True):
            cambios_m = 0
            for orig, new_row in zip(lista_m2, edited_min.to_dict("records")):
                nuevo_min = new_row["Stock mínimo"]
                if float(orig.get("minimo",0)) != nuevo_min:
                    db.update_insumo(orig["id"], {"minimo": nuevo_min})
                    cambios_m += 1
            if cambios_m:
                st.success(f"✅ {cambios_m} mínimos actualizados — las alertas se activarán automáticamente.")
                reload()
            else:
                st.info("No se detectaron cambios.")

    with tab_add:
        with st.form("add_ins",clear_on_submit=True):
            r1,r2=st.columns(2)
            nombre=r1.text_input("Nombre *"); cat=r2.selectbox("Categoría",CATEGORIAS)
            r3,r4,r5=st.columns(3)
            unidad=r3.selectbox("Unidad",UNIDADES)
            stock=r4.number_input("Stock inicial",min_value=0.0,step=0.5)
            minimo=r5.number_input("Stock mínimo",min_value=0.0,step=0.5)
            r6,r7,r8=st.columns(3)
            costo=r6.number_input("Costo por unidad (COP)",min_value=0.0,step=100.0)
            proveedor=r7.text_input("Proveedor"); vida_util=r8.number_input("Vida útil (días)",min_value=0,step=1)
            if st.form_submit_button("💾 Guardar insumo",use_container_width=True):
                if not nombre.strip(): st.error("El nombre es obligatorio")
                else:
                    db.add_insumo({"nombre":nombre.strip(),"categoria":cat,"unidad":unidad,"stock":stock,
                        "minimo":minimo,"costo":costo,"proveedor":proveedor.strip(),"vida_util":vida_util,
                        "ultima_entrada":hoy(),"historial_precios":[{"fecha":hoy(),"precio":costo}] if costo>0 else []})
                    st.success(f"✅ Insumo guardado: {nombre}"); reload()

    with tab_imp:
        st.subheader("Importar insumos desde CSV")
        st.markdown("**Columnas requeridas:** `nombre, categoria, unidad, stock, minimo, costo, proveedor, vida_util`")
        plantilla=pd.DataFrame([{"nombre":"Harina","categoria":"Granos / Harinas","unidad":"kg","stock":10,"minimo":2,"costo":3500,"proveedor":"Ejemplo","vida_util":0}])
        st.download_button("⬇️ Descargar plantilla CSV",plantilla.to_csv(index=False).encode("utf-8"),"plantilla_insumos.csv","text/csv")
        uploaded=st.file_uploader("Sube tu archivo CSV",type=["csv"])
        if uploaded:
            try:
                df_up=pd.read_csv(uploaded); df_up.columns=[c.strip().lower().replace(" ","_") for c in df_up.columns]
                st.dataframe(df_up.head(10),hide_index=True,use_container_width=True)
                if st.button("✅ Confirmar importación",type="primary"):
                    nombres_exist={i["nombre"].lower():i for i in insumos}
                    creados=actualizados=errores=0
                    for _,row in df_up.iterrows():
                        try:
                            n=str(row.get("nombre","")).strip()
                            if not n: continue
                            d={"nombre":n,"categoria":str(row.get("categoria","Otros")),
                               "unidad":str(row.get("unidad","unidad")),"stock":float(row.get("stock",0) or 0),
                               "minimo":float(row.get("minimo",0) or 0),"costo":float(row.get("costo",0) or 0),
                               "proveedor":str(row.get("proveedor","") or ""),"vida_util":int(row.get("vida_util",0) or 0),
                               "ultima_entrada":hoy()}
                            if n.lower() in nombres_exist:
                                db.update_insumo(nombres_exist[n.lower()]["id"],d); actualizados+=1
                            else:
                                d["historial_precios"]=[{"fecha":hoy(),"precio":d["costo"]}] if d["costo"]>0 else []
                                db.add_insumo(d); creados+=1
                        except Exception: errores+=1
                    st.success(f"✅ {creados} creados, {actualizados} actualizados, {errores} errores"); reload()
            except Exception as e: st.error(f"Error: {e}")

    with tab_exp:
        if not insumos: st.info("No hay insumos para exportar.")
        else:
            df_exp=pd.DataFrame([{"nombre":i["nombre"],"categoria":i.get("categoria",""),"unidad":i.get("unidad",""),
                "stock":i.get("stock",0),"minimo":i.get("minimo",0),"costo":i.get("costo",0),
                "proveedor":i.get("proveedor",""),"vida_util":i.get("vida_util",0),
                "valor_total":round(i.get("stock",0)*i.get("costo",0))} for i in insumos])
            st.dataframe(df_exp,hide_index=True,use_container_width=True)
            st.download_button(f"⬇️ Exportar inventario ({len(insumos)} insumos)",
                df_exp.to_csv(index=False).encode("utf-8"),f"inventario_{hoy()}.csv","text/csv",use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  RECETAS
# ══════════════════════════════════════════════════════════════════════════════
elif current == "recetas":
    st.title("📋 Recetas")
    tab_list,tab_add,tab_imp,tab_exp,tab_cf = st.tabs(["📋 Listado","➕ Nueva receta","📥 Importar","📤 Exportar","⚙️ Costos fijos"])

    with tab_cf:
        st.subheader("Costos fijos de cocina")
        # Resumen del % actual
        if cf_items and ventas_esperadas>0:
            _tot_act=sum(float(i.get("monto",0)) for i in cf_items if i.get("activo",True))
            st.success(f"% costos fijos vigente: **{costos_fijos}%** — calculado desde {len([i for i in cf_items if i.get('activo',True)])} rubro(s) activo(s) · Total: {fmt_cop(round(_tot_act))}/mes")
            st.caption("🥤 Aplica solo a recetas de comida. Las bebidas cargan 0% de costos fijos.")
            with st.expander("Ver detalle de costos fijos",expanded=False):
                rows_cfi=[{"Ítem":i["nombre"],"Monto":fmt_cop(i.get("monto",0)),"Estado":"✅ Activo" if i.get("activo",True) else "⏸️ Inactivo"} for i in cf_items]
                st.dataframe(pd.DataFrame(rows_cfi),hide_index=True,use_container_width=True)
                st.caption("Para agregar o modificar costos fijos, ve a ⚙️ Configuración → 💰 Costos Fijos.")
        else:
            st.info(f"% costos fijos aplicado: **{costos_fijos}%** (configurado manualmente en ⚙️ Configuración)")
        # Impacto en recetas
        if recetas:
            st.markdown("---")
            rows_cf=[]
            for r in recetas[:20]:
                _pct=cf_cat(r.get("categoria",""))
                ci=calc.costo_ingredientes_receta(r,insumos,subrecetas)
                ct=calc.costo_receta(r,insumos,subrecetas,_pct)
                m=calc.margen_receta(r,insumos,subrecetas,_pct)
                rows_cf.append({"Receta":r["nombre"],"Categoría":r.get("categoria",""),
                    "CF%":f"{_pct}%","Costo ing.":fmt_cop(round(ci)),
                    "Costos fijos":fmt_cop(round(ci*_pct/100)),"Costo total":fmt_cop(round(ct)),
                    "Precio venta":fmt_cop(r.get("precio",0)),"Margen":f"{m:.1f}%" if m is not None else "—"})
            st.dataframe(pd.DataFrame(rows_cf),hide_index=True,use_container_width=True)

    with tab_add:
        if not insumos and not subrecetas:
            st.warning("Agrega insumos primero.")
        else:
            n_r=st.text_input("Nombre de la receta *")
            rc1,rc2,rc3=st.columns(3)
            cat_r=rc1.selectbox("Categoría",CAT_RECETA)
            porc_r=rc2.number_input("Porciones",min_value=1,value=1)
            prec_r=rc3.number_input("Precio de venta (COP)",min_value=0.0,step=1000.0)
            req_leche_r=st.checkbox("🥛 Lleva leche (el cliente elige el tipo al vender)",
                help="Marca esto en bebidas con leche. NO incluyas la leche en los ingredientes: se elige y se descuenta al registrar la venta.")
            st.markdown("**Ingredientes**")
            if "ing_rows" not in st.session_state: st.session_state.ing_rows=[{}]
            opts_ing={}
            for i in insumos: opts_ing[f"📦 {i['nombre']} ({i.get('unidad','')})"]=f"ins:{i['id']}"
            for s in subrecetas: opts_ing[f"🧪 {s['nombre']} / {s.get('rendimiento',1)}{s.get('unidad_rendimiento','')}"]=f"sub:{s['id']}"
            labels_ing=list(opts_ing.keys()); ing_data=[]
            for idx in range(len(st.session_state.ing_rows)):
                ic1,ic2,ic3,ic4=st.columns([4,1.5,1.5,0.5])
                sel_i=ic1.selectbox("Ingrediente",["— Selecciona —"]+labels_ing,key=f"ri_{idx}")
                cant=ic2.number_input("Cant. neta",min_value=0.0,step=0.01,key=f"rc_{idx}")
                merma=ic3.number_input("Merma %",min_value=0.0,max_value=99.0,step=0.5,key=f"rm_{idx}")
                if ic4.button("✕",key=f"rd_{idx}"): st.session_state.ing_rows.pop(idx); st.rerun()
                if sel_i!="— Selecciona —":
                    rid=opts_ing[sel_i]; ing_data.append({"ref_id":rid,"cantidad":cant,"merma":merma})
                    bruta=calc.cant_bruta(cant,merma); ref=calc.resolve_ref(rid,insumos,subrecetas)
                    st.caption(f"  ↳ Bruta: **{bruta:.3f} {ref['unidad']}** | Costo: **{fmt_cop(round(ref['costo_unit']*bruta))}**")
            if st.button("➕ Agregar ingrediente"): st.session_state.ing_rows.append({}); st.rerun()
            if ing_data:
                ci=sum(calc.costo_ingrediente(i["ref_id"],i["cantidad"],i["merma"],insumos,subrecetas) for i in ing_data)
                _pct_new=cf_cat(cat_r); ct=ci*(1+_pct_new/100); m=(prec_r-ct)/prec_r*100 if prec_r>0 else None
                st.info(f"💰 Costo ingredientes: **{fmt_cop(round(ci))}** | CF {_pct_new}%: **{fmt_cop(round(ci*_pct_new/100))}** | Costo total: **{fmt_cop(round(ct))}** | Margen: **{f'{m:.1f}%' if m is not None else '—'}**")
            if st.button("💾 Guardar receta",type="primary"):
                if not n_r.strip(): st.error("El nombre es obligatorio")
                elif not ing_data: st.error("Agrega al menos un ingrediente")
                else:
                    db.add_receta({"nombre":n_r.strip(),"categoria":cat_r,"porciones":porc_r,"precio":prec_r,"ingredientes":ing_data,"requiere_leche":req_leche_r})
                    st.session_state.ing_rows=[{}]; st.success(f"✅ Receta guardada: {n_r}"); reload()

    with tab_imp:
        st.subheader("Importar recetas desde JSON")
        st.markdown("Sube un archivo JSON exportado previamente desde esta misma app.")
        up_r=st.file_uploader("Archivo JSON de recetas",type=["json"])
        if up_r:
            try:
                recetas_imp=json.load(up_r)
                if not isinstance(recetas_imp,list): recetas_imp=[recetas_imp]
                st.markdown(f"**{len(recetas_imp)} recetas en el archivo:**")
                st.dataframe(pd.DataFrame([{"Nombre":r.get("nombre"),"Categoría":r.get("categoria"),
                    "Precio":fmt_cop(r.get("precio",0)),"Ingredientes":len(r.get("ingredientes",[]))} for r in recetas_imp]),
                    hide_index=True,use_container_width=True)
                if st.button("✅ Importar recetas",type="primary"):
                    nombres_exist={r["nombre"].lower() for r in recetas}
                    creadas=omitidas=0
                    for r in recetas_imp:
                        if r.get("nombre","").lower() not in nombres_exist:
                            db.add_receta({"nombre":r.get("nombre"),"categoria":r.get("categoria","Plato Principal"),
                                "porciones":r.get("porciones",1),"precio":r.get("precio",0),"ingredientes":r.get("ingredientes",[])})
                            creadas+=1
                        else: omitidas+=1
                    st.success(f"✅ {creadas} recetas importadas, {omitidas} omitidas (ya existían)"); reload()
            except Exception as e: st.error(f"Error al leer el archivo: {e}")

    with tab_exp:
        st.subheader("Exportar recetas a JSON")
        if not recetas: st.info("Sin recetas para exportar.")
        else:
            fcat_e=st.selectbox("Filtrar categoría",["Todas"]+CAT_RECETA,key="rcat_exp")
            lista_exp=[r for r in recetas if fcat_e=="Todas" or r.get("categoria")==fcat_e]
            st.markdown(f"**{len(lista_exp)} recetas**")
            export_data=[{"nombre":r["nombre"],"categoria":r.get("categoria"),"porciones":r.get("porciones",1),
                "precio":r.get("precio",0),"ingredientes":r.get("ingredientes",[])} for r in lista_exp]
            st.download_button(f"⬇️ Exportar {len(lista_exp)} recetas (JSON)",
                json.dumps(export_data,ensure_ascii=False,indent=2).encode("utf-8"),
                f"recetas_{hoy()}.json","application/json",use_container_width=True)

    with tab_list:
        fl1, fl2 = st.columns([3,2])
        busq_r = fl1.text_input("🔍 Buscar receta", key="busq_r")
        catf   = fl2.selectbox("Filtrar categoría", ["Todas"]+CAT_RECETA, key="rcatf")
        lista_r = [r for r in recetas
                   if (not busq_r or busq_r.lower() in r["nombre"].lower())
                   and (catf=="Todas" or r.get("categoria")==catf)]
        if not lista_r:
            st.info("Sin recetas.")
        else:
            st.markdown(f"**{len(lista_r)} recetas** — haz clic en el nombre para ver el detalle")
            # Agrupar por categoría
            cats_presentes = sorted({r.get("categoria","Sin categoría") for r in lista_r})
            for cat in cats_presentes:
                recetas_cat = [r for r in lista_r if r.get("categoria","Sin categoría")==cat]
                st.markdown(f"##### 🍽️ {cat} ({len(recetas_cat)})")
                # mapa nombre→ref_id para el selector de ingredientes
                opts_rec = {}
                for _ins in insumos:
                    opts_rec[_ins["nombre"]] = f"ins:{_ins['id']}"
                for _sub in subrecetas:
                    opts_rec[f"🧪 {_sub['nombre']}"] = f"sub:{_sub['id']}"
                opts_names_rec = list(opts_rec.keys())

                for rec in recetas_cat:
                    ci = calc.costo_ingredientes_receta(rec, insumos, subrecetas)
                    _pct=cf_cat(rec.get("categoria",""))
                    ct = calc.costo_receta(rec, insumos, subrecetas, _pct)
                    m  = calc.margen_receta(rec, insumos, subrecetas, _pct)
                    margen_txt = f"{m:.1f}%" if m is not None else "—"
                    label = f"**{rec['nombre']}** — Precio: {fmt_cop(rec.get('precio',0))} · Costo: {fmt_cop(round(ct))} · Margen: {margen_txt}"
                    with st.expander(label, expanded=False):
                        mc1,mc2,mc3,mc4 = st.columns(4)
                        mc1.metric("Precio venta",       fmt_cop(rec.get("precio",0)))
                        mc2.metric("Costo ingredientes", fmt_cop(round(ci)))
                        mc3.metric("Costo total",        fmt_cop(round(ct)))
                        mc4.metric("Margen",             margen_txt)

                        # ── opción: lleva leche (cliente elige tipo al vender) ──
                        req_leche_e = st.checkbox(
                            "🥛 Lleva leche (el cliente elige el tipo al vender)",
                            value=bool(rec.get("requiere_leche")),
                            key=f"reqleche_{rec['id']}",
                            help="Bebida con leche: NO incluyas la leche en los ingredientes; se elige y descuenta en la venta.")

                        # ── editor de ingredientes ──────────────────────────
                        st.markdown("**✏️ Ingredientes** — edita cantidades, merma, cambia o agrega ingredientes:")
                        ing_list = rec.get("ingredientes", [])
                        rows_ing = []
                        for ing in ing_list:
                            ref   = calc.resolve_ref(ing.get("ref_id",""), insumos, subrecetas)
                            cant  = ing.get("cantidad", ing.get("cant_neta", 0))
                            merma = ing.get("merma", 0)
                            bruta = calc.cant_bruta(cant, merma)
                            rid   = ing.get("ref_id","")
                            disp  = next((k for k,v in opts_rec.items() if v==rid), ref["nombre"])
                            rows_ing.append({
                                "Ingrediente": disp,
                                "Cant. neta":  float(cant),
                                "Merma %":     float(merma),
                                "Cant. bruta": round(bruta, 3),
                                "Unidad":      ref["unidad"],
                                "Costo":       fmt_cop(round(ref["costo_unit"] * bruta)),
                            })
                        edited_ing = st.data_editor(
                            pd.DataFrame(rows_ing) if rows_ing else pd.DataFrame(columns=["Ingrediente","Cant. neta","Merma %","Cant. bruta","Unidad","Costo"]),
                            hide_index=True,
                            use_container_width=True,
                            num_rows="dynamic",
                            column_config={
                                "Ingrediente": st.column_config.SelectboxColumn("Ingrediente", options=opts_names_rec, required=True, width="large"),
                                "Cant. neta":  st.column_config.NumberColumn("Cant. neta",  step=0.001, format="%.3f", min_value=0),
                                "Merma %":     st.column_config.NumberColumn("Merma %",     step=0.5,   format="%.1f", min_value=0, max_value=99),
                                "Cant. bruta": st.column_config.NumberColumn("Cant. bruta", disabled=True, format="%.3f"),
                                "Unidad":      st.column_config.Column("Unidad", disabled=True, width="small"),
                                "Costo":       st.column_config.Column("Costo",  disabled=True, width="small"),
                            },
                            key=f"edit_rec_ing_{rec['id']}",
                        )
                        ri_c1, ri_c2 = st.columns([2,1])
                        if ri_c1.button("💾 Guardar ingredientes", type="primary", key=f"save_rec_{rec['id']}"):
                            nuevos_ing = []
                            for _, row in edited_ing.iterrows():
                                nombre_sel = row.get("Ingrediente","")
                                if not nombre_sel: continue
                                ref_id = opts_rec.get(nombre_sel, "")
                                if not ref_id: continue
                                nuevos_ing.append({
                                    "ref_id":    ref_id,
                                    "cantidad":  float(row["Cant. neta"] or 0),
                                    "cant_neta": float(row["Cant. neta"] or 0),
                                    "merma":     float(row["Merma %"] or 0),
                                })
                            db.update_receta(rec["id"], {"ingredientes": nuevos_ing, "requiere_leche": req_leche_e})
                            st.success("✅ Ingredientes actualizados"); reload()
                        if ri_c2.button("🗑️ Eliminar receta", type="secondary", key=f"del_rec_{rec['id']}"):
                            db.delete_receta(rec["id"]); st.warning("Receta eliminada"); reload()


# ══════════════════════════════════════════════════════════════════════════════
#  SUB-RECETAS
# ══════════════════════════════════════════════════════════════════════════════
elif current == "subrecetas":
    st.title("🧪 Sub-recetas")
    tab_list,tab_add,tab_imp,tab_exp=st.tabs(["📋 Listado","➕ Nueva","📥 Importar","📤 Exportar"])

    with tab_add:
        # ── Atajo: crear los panes de sanduche ──
        PANES_SANDUCHE=["Croissant La O","Croissant tradicional","Porción pan baguette",
                        "Porción pan masa madre","Bagel"]
        _panes_existentes={(s.get("nombre") or "").strip().lower() for s in subrecetas
                           if s.get("categoria")==CAT_PAN_SUB}
        _panes_faltan=[p for p in PANES_SANDUCHE if p.lower() not in _panes_existentes]
        if _panes_faltan:
            with st.expander(f"🍞 Crear panes de sanduche ({len(_panes_faltan)} faltan)",expanded=False):
                st.caption("Crea los tipos de pan que el cliente puede elegir en los sanduches. "
                           "Se crean vacíos (sin ingredientes) para que el selector funcione de inmediato; "
                           "luego edita cada uno y agrégale sus insumos para que descuente del inventario.")
                st.write("• "+"  \n• ".join(_panes_faltan))
                if st.button("🍞 Crear estos panes",use_container_width=True):
                    for p in _panes_faltan:
                        db.add_subreceta({"nombre":p,"categoria":CAT_PAN_SUB,"rendimiento":1,
                                          "unidad_rendimiento":"unidad","ingredientes":[]})
                    st.success(f"✅ {len(_panes_faltan)} pan(es) creado(s) con categoría «{CAT_PAN_SUB}». "
                               "Edítalos para agregar sus ingredientes."); reload()

        if not insumos: st.warning("Agrega insumos primero.")
        else:
            n_s=st.text_input("Nombre de la sub-receta *")
            sc1,sc2,sc3=st.columns(3)
            cat_s=sc1.selectbox("Categoría",["Base","Salsa","Aliño","Masa","Relleno","Pastelería","Panadería","Tipo de pan","Tipo de leche","Otro"])
            rend_s=sc2.number_input("Rendimiento",min_value=0.01,step=1.0)
            u_s=sc3.selectbox("Unidad rendimiento",UNIDADES)
            st.markdown("**Ingredientes**")
            if "sub_rows" not in st.session_state: st.session_state.sub_rows=[{}]
            opts_s={f"📦 {i['nombre']} ({i.get('unidad','')})":f"ins:{i['id']}" for i in insumos}
            sub_data=[]
            for idx in range(len(st.session_state.sub_rows)):
                si1,si2,si3,si4=st.columns([4,1.5,1.5,0.5])
                sel_s=si1.selectbox("Ingrediente",["— Selecciona —"]+list(opts_s.keys()),key=f"si_{idx}")
                cant_s=si2.number_input("Cant.",min_value=0.0,step=0.01,key=f"sc_{idx}")
                merma_s=si3.number_input("Merma %",min_value=0.0,max_value=99.0,key=f"sm_{idx}")
                if si4.button("✕",key=f"sd_{idx}"): st.session_state.sub_rows.pop(idx); st.rerun()
                if sel_s!="— Selecciona —": sub_data.append({"ref_id":opts_s[sel_s],"cantidad":cant_s,"merma":merma_s})
            if st.button("➕ Agregar ingrediente",key="sub_add"): st.session_state.sub_rows.append({}); st.rerun()
            if sub_data and rend_s>0:
                ct_s=sum(calc.costo_ingrediente(i["ref_id"],i["cantidad"],i["merma"],insumos,subrecetas) for i in sub_data)
                st.info(f"💰 Costo elaboración: **{fmt_cop(round(ct_s))}** | Costo/{u_s}: **{fmt_cop(round(ct_s/rend_s))}**")
            if st.button("💾 Guardar sub-receta",type="primary"):
                if not n_s.strip(): st.error("El nombre es obligatorio")
                elif rend_s<=0: st.error("Define el rendimiento")
                elif not sub_data: st.error("Agrega al menos un ingrediente")
                else:
                    db.add_subreceta({"nombre":n_s.strip(),"categoria":cat_s,"rendimiento":rend_s,
                        "unidad_rendimiento":u_s,"ingredientes":sub_data})
                    st.session_state.sub_rows=[{}]; st.success(f"✅ Sub-receta guardada: {n_s}"); reload()

    with tab_imp:
        st.subheader("Importar sub-recetas desde JSON")
        up_s=st.file_uploader("Archivo JSON de sub-recetas",type=["json"])
        if up_s:
            try:
                subs_imp=json.load(up_s)
                if not isinstance(subs_imp,list): subs_imp=[subs_imp]
                st.markdown(f"**{len(subs_imp)} sub-recetas en el archivo**")
                if st.button("✅ Importar sub-recetas",type="primary"):
                    nombres_exist={s["nombre"].lower() for s in subrecetas}
                    creadas=omitidas=0
                    for s in subs_imp:
                        if s.get("nombre","").lower() not in nombres_exist:
                            db.add_subreceta({"nombre":s.get("nombre"),"categoria":s.get("categoria","Base"),
                                "rendimiento":s.get("rendimiento",1),"unidad_rendimiento":s.get("unidad_rendimiento","g"),
                                "ingredientes":s.get("ingredientes",[])})
                            creadas+=1
                        else: omitidas+=1
                    st.success(f"✅ {creadas} importadas, {omitidas} omitidas"); reload()
            except Exception as e: st.error(f"Error: {e}")

    with tab_exp:
        if not subrecetas: st.info("Sin sub-recetas para exportar.")
        else:
            export_s=[{"nombre":s["nombre"],"categoria":s.get("categoria"),"rendimiento":s.get("rendimiento"),
                "unidad_rendimiento":s.get("unidad_rendimiento"),"ingredientes":s.get("ingredientes",[])} for s in subrecetas]
            st.download_button(f"⬇️ Exportar {len(subrecetas)} sub-recetas (JSON)",
                json.dumps(export_s,ensure_ascii=False,indent=2).encode("utf-8"),
                f"subrecetas_{hoy()}.json","application/json",use_container_width=True)

    with tab_list:
        if not subrecetas: st.info("Sin sub-recetas aún.")
        else:
            busq_s2 = st.text_input("🔍 Buscar sub-receta", key="busq_sub")
            lista_s2 = [s for s in subrecetas
                        if not busq_s2 or busq_s2.lower() in s["nombre"].lower()]
            st.markdown(f"**{len(lista_s2)} sub-recetas** — haz clic en el nombre para ver el detalle")
            # mapa nombre→ref_id para selector de sub-recetas
            opts_sub = {}
            for _ins in insumos:
                opts_sub[_ins["nombre"]] = f"ins:{_ins['id']}"
            opts_names_sub = list(opts_sub.keys())

            cats_sub = sorted({s.get("categoria","Sin categoría") for s in lista_s2})
            for cat in cats_sub:
                subs_cat = [s for s in lista_s2 if s.get("categoria","Sin categoría")==cat]
                st.markdown(f"##### 🧪 {cat} ({len(subs_cat)})")
                for sub in subs_cat:
                    ct_sub = calc.costo_subreceta(sub, insumos, subrecetas)
                    rend   = sub.get("rendimiento",1) or 1
                    label  = f"**{sub['nombre']}** — Rend: {rend} {sub.get('unidad_rendimiento','')} · Costo: {fmt_cop(round(ct_sub))} · Costo/u: {fmt_cop(round(ct_sub/rend))}"
                    with st.expander(label, expanded=False):
                        km1, km2, km3 = st.columns(3)
                        km1.metric("Rendimiento",       f"{rend} {sub.get('unidad_rendimiento','')}")
                        km2.metric("Costo elaboración", fmt_cop(round(ct_sub)))
                        km3.metric("Costo / unidad",    fmt_cop(round(ct_sub/rend)))

                        # ── editor de ingredientes ──────────────────────────
                        st.markdown("**✏️ Ingredientes** — edita cantidades, merma, cambia o agrega ingredientes:")
                        ing_list_s = sub.get("ingredientes", [])
                        rows_si = []
                        for ing in ing_list_s:
                            ref   = calc.resolve_ref(ing.get("ref_id",""), insumos, subrecetas)
                            cant  = ing.get("cantidad", ing.get("cant_neta", 0))
                            merma = ing.get("merma", 0)
                            bruta = calc.cant_bruta(cant, merma)
                            rid   = ing.get("ref_id","")
                            disp  = next((k for k,v in opts_sub.items() if v==rid), ref["nombre"])
                            rows_si.append({
                                "Ingrediente": disp,
                                "Cant. neta":  float(cant),
                                "Merma %":     float(merma),
                                "Cant. bruta": round(bruta, 3),
                                "Unidad":      ref.get("unidad",""),
                                "Costo":       fmt_cop(round(ref["costo_unit"] * bruta)),
                            })
                        edited_si = st.data_editor(
                            pd.DataFrame(rows_si) if rows_si else pd.DataFrame(columns=["Ingrediente","Cant. neta","Merma %","Cant. bruta","Unidad","Costo"]),
                            hide_index=True,
                            use_container_width=True,
                            num_rows="dynamic",
                            column_config={
                                "Ingrediente": st.column_config.SelectboxColumn("Ingrediente", options=opts_names_sub, required=True, width="large"),
                                "Cant. neta":  st.column_config.NumberColumn("Cant. neta",  step=0.001, format="%.3f", min_value=0),
                                "Merma %":     st.column_config.NumberColumn("Merma %",     step=0.5,   format="%.1f", min_value=0, max_value=99),
                                "Cant. bruta": st.column_config.NumberColumn("Cant. bruta", disabled=True, format="%.3f"),
                                "Unidad":      st.column_config.Column("Unidad", disabled=True, width="small"),
                                "Costo":       st.column_config.Column("Costo",  disabled=True, width="small"),
                            },
                            key=f"edit_sub_ing_{sub['id']}",
                        )
                        si_c1, si_c2 = st.columns([2,1])
                        if si_c1.button("💾 Guardar ingredientes", type="primary", key=f"save_sub_{sub['id']}"):
                            nuevos_si = []
                            for _, row in edited_si.iterrows():
                                nombre_sel = row.get("Ingrediente","")
                                if not nombre_sel: continue
                                ref_id = opts_sub.get(nombre_sel, "")
                                if not ref_id: continue
                                nuevos_si.append({
                                    "ref_id":    ref_id,
                                    "cantidad":  float(row["Cant. neta"] or 0),
                                    "cant_neta": float(row["Cant. neta"] or 0),
                                    "merma":     float(row["Merma %"] or 0),
                                })
                            db.update_subreceta(sub["id"], {"ingredientes": nuevos_si})
                            st.success("✅ Ingredientes actualizados"); reload()
                        if si_c2.button("🗑️ Eliminar sub-receta", type="secondary", key=f"del_sub_{sub['id']}"):
                            db.delete_subreceta(sub["id"]); st.warning("Eliminada"); reload()


# ══════════════════════════════════════════════════════════════════════════════
#  MOVIMIENTOS
# ══════════════════════════════════════════════════════════════════════════════
elif current == "movimientos":
    st.title("🔄 Movimientos de Inventario")
    tab_e,tab_s,tab_v,tab_hist=st.tabs(["📥 Entrada","📤 Salida","🍽️ Venta / Despacho","📋 Historial"])

    with tab_e:
        st.subheader("Registrar entrada")
        tipo_e=st.radio("Tipo de ítem",["🥚 Insumo (materia prima)","🧪 Sub-receta / Elaboración","🍽️ Producto terminado"],
                        horizontal=True,key="radio_tipo_e")
        _te="insumo" if "Insumo" in tipo_e else "subreceta" if "Sub-receta" in tipo_e else "producto"
        if _te=="insumo":
            cat_e={f"{i['nombre']} — stock: {fmt_n(i.get('stock',0))} {i.get('unidad','')}":i for i in insumos}
        elif _te=="subreceta":
            cat_e={f"{s['nombre']} — {s.get('categoria','')} | stock: {fmt_n(s.get('stock') or 0)}":s for s in subrecetas}
        else:
            cat_e={f"{r['nombre']} — {r.get('categoria','')} | stock: {fmt_n(r.get('stock') or 0)}":r for r in recetas}
        if not cat_e:
            st.warning("No hay ítems de este tipo registrados.")
        else:
            with st.form("form_entrada",clear_on_submit=True):
                sel_e=st.selectbox("Ítem *",["— Selecciona —"]+list(cat_e.keys()))
                ec1,ec2=st.columns(2)
                cant_e=ec1.number_input("Cantidad que entra *",min_value=0.0,value=0.0,step=1.0,format="%.3f")
                costo_e=ec2.number_input("Costo/unidad (COP, 0=mantener)",min_value=0.0,step=50.0,format="%.0f")
                ec3,ec4=st.columns(2)
                fecha_e=ec3.date_input("Fecha",value=date.today()); resp_e=ec4.text_input("Responsable")
                prov_e=st.text_input("Proveedor"); nota_e=st.text_input("Nota")
                if st.form_submit_button("✅ Registrar entrada",use_container_width=True,type="primary"):
                    if sel_e=="— Selecciona —": st.error("Selecciona un ítem")
                    elif cant_e<=0: st.error("Ingresa una cantidad mayor a 0")
                    else:
                        item_e=cat_e[sel_e]; nc=costo_e if costo_e>0 else item_e.get("costo",0)
                        if _te=="insumo":
                            upd={"stock":item_e.get("stock",0)+cant_e,"ultima_entrada":str(fecha_e)}
                            if costo_e>0 and costo_e!=item_e.get("costo",0):
                                hist=item_e.get("historial_precios") or []
                                hist.append({"fecha":str(fecha_e),"precio":costo_e,"precio_anterior":item_e.get("costo",0)})
                                upd["costo"]=costo_e; upd["historial_precios"]=hist
                            db.update_insumo(item_e["id"],upd)
                        elif _te=="subreceta":
                            try: db.update_subreceta(item_e["id"],{"stock":(item_e.get("stock") or 0)+cant_e})
                            except: pass
                        else:
                            try: db.update_receta(item_e["id"],{"stock":(item_e.get("stock") or 0)+cant_e})
                            except: pass
                        db.add_movimiento({"tipo":"entrada","insumo_id":item_e["id"],"nombre":item_e["nombre"],
                            "cantidad":cant_e,"costo_unit":nc,"fecha":str(fecha_e),
                            "responsable":resp_e or "—","nota":f"[{_te}] {nota_e}".strip(),"proveedor":prov_e})
                        unidad_e=item_e.get("unidad","und")
                        st.success(f"✅ +{fmt_n(cant_e)} {unidad_e} de **{item_e['nombre']}**"); reload()

    with tab_s:
        st.subheader("Registrar salida")
        tipo_s=st.radio("Tipo de ítem",["🥚 Insumo (materia prima)","🧪 Sub-receta / Elaboración","🍽️ Producto terminado"],
                        horizontal=True,key="radio_tipo_s")
        _ts="insumo" if "Insumo" in tipo_s else "subreceta" if "Sub-receta" in tipo_s else "producto"
        if _ts=="insumo":
            cat_s2={f"{i['nombre']} — stock: {fmt_n(i.get('stock',0))} {i.get('unidad','')}":i for i in insumos}
        elif _ts=="subreceta":
            cat_s2={f"{s['nombre']} — {s.get('categoria','')} | stock: {fmt_n(s.get('stock') or 0)}":s for s in subrecetas}
        else:
            cat_s2={f"{r['nombre']} — {r.get('categoria','')} | stock: {fmt_n(r.get('stock') or 0)}":r for r in recetas}
        if not cat_s2:
            st.warning("No hay ítems de este tipo registrados.")
        else:
            with st.form("form_salida",clear_on_submit=True):
                sel_s2=st.selectbox("Ítem *",["— Selecciona —"]+list(cat_s2.keys()))
                sc1,sc2=st.columns(2)
                cant_s2=sc1.number_input("Cantidad que sale *",min_value=0.0,value=0.0,step=1.0,format="%.3f")
                fecha_s2=sc2.date_input("Fecha",value=date.today())
                sc3,sc4=st.columns(2)
                resp_s2=sc3.text_input("Responsable")
                motivo_s=sc4.selectbox("Motivo",["Consumo cocina","Merma","Transferencia","Otro"])
                nota_s2=st.text_input("Nota adicional")
                if st.form_submit_button("✅ Registrar salida",use_container_width=True,type="primary"):
                    if sel_s2=="— Selecciona —": st.error("Selecciona un ítem")
                    elif cant_s2<=0: st.error("Ingresa una cantidad mayor a 0")
                    else:
                        ins_s2=cat_s2[sel_s2]; stk=ins_s2.get("stock") or 0
                        if cant_s2>stk: st.error(f"Stock insuficiente: {fmt_n(stk)} {ins_s2.get('unidad','und')}")
                        else:
                            ns=stk-cant_s2
                            if _ts=="insumo": db.update_insumo(ins_s2["id"],{"stock":ns})
                            elif _ts=="subreceta":
                                try: db.update_subreceta(ins_s2["id"],{"stock":ns})
                                except: pass
                            else:
                                try: db.update_receta(ins_s2["id"],{"stock":ns})
                                except: pass
                            db.add_movimiento({"tipo":"salida","insumo_id":ins_s2["id"],"nombre":ins_s2["nombre"],
                                "cantidad":cant_s2,"costo_unit":ins_s2.get("costo",0),"fecha":str(fecha_s2),
                                "responsable":resp_s2 or "—","nota":f"[{_ts}] {motivo_s} · {nota_s2}".strip(" ·")})
                            unidad_s=ins_s2.get("unidad","und")
                            st.success(f"✅ -{fmt_n(cant_s2)} {unidad_s} de **{ins_s2['nombre']}** → Stock nuevo: **{fmt_n(ns)}**"); reload()

    with tab_v:
        st.subheader("Registrar venta / despacho de plato")
        if not recetas: st.warning("No hay recetas.")
        else:
            opts_v={r["nombre"]:r for r in recetas}
            sel_v=st.selectbox("Receta *",["— Selecciona —"]+list(opts_v.keys()))
            cant_v=st.number_input("Porciones",min_value=1,step=1,value=1)
            vc1,vc2=st.columns(2)
            fecha_v=vc1.date_input("Fecha",value=date.today()); resp_v=vc2.text_input("Responsable")

            # ── Selectores de variantes (pan / leche) ─────────────────────────
            pan_elegido=None
            leche_elegida=None
            if sel_v!="— Selecciona —":
                rec_v=opts_v[sel_v]
                es_sanduche=rec_v.get("categoria") in CAT_SANDUCHE
                if es_sanduche:
                    if not panes_sub:
                        st.warning("⚠️ No hay sub-recetas con categoría **'Tipo de pan'** registradas. "
                                   "Ve a Sub-recetas → ➕ Nueva y agrégalas con esa categoría.")
                    else:
                        st.markdown("---")
                        opts_pan={"— Selecciona pan —":None}
                        for p in panes_sub: opts_pan[f"🍞 {p['nombre']}  ×{cant_v}"]=p
                        sel_pan=st.selectbox("🍞 Tipo de pan *",list(opts_pan.keys()),key="sel_pan_v")
                        pan_elegido=opts_pan[sel_pan]
                        if pan_elegido:
                            st.caption(f"Ingredientes del pan que también se descontarán:")
                            for pi in pan_elegido.get("ingredientes",[]):
                                if pi.get("ref_id","").startswith("ins:"):
                                    pins=next((i for i in insumos if i["id"]==pi["ref_id"][4:]),None)
                                    if pins:
                                        pneed=calc.cant_bruta(pi.get("cantidad",pi.get("cant_neta",0))*cant_v,pi.get("merma",0))
                                        pok=pins.get("stock",0)>=pneed
                                        color="green" if pok else "red"
                                        st.markdown(f"  :{color}[{'✓' if pok else '⚠️'}] {pins['nombre']}: -{fmt_n(round(pneed,3))} {pins.get('unidad','')}")
                        st.markdown("---")

                # ── Selector de leche (bebidas que llevan leche) ──────────────────
                if rec_v.get("requiere_leche"):
                    if not leches_sub:
                        st.warning("⚠️ No hay sub-recetas con categoría **'Tipo de leche'** registradas. "
                                   "Ve a Sub-recetas → ➕ Nueva y agrégalas con esa categoría.")
                    else:
                        st.markdown("---")
                        opts_leche={"— Selecciona leche —":None}
                        for l in leches_sub: opts_leche[f"🥛 {l['nombre']}  ×{cant_v}"]=l
                        sel_leche=st.selectbox("🥛 Tipo de leche *",list(opts_leche.keys()),key="sel_leche_v")
                        leche_elegida=opts_leche[sel_leche]
                        if leche_elegida:
                            st.caption("Ingredientes de la leche que también se descontarán:")
                            for li in leche_elegida.get("ingredientes",[]):
                                if li.get("ref_id","").startswith("ins:"):
                                    lins=next((i for i in insumos if i["id"]==li["ref_id"][4:]),None)
                                    if lins:
                                        lneed=calc.cant_bruta(li.get("cantidad",li.get("cant_neta",0))*cant_v,li.get("merma",0))
                                        lok=lins.get("stock",0)>=lneed
                                        color="green" if lok else "red"
                                        st.markdown(f"  :{color}[{'✓' if lok else '⚠️'}] {lins['nombre']}: -{fmt_n(round(lneed,3))} {lins.get('unidad','')}")
                        st.markdown("---")

                ct=calc.costo_receta(rec_v,insumos,subrecetas,cf_cat(rec_v.get("categoria","")))
                precio=(rec_v.get("precio",0) or 0)
                st.markdown("**Insumos del plato que se descontarán** (incluye sub-recetas):")
                need_prev=consumo_insumos(rec_v.get("ingredientes",[]),cant_v)
                if not need_prev:
                    st.caption("Esta receta no tiene insumos directos enlazados.")
                for iid,qty in need_prev.items():
                    ins_obj=next((i for i in insumos if i["id"]==iid),None)
                    if ins_obj:
                        disp=ins_obj.get("stock",0); ok=disp>=qty
                        color="green" if ok else "red"
                        st.markdown(f":{color}[{'✓' if ok else '⚠️'}] **{ins_obj['nombre']}**: -{fmt_n(round(qty,3))} {ins_obj.get('unidad','')} (disponible: {fmt_n(disp)})")
                st.info(f"Costo: **{fmt_cop(round(ct*cant_v))}** | Venta: **{fmt_cop(round(precio*cant_v))}** | Margen: **{f'{(precio-ct)/precio*100:.1f}%' if precio>0 else '—'}**")

            if st.button("✅ Registrar venta",type="primary",use_container_width=True):
                if sel_v=="— Selecciona —": st.error("Selecciona una receta")
                else:
                    rec_v2=opts_v[sel_v]
                    es_sanduche2=rec_v2.get("categoria") in CAT_SANDUCHE
                    req_leche2=bool(rec_v2.get("requiere_leche"))
                    if es_sanduche2 and panes_sub and pan_elegido is None:
                        st.error("Selecciona el tipo de pan para este sanduche")
                    elif req_leche2 and leches_sub and leche_elegida is None:
                        st.error("Selecciona el tipo de leche para esta bebida")
                    else:
                        # Necesidad TOTAL de insumos = plato + pan + leche (descompone sub-recetas)
                        need=consumo_insumos(rec_v2.get("ingredientes",[]),cant_v)
                        if pan_elegido:
                            for k,v in consumo_insumos(pan_elegido.get("ingredientes",[]),cant_v).items(): need[k]=need.get(k,0)+v
                        if leche_elegida:
                            for k,v in consumo_insumos(leche_elegida.get("ingredientes",[]),cant_v).items(): need[k]=need.get(k,0)+v
                        # Verificar stock de todo lo enlazado
                        sin_stock=[]
                        for iid,qty in need.items():
                            ins_obj=next((i for i in insumos if i["id"]==iid),None)
                            if ins_obj and ins_obj.get("stock",0)<qty:
                                falta=qty-ins_obj.get("stock",0)
                                sin_stock.append(f"{ins_obj['nombre']} (faltan {fmt_n(round(falta,3))} {ins_obj.get('unidad','')})")
                        if sin_stock: st.error("⚠️ Stock insuficiente: "+", ".join(sin_stock))
                        else:
                            # Descontar TODO el inventario enlazado de una vez
                            for iid,qty in need.items():
                                ins_obj=next((i for i in insumos if i["id"]==iid),None)
                                if ins_obj:
                                    db.update_insumo(iid,{"stock":max(0,ins_obj.get("stock",0)-qty)})
                            pan_nota=f" | Pan: {pan_elegido['nombre']}" if pan_elegido else ""
                            leche_nota=f" | Leche: {leche_elegida['nombre']}" if leche_elegida else ""
                            db.add_movimiento({"tipo":"venta","receta_id":rec_v2["id"],
                                "nombre":f"{rec_v2['nombre']}"+(f" x{cant_v}" if cant_v>1 else ""),
                                "cantidad":cant_v,"fecha":str(fecha_v),"responsable":resp_v or "—",
                                "nota":f"Venta registrada{pan_nota}{leche_nota}",
                                "pan_id":pan_elegido["id"] if pan_elegido else None})
                            st.success(f"✅ Venta: {cant_v} × **{rec_v2['nombre']}**{pan_nota}{leche_nota}"); reload()

    with tab_hist:
        st.subheader("Historial de movimientos")
        hc1,hc2,hc3,hc4=st.columns([2,1,1,1])
        busq_m  = hc1.text_input("🔍 Buscar insumo / plato")
        ftipo   = hc2.selectbox("Tipo",["Todos","entrada","salida","venta","baja"])
        ffecha  = hc3.date_input("Fecha exacta", value=None)
        max_filas = hc4.number_input("Mostrar", min_value=10, max_value=500, value=50, step=10)

        lista_m = movs
        if busq_m:  lista_m = [m for m in lista_m if busq_m.lower() in (m.get("nombre") or "").lower()]
        if ftipo != "Todos": lista_m = [m for m in lista_m if m.get("tipo") == ftipo]
        if ffecha:  lista_m = [m for m in lista_m if m.get("fecha") == str(ffecha)]

        st.caption(f"{len(lista_m)} movimientos encontrados — mostrando {min(len(lista_m), int(max_filas))}")

        if lista_m:
            # Export siempre disponible
            df_mh = pd.DataFrame([{
                "Fecha":m.get("fecha"),"Tipo":m.get("tipo"),
                "Insumo/Plato":m.get("nombre") or "—",
                "Cantidad":m.get("cantidad"),"Costo unit.":fmt_cop(m.get("costo_unit")),
                "Responsable":m.get("responsable") or "—","Nota":m.get("nota") or "—"
            } for m in lista_m])
            st.download_button("⬇️ Exportar CSV", df_mh.to_csv(index=False).encode("utf-8"),
                               f"movimientos_{hoy()}.csv", "text/csv", use_container_width=True)
            st.markdown("---")

            TIPO_ICON = {"entrada":"📥","salida":"📤","venta":"🍽️","baja":"🗑️"}
            for mov in lista_m[:int(max_filas)]:
                icono = TIPO_ICON.get(mov.get("tipo",""), "•")
                lbl   = (f"{icono} **{mov.get('fecha','')}** · {mov.get('tipo','').upper()} · "
                         f"**{mov.get('nombre','—')}** · {fmt_n(mov.get('cantidad',0))} "
                         f"· {mov.get('responsable','—')}")
                with st.expander(lbl, expanded=False):
                    ec1,ec2,ec3,ec4 = st.columns(4)
                    ec1.metric("Tipo",        mov.get("tipo","—").upper())
                    ec2.metric("Cantidad",    fmt_n(mov.get("cantidad",0)))
                    ec3.metric("Costo unit.", fmt_cop(mov.get("costo_unit",0)))
                    ec4.metric("Fecha",       mov.get("fecha","—"))

                    st.markdown("**✏️ Editar datos del movimiento** *(nota, fecha, responsable)*")
                    mid = mov["id"]
                    ef1,ef2 = st.columns(2)
                    new_fecha = ef1.date_input("Fecha", value=date.fromisoformat(mov["fecha"]) if mov.get("fecha") else date.today(), key=f"mf_{mid}")
                    new_resp  = ef2.text_input("Responsable", value=mov.get("responsable",""), key=f"mr_{mid}")
                    new_nota  = st.text_input("Nota", value=mov.get("nota",""), key=f"mn_{mid}")

                    btn_c1, btn_c2 = st.columns([2,1])
                    if btn_c1.button("💾 Guardar cambios", key=f"msave_{mid}", type="primary"):
                        db.update_movimiento(mid, {"fecha": str(new_fecha), "responsable": new_resp, "nota": new_nota})
                        st.success("✅ Movimiento actualizado"); reload()

                    if btn_c2.button("🗑️ Eliminar y revertir stock", key=f"mdel_{mid}", type="secondary"):
                        tipo_m = mov.get("tipo")
                        cant_m = mov.get("cantidad", 0)
                        # ── revertir stock según tipo ─────────────────────
                        if tipo_m == "entrada":
                            ins_obj = next((i for i in insumos if i["id"] == mov.get("insumo_id")), None)
                            if ins_obj:
                                db.update_insumo(ins_obj["id"], {"stock": max(0, ins_obj.get("stock",0) - cant_m)})
                        elif tipo_m == "salida":
                            ins_obj = next((i for i in insumos if i["id"] == mov.get("insumo_id")), None)
                            if ins_obj:
                                db.update_insumo(ins_obj["id"], {"stock": ins_obj.get("stock",0) + cant_m})
                        elif tipo_m == "venta":
                            rec_v = next((r for r in recetas if r["id"] == mov.get("receta_id")), None)
                            if rec_v:
                                for ing in rec_v.get("ingredientes",[]):
                                    if ing.get("ref_id","").startswith("ins:"):
                                        ins_id = ing["ref_id"][4:]
                                        ins_obj = next((i for i in insumos if i["id"] == ins_id), None)
                                        if ins_obj:
                                            devolver = calc.cant_bruta(ing.get("cantidad", ing.get("cant_neta",0)) * cant_m, ing.get("merma",0))
                                            db.update_insumo(ins_id, {"stock": ins_obj.get("stock",0) + devolver})
                        db.delete_movimiento(mid)
                        st.warning("🗑️ Movimiento eliminado y stock revertido"); reload()
        else:
            st.info("Sin movimientos en este filtro.")


# ══════════════════════════════════════════════════════════════════════════════
#  KARDEX
# ══════════════════════════════════════════════════════════════════════════════
elif current == "kardex":
    st.title("📒 Kardex — Trazabilidad")
    if not insumos: st.info("Sin insumos.")
    else:
        kc1,kc2,kc3=st.columns([3,2,2])
        sel_k=kc1.selectbox("Insumo",["— Selecciona —"]+[i["nombre"] for i in insumos])
        desde_k=kc2.date_input("Desde",value=date.today()-timedelta(days=30))
        hasta_k=kc3.date_input("Hasta",value=date.today())
        if sel_k!="— Selecciona —":
            ins_k=next(i for i in insumos if i["nombre"]==sel_k)
            d_str,h_str=str(desde_k),str(hasta_k)
            st.markdown(f"### 📒 {ins_k['nombre']}")
            mc1,mc2,mc3,mc4=st.columns(4)
            mc1.metric("Stock actual",f"{fmt_n(ins_k.get('stock',0))} {ins_k.get('unidad','')}")
            mc2.metric("Costo unitario",fmt_cop(ins_k.get("costo",0)))
            mc3.metric("Valor en stock",fmt_cop(round(ins_k.get("stock",0)*ins_k.get("costo",0))))
            mc4.metric("Mínimo",f"{fmt_n(ins_k.get('minimo',0))} {ins_k.get('unidad','')}")
            movs_k=[m for m in movs if m.get("insumo_id")==ins_k["id"] and d_str<=(m.get("fecha") or "")<=h_str]
            ventas_k=[]
            for m in movs:
                if m.get("tipo")!="venta" or not(d_str<=(m.get("fecha") or "")<=h_str): continue
                rec_v=next((r for r in recetas if r["id"]==m.get("receta_id")),None)
                if not rec_v: continue
                for ing in rec_v.get("ingredientes",[]):
                    if ing.get("ref_id","")==f"ins:{ins_k['id']}":
                        bruta=calc.cant_bruta(ing.get("cantidad", ing.get("cant_neta", 0))*m.get("cantidad",1),ing.get("merma",0))
                        ventas_k.append({"tipo":"venta","nombre":f"Venta: {rec_v['nombre']}","cantidad":bruta,
                            "costo_unit":ins_k.get("costo",0),"fecha":m.get("fecha"),"responsable":m.get("responsable","—"),"signo":-1})
            all_k=sorted([dict(m,signo=1 if m.get("tipo")=="entrada" else -1) for m in movs_k]+ventas_k,key=lambda m:m.get("fecha",""))
            kk1,kk2,kk3,kk4=st.columns(4)
            kk1.metric("Entradas",fmt_n(sum(m["cantidad"] for m in all_k if m.get("tipo")=="entrada")))
            kk2.metric("Salidas",fmt_n(sum(m["cantidad"] for m in all_k if m.get("tipo")=="salida")))
            kk3.metric("Consumido ventas",fmt_n(sum(m["cantidad"] for m in all_k if m.get("tipo")=="venta")))
            kk4.metric("Bajas",fmt_n(sum(m["cantidad"] for m in all_k if m.get("tipo")=="baja")))
            if all_k:
                balance=0.0; rows_k=[]
                for m in all_k:
                    ent=m["cantidad"] if m.get("signo",1)>0 else None
                    sal=m["cantidad"] if m.get("signo",1)<0 else None
                    balance+=(ent or 0)-(sal or 0)
                    rows_k.append({"Fecha":m.get("fecha"),"Tipo":m.get("tipo"),"Descripción":m.get("nombre") or "—",
                        "Entrada":f"+{fmt_n(ent)}" if ent else "—","Salida":f"-{fmt_n(sal)}" if sal else "—",
                        "Saldo":fmt_n(max(0,balance)),"Costo unit.":fmt_cop(m.get("costo_unit",ins_k.get("costo",0))),
                        "Responsable":m.get("responsable") or "—"})
                st.dataframe(pd.DataFrame(rows_k),hide_index=True,use_container_width=True)
            if ins_k.get("historial_precios") and len(ins_k["historial_precios"])>1:
                df_hp=pd.DataFrame(ins_k["historial_precios"])
                fig_hp=px.line(df_hp,x="fecha",y="precio",markers=True,color_discrete_sequence=["#7C4A1E"])
                fig_hp.update_layout(height=200,margin=dict(t=10,b=10),plot_bgcolor="#fff8f0",paper_bgcolor="#fff8f0")
                st.plotly_chart(fig_hp,use_container_width=True)
            else: st.info("Sin movimientos en el período.")


# ══════════════════════════════════════════════════════════════════════════════
#  BAJAS
# ══════════════════════════════════════════════════════════════════════════════
elif current == "bajas":
    st.title("🗑️ Control de Bajas")
    tab_reg,tab_hist=st.tabs(["➕ Registrar baja","📋 Historial y resumen"])
    with tab_reg:
        tipo_b=st.radio("Tipo de ítem",["🥚 Insumo (materia prima)","🧪 Sub-receta / Elaboración","🍽️ Producto terminado"],
                        horizontal=True,key="radio_tipo_b")
        _tb="insumo" if "Insumo" in tipo_b else "subreceta" if "Sub-receta" in tipo_b else "producto"
        if _tb=="insumo":
            cat_b={f"{i['nombre']} — stock: {fmt_n(i.get('stock',0))} {i.get('unidad','')}":i for i in insumos}
        elif _tb=="subreceta":
            cat_b={f"{s['nombre']} — {s.get('categoria','')} | stock: {fmt_n(s.get('stock') or 0)}":s for s in subrecetas}
        else:
            cat_b={f"{r['nombre']} — {r.get('categoria','')} | stock: {fmt_n(r.get('stock') or 0)}":r for r in recetas}
        if not cat_b:
            st.warning("No hay ítems de este tipo registrados.")
        else:
            with st.form("form_baja",clear_on_submit=True):
                sel_b=st.selectbox("Ítem *",["— Selecciona —"]+list(cat_b.keys()))
                bc1,bc2=st.columns(2)
                cant_b=bc1.number_input("Cantidad *",min_value=0.01,step=0.5)
                fecha_b=bc2.date_input("Fecha",value=date.today())
                bc3,bc4=st.columns(2)
                causa_b=bc3.selectbox("Causa",CAUSAS_BAJA); turno_b=bc4.selectbox("Turno",TURNOS)
                bc5,bc6=st.columns(2)
                resp_b=bc5.text_input("Responsable"); autor_b=bc6.text_input("Autoriza")
                accion_b=st.text_input("Acción correctiva")
                if st.form_submit_button("✅ Registrar baja",use_container_width=True,type="primary"):
                    if sel_b=="— Selecciona —": st.error("Selecciona un ítem")
                    else:
                        item_b=cat_b[sel_b]; stk_b=item_b.get("stock") or 0
                        if cant_b>stk_b: st.error(f"Stock insuficiente: {fmt_n(stk_b)} {item_b.get('unidad','und')}")
                        else:
                            costo_b=item_b.get("costo",0); ct_b=costo_b*cant_b
                            if _tb=="insumo": db.update_insumo(item_b["id"],{"stock":stk_b-cant_b})
                            elif _tb=="subreceta":
                                try: db.update_subreceta(item_b["id"],{"stock":stk_b-cant_b})
                                except: pass
                            else:
                                try: db.update_receta(item_b["id"],{"stock":stk_b-cant_b})
                                except: pass
                            db.add_baja({"insumo_id":item_b["id"],"nombre":item_b["nombre"],
                                "unidad":item_b.get("unidad","und"),"cantidad":cant_b,
                                "costo_unit":costo_b,"costo_total":ct_b,"causa":causa_b,
                                "turno":turno_b,"fecha":str(fecha_b),"responsable":resp_b or "—",
                                "autoriza":autor_b or "—","accion":accion_b,
                                "tipo_item":_tb})
                            db.add_movimiento({"tipo":"baja","insumo_id":item_b["id"],"nombre":item_b["nombre"],
                                "cantidad":cant_b,"costo_unit":costo_b,"fecha":str(fecha_b),
                                "responsable":resp_b or "—","nota":f"[{_tb}] BAJA: {causa_b}"})
                            st.success(f"✅ Baja: {fmt_n(cant_b)} {item_b.get('unidad','und')} de **{item_b['nombre']}** — {fmt_cop(round(ct_b))}"); reload()
    with tab_hist:
        lunes_b=date.today()-timedelta(days=date.today().weekday())
        bajas_sem=[b for b in bajas if (b.get("fecha") or "")>=str(lunes_b)]
        total_sem=sum(b.get("costo_total",0) for b in bajas_sem)
        bc1,bc2=st.columns(2)
        bc1.metric("Bajas esta semana",fmt_cop(round(total_sem))); bc2.metric("Registros",len(bajas_sem))
        if bajas_sem:
            resumen_c={c:sum(b.get("costo_total",0) for b in bajas_sem if b.get("causa")==c) for c in CAUSAS_BAJA}
            df_rc=pd.DataFrame([{"Causa":c,"Total COP":fmt_cop(round(v)),"Registros":sum(1 for b in bajas_sem if b.get("causa")==c)} for c,v in resumen_c.items() if v>0])
            if not df_rc.empty: st.dataframe(df_rc,hide_index=True,use_container_width=True)
        fcausa=st.selectbox("Filtrar causa",["Todas"]+CAUSAS_BAJA)
        lista_b=bajas if fcausa=="Todas" else [b for b in bajas if b.get("causa")==fcausa]
        if lista_b:
            df_b=pd.DataFrame([{"Fecha":b.get("fecha"),"Turno":b.get("turno"),"Insumo":b.get("nombre"),
                "Cantidad":f"{fmt_n(b.get('cantidad',0))} {b.get('unidad','')}","Costo total":fmt_cop(round(b.get("costo_total",0))),
                "Causa":b.get("causa"),"Responsable":b.get("responsable"),"Autoriza":b.get("autoriza")} for b in lista_b[:300]])
            st.dataframe(df_b,hide_index=True,use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ALERTAS
# ══════════════════════════════════════════════════════════════════════════════
elif current == "alertas":
    st.title("🔔 Alertas")

    # ── resumen KPIs ──────────────────────────────────────────────────────────
    bajo_a  = [i for i in insumos if i.get("minimo",0)>0 and i.get("stock",0)<=i["minimo"]]
    hoy_d   = date.today()
    proximos_a = []
    for i in insumos:
        if not i.get("vida_util") or not i.get("ultima_entrada"): continue
        try:
            ult=date.fromisoformat(i["ultima_entrada"]); vence=ult+timedelta(days=int(i["vida_util"]))
            dias=(vence-hoy_d).days
            if dias<=7: proximos_a.append((i, dias, str(vence)))
        except: continue
    flucts_a = []
    for i in insumos:
        hist=i.get("historial_precios") or []
        if len(hist)<2: continue
        for j in range(len(hist)-1,0,-1):
            ant=hist[j-1].get("precio",0); act=hist[j].get("precio",0)
            if not ant or ant<=0: continue
            pct=(act-ant)/ant*100
            if pct>=umbral_precio:
                flucts_a.append((i,ant,act,pct,hist[j].get("fecha",""))); break

    ak1,ak2,ak3 = st.columns(3)
    kpi(ak1, len(bajo_a),      "Stock bajo mínimo",    "danger" if bajo_a    else "ok")
    kpi(ak2, len(proximos_a),  "Próximos a vencer",    "warn"   if proximos_a else "ok")
    kpi(ak3, len(flucts_a),    "Precios con alza",     "warn"   if flucts_a   else "ok")
    st.markdown("---")

    # ── 1. STOCK BAJO ─────────────────────────────────────────────────────────
    with st.expander(f"📦 Stock bajo el mínimo  ({len(bajo_a)} insumos)", expanded=bool(bajo_a)):
        if not bajo_a:
            st.success("✅ Todo el stock sobre el mínimo")
        else:
            # agrupar por categoría
            cats_bajo = sorted({i.get("categoria","Otros") for i in bajo_a})
            for cat in cats_bajo:
                items_cat = [i for i in bajo_a if i.get("categoria","Otros")==cat]
                st.markdown(f"**{cat}**")
                for i in items_cat:
                    falt = max(0, i.get("minimo",0) - i.get("stock",0))
                    pct_stock = (i.get("stock",0)/i.get("minimo",1)*100) if i.get("minimo",0)>0 else 0
                    color = "🔴" if pct_stock<=50 else "🟠"
                    with st.expander(
                        f"{color} **{i['nombre']}** — Stock: {fmt_n(i.get('stock',0))} / Mínimo: {fmt_n(i.get('minimo',0))} {i.get('unidad','')}",
                        expanded=False
                    ):
                        c1,c2,c3,c4 = st.columns(4)
                        c1.metric("Stock actual",  f"{fmt_n(i.get('stock',0))} {i.get('unidad','')}")
                        c2.metric("Stock mínimo",  f"{fmt_n(i.get('minimo',0))} {i.get('unidad','')}")
                        c3.metric("Faltante",      f"{fmt_n(round(falt,2))} {i.get('unidad','')}")
                        c4.metric("Proveedor",     i.get("proveedor") or "—")

    # ── 2. VENCIMIENTOS ───────────────────────────────────────────────────────
    with st.expander(f"⏰ Vencimientos próximos ({len(proximos_a)} insumos)", expanded=bool(proximos_a)):
        if not proximos_a:
            st.success("✅ Sin vencimientos próximos (7 días)")
        else:
            for i, dias, vence in sorted(proximos_a, key=lambda x: x[1]):
                estado = "🔴 VENCIDO" if dias<0 else ("🔴 HOY" if dias==0 else f"🟠 En {dias} día(s)")
                with st.expander(f"{estado} — **{i['nombre']}** · Vence: {vence}", expanded=False):
                    c1,c2,c3 = st.columns(3)
                    c1.metric("Stock actual",   f"{fmt_n(i.get('stock',0))} {i.get('unidad','')}")
                    c2.metric("Vida útil",      f"{i.get('vida_util',0)} días")
                    c3.metric("Última entrada", str(i.get("ultima_entrada","—")))

    # ── 3. PRECIOS ────────────────────────────────────────────────────────────
    with st.expander(f"💲 Fluctuaciones de precio ({len(flucts_a)} insumos)", expanded=bool(flucts_a)):
        if not flucts_a:
            st.success(f"✅ Sin fluctuaciones ≥ {umbral_precio}%")
        else:
            for i, ant, act, pct, fecha in sorted(flucts_a, key=lambda x: x[3], reverse=True):
                with st.expander(f"▲ {pct:.1f}% — **{i['nombre']}** · {fmt_cop(ant)} → {fmt_cop(act)}", expanded=False):
                    c1,c2,c3,c4 = st.columns(4)
                    c1.metric("Precio anterior", fmt_cop(ant))
                    c2.metric("Precio nuevo",    fmt_cop(act))
                    c3.metric("Variación",       f"▲ {pct:.1f}%")
                    c4.metric("Proveedor",       i.get("proveedor") or "—")


# ══════════════════════════════════════════════════════════════════════════════
#  REPORTES
# ══════════════════════════════════════════════════════════════════════════════
elif current == "reportes":
    st.title("📈 Reportes")
    tab_inv,tab_bajas,tab_movs,tab_cons=st.tabs(["📦 Inventario","🗑️ Bajas por período","↕️ Movimientos","📊 Consumo"])
    with tab_inv:
        if insumos:
            total_v=sum(i.get("stock",0)*i.get("costo",0) for i in insumos)
            ri1,ri2=st.columns([2,3])
            ri1.metric("Valor total inventario",fmt_cop(round(total_v)))
            ri2.metric("Total insumos",f"{len(insumos)} registrados")
            cat_s=st.selectbox("Filtrar categoría",["Todas"]+CATEGORIAS,key="rcat")
            lista_ri=insumos if cat_s=="Todas" else [i for i in insumos if i.get("categoria")==cat_s]
            df_ri=pd.DataFrame([{"Insumo":i["nombre"],"Categoría":i.get("categoria",""),"Stock":i.get("stock",0),
                "Unidad":i.get("unidad",""),"Costo unit.":i.get("costo",0),
                "Valor COP":round(i.get("stock",0)*i.get("costo",0)),
                "Mínimo":i.get("minimo",0),
                "Estado":"⚠️ Bajo" if i.get("minimo",0)>0 and i.get("stock",0)<=i["minimo"] else "✓ OK"} for i in lista_ri])
            st.dataframe(df_ri,hide_index=True,use_container_width=True)
            st.download_button("⬇️ Exportar inventario CSV",df_ri.to_csv(index=False).encode("utf-8"),
                               f"inventario_{hoy()}.csv","text/csv",use_container_width=True)
            cats_d={};[cats_d.update({i.get("categoria","Otros"):cats_d.get(i.get("categoria","Otros"),0)+i.get("stock",0)*i.get("costo",0)}) for i in insumos]
            fig_c=px.bar(x=list(cats_d.keys()),y=[round(v/1000) for v in cats_d.values()],
                         labels={"x":"Categoría","y":"Valor (miles COP)"},color_discrete_sequence=["#7C4A1E"],
                         title="Valor de inventario por categoría")
            fig_c.update_layout(height=300,margin=dict(t=40,b=10),plot_bgcolor="#fff8f0",paper_bgcolor="#fff8f0")
            st.plotly_chart(fig_c,use_container_width=True)
    with tab_bajas:
        rb1,rb2,rb3=st.columns([2,2,2])
        desde_b=rb1.date_input("Desde",value=date.today()-timedelta(days=30),key="rb_desde")
        hasta_b=rb2.date_input("Hasta",value=date.today(),key="rb_hasta")
        causa_filt=rb3.selectbox("Causa",["Todas"]+CAUSAS_BAJA,key="rb_causa")
        lista_rb=[b for b in bajas if str(desde_b)<=(b.get("fecha") or "")<=str(hasta_b)]
        if causa_filt!="Todas": lista_rb=[b for b in lista_rb if b.get("causa")==causa_filt]
        total_rb=sum(b.get("costo_total",0) for b in lista_rb)
        rb_k1,rb_k2,rb_k3=st.columns(3)
        rb_k1.metric("Registros en período",len(lista_rb))
        rb_k2.metric("Costo total bajas",fmt_cop(round(total_rb)))
        rb_k3.metric("Período analizado",f"{(hasta_b-desde_b).days} días")
        if lista_rb:
            df_rb=pd.DataFrame([{"Fecha":b.get("fecha"),"Turno":b.get("turno",""),"Tipo":b.get("tipo_item","insumo"),
                "Ítem":b.get("nombre"),"Cantidad":b.get("cantidad",0),"Unidad":b.get("unidad",""),
                "Causa":b.get("causa"),"Costo total":round(b.get("costo_total",0)),
                "Responsable":b.get("responsable"),"Autoriza":b.get("autoriza","—")} for b in lista_rb])
            st.dataframe(df_rb,hide_index=True,use_container_width=True)
            st.download_button("⬇️ Exportar bajas CSV",df_rb.to_csv(index=False).encode("utf-8"),
                               f"bajas_{desde_b}_{hasta_b}.csv","text/csv",use_container_width=True)
            st.markdown("---")
            sem_data=[]
            for w in range(7,-1,-1):
                hd=date.today(); lun=hd-timedelta(days=hd.weekday()+w*7); dom=lun+timedelta(days=6)
                t=sum(b.get("costo_total",0) for b in bajas if str(lun)<=(b.get("fecha") or "")<=str(dom))
                sem_data.append({"Semana":f"S-{w}","Bajas (miles COP)":round(t/1000)})
            c_charts1,c_charts2=st.columns(2)
            with c_charts1:
                fig_sem=px.line(pd.DataFrame(sem_data),x="Semana",y="Bajas (miles COP)",markers=True,
                                color_discrete_sequence=["#c0392b"],title="Tendencia semanal (8 semanas)")
                fig_sem.update_layout(height=260,margin=dict(t=40,b=10),plot_bgcolor="#fff8f0",paper_bgcolor="#fff8f0")
                st.plotly_chart(fig_sem,use_container_width=True)
            with c_charts2:
                causa_t={c:sum(b.get("costo_total",0) for b in lista_rb if b.get("causa")==c) for c in CAUSAS_BAJA}
                causa_t={k:v for k,v in causa_t.items() if v>0}
                if causa_t:
                    fig_pie=px.pie(values=list(causa_t.values()),names=list(causa_t.keys()),
                                   color_discrete_sequence=px.colors.qualitative.Warm,title="Por causa")
                    fig_pie.update_layout(height=260,margin=dict(t=40,b=10),paper_bgcolor="#fff8f0")
                    st.plotly_chart(fig_pie,use_container_width=True)
        else: st.info("Sin bajas en el período seleccionado.")
    with tab_movs:
        rm1,rm2,rm3=st.columns([2,2,2])
        desde_m=rm1.date_input("Desde",value=date.today()-timedelta(days=7),key="rm_desde")
        hasta_m=rm2.date_input("Hasta",value=date.today(),key="rm_hasta")
        tipo_m_filt=rm3.selectbox("Tipo",["Todos","entrada","salida","venta","baja"],key="rm_tipo")
        lista_rm=[m for m in movs if str(desde_m)<=(m.get("fecha") or "")<=str(hasta_m)]
        if tipo_m_filt!="Todos": lista_rm=[m for m in lista_rm if m.get("tipo")==tipo_m_filt]
        total_rm_e=sum(m.get("cantidad",0) for m in lista_rm if m.get("tipo")=="entrada")
        total_rm_s=sum(m.get("cantidad",0) for m in lista_rm if m.get("tipo")=="salida")
        rk1,rk2,rk3=st.columns(3)
        rk1.metric("Total registros",len(lista_rm))
        rk2.metric("Entradas",int(total_rm_e))
        rk3.metric("Salidas",int(total_rm_s))
        if lista_rm:
            df_rm=pd.DataFrame([{"Fecha":m.get("fecha"),"Tipo":m.get("tipo"),
                "Ítem":m.get("nombre","—"),"Cantidad":m.get("cantidad",0),
                "Costo unit.":m.get("costo_unit",0),"Responsable":m.get("responsable","—"),
                "Nota":m.get("nota","—")} for m in lista_rm])
            st.dataframe(df_rm,hide_index=True,use_container_width=True)
            st.download_button("⬇️ Exportar movimientos CSV",df_rm.to_csv(index=False).encode("utf-8"),
                               f"movimientos_{desde_m}_{hasta_m}.csv","text/csv",use_container_width=True)
        else: st.info("Sin movimientos en el período seleccionado.")
    with tab_cons:
        consumo={}
        for m in movs:
            if m.get("tipo")=="venta":
                rec_v=next((r for r in recetas if r["id"]==m.get("receta_id")),None)
                if rec_v:
                    for ing in rec_v.get("ingredientes",[]):
                        ref=calc.resolve_ref(ing.get("ref_id",""),insumos,subrecetas)
                        consumo[ref["nombre"]]=consumo.get(ref["nombre"],0)+ing.get("cantidad", ing.get("cant_neta", 0))*m.get("cantidad",1)
            elif m.get("tipo")=="salida":
                consumo[m.get("nombre","?")]=consumo.get(m.get("nombre","?"),0)+m.get("cantidad",0)
        top=sorted(consumo.items(),key=lambda x:x[1],reverse=True)[:10]
        if top:
            fig_top=px.bar(x=[t[1] for t in top],y=[t[0] for t in top],orientation="h",color_discrete_sequence=["#7C4A1E"])
            fig_top.update_layout(height=350,margin=dict(t=10,b=10),plot_bgcolor="#fff8f0",paper_bgcolor="#fff8f0",xaxis_title="Unidades consumidas")
            st.plotly_chart(fig_top,use_container_width=True)
        else: st.info("Sin datos de consumo aún.")


# ══════════════════════════════════════════════════════════════════════════════
#  PROYECCIÓN DE PRODUCCIÓN
# ══════════════════════════════════════════════════════════════════════════════
elif current == "produccion":
    st.title("🏭 Proyección de Producción Semanal")
    if not recetas:
        st.warning("No hay recetas registradas.")
    else:
        tab_manual,tab_ventas,tab_loggro=st.tabs(["✏️ Plan manual","📊 Sugerida por ventas","📥 Importar desde Loggro"])

        # ── PLAN MANUAL ───────────────────────────────────────────────────────
        with tab_manual:
            st.markdown("Define cuántas porciones producir esta semana por receta.")
            if "porciones_prod" not in st.session_state: st.session_state.porciones_prod={}

            # Import/Export del plan
            pm_c1,pm_c2,pm_c3=st.columns([2,2,2])
            cat_prod=pm_c1.selectbox("Filtrar categoría",["Todas"]+CAT_RECETA)

            # Exportar plan actual como CSV
            plan_rows=[{"receta_id":r["id"],"nombre":r["nombre"],"categoria":r.get("categoria",""),
                        "porciones":st.session_state.porciones_prod.get(r["id"],0)} for r in recetas]
            plan_csv=pd.DataFrame(plan_rows).to_csv(index=False).encode("utf-8")
            pm_c2.download_button("⬇️ Exportar plan CSV",plan_csv,f"plan_produccion_{hoy()}.csv","text/csv",use_container_width=True)

            # Importar plan desde CSV
            plan_upload=pm_c3.file_uploader("📥 Importar plan CSV",type=["csv"],key="plan_upload",label_visibility="collapsed")
            if plan_upload:
                try:
                    df_plan=pd.read_csv(plan_upload)
                    df_plan.columns=[c.strip().lower() for c in df_plan.columns]
                    for _,row in df_plan.iterrows():
                        rid=str(row.get("receta_id","")).strip()
                        p=int(row.get("porciones",0) or 0)
                        if rid: st.session_state.porciones_prod[rid]=p
                    st.success(f"✅ Plan importado: {len(df_plan)} recetas cargadas"); st.rerun()
                except Exception as ex: st.error(f"Error al importar: {ex}")

            recetas_prod=recetas if cat_prod=="Todas" else [r for r in recetas if r.get("categoria")==cat_prod]
            for r in recetas_prod:
                default=st.session_state.porciones_prod.get(r["id"],int(r.get("porciones",1)))
                c_n,c_p=st.columns([4,1])
                c_n.markdown(f"**{r['nombre']}** — *{r.get('categoria','')}*")
                val=c_p.number_input("Porciones",min_value=0,step=1,value=default,key=f"prod_{r['id']}",label_visibility="collapsed")
                st.session_state.porciones_prod[r["id"]]=val

            st.markdown("---"); st.subheader("📦 Insumos necesarios vs Stock")
            necesidades={}; subrecetas_nec={}
            for r in recetas_prod:
                porciones=st.session_state.porciones_prod.get(r["id"],0)
                if porciones<=0: continue
                for ing in r.get("ingredientes",[]):
                    rid=ing.get("ref_id","")
                    if rid.startswith("ins:"):
                        ins_id=rid[4:]; ins_obj=next((i for i in insumos if i["id"]==ins_id),None)
                        if ins_obj:
                            cb=calc.cant_bruta(ing.get("cantidad", ing.get("cant_neta", 0))*porciones,ing.get("merma",0))
                            if ins_id not in necesidades:
                                necesidades[ins_id]={"nombre":ins_obj["nombre"],"unidad":ins_obj.get("unidad",""),"stock":ins_obj.get("stock",0),"costo":ins_obj.get("costo",0),"cantidad_bruta":0}
                            necesidades[ins_id]["cantidad_bruta"]+=cb
                    elif rid.startswith("sub:"):
                        sub_id=rid[4:]; sub=next((s for s in subrecetas if s["id"]==sub_id),None)
                        if sub:
                            cant_sub=ing.get("cantidad", ing.get("cant_neta", 0))*porciones
                            rend=sub.get("rendimiento",1) or 1
                            # ── sub-recetas a preparar ──
                            if sub_id not in subrecetas_nec:
                                subrecetas_nec[sub_id]={"nombre":sub["nombre"],"rendimiento":rend,
                                    "unidad":sub.get("unidad_rendimiento",""),"cantidad_necesaria":0}
                            subrecetas_nec[sub_id]["cantidad_necesaria"]+=cant_sub
                            # ── descomponer insumos ──
                            for s_ing in sub.get("ingredientes",[]):
                                if s_ing.get("ref_id","").startswith("ins:"):
                                    s_ins_id=s_ing["ref_id"][4:]; s_ins=next((i for i in insumos if i["id"]==s_ins_id),None)
                                    if s_ins:
                                        sc=calc.cant_bruta(s_ing.get("cantidad", s_ing.get("cant_neta", 0))*(cant_sub/rend),s_ing.get("merma",0))
                                        if s_ins_id not in necesidades:
                                            necesidades[s_ins_id]={"nombre":s_ins["nombre"],"unidad":s_ins.get("unidad",""),"stock":s_ins.get("stock",0),"costo":s_ins.get("costo",0),"cantidad_bruta":0}
                                        necesidades[s_ins_id]["cantidad_bruta"]+=sc

            if necesidades:
                rows_prod=[]; compras=[]; costo_total_comp=0
                for ins_id,d in necesidades.items():
                    faltan=max(0,d["cantidad_bruta"]-d["stock"]); ct_comp=faltan*d["costo"]; costo_total_comp+=ct_comp
                    rows_prod.append({"Insumo":d["nombre"],"Necesario":f"{fmt_n(round(d['cantidad_bruta'],3))} {d['unidad']}",
                        "Stock actual":f"{fmt_n(d['stock'])} {d['unidad']}","Faltante":f"{fmt_n(round(faltan,3))} {d['unidad']}",
                        "Costo compra":fmt_cop(round(ct_comp)),"Estado":"✓ OK" if faltan==0 else "⚠️ Comprar"})
                    if faltan>0: compras.append({"Insumo":d["nombre"],"Cantidad a comprar":f"{fmt_n(round(faltan,3))} {d['unidad']}","Costo estimado":fmt_cop(round(ct_comp))})
                st.dataframe(pd.DataFrame(rows_prod),hide_index=True,use_container_width=True)
                if compras:
                    st.markdown("---"); st.subheader("🛒 Insumos a COMPRAR")
                    st.metric("Costo total estimado de compras",fmt_cop(round(costo_total_comp)))
                    df_compras=pd.DataFrame(compras)
                    for _,row in df_compras.iterrows():
                        with st.expander(f"🛒 **{row['Insumo']}** — Comprar: {row['Cantidad a comprar']} · {row['Costo estimado']}",expanded=False):
                            c1,c2=st.columns(2)
                            c1.metric("Cantidad a comprar",row["Cantidad a comprar"])
                            c2.metric("Costo estimado",row["Costo estimado"])
                    st.download_button("⬇️ Exportar lista de compras",df_compras.to_csv(index=False).encode("utf-8"),f"compras_{hoy()}.csv","text/csv",use_container_width=True)
                else: st.success("✅ Stock suficiente para toda la producción.")

            # ── Sub-recetas a PREPARAR ─────────────────────────────────────────
            if subrecetas_nec:
                st.markdown("---"); st.subheader("🧪 Sub-recetas a PREPARAR")
                rows_sub_prep=[]
                for sub_id,d in subrecetas_nec.items():
                    rend=d["rendimiento"] or 1
                    cant_nec=d["cantidad_necesaria"]
                    tandas=cant_nec/rend
                    rows_sub_prep.append({"Sub-receta":d["nombre"],"Rend./tanda":f"{fmt_n(rend)} {d['unidad']}",
                        "Total necesario":f"{fmt_n(round(cant_nec,3))} {d['unidad']}","Tandas a preparar":f"{tandas:.1f}"})
                    with st.expander(f"🧪 **{d['nombre']}** — Preparar {tandas:.1f} tanda(s) = {fmt_n(round(cant_nec,3))} {d['unidad']}",expanded=False):
                        c1,c2,c3=st.columns(3)
                        c1.metric("Total necesario",f"{fmt_n(round(cant_nec,3))} {d['unidad']}")
                        c2.metric("Rendimiento por tanda",f"{fmt_n(rend)} {d['unidad']}")
                        c3.metric("Tandas a preparar",f"{tandas:.1f}")
                df_sub_prep=pd.DataFrame(rows_sub_prep)
                st.download_button("⬇️ Exportar plan de sub-recetas",df_sub_prep.to_csv(index=False).encode("utf-8"),f"subrecetas_plan_{hoy()}.csv","text/csv",use_container_width=True)

            # ── Distribución de pan para SANDUCHES ────────────────────────────
            sanduches_plan=[r for r in recetas_prod if r.get("categoria") in CAT_SANDUCHE
                            and st.session_state.porciones_prod.get(r["id"],0)>0]
            if sanduches_plan and panes_sub:
                st.markdown("---"); st.subheader("🍞 Distribución de pan para Sanduches")
                total_sand=sum(st.session_state.porciones_prod.get(r["id"],0) for r in sanduches_plan)
                st.caption(f"Total sanduches en el plan: **{int(total_sand)}** unidades")

                with st.expander("Ver detalle de sanduches en el plan",expanded=False):
                    rows_sand=[{"Sanduche":r["nombre"],"Categoría":r.get("categoria",""),
                                "Porciones":int(st.session_state.porciones_prod.get(r["id"],0))} for r in sanduches_plan]
                    st.dataframe(pd.DataFrame(rows_sand),hide_index=True,use_container_width=True)

                st.markdown("**Define qué % de sanduches va en cada tipo de pan:**")
                if "dist_pan" not in st.session_state: st.session_state.dist_pan={}

                cols_pan=st.columns(min(len(panes_sub),4))
                total_pct=0
                for i,pan in enumerate(panes_sub):
                    col=cols_pan[i%len(cols_pan)]
                    pct=col.number_input(f"🍞 {pan['nombre']}",min_value=0,max_value=100,
                                         value=int(st.session_state.dist_pan.get(pan["id"],0)),
                                         step=5,key=f"pan_pct_{pan['id']}",help="% del total de sanduches")
                    st.session_state.dist_pan[pan["id"]]=pct
                    total_pct+=pct

                if total_pct==100:   st.success(f"✅ Distribución completa: {total_pct}%")
                elif total_pct<100:  st.warning(f"⚠️ Distribución: {total_pct}% — faltan {100-total_pct}%")
                else:                st.error(f"❌ Distribución: {total_pct}% — excede 100%")

                if total_pct>0:
                    st.markdown("**Insumos de pan necesarios por tipo:**")
                    rows_pan_total=[]
                    for pan in panes_sub:
                        pct=st.session_state.dist_pan.get(pan["id"],0)
                        if pct<=0: continue
                        cant_sand_pan=round(total_sand*(pct/100))
                        rend_pan=pan.get("rendimiento",1) or 1
                        tandas_pan=cant_sand_pan/rend_pan
                        with st.expander(f"🍞 {pan['nombre']} — {int(cant_sand_pan)} sanduches ({pct}%) · {tandas_pan:.1f} tanda(s)",expanded=False):
                            ing_pan=[]
                            for s_ing in pan.get("ingredientes",[]):
                                if s_ing.get("ref_id","").startswith("ins:"):
                                    ins_id=s_ing["ref_id"][4:]; ins_obj=next((i for i in insumos if i["id"]==ins_id),None)
                                    if ins_obj:
                                        cant_total=calc.cant_bruta(
                                            s_ing.get("cantidad",s_ing.get("cant_neta",0))*(cant_sand_pan/rend_pan),
                                            s_ing.get("merma",0))
                                        stock_ins=ins_obj.get("stock",0)
                                        falta_pan=max(0,cant_total-stock_ins)
                                        costo_pan=falta_pan*ins_obj.get("costo",0)
                                        ing_pan.append({"Insumo":ins_obj["nombre"],
                                            "Necesario":f"{fmt_n(round(cant_total,3))} {ins_obj.get('unidad','')}",
                                            "Stock":f"{fmt_n(stock_ins)} {ins_obj.get('unidad','')}",
                                            "Faltante":f"{fmt_n(round(falta_pan,3))} {ins_obj.get('unidad','')}",
                                            "Costo compra":fmt_cop(round(costo_pan)),
                                            "Estado":"✓ OK" if falta_pan==0 else "⚠️ Comprar"})
                                        rows_pan_total.append({"Pan":pan["nombre"],"Insumo":ins_obj["nombre"],
                                            "Cantidad necesaria":round(cant_total,3),"Unidad":ins_obj.get("unidad","")})
                            if ing_pan: st.dataframe(pd.DataFrame(ing_pan),hide_index=True,use_container_width=True)
                            else: st.info("Esta sub-receta no tiene insumos directos registrados.")
                    if rows_pan_total:
                        st.download_button("⬇️ Exportar insumos de pan",
                            pd.DataFrame(rows_pan_total).to_csv(index=False).encode("utf-8"),
                            f"insumos_pan_{hoy()}.csv","text/csv",use_container_width=True)

            if not necesidades and not subrecetas_nec:
                st.info("Ingresa porciones > 0 para ver la proyección.")

        # ── SUGERIDA POR VENTAS ───────────────────────────────────────────────
        with tab_ventas:
            st.markdown("Analiza las ventas de un período y sugiere cuánto producir la próxima semana.")
            sv1,sv2,sv3=st.columns(3)
            desde_v=sv1.date_input("Desde",value=date.today()-timedelta(days=30),key="sv_desde")
            hasta_v=sv2.date_input("Hasta",value=date.today(),key="sv_hasta")
            factor=sv3.number_input("Factor de ajuste (%)",min_value=50,max_value=200,value=100,step=5,
                                     help="100% = igual a promedio. 120% = 20% más que el promedio.")

            d_str,h_str=str(desde_v),str(hasta_v)
            ventas_periodo={}
            for m in movs:
                if m.get("tipo")=="venta" and d_str<=(m.get("fecha") or "")<=h_str:
                    rid=m.get("receta_id","")
                    ventas_periodo[rid]=ventas_periodo.get(rid,0)+m.get("cantidad",1)

            if not ventas_periodo:
                st.info("Sin ventas en el período seleccionado. Registra ventas en Movimientos primero.")
            else:
                dias_periodo=max(1,(hasta_v-desde_v).days+1)
                dias_semana=7

                st.subheader("📊 Sugerencia de producción semanal")
                rows_sug=[]; sug_porciones={}
                for rid,total_vendido in sorted(ventas_periodo.items(),key=lambda x:x[1],reverse=True):
                    rec=next((r for r in recetas if r["id"]==rid),None)
                    if not rec: continue
                    promedio_diario=total_vendido/dias_periodo
                    sugerido=round(promedio_diario*dias_semana*(factor/100))
                    sug_porciones[rid]=sugerido
                    ct=calc.costo_receta(rec,insumos,subrecetas,cf_cat(rec.get("categoria","")))
                    precio=rec.get("precio",0) or 0
                    rows_sug.append({
                        "Receta":rec["nombre"],"Categoría":rec.get("categoria",""),
                        "Vendido en período":int(total_vendido),
                        "Promedio diario":f"{promedio_diario:.1f}",
                        "Sugerido semana":sugerido,
                        "Costo total":fmt_cop(round(ct*sugerido)),
                        "Venta estimada":fmt_cop(round(precio*sugerido)),
                    })
                st.caption(f"Período analizado: {dias_periodo} días | Factor: {factor}% — Puedes editar la columna **'Sugerido semana'** antes de cargar el plan.")
                df_sug=pd.DataFrame(rows_sug)
                edited_sug=st.data_editor(
                    df_sug,hide_index=True,use_container_width=True,
                    column_config={
                        "Receta":st.column_config.Column(disabled=True),
                        "Categoría":st.column_config.Column(disabled=True),
                        "Vendido en período":st.column_config.NumberColumn(disabled=True),
                        "Promedio diario":st.column_config.Column(disabled=True),
                        "Sugerido semana":st.column_config.NumberColumn("Sugerido semana ✏️",min_value=0,step=1,format="%d",help="Edita esta columna para ajustar la cantidad sugerida"),
                        "Costo total":st.column_config.Column(disabled=True),
                        "Venta estimada":st.column_config.Column(disabled=True),
                    },
                    key="edit_sug",
                )
                # Recalcular sug_porciones con los valores editados
                for i,(rid,_) in enumerate(sorted(ventas_periodo.items(),key=lambda x:x[1],reverse=True)):
                    if i<len(edited_sug):
                        sug_porciones[rid]=int(edited_sug.iloc[i]["Sugerido semana"] or 0)

                c_btn1,c_btn2=st.columns(2)
                if c_btn1.button("✅ Usar como plan de producción",type="primary",use_container_width=True):
                    st.session_state.porciones_prod=sug_porciones
                    st.success("✅ Sugerencia cargada en el Plan Manual. Ve a la pestaña ✏️ Plan manual para ver los insumos.")
                df_sug_exp=pd.DataFrame([{"receta_id":rid,"nombre":next((r["nombre"] for r in recetas if r["id"]==rid),""),"porciones":p} for rid,p in sug_porciones.items()])
                c_btn2.download_button("⬇️ Exportar sugerencia CSV",df_sug_exp.to_csv(index=False).encode("utf-8"),
                                       f"sugerencia_{hoy()}.csv","text/csv",use_container_width=True)

                # Insumos necesarios para la sugerencia
                st.markdown("---"); st.subheader("📦 Insumos necesarios para esta sugerencia")
                nec_sug={}; sub_nec_sug={}
                for rid,porciones in sug_porciones.items():
                    if porciones<=0: continue
                    rec=next((r for r in recetas if r["id"]==rid),None)
                    if not rec: continue
                    for ing in rec.get("ingredientes",[]):
                        ri=ing.get("ref_id","")
                        if ri.startswith("ins:"):
                            ins_id=ri[4:]; ins_obj=next((i for i in insumos if i["id"]==ins_id),None)
                            if ins_obj:
                                cb=calc.cant_bruta(ing.get("cantidad", ing.get("cant_neta", 0))*porciones,ing.get("merma",0))
                                if ins_id not in nec_sug:
                                    nec_sug[ins_id]={"nombre":ins_obj["nombre"],"unidad":ins_obj.get("unidad",""),"stock":ins_obj.get("stock",0),"costo":ins_obj.get("costo",0),"cantidad_bruta":0}
                                nec_sug[ins_id]["cantidad_bruta"]+=cb
                        elif ri.startswith("sub:"):
                            sub_id=ri[4:]; sub=next((s for s in subrecetas if s["id"]==sub_id),None)
                            if sub:
                                cant_sub=ing.get("cantidad", ing.get("cant_neta", 0))*porciones
                                rend=sub.get("rendimiento",1) or 1
                                if sub_id not in sub_nec_sug:
                                    sub_nec_sug[sub_id]={"nombre":sub["nombre"],"rendimiento":rend,
                                        "unidad":sub.get("unidad_rendimiento",""),"cantidad_necesaria":0}
                                sub_nec_sug[sub_id]["cantidad_necesaria"]+=cant_sub
                                for s_ing in sub.get("ingredientes",[]):
                                    if s_ing.get("ref_id","").startswith("ins:"):
                                        s_ins_id=s_ing["ref_id"][4:]; s_ins=next((i for i in insumos if i["id"]==s_ins_id),None)
                                        if s_ins:
                                            sc=calc.cant_bruta(s_ing.get("cantidad", s_ing.get("cant_neta", 0))*(cant_sub/rend),s_ing.get("merma",0))
                                            if s_ins_id not in nec_sug:
                                                nec_sug[s_ins_id]={"nombre":s_ins["nombre"],"unidad":s_ins.get("unidad",""),"stock":s_ins.get("stock",0),"costo":s_ins.get("costo",0),"cantidad_bruta":0}
                                            nec_sug[s_ins_id]["cantidad_bruta"]+=sc

                if nec_sug:
                    compras_sug=[]; costo_sug=0
                    rows_nec=[]
                    for ins_id,d in nec_sug.items():
                        faltan=max(0,d["cantidad_bruta"]-d["stock"]); ct_c=faltan*d["costo"]; costo_sug+=ct_c
                        rows_nec.append({"Insumo":d["nombre"],"Necesario":f"{fmt_n(round(d['cantidad_bruta'],3))} {d['unidad']}",
                            "Stock":f"{fmt_n(d['stock'])} {d['unidad']}","Faltante":f"{fmt_n(round(faltan,3))} {d['unidad']}",
                            "Estado":"✓ OK" if faltan==0 else "⚠️ Comprar"})
                        if faltan>0: compras_sug.append({"Insumo":d["nombre"],"Cantidad":f"{fmt_n(round(faltan,3))} {d['unidad']}","Costo":fmt_cop(round(ct_c))})
                    st.dataframe(pd.DataFrame(rows_nec),hide_index=True,use_container_width=True)
                    if compras_sug:
                        st.subheader("🛒 Insumos a COMPRAR")
                        st.metric("Costo estimado de compras",fmt_cop(round(costo_sug)))
                        df_cs=pd.DataFrame(compras_sug)
                        for _,row in df_cs.iterrows():
                            with st.expander(f"🛒 **{row['Insumo']}** — Comprar: {row['Cantidad']} · {row['Costo']}",expanded=False):
                                c1,c2=st.columns(2)
                                c1.metric("Cantidad a comprar",row["Cantidad"])
                                c2.metric("Costo estimado",row["Costo"])
                        st.download_button("⬇️ Exportar lista de compras",df_cs.to_csv(index=False).encode("utf-8"),f"compras_sugeridas_{hoy()}.csv","text/csv",use_container_width=True)

                # ── Sub-recetas a PREPARAR (sugeridas) ───────────────────────
                if sub_nec_sug:
                    st.markdown("---"); st.subheader("🧪 Sub-recetas a PREPARAR")
                    rows_sp=[]
                    for sub_id,d in sub_nec_sug.items():
                        rend=d["rendimiento"] or 1
                        cant_nec=d["cantidad_necesaria"]
                        tandas=cant_nec/rend
                        rows_sp.append({"Sub-receta":d["nombre"],"Rend./tanda":f"{fmt_n(rend)} {d['unidad']}",
                            "Total necesario":f"{fmt_n(round(cant_nec,3))} {d['unidad']}","Tandas a preparar":f"{tandas:.1f}"})
                        with st.expander(f"🧪 **{d['nombre']}** — Preparar {tandas:.1f} tanda(s) = {fmt_n(round(cant_nec,3))} {d['unidad']}",expanded=False):
                            c1,c2,c3=st.columns(3)
                            c1.metric("Total necesario",f"{fmt_n(round(cant_nec,3))} {d['unidad']}")
                            c2.metric("Rendimiento por tanda",f"{fmt_n(rend)} {d['unidad']}")
                            c3.metric("Tandas a preparar",f"{tandas:.1f}")
                    df_sp=pd.DataFrame(rows_sp)
                    st.download_button("⬇️ Exportar plan de sub-recetas",df_sp.to_csv(index=False).encode("utf-8"),f"subrecetas_sugeridas_{hoy()}.csv","text/csv",use_container_width=True)

        # ── IMPORTAR DESDE LOGGRO ─────────────────────────────────────────────
        with tab_loggro:
            st.markdown("### 📥 Importar reporte de ventas desde Loggro")
            st.info("Descarga de Loggro: **Reportes → Reporte de ventas por productos** (formato Excel .xlsx). "
                    "El sistema leerá las columnas **Producto**, **Cantidad** y **Categoría** automáticamente.")

            loggro_file=st.file_uploader("Sube el archivo Excel de Loggro",type=["xlsx","xls"],key="loggro_upload")

            if loggro_file:
                try:
                    import io, openpyxl as _oxl
                    wb_l=_oxl.load_workbook(io.BytesIO(loggro_file.read()),data_only=True)
                    ws_l=wb_l.active
                    rows_l=list(ws_l.iter_rows(values_only=True))
                    if not rows_l: st.error("Archivo vacío"); st.stop()

                    header_l=[str(h).strip() if h else "" for h in rows_l[0]]
                    # Buscar índices tolerando variaciones de nombre
                    def _col(names):
                        for n in names:
                            for i,h in enumerate(header_l):
                                if n.lower() in h.lower(): return i
                        return None
                    idx_prod=_col(["Producto","Product"])
                    idx_cant=_col(["Cantidad","Qty","Quantity"])
                    idx_cat =_col(["Categoría","Categoria","Category"])
                    idx_fecha=_col(["Fecha","Date"])

                    if idx_prod is None or idx_cant is None:
                        st.error("No se encontraron las columnas 'Producto' y 'Cantidad'. Verifica que sea el reporte correcto de Loggro.")
                        st.stop()

                    # Agrupar ventas por producto (excluir Adiciones y filas vacías)
                    from collections import defaultdict
                    ventas_l=defaultdict(float); cats_l={}; fechas_l=[]
                    for r in rows_l[1:]:
                        cat=str(r[idx_cat] or "").strip() if idx_cat is not None else ""
                        if cat.lower() in ("adiciones","adición","adicion"): continue
                        prod=str(r[idx_prod] or "").strip() if r[idx_prod] else ""
                        cant=r[idx_cant] or 0
                        if prod and cant:
                            try: ventas_l[prod]+=float(cant); cats_l[prod]=cat
                            except: pass
                        if idx_fecha is not None and r[idx_fecha]: fechas_l.append(r[idx_fecha])

                    if not ventas_l: st.warning("No se encontraron productos en el archivo."); st.stop()

                    fecha_min=min(fechas_l).date() if fechas_l else "—"
                    fecha_max=max(fechas_l).date() if fechas_l else "—"
                    total_items=int(sum(ventas_l.values()))
                    lk1,lk2,lk3=st.columns(3)
                    lk1.metric("Período",f"{fecha_min} → {fecha_max}")
                    lk2.metric("Productos únicos",len(ventas_l))
                    lk3.metric("Total unidades vendidas",total_items)

                    # Matching con recetas del sistema
                    def _norm(s): return s.lower().strip()
                    recetas_map={_norm(r["nombre"]):r for r in recetas}

                    rows_match=[]
                    for prod,cant in sorted(ventas_l.items(),key=lambda x:x[1],reverse=True):
                        pn=_norm(prod)
                        # Exacto
                        match=recetas_map.get(pn)
                        # Parcial: nombre de receta contenido en producto o viceversa
                        if not match:
                            for rn,r in recetas_map.items():
                                if rn in pn or pn in rn: match=r; break
                        rows_match.append({
                            "Producto Loggro":prod,
                            "Categoría":cats_l.get(prod,""),
                            "Vendido":int(cant),
                            "Receta en sistema":match["nombre"] if match else "⚠️ Sin coincidencia",
                            "_receta_id":match["id"] if match else None,
                        })

                    st.markdown("---")
                    st.markdown("#### 🔗 Coincidencias detectadas")
                    st.caption("Solo los productos con receta vinculada se cargarán al plan. "
                               "Los marcados ⚠️ se omiten — puedes vincularlos manualmente después desde la pestaña ✏️ Plan manual.")

                    matched=[r for r in rows_match if r["_receta_id"]]
                    unmatched=[r for r in rows_match if not r["_receta_id"]]
                    sin_pct=round(len(unmatched)/len(rows_match)*100) if rows_match else 0

                    mc1,mc2=st.columns(2)
                    mc1.metric("✅ Con coincidencia",f"{len(matched)} productos")
                    mc2.metric("⚠️ Sin coincidencia",f"{len(unmatched)} productos ({sin_pct}%)")

                    # Tabla de coincidencias
                    nombre_opts=["— Omitir —"]+[r["nombre"] for r in recetas]
                    recetas_nombre={r["nombre"]:r for r in recetas}

                    df_match_show=pd.DataFrame([{
                        "Producto Loggro":r["Producto Loggro"],
                        "Categoría":r["Categoría"],
                        "Vendido":r["Vendido"],
                        "Receta vinculada":r["Receta en sistema"],
                    } for r in rows_match])
                    st.dataframe(df_match_show,hide_index=True,use_container_width=True)

                    # Sección de corrección manual para los sin coincidencia
                    if unmatched:
                        with st.expander(f"✏️ Vincular manualmente los {len(unmatched)} productos sin coincidencia",expanded=False):
                            st.caption("Selecciona la receta correspondiente para cada producto de Loggro.")
                            correcciones={}
                            for r in unmatched:
                                col_a,col_b=st.columns([3,3])
                                col_a.markdown(f"**{r['Producto Loggro']}** — {r['Vendido']} und")
                                sel_r=col_b.selectbox("Vincular a →",nombre_opts,key=f"lmatch_{r['Producto Loggro']}")
                                if sel_r!="— Omitir —":
                                    correcciones[r["Producto Loggro"]]=recetas_nombre[sel_r]["id"]

                            # Aplicar correcciones
                            for r in rows_match:
                                if r["_receta_id"] is None and r["Producto Loggro"] in correcciones:
                                    r["_receta_id"]=correcciones[r["Producto Loggro"]]

                    # Botón cargar plan
                    st.markdown("---")
                    lc1,lc2=st.columns(2)
                    factor_l=lc1.number_input("Factor de ajuste (%)",min_value=50,max_value=300,value=100,step=5,
                        help="100% = igual a lo vendido. 120% = 20% extra por seguridad.")
                    if lc2.button("✅ Cargar en Plan de Producción",type="primary",use_container_width=True):
                        nuevo_plan={}
                        for r in rows_match:
                            if r["_receta_id"]:
                                cant_ajust=round(r["Vendido"]*(factor_l/100))
                                rid=r["_receta_id"]
                                nuevo_plan[rid]=nuevo_plan.get(rid,0)+cant_ajust
                        st.session_state.porciones_prod=nuevo_plan
                        n_cargados=len([v for v in nuevo_plan.values() if v>0])
                        st.success(f"✅ Plan cargado con {n_cargados} recetas. Ve a **✏️ Plan manual** para ver los insumos necesarios.")

                    # Exportar tabla de coincidencias
                    df_exp_l=pd.DataFrame([{
                        "producto_loggro":r["Producto Loggro"],
                        "categoria":r["Categoría"],
                        "vendido":r["Vendido"],
                        "receta_sistema":r["Receta en sistema"],
                    } for r in rows_match])
                    st.download_button("⬇️ Exportar tabla de coincidencias CSV",
                        df_exp_l.to_csv(index=False).encode("utf-8"),
                        f"loggro_coincidencias_{hoy()}.csv","text/csv")

                except Exception as ex:
                    st.error(f"Error procesando el archivo: {ex}")
                    import traceback; st.code(traceback.format_exc())


# ══════════════════════════════════════════════════════════════════════════════
#  AYUDA
# ══════════════════════════════════════════════════════════════════════════════
elif current == "ayuda":
    st.title("❓ Ayuda — Manual de usuario")
    st.markdown("""
    <div style='background:#fff8f0;border-radius:12px;padding:20px;border-left:4px solid #C17F3E;margin-bottom:20px'>
    <b style='color:#3B1A0A;font-size:16px'>🍽️ Bienvenido al sistema de inventarios La Ocasión</b><br>
    <span style='color:#7C4A1E'>Esta guía explica paso a paso cómo usar cada módulo.</span>
    </div>
    """,unsafe_allow_html=True)

    with st.expander("📦 Módulo: Insumos",expanded=False):
        st.markdown("""
**¿Qué es?** El catálogo de todos tus ingredientes y materias primas.

**Cómo agregar un insumo:**
1. Ve a **Insumos → ➕ Agregar**
2. Llena: nombre, categoría, unidad de medida, stock inicial, stock mínimo, costo por unidad y proveedor
3. El **stock mínimo** activa una alerta cuando el stock llega a ese nivel
4. La **vida útil** en días activa alertas de vencimiento

**Importar desde Excel/CSV:**
1. Descarga la plantilla en **Insumos → 📥 Importar CSV**
2. Llénala en Excel con todos tus insumos
3. Guárdala como CSV y súbela
4. El sistema crea los nuevos y actualiza los existentes

**Exportar:**
- En **Insumos → 📤 Exportar CSV** descarga el inventario completo
        """)

    with st.expander("📋 Módulo: Recetas",expanded=False):
        st.markdown("""
**¿Qué es?** Las recetas de tu carta. Cada receta está compuesta por insumos y/o sub-recetas.

**Cómo crear una receta:**
1. Ve a **Recetas → ➕ Nueva receta**
2. Define nombre, categoría, porciones y precio de venta
3. Agrega ingredientes — cada uno tiene: **ingrediente, cantidad neta y % de merma**
4. La **merma** es el desperdicio al preparar (ej: 20% merma en cebolla = se pierde el 20% al pelar)
5. El sistema calcula automáticamente: costo, margen y cantidad bruta a comprar

**Costos fijos:** En la pestaña ⚙️ defines el % de costos fijos (gas, luz, MOD) que se suma al costo de ingredientes.

**Exportar/Importar:** Usa los tabs 📤 📥 para respaldar o copiar recetas entre sistemas.
        """)

    with st.expander("🧪 Módulo: Sub-recetas",expanded=False):
        st.markdown("""
**¿Qué es?** Preparaciones base que se usan dentro de recetas (ej: salsa bechamel, masa de pizza, mermelada).

**Ventaja:** Si cambias el costo de un insumo, todas las recetas que usen esa sub-receta se actualizan automáticamente.

**Ejemplo:** Salsa de tomate → se usa en 5 recetas. Al cambiar el precio del tomate, todas las 5 recetas se recalculan.
        """)

    with st.expander("🔄 Módulo: Movimientos",expanded=False):
        st.markdown("""
**📥 Entrada:** Cuando llega mercancía. Suma al stock y actualiza el precio si cambió.

**📤 Salida:** Cuando sale un insumo sin ser vendido (consumo directo, merma, transferencia). Resta del stock.

**🍽️ Venta / Despacho:** Cuando se vende un plato de la carta.
- Selecciona la receta y las porciones
- El sistema **descuenta automáticamente** todos los insumos usados (con merma incluida)
- Verifica que haya stock suficiente antes de registrar

**📋 Historial:** Consulta todos los movimientos con filtros por tipo, fecha y nombre.
        """)

    with st.expander("🏭 Módulo: Proyección de Producción",expanded=False):
        st.markdown("""
**✏️ Plan manual:** Tú defines cuántas porciones producir de cada receta. El sistema calcula:
- Qué insumos necesitas y en qué cantidad
- Cuánto te falta vs tu stock actual
- Lista de compras con costos estimados

**📊 Sugerida por ventas:**
1. Selecciona un período de referencia (ej: últimas 4 semanas)
2. El sistema analiza el promedio diario de ventas por receta
3. Proyecta la producción para 7 días
4. Puedes ajustar con el **Factor** (ej: 120% si esperas más ventas)
5. Carga la sugerencia al plan manual con un clic
        """)

    with st.expander("📒 Módulo: Kardex",expanded=False):
        st.markdown("""
**¿Qué es?** La trazabilidad completa de un insumo: todas sus entradas, salidas, ventas y bajas en un período.

**Incluye:**
- Saldo acumulado movimiento a movimiento
- Historial gráfico de evolución de precios
- Totales por tipo de movimiento

**Uso:** Selecciona un insumo y un rango de fechas para ver todo lo que pasó con ese insumo.
        """)

    with st.expander("🗑️ Módulo: Bajas",expanded=False):
        st.markdown("""
**¿Qué es?** Registro oficial de pérdidas de insumos con trazabilidad.

**Causas disponibles:** Vencimiento, Contaminación, Error de preparación, Sobre-producción, Accidente, Devolución, Error de porción, Otro.

**Flujo:** Al registrar una baja, el sistema automáticamente:
1. Descuenta la cantidad del stock
2. Registra el movimiento en el historial
3. Calcula el costo de la pérdida

**Resumen semanal:** Muestra el total de pérdidas por causa en la semana en curso.
        """)

    with st.expander("🔔 Módulo: Alertas",expanded=False):
        st.markdown("""
El sistema genera alertas automáticas en tres categorías:

**📦 Stock bajo el mínimo:** Cuando el stock de un insumo llega o pasa por debajo del mínimo definido.

**⏰ Vencimientos próximos:** Insumos que vencen en 3 días o menos (basado en última entrada + vida útil).

**💲 Fluctuaciones de precio:** Cuando el precio de un insumo sube por encima del umbral definido en Configuración.
        """)

    with st.expander("⚙️ Configuración",expanded=False):
        st.markdown("""
**% Costos fijos de cocina:** Porcentaje que se suma al costo de ingredientes para cubrir gas, electricidad y mano de obra indirecta. Afecta el margen de todas las recetas.

**% Umbral alerta de precio:** Si el precio de un insumo sube más de este porcentaje entre compras, aparece una alerta. Recomendado: 5%.
        """)

    st.markdown("---")
    st.subheader("📥 Descargar manual completo")
    try:
        with open("manual_usuario.pdf","rb") as f:
            st.download_button(
                "⬇️ Descargar Manual de Usuario (PDF)",
                f.read(),
                "Manual_La_Ocasion_Inventarios.pdf",
                "application/pdf",
                use_container_width=True,
                type="primary",
            )
    except Exception:
        st.warning("Manual no disponible en este momento.")

    st.info("Para soporte o sugerencias, contacta a tu consultor de ingeniería de menú.")


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════
elif current == "config":
    st.title("⚙️ Configuración")

    tab_cf_cfg, tab_otros = st.tabs(["💰 Costos Fijos","⚙️ Otros parámetros"])

    # ── TAB COSTOS FIJOS ──────────────────────────────────────────────────────
    with tab_cf_cfg:
        st.subheader("Costos fijos del negocio")

        # ── Detección: ¿falta crear la tabla en Supabase? ──
        if not cf_table_ok:
            st.error("⚠️ **Falta activar la base de datos de costos fijos.** "
                     "La tabla todavía no existe en Supabase, por eso no se pueden guardar los rubros.")
            st.markdown("**Solución (1 sola vez):** copia este código, pégalo en el "
                        "**SQL Editor** de Supabase y dale **RUN**. Luego vuelve aquí y pulsa *Ya lo ejecuté*.")
            st.code(
"""-- Activar costos fijos en La Ocasión
CREATE TABLE IF NOT EXISTS costos_fijos_items (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    monto NUMERIC DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE config ADD COLUMN IF NOT EXISTS ventas_esperadas NUMERIC DEFAULT 0;
ALTER TABLE movimientos ADD COLUMN IF NOT EXISTS pan_id TEXT;""",
                language="sql")
            st.link_button("🔗 Abrir SQL Editor de Supabase","https://supabase.com/dashboard/project/_/sql/new",
                           use_container_width=True)
            if st.button("✅ Ya lo ejecuté — recargar",type="primary",use_container_width=True):
                reload()
            st.stop()

        st.info("ℹ️ Los costos fijos se aplican **solo a las recetas de comida**. "
                "Las **bebidas no cargan costos fijos**: se costean con materia prima + margen.")

        # ── Pre-cargar lista de rubros sugeridos ──
        RUBROS_SUGERIDOS=[
            "Arriendo del local","Energía eléctrica","Agua y alcantarillado","Gas",
            "Internet / teléfono","Nómina fija + prestaciones","Mantenimiento de equipos",
            "Depreciación de equipos y menaje","Seguros","Licencias e impuestos fijos",
            "Contador / administración","Aseo y cafetería","Software / POS / facturación",
            "Publicidad / marketing fijo","Dotación y uniformes",
        ]
        _existentes={(i.get("nombre") or "").strip().lower() for i in cf_items}
        _faltantes=[r for r in RUBROS_SUGERIDOS if r.lower() not in _existentes]
        if _faltantes:
            cpc1,cpc2=st.columns([3,2])
            cpc1.caption(f"💡 Hay {len(_faltantes)} rubro(s) sugerido(s) sin registrar. "
                         "Se agregan en $0 para que solo escribas los montos.")
            if cpc2.button("📋 Cargar rubros sugeridos",use_container_width=True):
                for r in _faltantes:
                    db.add_costo_fijo({"nombre":r,"monto":0,"activo":True})
                st.success(f"✅ {len(_faltantes)} rubro(s) agregado(s) en $0. Edita los montos abajo."); reload()

        # ── Agregar nuevo ítem ──
        with st.expander("➕ Agregar otro rubro",expanded=not cf_items):
            with st.form("form_add_cf"):
                fa1,fa2,fa3=st.columns([3,2,1])
                cf_nom=fa1.text_input("Nombre del rubro *",placeholder="Ej: Arriendo, Servicios, Nómina")
                cf_monto=fa2.number_input("Monto mensual (COP) *",min_value=0,step=10000,value=0)
                cf_activo=fa3.selectbox("Estado",["Activo","Inactivo"])
                if st.form_submit_button("💾 Agregar",use_container_width=True):
                    if not cf_nom.strip(): st.error("Escribe el nombre del rubro.")
                    else:
                        db.add_costo_fijo({"nombre":cf_nom.strip(),"monto":cf_monto,"activo":cf_activo=="Activo"})
                        st.success(f"✅ Rubro '{cf_nom}' agregado."); reload()

        # ── Tabla de ítems actuales ──
        if cf_items:
            st.markdown("**Rubros de costos fijos** — escribe el valor mensual de cada uno:")
            for item in cf_items:
                estado_icon="✅" if item.get("activo",True) else "⏸️"
                with st.expander(
                    f"{estado_icon} **{item['nombre']}** — {fmt_cop(item.get('monto',0))}/mes",
                    expanded=False):
                    with st.form(f"form_cf_{item['id']}"):
                        ec1,ec2,ec3=st.columns([3,2,1])
                        e_nom=ec1.text_input("Nombre",value=item["nombre"],key=f"cfn_{item['id']}")
                        e_monto=ec2.number_input("Monto mensual (COP)",min_value=0,step=10000,
                                                  value=int(item.get("monto",0)),key=f"cfm_{item['id']}")
                        e_act=ec3.selectbox("Estado",["Activo","Inactivo"],
                                             index=0 if item.get("activo",True) else 1,key=f"cfa_{item['id']}")
                        sb1,sb2=st.columns(2)
                        if sb1.form_submit_button("💾 Guardar cambios",use_container_width=True):
                            db.update_costo_fijo(item["id"],{"nombre":e_nom.strip(),"monto":e_monto,"activo":e_act=="Activo"})
                            st.success("✅ Actualizado"); reload()
                        if sb2.form_submit_button("🗑️ Eliminar",use_container_width=True):
                            db.delete_costo_fijo(item["id"]); st.success("✅ Eliminado"); reload()

            # ── Resumen y cálculo del % ──
            st.markdown("---")
            activos=[i for i in cf_items if i.get("activo",True)]
            total_cf=sum(float(i.get("monto",0)) for i in activos)
            st.metric("Total costos fijos activos (mensual)",fmt_cop(round(total_cf)))

            st.markdown("**Ventas esperadas mensuales** (para calcular el % automático):")
            with st.form("form_ventas_esp"):
                ve_v=st.number_input("Ventas esperadas (COP/mes)",min_value=0,step=100000,
                                      value=int(ventas_esperadas),
                                      help="Ingresa tus ventas brutas esperadas al mes para que el sistema calcule el % de costos fijos.")
                if st.form_submit_button("💾 Guardar ventas esperadas",use_container_width=True):
                    cf_pct=round((total_cf/ve_v)*100,2) if ve_v>0 else costos_fijos
                    db.update_config(cf_pct,umbral_precio,ve_v)
                    st.success(f"✅ Guardado. % de costos fijos: **{cf_pct}%**"); reload()

            if ventas_esperadas>0:
                cf_calc=round((total_cf/ventas_esperadas)*100,2)
                c_kpi1,c_kpi2,c_kpi3=st.columns(3)
                c_kpi1.metric("Ventas esperadas/mes",fmt_cop(round(ventas_esperadas)))
                c_kpi2.metric("Total costos fijos",fmt_cop(round(total_cf)))
                c_kpi3.metric("% en recetas de comida",f"{cf_calc}%",
                               help="Se aplica al costo de ingredientes de todas las recetas EXCEPTO bebidas.")
                st.caption("🥤 Bebidas: 0% de costos fijos (se costean solo con materia prima + margen).")
            else:
                st.info("Ingresa las ventas esperadas para calcular el % automáticamente.")
                st.caption(f"% actual aplicado en recetas de comida: **{costos_fijos}%** (configurado manualmente)")
        else:
            st.info("Aún no hay rubros registrados. Usa **📋 Cargar rubros sugeridos** o agrega el primero arriba.")

    # ── TAB OTROS PARÁMETROS ─────────────────────────────────────────────────
    with tab_otros:
        st.subheader("Parámetros del sistema")
        with st.form("form_cfg_otros"):
            cf_manual=st.number_input("% Costos fijos (manual, si no usas la lista)",
                                       0.0,100.0,value=costos_fijos,step=0.5,
                                       help="Se ignora automáticamente si tienes costos fijos registrados con ventas esperadas.")
            up_v=st.number_input("% Umbral alerta de precio",0.1,100.0,value=umbral_precio,step=0.5)
            if st.form_submit_button("💾 Guardar",use_container_width=True):
                db.update_config(cf_manual,up_v,ventas_esperadas)
                st.success("✅ Configuración guardada"); reload()
        st.markdown("---")
        if st.button("🔄 Recargar datos desde la base de datos"):
            reload()
