"""
La Ocasión · Sistema de Inventarios
Streamlit + Supabase — versión 2
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import io

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

st.markdown("""
<style>
[data-testid="stSidebar"]{ background-color:#1b4332; }
[data-testid="stSidebar"] *{ color:#c8e6d4 !important; }
.kpi-box{background:white;border-radius:10px;padding:16px 18px;
         border-top:3px solid #2d6a4f;box-shadow:0 1px 4px rgba(0,0,0,.08);text-align:center;}
.kpi-box.danger{border-top-color:#c0392b;}
.kpi-box.warn{border-top-color:#f0a500;}
.kpi-val{font-size:24px;font-weight:800;color:#1e2b24;}
.kpi-lbl{font-size:12px;color:#5a7060;margin-top:3px;}
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────────────────────────────────────
def check_password():
    if st.session_state.get("authenticated"):
        return True
    st.markdown("## 🍽️ La Ocasión · Inventarios")
    st.markdown("---")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if pwd == st.secrets.get("APP_PASSWORD", "laocasion2024"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    return False

if not check_password():
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fmt_cop(n):
    if n is None: return "—"
    return f"$ {int(round(float(n))):,}".replace(",", ".")

def fmt_n(n):
    if n is None: return "—"
    v = float(n)
    return f"{v:,.2f}".rstrip("0").rstrip(".")

def hoy(): return str(date.today())

CATEGORIAS = ["Proteínas","Lácteos","Verduras","Frutas","Granos / Harinas",
              "Aceites / Grasas","Condimentos","Bebidas","Pastelería","Panadería","Otros"]
UNIDADES   = ["g","kg","ml","L","unidad","porción","taza","cucharada","cucharadita","manojo","lámina"]
CAUSAS_BAJA= ["Vencimiento","Contaminación","Error de preparación","Sobre-producción",
               "Accidente / caída","Devolución cliente","Error de porción","Otro"]
TURNOS     = ["Mañana","Tarde","Noche"]
CAT_RECETA = ["Plato Principal","Entrada","Postre","Bebida","Brunch","Panadería","Pastelería","Especial"]

# ─────────────────────────────────────────────────────────────────────────────
#  NAVEGACIÓN
# ─────────────────────────────────────────────────────────────────────────────
PAGES = {
    "📊 Dashboard":             "dashboard",
    "📦 Insumos":               "insumos",
    "📋 Recetas":               "recetas",
    "🧪 Sub-recetas":           "subrecetas",
    "↕️ Movimientos":           "movimientos",
    "📒 Kardex":                "kardex",
    "🗑️ Bajas":                "bajas",
    "🔔 Alertas":               "alertas",
    "📈 Reportes":              "reportes",
    "🏭 Proyección Producción": "produccion",
    "⚙️ Configuración":         "config",
}

with st.sidebar:
    st.markdown("### 🍽️ La Ocasión")
    st.markdown("*Sistema de Inventarios*")
    st.markdown("---")
    page = st.radio("Módulos", list(PAGES.keys()), label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f"<small>📅 {date.today().strftime('%d/%m/%Y')}</small>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar sesión"):
        st.session_state.authenticated = False
        st.rerun()

current = PAGES[page]

# ─────────────────────────────────────────────────────────────────────────────
#  CARGA DE DATOS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=8)
def load_all():
    return {
        "insumos":    db.get_insumos(),
        "recetas":    db.get_recetas(),
        "subrecetas": db.get_subrecetas(),
        "movs":       db.get_movimientos(),
        "bajas":      db.get_bajas(),
        "config":     db.get_config(),
    }

def reload():
    load_all.clear()
    st.rerun()

data       = load_all()
insumos    = data["insumos"]
recetas    = data["recetas"]
subrecetas = data["subrecetas"]
movs       = data["movs"]
bajas      = data["bajas"]
cfg        = data["config"]
costos_fijos  = float(cfg.get("costos_fijos", 15))
umbral_precio = float(cfg.get("umbral_precio", 3))


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if current == "dashboard":
    st.title("📊 Dashboard")

    bajo       = [i for i in insumos if i.get("minimo",0)>0 and i.get("stock",0)<=i["minimo"]]
    lunes      = date.today() - timedelta(days=date.today().weekday())
    bajas_sem  = sum(b.get("costo_total",0) for b in bajas if (b.get("fecha") or "")>=str(lunes))
    movs_hoy   = sum(1 for m in movs if m.get("fecha")==hoy())
    valor_total= sum(i.get("stock",0)*i.get("costo",0) for i in insumos)

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    def kpi(col,val,lbl,t=""):
        col.markdown(f'<div class="kpi-box {t}"><div class="kpi-val">{val}</div><div class="kpi-lbl">{lbl}</div></div>',
                     unsafe_allow_html=True)
    kpi(c1, len(insumos),       "Insumos")
    kpi(c2, len(bajo),          "Stock crítico", "danger" if bajo else "")
    kpi(c3, len(recetas),       "Recetas")
    kpi(c4, fmt_cop(round(bajas_sem/1000))+"k", "Bajas semana", "warn")
    kpi(c5, movs_hoy,           "Movimientos hoy")
    kpi(c6, fmt_cop(round(valor_total/1000))+"k", "Valor inventario")

    st.markdown("---")
    cl, cr = st.columns(2)

    with cl:
        st.subheader("📉 Stock vs Mínimo")
        criticos = sorted([i for i in insumos if i.get("minimo",0)>0],
                          key=lambda i: i.get("stock",0)/max(i["minimo"],0.001))[:12]
        if criticos:
            df_c = pd.DataFrame({
                "Insumo": [i["nombre"][:20] for i in criticos],
                "Stock":  [i.get("stock",0) for i in criticos],
                "Mínimo": [i.get("minimo",0) for i in criticos],
            })
            fig = go.Figure()
            colors = ["#ef4444" if r["Stock"]<=r["Mínimo"] else "#40916c" for _,r in df_c.iterrows()]
            fig.add_bar(x=df_c["Insumo"], y=df_c["Stock"], name="Stock", marker_color=colors)
            fig.add_scatter(x=df_c["Insumo"], y=df_c["Mínimo"], name="Mínimo",
                            mode="lines+markers", line=dict(color="#f0a500",width=2))
            fig.update_layout(height=300, margin=dict(t=10,b=10), legend=dict(orientation="h"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin insumos con stock mínimo definido.")

    with cr:
        st.subheader("📅 Movimientos últimos 7 días")
        days     = [str(date.today()-timedelta(days=i)) for i in range(6,-1,-1)]
        tipos_c  = {"Entradas":"entrada","Ventas":"venta","Bajas":"baja"}
        colores  = {"Entradas":("#22c55e","rgba(34,197,94,0.15)"),
                    "Ventas":  ("#3b82f6","rgba(59,130,246,0.15)"),
                    "Bajas":   ("#ef4444","rgba(239,68,68,0.15)")}
        fig2 = go.Figure()
        for label, tipo in tipos_c.items():
            counts = [sum(1 for m in movs if m.get("fecha")==d and m.get("tipo")==tipo) for d in days]
            lc, fc = colores[label]
            fig2.add_scatter(x=[d[5:] for d in days], y=counts, name=label,
                             mode="lines+markers", line=dict(color=lc,width=2),
                             fill="tozeroy", fillcolor=fc)
        fig2.update_layout(height=300, margin=dict(t=10,b=10), legend=dict(orientation="h"))
        st.plotly_chart(fig2, use_container_width=True)

    cl2, cr2 = st.columns(2)
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
            df_m = pd.DataFrame([{"Fecha":m.get("fecha"),"Tipo":m.get("tipo"),
                                   "Insumo/Plato":m.get("nombre"),"Cantidad":m.get("cantidad"),
                                   "Resp.":m.get("responsable")} for m in movs[:8]])
            st.dataframe(df_m, hide_index=True, use_container_width=True)
        else:
            st.info("Sin movimientos aún.")


# ══════════════════════════════════════════════════════════════════════════════
#  INSUMOS
# ══════════════════════════════════════════════════════════════════════════════
elif current == "insumos":
    st.title("📦 Insumos")

    tab_list, tab_add, tab_imp, tab_exp = st.tabs(["📋 Listado","➕ Agregar","📥 Importar CSV","📤 Exportar CSV"])

    # ── LISTADO ──────────────────────────────────────────────────────────────
    with tab_list:
        c1,c2,c3 = st.columns([3,2,2])
        busq       = c1.text_input("🔍 Buscar nombre o proveedor")
        filtro_cat = c2.selectbox("Categoría", ["Todas"]+CATEGORIAS, key="fcat")
        filtro_stk = c3.selectbox("Stock", ["Todos","Stock bajo","Stock OK"], key="fstk")

        lista = insumos
        if busq:
            lista = [i for i in lista if busq.lower() in i["nombre"].lower()
                     or busq.lower() in (i.get("proveedor") or "").lower()]
        if filtro_cat != "Todas":
            lista = [i for i in lista if i.get("categoria")==filtro_cat]
        if filtro_stk=="Stock bajo":
            lista = [i for i in lista if i.get("minimo",0)>0 and i.get("stock",0)<=i["minimo"]]
        elif filtro_stk=="Stock OK":
            lista = [i for i in lista if not (i.get("minimo",0)>0 and i.get("stock",0)<=i["minimo"])]

        st.markdown(f"**{len(lista)} insumos**")
        if lista:
            df_ins = pd.DataFrame([{
                "Nombre":      i["nombre"],
                "Categoría":   i.get("categoria",""),
                "Stock":       i.get("stock",0),
                "Mínimo":      i.get("minimo",0),
                "Unidad":      i.get("unidad",""),
                "Costo unit.": fmt_cop(i.get("costo",0)),
                "Valor total": fmt_cop(round(i.get("stock",0)*i.get("costo",0))),
                "Proveedor":   i.get("proveedor") or "—",
                "Estado":      "⚠️ Bajo" if i.get("minimo",0)>0 and i.get("stock",0)<=i["minimo"] else "✓ OK",
            } for i in lista])
            st.dataframe(df_ins, hide_index=True, use_container_width=True)

            st.markdown("---")
            st.subheader("✏️ Editar insumo")
            nombres_map = {i["nombre"]: i for i in lista}
            sel = st.selectbox("Selecciona insumo", ["— Selecciona —"]+list(nombres_map.keys()))
            if sel != "— Selecciona —":
                ins = nombres_map[sel]
                with st.form("edit_ins", clear_on_submit=False):
                    r1c1,r1c2 = st.columns(2)
                    e_nombre = r1c1.text_input("Nombre", value=ins["nombre"])
                    e_cat    = r1c2.selectbox("Categoría", CATEGORIAS,
                                              index=CATEGORIAS.index(ins.get("categoria","Otros"))
                                              if ins.get("categoria") in CATEGORIAS else 0)
                    r2c1,r2c2,r2c3 = st.columns(3)
                    e_unidad = r2c1.selectbox("Unidad", UNIDADES,
                                              index=UNIDADES.index(ins["unidad"])
                                              if ins.get("unidad") in UNIDADES else 0)
                    e_stock  = r2c2.number_input("Stock actual", value=float(ins.get("stock",0)), step=0.5)
                    e_min    = r2c3.number_input("Stock mínimo", value=float(ins.get("minimo",0)), step=0.5)
                    r3c1,r3c2,r3c3 = st.columns(3)
                    e_costo  = r3c1.number_input("Costo por unidad (COP)",
                                                  value=float(ins.get("costo",0)), step=100.0)
                    e_prov   = r3c2.text_input("Proveedor", value=ins.get("proveedor") or "")
                    e_vida   = r3c3.number_input("Vida útil (días, 0=sin límite)",
                                                  value=int(ins.get("vida_util",0)), step=1)
                    col_s, col_d = st.columns(2)
                    if col_s.form_submit_button("💾 Guardar cambios", use_container_width=True):
                        upd = {"nombre":e_nombre.strip(),"categoria":e_cat,"unidad":e_unidad,
                               "stock":e_stock,"minimo":e_min,"proveedor":e_prov.strip(),"vida_util":e_vida}
                        if e_costo != float(ins.get("costo",0)):
                            hist = ins.get("historial_precios") or []
                            hist.append({"fecha":hoy(),"precio":e_costo,"precio_anterior":ins.get("costo",0)})
                            upd["historial_precios"] = hist
                        upd["costo"] = e_costo
                        db.update_insumo(ins["id"], upd)
                        st.success("✅ Insumo actualizado")
                        reload()
                    if col_d.form_submit_button("🗑️ Eliminar", use_container_width=True, type="secondary"):
                        db.delete_insumo(ins["id"])
                        st.warning(f"Insumo '{ins['nombre']}' eliminado")
                        reload()
        else:
            st.info("Sin insumos. Agrega en la pestaña ➕ o importa un CSV.")

    # ── AGREGAR ───────────────────────────────────────────────────────────────
    with tab_add:
        st.subheader("Agregar insumo manualmente")
        with st.form("add_ins", clear_on_submit=True):
            r1c1,r1c2 = st.columns(2)
            nombre  = r1c1.text_input("Nombre *")
            cat     = r1c2.selectbox("Categoría", CATEGORIAS)
            r2c1,r2c2,r2c3 = st.columns(3)
            unidad  = r2c1.selectbox("Unidad", UNIDADES)
            stock   = r2c2.number_input("Stock inicial", min_value=0.0, step=0.5)
            minimo  = r2c3.number_input("Stock mínimo", min_value=0.0, step=0.5)
            r3c1,r3c2,r3c3 = st.columns(3)
            costo   = r3c1.number_input("Costo por unidad (COP)", min_value=0.0, step=100.0)
            proveedor = r3c2.text_input("Proveedor")
            vida_util = r3c3.number_input("Vida útil (días)", min_value=0, step=1)
            if st.form_submit_button("💾 Guardar insumo", use_container_width=True):
                if not nombre.strip():
                    st.error("El nombre es obligatorio")
                else:
                    db.add_insumo({
                        "nombre": nombre.strip(), "categoria": cat, "unidad": unidad,
                        "stock": stock, "minimo": minimo, "costo": costo,
                        "proveedor": proveedor.strip(), "vida_util": vida_util,
                        "ultima_entrada": hoy(),
                        "historial_precios": [{"fecha":hoy(),"precio":costo}] if costo>0 else [],
                    })
                    st.success(f"✅ Insumo guardado: {nombre}")
                    reload()

    # ── IMPORTAR CSV ──────────────────────────────────────────────────────────
    with tab_imp:
        st.subheader("Importar insumos desde CSV")
        st.markdown("""
**Formato del archivo CSV** (columnas requeridas):

| nombre | categoria | unidad | stock | minimo | costo | proveedor | vida_util |
|--------|-----------|--------|-------|--------|-------|-----------|-----------|
| Harina | Granos / Harinas | kg | 10 | 2 | 3500 | Proveedor X | 0 |

- Descarga la plantilla de abajo, llénala en Excel y sube el archivo.
- Los insumos existentes con el mismo nombre serán **actualizados**.
- Los nuevos serán **creados**.
        """)

        # Plantilla para descargar
        plantilla = pd.DataFrame([{
            "nombre":"Ejemplo insumo","categoria":"Proteínas","unidad":"kg",
            "stock":5,"minimo":1,"costo":15000,"proveedor":"Proveedor","vida_util":0
        }])
        csv_plantilla = plantilla.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Descargar plantilla CSV", csv_plantilla,
                           "plantilla_insumos.csv", "text/csv")

        uploaded = st.file_uploader("Sube tu archivo CSV", type=["csv"])
        if uploaded:
            try:
                df_up = pd.read_csv(uploaded)
                df_up.columns = [c.strip().lower().replace(" ","_") for c in df_up.columns]
                st.markdown(f"**Vista previa — {len(df_up)} filas:**")
                st.dataframe(df_up.head(10), hide_index=True, use_container_width=True)

                if st.button("✅ Confirmar importación", type="primary"):
                    nombres_exist = {i["nombre"].lower(): i for i in insumos}
                    creados = actualizados = errores = 0
                    for _, row in df_up.iterrows():
                        try:
                            n = str(row.get("nombre","")).strip()
                            if not n: continue
                            datos = {
                                "nombre":    n,
                                "categoria": str(row.get("categoria","Otros")),
                                "unidad":    str(row.get("unidad","unidad")),
                                "stock":     float(row.get("stock",0) or 0),
                                "minimo":    float(row.get("minimo",0) or 0),
                                "costo":     float(row.get("costo",0) or 0),
                                "proveedor": str(row.get("proveedor","") or ""),
                                "vida_util": int(row.get("vida_util",0) or 0),
                                "ultima_entrada": hoy(),
                            }
                            if n.lower() in nombres_exist:
                                db.update_insumo(nombres_exist[n.lower()]["id"], datos)
                                actualizados += 1
                            else:
                                datos["historial_precios"] = [{"fecha":hoy(),"precio":datos["costo"]}] if datos["costo"]>0 else []
                                db.add_insumo(datos)
                                creados += 1
                        except Exception:
                            errores += 1
                    st.success(f"✅ Importación completa: {creados} creados, {actualizados} actualizados, {errores} errores")
                    reload()
            except Exception as e:
                st.error(f"Error al leer el CSV: {e}")

    # ── EXPORTAR CSV ──────────────────────────────────────────────────────────
    with tab_exp:
        st.subheader("Exportar insumos a CSV")
        if not insumos:
            st.info("No hay insumos para exportar.")
        else:
            df_exp = pd.DataFrame([{
                "nombre":      i["nombre"],
                "categoria":   i.get("categoria",""),
                "unidad":      i.get("unidad",""),
                "stock":       i.get("stock",0),
                "minimo":      i.get("minimo",0),
                "costo":       i.get("costo",0),
                "proveedor":   i.get("proveedor",""),
                "vida_util":   i.get("vida_util",0),
                "valor_total": round(i.get("stock",0)*i.get("costo",0)),
                "estado":      "Bajo" if i.get("minimo",0)>0 and i.get("stock",0)<=i["minimo"] else "OK",
            } for i in insumos])
            st.dataframe(df_exp, hide_index=True, use_container_width=True)
            csv_out = df_exp.to_csv(index=False).encode("utf-8")
            st.download_button(
                f"⬇️ Descargar inventario ({len(insumos)} insumos)",
                csv_out, f"inventario_{hoy()}.csv", "text/csv", use_container_width=True
            )


# ══════════════════════════════════════════════════════════════════════════════
#  RECETAS
# ══════════════════════════════════════════════════════════════════════════════
elif current == "recetas":
    st.title("📋 Recetas")
    tab_list, tab_add, tab_cf = st.tabs(["📋 Listado","➕ Nueva receta","⚙️ Costos fijos"])

    with tab_cf:
        st.subheader("Costos fijos de cocina")
        st.info("Porcentaje adicional sobre el costo de ingredientes para cubrir gas, electricidad, mano de obra.")
        with st.form("form_cf"):
            val_cf = st.number_input("% Costos fijos", 0.0, 100.0, value=costos_fijos, step=0.5)
            if st.form_submit_button("💾 Guardar"):
                db.update_config(val_cf, umbral_precio)
                st.success(f"✅ Costos fijos: {val_cf}%")
                reload()
        if recetas:
            st.subheader("Comparativa de recetas")
            rows_cf = []
            for r in recetas[:15]:
                ci = calc.costo_ingredientes_receta(r, insumos, subrecetas)
                ct = calc.costo_receta(r, insumos, subrecetas, costos_fijos)
                m  = calc.margen_receta(r, insumos, subrecetas, costos_fijos)
                rows_cf.append({"Receta":r["nombre"],"Costo ing.":fmt_cop(round(ci)),
                                 "Costos fijos":fmt_cop(round(ci*costos_fijos/100)),
                                 "Costo total":fmt_cop(round(ct)),
                                 "Precio venta":fmt_cop(r.get("precio",0)),
                                 "Margen":f"{m:.1f}%" if m is not None else "—"})
            st.dataframe(pd.DataFrame(rows_cf), hide_index=True, use_container_width=True)

    with tab_add:
        if not insumos and not subrecetas:
            st.warning("Agrega insumos primero antes de crear recetas.")
        else:
            st.subheader("Nueva receta")
            n_r   = st.text_input("Nombre de la receta *")
            rc1,rc2,rc3 = st.columns(3)
            cat_r  = rc1.selectbox("Categoría", CAT_RECETA)
            porc_r = rc2.number_input("Porciones", min_value=1, value=1)
            prec_r = rc3.number_input("Precio de venta (COP)", min_value=0.0, step=1000.0)

            st.markdown("**Ingredientes** *(insumos o sub-recetas)*")
            if "ing_rows" not in st.session_state:
                st.session_state.ing_rows = [{}]

            opts_ing = {}
            for i in insumos:
                opts_ing[f"📦 {i['nombre']} ({i.get('unidad','')})"] = f"ins:{i['id']}"
            for s in subrecetas:
                opts_ing[f"🧪 {s['nombre']} / {s.get('rendimiento',1)}{s.get('unidad_rendimiento','')}"] = f"sub:{s['id']}"
            labels_ing = list(opts_ing.keys())

            ing_data = []
            for idx in range(len(st.session_state.ing_rows)):
                ic1,ic2,ic3,ic4 = st.columns([4,1.5,1.5,0.5])
                sel_i = ic1.selectbox("Ingrediente", ["— Selecciona —"]+labels_ing, key=f"ri_{idx}")
                cant  = ic2.number_input("Cant. neta", min_value=0.0, step=0.01, key=f"rc_{idx}")
                merma = ic3.number_input("Merma %", min_value=0.0, max_value=99.0, step=0.5, key=f"rm_{idx}")
                if ic4.button("✕", key=f"rd_{idx}"):
                    st.session_state.ing_rows.pop(idx); st.rerun()
                if sel_i != "— Selecciona —":
                    ref_id = opts_ing[sel_i]
                    ing_data.append({"ref_id":ref_id,"cantidad":cant,"merma":merma})
                    bruta = calc.cant_bruta(cant, merma)
                    ref   = calc.resolve_ref(ref_id, insumos, subrecetas)
                    st.caption(f"  ↳ Cant. bruta: **{bruta:.3f} {ref['unidad']}** | Costo: **{fmt_cop(round(ref['costo_unit']*bruta))}**")

            if st.button("➕ Agregar ingrediente"):
                st.session_state.ing_rows.append({}); st.rerun()

            if ing_data:
                ci = sum(calc.costo_ingrediente(i["ref_id"],i["cantidad"],i["merma"],insumos,subrecetas) for i in ing_data)
                ct = ci*(1+costos_fijos/100)
                m  = (prec_r-ct)/prec_r*100 if prec_r>0 else None
                color = "green" if (m or 0)>=60 else ("orange" if (m or 0)>=40 else "red")
                st.info(f"💰 Costo ingredientes: **{fmt_cop(round(ci))}** | Costo total: **{fmt_cop(round(ct))}** | Margen: **:{color}[{f'{m:.1f}%' if m is not None else '—'}]**")

            if st.button("💾 Guardar receta", type="primary"):
                if not n_r.strip():        st.error("El nombre es obligatorio")
                elif not ing_data:         st.error("Agrega al menos un ingrediente")
                else:
                    db.add_receta({"nombre":n_r.strip(),"categoria":cat_r,"porciones":porc_r,
                                   "precio":prec_r,"ingredientes":ing_data})
                    st.session_state.ing_rows = [{}]
                    st.success(f"✅ Receta guardada: {n_r}")
                    reload()

    with tab_list:
        if not recetas:
            st.info("Sin recetas. Crea la primera en ➕ Nueva receta.")
        else:
            busq_r = st.text_input("🔍 Buscar receta")
            cat_f  = st.selectbox("Filtrar categoría", ["Todas"]+CAT_RECETA, key="rcatf")
            lista_r = [r for r in recetas
                       if (not busq_r or busq_r.lower() in r["nombre"].lower())
                       and (cat_f=="Todas" or r.get("categoria")==cat_f)]

            rows_r = []
            for r in lista_r:
                ci = calc.costo_ingredientes_receta(r, insumos, subrecetas)
                ct = calc.costo_receta(r, insumos, subrecetas, costos_fijos)
                m  = calc.margen_receta(r, insumos, subrecetas, costos_fijos)
                rows_r.append({"Receta":r["nombre"],"Categoría":r.get("categoria",""),
                                "Porciones":r.get("porciones",1),"Precio":fmt_cop(r.get("precio",0)),
                                "Costo total":fmt_cop(round(ct)),
                                "Margen":f"{m:.1f}%" if m is not None else "—",
                                "# Ing.":len(r.get("ingredientes",[]))})
            st.dataframe(pd.DataFrame(rows_r), hide_index=True, use_container_width=True)

            st.markdown("---")
            sel_r = st.selectbox("Ver detalle / eliminar", ["— Selecciona —"]+[r["nombre"] for r in lista_r])
            if sel_r != "— Selecciona —":
                rec = next(r for r in lista_r if r["nombre"]==sel_r)
                ci  = calc.costo_ingredientes_receta(rec, insumos, subrecetas)
                ct  = calc.costo_receta(rec, insumos, subrecetas, costos_fijos)
                m   = calc.margen_receta(rec, insumos, subrecetas, costos_fijos)
                st.subheader(f"📋 {rec['nombre']}")
                mc1,mc2,mc3,mc4 = st.columns(4)
                mc1.metric("Precio venta", fmt_cop(rec.get("precio",0)))
                mc2.metric("Costo ingredientes", fmt_cop(round(ci)))
                mc3.metric("Costo total", fmt_cop(round(ct)))
                mc4.metric("Margen", f"{m:.1f}%" if m is not None else "—")
                if rec.get("ingredientes"):
                    rows_ing = []
                    for ing in rec["ingredientes"]:
                        ref   = calc.resolve_ref(ing.get("ref_id",""), insumos, subrecetas)
                        bruta = calc.cant_bruta(ing.get("cantidad",0), ing.get("merma",0))
                        rows_ing.append({
                            "Ingrediente": ref["nombre"],
                            "Cant. neta":  ing.get("cantidad",0),
                            "Merma %":     ing.get("merma",0),
                            "Cant. bruta": round(bruta,3),
                            "Unidad":      ref["unidad"],
                            "Costo":       fmt_cop(round(ref["costo_unit"]*bruta)),
                        })
                    st.dataframe(pd.DataFrame(rows_ing), hide_index=True, use_container_width=True)
                if st.button(f"🗑️ Eliminar receta '{sel_r}'", type="secondary"):
                    db.delete_receta(rec["id"]); st.warning("Receta eliminada"); reload()


# ══════════════════════════════════════════════════════════════════════════════
#  SUB-RECETAS
# ══════════════════════════════════════════════════════════════════════════════
elif current == "subrecetas":
    st.title("🧪 Sub-recetas")
    tab_list, tab_add = st.tabs(["📋 Listado","➕ Nueva sub-receta"])

    with tab_add:
        if not insumos:
            st.warning("Agrega insumos primero.")
        else:
            n_s   = st.text_input("Nombre de la sub-receta *")
            sc1,sc2,sc3 = st.columns(3)
            cat_s  = sc1.selectbox("Categoría", ["Base","Salsa","Aliño","Masa","Relleno","Pastelería","Panadería","Otro"])
            rend_s = sc2.number_input("Rendimiento", min_value=0.01, step=1.0)
            u_s    = sc3.selectbox("Unidad rendimiento", UNIDADES)

            st.markdown("**Ingredientes**")
            if "sub_rows" not in st.session_state:
                st.session_state.sub_rows = [{}]

            opts_s = {f"📦 {i['nombre']} ({i.get('unidad','')})": f"ins:{i['id']}" for i in insumos}
            sub_data = []
            for idx in range(len(st.session_state.sub_rows)):
                si1,si2,si3,si4 = st.columns([4,1.5,1.5,0.5])
                sel_s = si1.selectbox("Ingrediente", ["— Selecciona —"]+list(opts_s.keys()), key=f"si_{idx}")
                cant_s = si2.number_input("Cant.", min_value=0.0, step=0.01, key=f"sc_{idx}")
                merma_s = si3.number_input("Merma %", min_value=0.0, max_value=99.0, key=f"sm_{idx}")
                if si4.button("✕", key=f"sd_{idx}"):
                    st.session_state.sub_rows.pop(idx); st.rerun()
                if sel_s != "— Selecciona —":
                    sub_data.append({"ref_id":opts_s[sel_s],"cantidad":cant_s,"merma":merma_s})

            if st.button("➕ Agregar ingrediente", key="sub_add"):
                st.session_state.sub_rows.append({}); st.rerun()

            if sub_data and rend_s > 0:
                ct_s = sum(calc.costo_ingrediente(i["ref_id"],i["cantidad"],i["merma"],insumos,subrecetas) for i in sub_data)
                st.info(f"💰 Costo elaboración: **{fmt_cop(round(ct_s))}** | Costo / {u_s}: **{fmt_cop(round(ct_s/rend_s))}**")

            if st.button("💾 Guardar sub-receta", type="primary"):
                if not n_s.strip():     st.error("El nombre es obligatorio")
                elif rend_s <= 0:       st.error("Define el rendimiento")
                elif not sub_data:      st.error("Agrega al menos un ingrediente")
                else:
                    db.add_subreceta({"nombre":n_s.strip(),"categoria":cat_s,"rendimiento":rend_s,
                                      "unidad_rendimiento":u_s,"ingredientes":sub_data})
                    st.session_state.sub_rows = [{}]
                    st.success(f"✅ Sub-receta guardada: {n_s}")
                    reload()

    with tab_list:
        if not subrecetas:
            st.info("Sin sub-recetas aún.")
        else:
            rows_s = []
            for s in subrecetas:
                ct_s = calc.costo_subreceta(s, insumos, subrecetas)
                rend = s.get("rendimiento",1) or 1
                rows_s.append({"Nombre":s["nombre"],"Categoría":s.get("categoria",""),
                                "Rendimiento":f"{rend} {s.get('unidad_rendimiento','')}",
                                "Costo elaboración":fmt_cop(round(ct_s)),
                                "Costo / unidad":fmt_cop(round(ct_s/rend)),
                                "# Ingredientes":len(s.get("ingredientes",[]))})
            st.dataframe(pd.DataFrame(rows_s), hide_index=True, use_container_width=True)

            st.markdown("---")
            sel_s2 = st.selectbox("Ver detalle / eliminar", ["— Selecciona —"]+[s["nombre"] for s in subrecetas])
            if sel_s2 != "— Selecciona —":
                sub = next(s for s in subrecetas if s["nombre"]==sel_s2)
                ct_sub = calc.costo_subreceta(sub, insumos, subrecetas)
                rend   = sub.get("rendimiento",1) or 1
                st.markdown(f"**Rendimiento:** {rend} {sub.get('unidad_rendimiento','')} | **Costo elaboración:** {fmt_cop(round(ct_sub))} | **Costo/unidad:** {fmt_cop(round(ct_sub/rend))}")
                rows_si = []
                for ing in sub.get("ingredientes",[]):
                    ref   = calc.resolve_ref(ing.get("ref_id",""), insumos, subrecetas)
                    bruta = calc.cant_bruta(ing.get("cantidad",0), ing.get("merma",0))
                    rows_si.append({"Ingrediente":ref["nombre"],"Cant. neta":ing.get("cantidad",0),
                                    "Merma %":ing.get("merma",0),"Cant. bruta":round(bruta,3),
                                    "Unidad":ref["unidad"],"Costo":fmt_cop(round(ref["costo_unit"]*bruta))})
                st.dataframe(pd.DataFrame(rows_si), hide_index=True, use_container_width=True)
                if st.button(f"🗑️ Eliminar '{sel_s2}'", type="secondary"):
                    db.delete_subreceta(sub["id"]); st.warning("Sub-receta eliminada"); reload()


# ══════════════════════════════════════════════════════════════════════════════
#  MOVIMIENTOS
# ══════════════════════════════════════════════════════════════════════════════
elif current == "movimientos":
    st.title("↕️ Movimientos de Inventario")
    tab_e, tab_s, tab_v, tab_hist = st.tabs(["📥 Entrada de insumo","📤 Salida de insumo","🍽️ Venta / Despacho","📋 Historial"])

    # ── ENTRADA ───────────────────────────────────────────────────────────────
    with tab_e:
        st.subheader("Registrar entrada de insumo")
        st.info("Suma la cantidad al stock existente. Si el costo cambió, actualiza el precio del insumo.")
        if not insumos:
            st.warning("No hay insumos registrados.")
        else:
            with st.form("form_entrada", clear_on_submit=True):
                opts_e = {f"{i['nombre']} — stock actual: {fmt_n(i.get('stock',0))} {i.get('unidad','')}": i for i in insumos}
                sel_e  = st.selectbox("Insumo *", ["— Selecciona —"]+list(opts_e.keys()))
                ec1,ec2 = st.columns(2)
                cant_e  = ec1.number_input("Cantidad que entra *", min_value=0.01, step=0.5)
                costo_e = ec2.number_input("Costo por unidad (COP, 0 = mantener actual)", min_value=0.0, step=100.0)
                ec3,ec4 = st.columns(2)
                fecha_e = ec3.date_input("Fecha", value=date.today())
                resp_e  = ec4.text_input("Responsable")
                prov_e  = st.text_input("Proveedor")
                nota_e  = st.text_input("Nota")
                if st.form_submit_button("✅ Registrar entrada", use_container_width=True, type="primary"):
                    if sel_e == "— Selecciona —":
                        st.error("Selecciona un insumo")
                    else:
                        ins_e = opts_e[sel_e]
                        nuevo_costo = costo_e if costo_e > 0 else ins_e.get("costo",0)
                        upd = {"stock": ins_e.get("stock",0)+cant_e, "ultima_entrada": str(fecha_e)}
                        if costo_e > 0 and costo_e != ins_e.get("costo",0):
                            hist = ins_e.get("historial_precios") or []
                            hist.append({"fecha":str(fecha_e),"precio":costo_e,"precio_anterior":ins_e.get("costo",0)})
                            upd["costo"] = costo_e
                            upd["historial_precios"] = hist
                        db.update_insumo(ins_e["id"], upd)
                        db.add_movimiento({"tipo":"entrada","insumo_id":ins_e["id"],"nombre":ins_e["nombre"],
                                           "cantidad":cant_e,"costo_unit":nuevo_costo,"fecha":str(fecha_e),
                                           "responsable":resp_e or "—","nota":nota_e,"proveedor":prov_e})
                        nuevo_stock = ins_e.get("stock",0)+cant_e
                        st.success(f"✅ Entrada registrada: +{fmt_n(cant_e)} {ins_e.get('unidad','')} de **{ins_e['nombre']}** → Stock nuevo: **{fmt_n(nuevo_stock)}**")
                        reload()

    # ── SALIDA ────────────────────────────────────────────────────────────────
    with tab_s:
        st.subheader("Registrar salida de insumo")
        st.info("Descuenta la cantidad del stock (consumo de cocina, transferencia, etc.).")
        if not insumos:
            st.warning("No hay insumos registrados.")
        else:
            with st.form("form_salida", clear_on_submit=True):
                opts_s2 = {f"{i['nombre']} — stock actual: {fmt_n(i.get('stock',0))} {i.get('unidad','')}": i for i in insumos}
                sel_s2  = st.selectbox("Insumo *", ["— Selecciona —"]+list(opts_s2.keys()))
                sc1,sc2 = st.columns(2)
                cant_s2  = sc1.number_input("Cantidad que sale *", min_value=0.01, step=0.5)
                fecha_s2 = sc2.date_input("Fecha", value=date.today())
                sc3,sc4  = st.columns(2)
                resp_s2  = sc3.text_input("Responsable")
                motivo_s = sc4.selectbox("Motivo", ["Consumo cocina","Merma","Transferencia","Otro"])
                nota_s2  = st.text_input("Nota adicional")
                if st.form_submit_button("✅ Registrar salida", use_container_width=True, type="primary"):
                    if sel_s2 == "— Selecciona —":
                        st.error("Selecciona un insumo")
                    else:
                        ins_s2 = opts_s2[sel_s2]
                        if cant_s2 > ins_s2.get("stock",0):
                            st.error(f"Stock insuficiente. Disponible: {fmt_n(ins_s2.get('stock',0))} {ins_s2.get('unidad','')}")
                        else:
                            nuevo_stk = ins_s2.get("stock",0)-cant_s2
                            db.update_insumo(ins_s2["id"], {"stock": nuevo_stk})
                            db.add_movimiento({"tipo":"salida","insumo_id":ins_s2["id"],"nombre":ins_s2["nombre"],
                                               "cantidad":cant_s2,"costo_unit":ins_s2.get("costo",0),
                                               "fecha":str(fecha_s2),"responsable":resp_s2 or "—",
                                               "nota":f"{motivo_s} · {nota_s2}".strip(" ·")})
                            st.success(f"✅ Salida registrada: -{fmt_n(cant_s2)} {ins_s2.get('unidad','')} de **{ins_s2['nombre']}** → Stock nuevo: **{fmt_n(nuevo_stk)}**")
                            reload()

    # ── VENTA ─────────────────────────────────────────────────────────────────
    with tab_v:
        st.subheader("Registrar venta / despacho")
        st.info("Selecciona la receta vendida. El sistema descuenta automáticamente los insumos del inventario.")
        if not recetas:
            st.warning("No hay recetas registradas.")
        else:
            opts_v  = {r["nombre"]: r for r in recetas}
            sel_v   = st.selectbox("Receta vendida *", ["— Selecciona —"]+list(opts_v.keys()))
            cant_v  = st.number_input("Cantidad de porciones", min_value=1, step=1, value=1)
            vc1,vc2 = st.columns(2)
            fecha_v = vc1.date_input("Fecha", value=date.today())
            resp_v  = vc2.text_input("Responsable")

            if sel_v != "— Selecciona —":
                rec_v = opts_v[sel_v]
                ci    = calc.costo_ingredientes_receta(rec_v, insumos, subrecetas)
                ct    = calc.costo_receta(rec_v, insumos, subrecetas, costos_fijos)
                st.markdown("**Insumos que se descontarán:**")
                ok_all = True
                for ing in rec_v.get("ingredientes",[]):
                    ref_id = ing.get("ref_id","")
                    if ref_id.startswith("ins:"):
                        ins_id  = ref_id[4:]
                        ins_obj = next((i for i in insumos if i["id"]==ins_id), None)
                        if ins_obj:
                            need  = ing.get("cantidad",0)*cant_v
                            bruta = calc.cant_bruta(need, ing.get("merma",0))
                            disp  = ins_obj.get("stock",0)
                            ok    = disp >= bruta
                            if not ok: ok_all = False
                            color = "green" if ok else "red"
                            st.markdown(f":{color}[{'✓' if ok else '⚠️ INSUFICIENTE'}] **{ins_obj['nombre']}**: -{fmt_n(round(bruta,3))} {ins_obj.get('unidad','')} (disponible: {fmt_n(disp)})")
                st.info(f"Costo de esta venta: **{fmt_cop(round(ct*cant_v))}** | Precio: **{fmt_cop(round((rec_v.get('precio',0) or 0)*cant_v))}**")

            if st.button("✅ Registrar venta", type="primary", use_container_width=True):
                if sel_v == "— Selecciona —":
                    st.error("Selecciona una receta")
                else:
                    rec_v2 = opts_v[sel_v]
                    sin_stock = []
                    for ing in rec_v2.get("ingredientes",[]):
                        if ing.get("ref_id","").startswith("ins:"):
                            ins_id = ing["ref_id"][4:]
                            ins_obj = next((i for i in insumos if i["id"]==ins_id), None)
                            if ins_obj:
                                bruta = calc.cant_bruta(ing.get("cantidad",0)*cant_v, ing.get("merma",0))
                                if ins_obj.get("stock",0) < bruta:
                                    sin_stock.append(ins_obj["nombre"])
                    if sin_stock:
                        st.error(f"Stock insuficiente: {', '.join(sin_stock)}")
                    else:
                        for ing in rec_v2.get("ingredientes",[]):
                            if ing.get("ref_id","").startswith("ins:"):
                                ins_id = ing["ref_id"][4:]
                                ins_obj = next((i for i in insumos if i["id"]==ins_id), None)
                                if ins_obj:
                                    bruta = calc.cant_bruta(ing.get("cantidad",0)*cant_v, ing.get("merma",0))
                                    db.update_insumo(ins_id, {"stock": max(0, ins_obj.get("stock",0)-bruta)})
                        db.add_movimiento({"tipo":"venta","receta_id":rec_v2["id"],
                                           "nombre":f"{rec_v2['nombre']}"+(f" x{cant_v}" if cant_v>1 else ""),
                                           "cantidad":cant_v,"fecha":str(fecha_v),
                                           "responsable":resp_v or "—","nota":"Venta registrada"})
                        st.success(f"✅ Venta registrada: {cant_v} × **{rec_v2['nombre']}**")
                        reload()

    # ── HISTORIAL ─────────────────────────────────────────────────────────────
    with tab_hist:
        st.subheader("Historial de movimientos")
        hc1,hc2,hc3 = st.columns(3)
        busq_m  = hc1.text_input("🔍 Buscar")
        ftipo   = hc2.selectbox("Tipo", ["Todos","entrada","salida","venta","baja"])
        ffecha  = hc3.date_input("Fecha", value=None)

        lista_m = movs
        if busq_m:  lista_m = [m for m in lista_m if busq_m.lower() in (m.get("nombre") or "").lower()]
        if ftipo != "Todos": lista_m = [m for m in lista_m if m.get("tipo")==ftipo]
        if ffecha:  lista_m = [m for m in lista_m if m.get("fecha")==str(ffecha)]

        if lista_m:
            df_mh = pd.DataFrame([{"Fecha":m.get("fecha"),"Tipo":m.get("tipo"),
                                    "Insumo/Plato":m.get("nombre") or "—","Cantidad":m.get("cantidad"),
                                    "Costo unit.":fmt_cop(m.get("costo_unit")),"Responsable":m.get("responsable") or "—",
                                    "Nota":m.get("nota") or "—"} for m in lista_m[:500]])
            st.dataframe(df_mh, hide_index=True, use_container_width=True)
            csv_m = df_mh.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Exportar movimientos CSV", csv_m, f"movimientos_{hoy()}.csv", "text/csv")
        else:
            st.info("Sin movimientos en este filtro.")


# ══════════════════════════════════════════════════════════════════════════════
#  KARDEX
# ══════════════════════════════════════════════════════════════════════════════
elif current == "kardex":
    st.title("📒 Kardex — Trazabilidad por insumo")
    if not insumos:
        st.info("Sin insumos registrados.")
    else:
        kc1,kc2,kc3 = st.columns([3,2,2])
        sel_k  = kc1.selectbox("Insumo", ["— Selecciona —"]+[i["nombre"] for i in insumos])
        desde_k = kc2.date_input("Desde", value=date.today()-timedelta(days=30))
        hasta_k = kc3.date_input("Hasta", value=date.today())

        if sel_k != "— Selecciona —":
            ins_k = next(i for i in insumos if i["nombre"]==sel_k)
            d_str, h_str = str(desde_k), str(hasta_k)

            st.markdown(f"### 📒 {ins_k['nombre']}")
            mc1,mc2,mc3,mc4 = st.columns(4)
            mc1.metric("Stock actual", f"{fmt_n(ins_k.get('stock',0))} {ins_k.get('unidad','')}")
            mc2.metric("Costo unitario", fmt_cop(ins_k.get("costo",0)))
            mc3.metric("Valor en stock", fmt_cop(round(ins_k.get("stock",0)*ins_k.get("costo",0))))
            mc4.metric("Mínimo", f"{fmt_n(ins_k.get('minimo',0))} {ins_k.get('unidad','')}")

            movs_k = [m for m in movs if m.get("insumo_id")==ins_k["id"] and d_str<=(m.get("fecha") or "")<=h_str]
            ventas_k = []
            for m in movs:
                if m.get("tipo")!="venta" or not (d_str<=(m.get("fecha") or "")<=h_str): continue
                rec_v = next((r for r in recetas if r["id"]==m.get("receta_id")), None)
                if not rec_v: continue
                for ing in rec_v.get("ingredientes",[]):
                    if ing.get("ref_id","")==f"ins:{ins_k['id']}":
                        bruta = calc.cant_bruta(ing.get("cantidad",0)*m.get("cantidad",1), ing.get("merma",0))
                        ventas_k.append({"tipo":"venta","nombre":f"Venta: {rec_v['nombre']}",
                                         "cantidad":bruta,"costo_unit":ins_k.get("costo",0),
                                         "fecha":m.get("fecha"),"responsable":m.get("responsable","—"),"signo":-1})

            all_k = sorted(
                [dict(m, signo=1 if m.get("tipo")=="entrada" else -1) for m in movs_k]+ventas_k,
                key=lambda m: m.get("fecha","")
            )

            ent_t = sum(m["cantidad"] for m in all_k if m.get("tipo")=="entrada")
            sal_t = sum(m["cantidad"] for m in all_k if m.get("tipo")=="salida")
            ven_t = sum(m["cantidad"] for m in all_k if m.get("tipo")=="venta")
            baj_t = sum(m["cantidad"] for m in all_k if m.get("tipo")=="baja")

            st.markdown("---")
            kk1,kk2,kk3,kk4 = st.columns(4)
            kk1.metric("Entradas", fmt_n(ent_t))
            kk2.metric("Salidas manuales", fmt_n(sal_t))
            kk3.metric("Consumido en ventas", fmt_n(ven_t))
            kk4.metric("Bajas", fmt_n(baj_t))

            if all_k:
                balance = 0.0
                rows_k = []
                for m in all_k:
                    ent = m["cantidad"] if m.get("signo",1)>0 else None
                    sal = m["cantidad"] if m.get("signo",1)<0 else None
                    balance += (ent or 0)-(sal or 0)
                    rows_k.append({"Fecha":m.get("fecha"),"Tipo":m.get("tipo"),
                                   "Descripción":m.get("nombre") or "—",
                                   "Entrada":f"+{fmt_n(ent)}" if ent else "—",
                                   "Salida":f"-{fmt_n(sal)}" if sal else "—",
                                   "Saldo":fmt_n(max(0,balance)),
                                   "Costo unit.":fmt_cop(m.get("costo_unit",ins_k.get("costo",0))),
                                   "Responsable":m.get("responsable") or "—"})
                st.dataframe(pd.DataFrame(rows_k), hide_index=True, use_container_width=True)

            if ins_k.get("historial_precios") and len(ins_k["historial_precios"])>1:
                st.subheader("📊 Historial de precios")
                df_hp = pd.DataFrame(ins_k["historial_precios"])
                fig_hp = px.line(df_hp, x="fecha", y="precio", markers=True,
                                 color_discrete_sequence=["#2d6a4f"])
                fig_hp.update_layout(height=220, margin=dict(t=10,b=10))
                st.plotly_chart(fig_hp, use_container_width=True)
            else:
                st.info("Sin movimientos en el período seleccionado.")


# ══════════════════════════════════════════════════════════════════════════════
#  BAJAS
# ══════════════════════════════════════════════════════════════════════════════
elif current == "bajas":
    st.title("🗑️ Control de Bajas")
    tab_reg, tab_hist = st.tabs(["➕ Registrar baja","📋 Historial y resumen"])

    with tab_reg:
        if not insumos:
            st.warning("Sin insumos registrados.")
        else:
            with st.form("form_baja", clear_on_submit=True):
                opts_b = {f"{i['nombre']} — stock: {fmt_n(i.get('stock',0))} {i.get('unidad','')}": i for i in insumos}
                sel_b  = st.selectbox("Insumo *", ["— Selecciona —"]+list(opts_b.keys()))
                bc1,bc2 = st.columns(2)
                cant_b  = bc1.number_input("Cantidad *", min_value=0.01, step=0.5)
                fecha_b = bc2.date_input("Fecha", value=date.today())
                bc3,bc4 = st.columns(2)
                causa_b = bc3.selectbox("Causa", CAUSAS_BAJA)
                turno_b = bc4.selectbox("Turno", TURNOS)
                bc5,bc6 = st.columns(2)
                resp_b  = bc5.text_input("Responsable")
                autor_b = bc6.text_input("Autoriza")
                accion_b = st.text_input("Acción correctiva")
                if st.form_submit_button("✅ Registrar baja", use_container_width=True, type="primary"):
                    if sel_b == "— Selecciona —":
                        st.error("Selecciona un insumo")
                    else:
                        ins_b = opts_b[sel_b]
                        if cant_b > ins_b.get("stock",0):
                            st.error(f"Cantidad mayor al stock disponible: {fmt_n(ins_b.get('stock',0))}")
                        else:
                            costo_t = ins_b.get("costo",0)*cant_b
                            db.update_insumo(ins_b["id"], {"stock": ins_b.get("stock",0)-cant_b})
                            db.add_baja({"insumo_id":ins_b["id"],"nombre":ins_b["nombre"],
                                         "unidad":ins_b.get("unidad",""),"cantidad":cant_b,
                                         "costo_unit":ins_b.get("costo",0),"costo_total":costo_t,
                                         "causa":causa_b,"turno":turno_b,"fecha":str(fecha_b),
                                         "responsable":resp_b or "—","autoriza":autor_b or "—","accion":accion_b})
                            db.add_movimiento({"tipo":"baja","insumo_id":ins_b["id"],"nombre":ins_b["nombre"],
                                               "cantidad":cant_b,"costo_unit":ins_b.get("costo",0),
                                               "fecha":str(fecha_b),"responsable":resp_b or "—",
                                               "nota":f"BAJA: {causa_b}"})
                            st.success(f"✅ Baja: {fmt_n(cant_b)} {ins_b.get('unidad','')} de **{ins_b['nombre']}** — {fmt_cop(round(costo_t))}")
                            reload()

    with tab_hist:
        lunes_b = date.today()-timedelta(days=date.today().weekday())
        bajas_sem = [b for b in bajas if (b.get("fecha") or "")>=str(lunes_b)]
        total_sem = sum(b.get("costo_total",0) for b in bajas_sem)
        bc1,bc2 = st.columns(2)
        bc1.metric("Bajas esta semana", fmt_cop(round(total_sem)))
        bc2.metric("Registros", len(bajas_sem))

        if bajas_sem:
            resumen_c = {c: sum(b.get("costo_total",0) for b in bajas_sem if b.get("causa")==c) for c in CAUSAS_BAJA}
            df_rc = pd.DataFrame([{"Causa":c,"Total COP":fmt_cop(round(v)),
                                    "Registros":sum(1 for b in bajas_sem if b.get("causa")==c)}
                                   for c,v in resumen_c.items() if v>0])
            if not df_rc.empty:
                st.dataframe(df_rc, hide_index=True, use_container_width=True)

        fcausa = st.selectbox("Filtrar causa", ["Todas"]+CAUSAS_BAJA)
        lista_b = bajas if fcausa=="Todas" else [b for b in bajas if b.get("causa")==fcausa]
        if lista_b:
            df_b = pd.DataFrame([{"Fecha":b.get("fecha"),"Turno":b.get("turno"),
                                   "Insumo":b.get("nombre"),"Cantidad":f"{fmt_n(b.get('cantidad',0))} {b.get('unidad','')}",
                                   "Costo total":fmt_cop(round(b.get("costo_total",0))),"Causa":b.get("causa"),
                                   "Responsable":b.get("responsable"),"Autoriza":b.get("autoriza")} for b in lista_b[:300]])
            st.dataframe(df_b, hide_index=True, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ALERTAS
# ══════════════════════════════════════════════════════════════════════════════
elif current == "alertas":
    st.title("🔔 Alertas")

    st.subheader("📦 Stock bajo el mínimo")
    bajo_a = [i for i in insumos if i.get("minimo",0)>0 and i.get("stock",0)<=i["minimo"]]
    if bajo_a:
        df_bajo = pd.DataFrame([{"Insumo":i["nombre"],"Categoría":i.get("categoria"),
                                  "Stock actual":fmt_n(i.get("stock",0)),"Stock mínimo":fmt_n(i.get("minimo",0)),
                                  "Faltante":fmt_n(max(0,i.get("minimo",0)-i.get("stock",0))),
                                  "Unidad":i.get("unidad"),"Proveedor":i.get("proveedor") or "—"} for i in bajo_a])
        st.dataframe(df_bajo, hide_index=True, use_container_width=True)
    else:
        st.success("✅ Todo el stock sobre el mínimo")

    st.markdown("---")
    st.subheader("⏰ Vencimientos próximos (≤ 3 días)")
    hoy_d = date.today()
    proximos = []
    for i in insumos:
        if not i.get("vida_util") or not i.get("ultima_entrada"): continue
        try:
            ult   = date.fromisoformat(i["ultima_entrada"])
            vence = ult+timedelta(days=int(i["vida_util"]))
            dias  = (vence-hoy_d).days
            if dias <= 3:
                proximos.append({"Insumo":i["nombre"],"Vida útil":f"{i['vida_util']}d",
                                  "Última entrada":str(ult),"Vence":str(vence),
                                  "Estado":"VENCIDO" if dias<0 else ("HOY" if dias==0 else f"En {dias}d")})
        except Exception: continue
    if proximos:
        st.dataframe(pd.DataFrame(proximos), hide_index=True, use_container_width=True)
    else:
        st.success("✅ Sin vencimientos próximos")

    st.markdown("---")
    st.subheader("💲 Fluctuaciones de precio")
    flucts = []
    for i in insumos:
        hist = i.get("historial_precios") or []
        if len(hist)<2: continue
        for j in range(len(hist)-1,0,-1):
            ant = hist[j-1].get("precio",0)
            act = hist[j].get("precio",0)
            if not ant or ant<=0: continue
            pct = (act-ant)/ant*100
            if pct >= umbral_precio:
                flucts.append({"Insumo":i["nombre"],"Categoría":i.get("categoria"),
                                "Precio anterior":fmt_cop(ant),"Precio nuevo":fmt_cop(act),
                                "Variación":f"▲ {pct:.1f}%","Fecha":hist[j].get("fecha"),
                                "Proveedor":i.get("proveedor") or "—"})
                break
    if flucts:
        st.warning(f"{len(flucts)} insumo(s) con aumento ≥ {umbral_precio}%")
        st.dataframe(pd.DataFrame(flucts), hide_index=True, use_container_width=True)
    else:
        st.success(f"✅ Sin fluctuaciones ≥ {umbral_precio}%")


# ══════════════════════════════════════════════════════════════════════════════
#  REPORTES
# ══════════════════════════════════════════════════════════════════════════════
elif current == "reportes":
    st.title("📈 Reportes")
    tab_inv, tab_bajas, tab_cons = st.tabs(["📦 Inventario","🗑️ Bajas","📊 Consumo"])

    with tab_inv:
        if insumos:
            total_v = sum(i.get("stock",0)*i.get("costo",0) for i in insumos)
            st.metric("Valor total inventario", fmt_cop(round(total_v)))
            cat_s = st.selectbox("Filtrar categoría", ["Todas"]+CATEGORIAS, key="rcat")
            lista_ri = insumos if cat_s=="Todas" else [i for i in insumos if i.get("categoria")==cat_s]
            df_ri = pd.DataFrame([{"Insumo":i["nombre"],"Categoría":i.get("categoria"),
                                    "Stock":i.get("stock",0),"Unidad":i.get("unidad"),
                                    "Mínimo":i.get("minimo",0),"Costo":fmt_cop(i.get("costo",0)),
                                    "Valor":fmt_cop(round(i.get("stock",0)*i.get("costo",0))),
                                    "Estado":"⚠️ Bajo" if i.get("minimo",0)>0 and i.get("stock",0)<=i["minimo"] else "✓ OK"}
                                   for i in lista_ri])
            st.dataframe(df_ri, hide_index=True, use_container_width=True)
            cats_d = {}
            for i in insumos:
                cats_d[i.get("categoria","Otros")] = cats_d.get(i.get("categoria","Otros"),0)+i.get("stock",0)*i.get("costo",0)
            fig_c = px.bar(x=list(cats_d.keys()), y=[round(v/1000) for v in cats_d.values()],
                           labels={"x":"Categoría","y":"Valor (miles COP)"}, color_discrete_sequence=["#2d6a4f"])
            fig_c.update_layout(height=280, margin=dict(t=10,b=10))
            st.plotly_chart(fig_c, use_container_width=True)
            csv_ri = df_ri.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Exportar reporte inventario", csv_ri, f"reporte_inventario_{hoy()}.csv","text/csv")

    with tab_bajas:
        if bajas:
            sem_data = []
            for w in range(7,-1,-1):
                lun = hoy_d = date.today()
                lun = lun-timedelta(days=lun.weekday()+w*7)
                dom = lun+timedelta(days=6)
                t   = sum(b.get("costo_total",0) for b in bajas if str(lun)<=(b.get("fecha") or "")<=str(dom))
                sem_data.append({"Semana":f"S-{w}","Bajas (COP)":round(t/1000)})
            fig_sem = px.line(pd.DataFrame(sem_data), x="Semana", y="Bajas (COP)",
                              markers=True, color_discrete_sequence=["#ef4444"])
            fig_sem.update_layout(height=250, margin=dict(t=10,b=10))
            st.plotly_chart(fig_sem, use_container_width=True)
            causa_t = {c: sum(b.get("costo_total",0) for b in bajas if b.get("causa")==c) for c in CAUSAS_BAJA}
            fig_pie = px.pie(values=list(causa_t.values()), names=list(causa_t.keys()),
                             color_discrete_sequence=px.colors.qualitative.Set2)
            fig_pie.update_layout(height=300, margin=dict(t=10,b=10))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Sin bajas registradas.")

    with tab_cons:
        st.subheader("Top 10 ingredientes más consumidos (ventas + salidas)")
        consumo = {}
        for m in movs:
            if m.get("tipo")=="venta":
                rec_v = next((r for r in recetas if r["id"]==m.get("receta_id")), None)
                if rec_v:
                    for ing in rec_v.get("ingredientes",[]):
                        ref = calc.resolve_ref(ing.get("ref_id",""), insumos, subrecetas)
                        consumo[ref["nombre"]] = consumo.get(ref["nombre"],0)+ing.get("cantidad",0)*m.get("cantidad",1)
            elif m.get("tipo")=="salida":
                consumo[m.get("nombre","?")] = consumo.get(m.get("nombre","?"),0)+m.get("cantidad",0)
        top = sorted(consumo.items(), key=lambda x:x[1], reverse=True)[:10]
        if top:
            fig_top = px.bar(x=[t[1] for t in top], y=[t[0] for t in top], orientation="h",
                             color_discrete_sequence=["#40916c"])
            fig_top.update_layout(height=350, margin=dict(t=10,b=10), xaxis_title="Unidades consumidas")
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("Sin datos de consumo aún.")


# ══════════════════════════════════════════════════════════════════════════════
#  PROYECCIÓN DE PRODUCCIÓN SEMANAL
# ══════════════════════════════════════════════════════════════════════════════
elif current == "produccion":
    st.title("🏭 Proyección de Producción Semanal")
    st.markdown("Define cuántas porciones de cada receta vas a producir esta semana. El sistema calcula los insumos necesarios y los compara con tu stock actual.")

    if not recetas:
        st.warning("No hay recetas registradas. Crea recetas primero.")
    else:
        # Filtros por categoría
        cats_prod = ["Todas"] + sorted(set(r.get("categoria","") for r in recetas))
        col_f1, col_f2 = st.columns([2,3])
        cat_prod = col_f1.selectbox("Filtrar por categoría", cats_prod)
        semana_label = col_f2.text_input("Etiqueta de semana", value=f"Semana del {str(date.today()-timedelta(days=date.today().weekday()))}")

        recetas_prod = recetas if cat_prod=="Todas" else [r for r in recetas if r.get("categoria")==cat_prod]

        st.markdown("---")
        st.subheader("📝 Definir porciones por receta")
        st.markdown("*Modifica las cantidades según tu proyección de ventas:*")

        # Tabla de porciones
        if "porciones_prod" not in st.session_state:
            st.session_state.porciones_prod = {}

        for r in recetas_prod:
            default = st.session_state.porciones_prod.get(r["id"], int(r.get("porciones",1)))
            col_n, col_p = st.columns([4,1])
            col_n.markdown(f"**{r['nombre']}** — *{r.get('categoria','')}*")
            val = col_p.number_input("Porciones", min_value=0, step=1, value=default,
                                      key=f"prod_{r['id']}", label_visibility="collapsed")
            st.session_state.porciones_prod[r["id"]] = val

        st.markdown("---")
        st.subheader("📦 Insumos necesarios vs Stock disponible")

        # Calcular totales de insumos necesarios
        necesidades = {}  # insumo_id -> {nombre, unidad, cantidad_neta, cantidad_bruta}
        costo_total_prod = 0

        for r in recetas_prod:
            porciones = st.session_state.porciones_prod.get(r["id"], 0)
            if porciones <= 0: continue
            for ing in r.get("ingredientes",[]):
                ref_id = ing.get("ref_id","")
                if ref_id.startswith("ins:"):
                    ins_id = ref_id[4:]
                    ins_obj = next((i for i in insumos if i["id"]==ins_id), None)
                    if ins_obj:
                        cant_neta  = ing.get("cantidad",0)*porciones
                        cant_bruta = calc.cant_bruta(cant_neta, ing.get("merma",0))
                        if ins_id not in necesidades:
                            necesidades[ins_id] = {"nombre":ins_obj["nombre"],"unidad":ins_obj.get("unidad",""),
                                                    "stock":ins_obj.get("stock",0),"costo":ins_obj.get("costo",0),
                                                    "cantidad_bruta":0}
                        necesidades[ins_id]["cantidad_bruta"] += cant_bruta
                elif ref_id.startswith("sub:"):
                    sub_id = ref_id[4:]
                    sub    = next((s for s in subrecetas if s["id"]==sub_id), None)
                    if sub:
                        cant_sub = ing.get("cantidad",0)*porciones
                        for s_ing in sub.get("ingredientes",[]):
                            s_ref = s_ing.get("ref_id","")
                            if s_ref.startswith("ins:"):
                                s_ins_id = s_ref[4:]
                                s_ins = next((i for i in insumos if i["id"]==s_ins_id), None)
                                if s_ins:
                                    rend = sub.get("rendimiento",1) or 1
                                    factor = cant_sub/rend
                                    s_cant = calc.cant_bruta(s_ing.get("cantidad",0)*factor, s_ing.get("merma",0))
                                    if s_ins_id not in necesidades:
                                        necesidades[s_ins_id] = {"nombre":s_ins["nombre"],"unidad":s_ins.get("unidad",""),
                                                                   "stock":s_ins.get("stock",0),"costo":s_ins.get("costo",0),
                                                                   "cantidad_bruta":0}
                                    necesidades[s_ins_id]["cantidad_bruta"] += s_cant

        if necesidades:
            rows_prod = []
            compras_necesarias = []
            for ins_id, data in necesidades.items():
                stock  = data["stock"]
                need   = data["cantidad_bruta"]
                faltan = max(0, need-stock)
                estado = "✓ OK" if faltan==0 else "⚠️ Comprar"
                costo_t = faltan*data["costo"]
                costo_total_prod += costo_t
                rows_prod.append({
                    "Insumo":        data["nombre"],
                    "Necesario":     f"{fmt_n(round(need,3))} {data['unidad']}",
                    "Stock actual":  f"{fmt_n(stock)} {data['unidad']}",
                    "Faltante":      f"{fmt_n(round(faltan,3))} {data['unidad']}",
                    "Costo compra":  fmt_cop(round(costo_t)),
                    "Estado":        estado,
                })
                if faltan > 0:
                    compras_necesarias.append({"Insumo":data["nombre"],"Cantidad a comprar":f"{fmt_n(round(faltan,3))} {data['unidad']}","Costo estimado":fmt_cop(round(costo_t))})

            df_prod = pd.DataFrame(rows_prod)
            st.dataframe(df_prod, hide_index=True, use_container_width=True)

            if compras_necesarias:
                st.markdown("---")
                st.subheader("🛒 Lista de compras necesaria")
                st.metric("Costo total estimado de compras", fmt_cop(round(costo_total_prod)))
                df_compras = pd.DataFrame(compras_necesarias)
                st.dataframe(df_compras, hide_index=True, use_container_width=True)
                csv_comp = df_compras.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Exportar lista de compras", csv_comp,
                                   f"lista_compras_{hoy()}.csv","text/csv", use_container_width=True)
            else:
                st.success("✅ Tienes suficiente stock para toda la producción planificada.")

            # Resumen por receta
            st.markdown("---")
            st.subheader("📊 Resumen de costos por receta")
            rows_costo = []
            for r in recetas_prod:
                porciones = st.session_state.porciones_prod.get(r["id"],0)
                if porciones <= 0: continue
                ct = calc.costo_receta(r, insumos, subrecetas, costos_fijos)
                precio = r.get("precio",0) or 0
                rows_costo.append({
                    "Receta":     r["nombre"],
                    "Porciones":  porciones,
                    "Costo unit.":fmt_cop(round(ct)),
                    "Costo total":fmt_cop(round(ct*porciones)),
                    "Venta total":fmt_cop(round(precio*porciones)),
                    "Margen est.":f"{((precio-ct)/precio*100):.1f}%" if precio>0 else "—",
                })
            if rows_costo:
                st.dataframe(pd.DataFrame(rows_costo), hide_index=True, use_container_width=True)
                csv_plan = pd.DataFrame(rows_costo).to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Exportar plan de producción", csv_plan,
                                   f"plan_produccion_{hoy()}.csv","text/csv", use_container_width=True)
        else:
            st.info("Ingresa porciones mayores a 0 para ver la proyección de insumos.")


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════
elif current == "config":
    st.title("⚙️ Configuración")
    with st.form("form_cfg"):
        st.subheader("Parámetros del sistema")
        cf_v = st.number_input("% Costos fijos de cocina", 0.0, 100.0, value=costos_fijos, step=0.5,
                                help="Gas, electricidad, mano de obra indirecta, etc.")
        up_v = st.number_input("% Umbral alerta de precio", 0.1, 100.0, value=umbral_precio, step=0.5,
                                help="Alerta cuando un insumo sube su precio por encima de este %")
        if st.form_submit_button("💾 Guardar configuración", use_container_width=True):
            db.update_config(cf_v, up_v)
            st.success(f"✅ Configuración guardada")
            reload()
    st.markdown("---")
    st.subheader("🔄 Actualizar datos")
    if st.button("🔄 Recargar datos desde la base de datos"):
        reload()
