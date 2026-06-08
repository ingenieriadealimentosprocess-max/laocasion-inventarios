"""
La Ocasión · Sistema de Inventarios
Streamlit + Supabase — acceso desde cualquier PC con internet
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta

import db
import costos as calc

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIG DE PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="La Ocasión · Inventarios",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado
st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #1b4332; }
[data-testid="stSidebar"] * { color: #c8e6d4 !important; }
[data-testid="stSidebar"] .stButton button {
    background: transparent; border: none; color: #c8e6d4;
    text-align: left; width: 100%; padding: 8px 12px;
    border-radius: 6px; font-size: 14px;
}
[data-testid="stSidebar"] .stButton button:hover { background: rgba(255,255,255,.1); }
.kpi-box {
    background: white; border-radius: 10px; padding: 18px 20px;
    border-top: 3px solid #2d6a4f; box-shadow: 0 1px 4px rgba(0,0,0,.08);
    text-align: center;
}
.kpi-box.danger { border-top-color: #c0392b; }
.kpi-box.warn { border-top-color: #f0a500; }
.kpi-val { font-size: 26px; font-weight: 800; color: #1e2b24; }
.kpi-lbl { font-size: 12px; color: #5a7060; margin-top: 4px; }
.badge-ok { background: #d1fae5; color: #065f46; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
.badge-warn { background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
.badge-danger { background: #fee2e2; color: #991b1b; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  AUTENTICACIÓN SIMPLE
# ─────────────────────────────────────────────────────────────────────────────
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True
    st.markdown("## 🍽️ La Ocasión · Inventarios")
    st.markdown("---")
    pwd = st.text_input("Contraseña de acceso", type="password")
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
#  HELPERS DE FORMATO
# ─────────────────────────────────────────────────────────────────────────────
def fmt_cop(n):
    if n is None:
        return "—"
    return f"$ {int(round(n)):,}".replace(",", ".")


def fmt_n(n):
    if n is None:
        return "—"
    return f"{float(n):,.2f}".rstrip("0").rstrip(".")


# ─────────────────────────────────────────────────────────────────────────────
#  NAVEGACIÓN SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
PAGES = {
    "📊 Dashboard":      "dashboard",
    "📦 Insumos":        "insumos",
    "📋 Recetas":        "recetas",
    "🧪 Sub-recetas":    "subrecetas",
    "↕️ Movimientos":    "movimientos",
    "📒 Kardex":         "kardex",
    "🗑️ Bajas":         "bajas",
    "🔔 Alertas":        "alertas",
    "📈 Reportes":       "reportes",
    "⚙️ Configuración":  "config",
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
#  CARGA DE DATOS (con caché corto para que se actualice entre usuarios)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=10)
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


data = load_all()
insumos    = data["insumos"]
recetas    = data["recetas"]
subrecetas = data["subrecetas"]
movs       = data["movs"]
bajas      = data["bajas"]
cfg        = data["config"]
costos_fijos = float(cfg.get("costos_fijos", 15))
umbral_precio = float(cfg.get("umbral_precio", 3))

CATEGORIAS_INSUMO = ["Proteínas", "Lácteos", "Verduras", "Frutas", "Granos / Harinas",
                      "Aceites / Grasas", "Condimentos", "Bebidas", "Pastelería", "Otros"]
UNIDADES = ["g", "kg", "ml", "L", "unidad", "porción", "taza", "cucharada", "cucharadita", "manojo"]
CAUSAS_BAJA = ["Vencimiento", "Contaminación", "Error de preparación", "Sobre-producción",
               "Accidente / caída", "Devolución cliente", "Error de porción", "Otro"]
TURNOS = ["Mañana", "Tarde", "Noche"]


# ─────────────────────────────────────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if current == "dashboard":
    st.title("📊 Dashboard")

    bajo = [i for i in insumos if i.get("minimo", 0) > 0 and i.get("stock", 0) <= i["minimo"]]
    hoy_str = str(date.today())
    lunes = date.today() - timedelta(days=(date.today().weekday()))
    bajas_semana = sum(b.get("costo_total", 0) for b in bajas if b.get("fecha", "") >= str(lunes))
    movs_hoy = sum(1 for m in movs if m.get("fecha") == hoy_str)
    valor_total = sum(i.get("stock", 0) * i.get("costo", 0) for i in insumos)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    def kpi(col, val, lbl, tipo=""):
        col.markdown(f'<div class="kpi-box {tipo}"><div class="kpi-val">{val}</div><div class="kpi-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    kpi(c1, len(insumos), "Insumos")
    kpi(c2, len(bajo), "Stock crítico", "danger" if bajo else "")
    kpi(c3, len(recetas), "Recetas")
    kpi(c4, fmt_cop(round(bajas_semana / 1000)) + "k", "Bajas semana", "warn")
    kpi(c5, movs_hoy, "Movimientos hoy")
    kpi(c6, fmt_cop(round(valor_total / 1000)) + "k", "Valor inventario")

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("📉 Stock vs Mínimo")
        criticos = sorted(
            [i for i in insumos if i.get("minimo", 0) > 0],
            key=lambda i: (i.get("stock", 0) / max(i["minimo"], 0.001))
        )[:12]
        if criticos:
            df_c = pd.DataFrame({
                "Insumo": [i["nombre"][:22] for i in criticos],
                "Stock": [i.get("stock", 0) for i in criticos],
                "Mínimo": [i.get("minimo", 0) for i in criticos],
            })
            fig = go.Figure()
            colors = ["#ef4444" if r["Stock"] <= r["Mínimo"] else "#40916c" for _, r in df_c.iterrows()]
            fig.add_bar(x=df_c["Insumo"], y=df_c["Stock"], name="Stock", marker_color=colors)
            fig.add_scatter(x=df_c["Insumo"], y=df_c["Mínimo"], name="Mínimo",
                            mode="lines+markers", line=dict(color="#f0a500", width=2))
            fig.update_layout(height=300, margin=dict(t=10, b=10), legend=dict(orientation="h"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin insumos con stock mínimo definido.")

    with col_r:
        st.subheader("📅 Movimientos últimos 7 días")
        days = [(date.today() - timedelta(days=i)) for i in range(6, -1, -1)]
        day_strs = [str(d) for d in days]
        tipos_mov = {"Entradas": "entrada", "Ventas": "venta", "Bajas": "baja"}
        colors_mov = {
            "Entradas": ("#22c55e", "rgba(34,197,94,0.15)"),
            "Ventas":   ("#3b82f6", "rgba(59,130,246,0.15)"),
            "Bajas":    ("#ef4444", "rgba(239,68,68,0.15)"),
        }
        fig2 = go.Figure()
        for label, tipo in tipos_mov.items():
            counts = [sum(1 for m in movs if m.get("fecha") == d and m.get("tipo") == tipo) for d in day_strs]
            line_color, fill_color = colors_mov[label]
            fig2.add_scatter(x=[d[5:] for d in day_strs], y=counts, name=label,
                             mode="lines+markers", line=dict(color=line_color, width=2),
                             fill="tozeroy", fillcolor=fill_color)
        fig2.update_layout(height=300, margin=dict(t=10, b=10), legend=dict(orientation="h"))
        st.plotly_chart(fig2, use_container_width=True)

    col_l2, col_r2 = st.columns(2)
    with col_l2:
        st.subheader("⚠️ Alertas de stock bajo")
        if bajo:
            for i in bajo[:8]:
                st.markdown(
                    f"🔴 **{i['nombre']}** — {fmt_n(i.get('stock',0))} / {fmt_n(i.get('minimo',0))} {i.get('unidad','')} "
                    f"*({i.get('categoria','')})*"
                )
        else:
            st.success("✅ Todo el stock está sobre el mínimo")

    with col_r2:
        st.subheader("🕐 Últimos movimientos")
        if movs:
            df_movs = pd.DataFrame(movs[:8])[["fecha", "tipo", "nombre", "cantidad", "responsable"]]
            df_movs.columns = ["Fecha", "Tipo", "Insumo/Plato", "Cantidad", "Responsable"]
            st.dataframe(df_movs, hide_index=True, use_container_width=True)
        else:
            st.info("Sin movimientos registrados.")


# ─────────────────────────────────────────────────────────────────────────────
#  INSUMOS
# ─────────────────────────────────────────────────────────────────────────────
elif current == "insumos":
    st.title("📦 Insumos")

    tab1, tab2 = st.tabs(["📋 Listado", "➕ Agregar insumo"])

    with tab2:
        with st.form("form_insumo", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nombre  = c1.text_input("Nombre del insumo *")
            cat     = c2.selectbox("Categoría", CATEGORIAS_INSUMO)
            c3, c4, c5 = st.columns(3)
            unidad  = c3.selectbox("Unidad", UNIDADES)
            stock   = c4.number_input("Stock inicial", min_value=0.0, step=0.5)
            minimo  = c5.number_input("Stock mínimo", min_value=0.0, step=0.5)
            c6, c7, c8 = st.columns(3)
            costo   = c6.number_input("Costo por unidad (COP)", min_value=0.0, step=100.0)
            proveedor = c7.text_input("Proveedor")
            vida_util = c8.number_input("Vida útil (días, 0=sin límite)", min_value=0, step=1)
            submit = st.form_submit_button("💾 Guardar insumo", use_container_width=True)
            if submit:
                if not nombre.strip():
                    st.error("El nombre es obligatorio")
                else:
                    db.add_insumo({
                        "nombre": nombre.strip(),
                        "categoria": cat,
                        "unidad": unidad,
                        "stock": stock,
                        "minimo": minimo,
                        "costo": costo,
                        "proveedor": proveedor.strip(),
                        "vida_util": vida_util,
                        "ultima_entrada": db.hoy(),
                        "historial_precios": [{"fecha": db.hoy(), "precio": costo}] if costo > 0 else [],
                    })
                    st.success(f"✅ Insumo guardado: {nombre}")
                    reload()

    with tab1:
        col_b, col_c, col_s = st.columns([3, 2, 2])
        busq = col_b.text_input("🔍 Buscar", placeholder="Nombre o proveedor...")
        filtro_cat = col_c.selectbox("Categoría", ["Todas"] + CATEGORIAS_INSUMO, key="fcat")
        filtro_stk = col_s.selectbox("Stock", ["Todos", "Stock bajo", "Stock OK"], key="fstk")

        lista = insumos
        if busq:
            lista = [i for i in lista if busq.lower() in i["nombre"].lower() or busq.lower() in (i.get("proveedor") or "").lower()]
        if filtro_cat != "Todas":
            lista = [i for i in lista if i.get("categoria") == filtro_cat]
        if filtro_stk == "Stock bajo":
            lista = [i for i in lista if i.get("minimo", 0) > 0 and i.get("stock", 0) <= i["minimo"]]
        elif filtro_stk == "Stock OK":
            lista = [i for i in lista if not (i.get("minimo", 0) > 0 and i.get("stock", 0) <= i["minimo"])]

        st.markdown(f"**{len(lista)} insumos**")

        if lista:
            df = pd.DataFrame([{
                "Nombre": i["nombre"],
                "Categoría": i.get("categoria", ""),
                "Stock": i.get("stock", 0),
                "Mínimo": i.get("minimo", 0),
                "Unidad": i.get("unidad", ""),
                "Costo unit.": fmt_cop(i.get("costo", 0)),
                "Valor total": fmt_cop(round(i.get("stock", 0) * i.get("costo", 0))),
                "Proveedor": i.get("proveedor") or "—",
                "Estado": "⚠️ Bajo" if i.get("minimo", 0) > 0 and i.get("stock", 0) <= i["minimo"] else "✓ OK",
                "_id": i["id"],
            } for i in lista])

            st.dataframe(
                df.drop(columns=["_id"]),
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Stock": st.column_config.NumberColumn(format="%.2f"),
                    "Mínimo": st.column_config.NumberColumn(format="%.2f"),
                }
            )

            st.markdown("---")
            st.subheader("✏️ Editar / Eliminar insumo")
            nombres_lista = {i["nombre"]: i for i in lista}
            sel_nombre = st.selectbox("Selecciona insumo a editar", ["— Selecciona —"] + list(nombres_lista.keys()))
            if sel_nombre != "— Selecciona —":
                ins = nombres_lista[sel_nombre]
                with st.form("edit_insumo"):
                    ec1, ec2 = st.columns(2)
                    e_nombre = ec1.text_input("Nombre", value=ins["nombre"])
                    e_cat    = ec2.selectbox("Categoría", CATEGORIAS_INSUMO,
                                              index=CATEGORIAS_INSUMO.index(ins.get("categoria", "Otros")) if ins.get("categoria") in CATEGORIAS_INSUMO else 0)
                    ec3, ec4, ec5 = st.columns(3)
                    e_unidad  = ec3.selectbox("Unidad", UNIDADES, index=UNIDADES.index(ins["unidad"]) if ins.get("unidad") in UNIDADES else 0)
                    e_stock   = ec4.number_input("Stock", value=float(ins.get("stock", 0)), step=0.5)
                    e_minimo  = ec5.number_input("Stock mínimo", value=float(ins.get("minimo", 0)), step=0.5)
                    ec6, ec7, ec8 = st.columns(3)
                    e_costo   = ec6.number_input("Costo (COP)", value=float(ins.get("costo", 0)), step=100.0)
                    e_prov    = ec7.text_input("Proveedor", value=ins.get("proveedor") or "")
                    e_vida    = ec8.number_input("Vida útil (días)", value=int(ins.get("vida_util", 0)), step=1)
                    col_save, col_del = st.columns(2)
                    if col_save.form_submit_button("💾 Guardar cambios", use_container_width=True):
                        upd = {
                            "nombre": e_nombre.strip(),
                            "categoria": e_cat,
                            "unidad": e_unidad,
                            "stock": e_stock,
                            "minimo": e_minimo,
                            "proveedor": e_prov.strip(),
                            "vida_util": e_vida,
                        }
                        if e_costo != float(ins.get("costo", 0)):
                            hist = ins.get("historial_precios") or []
                            hist.append({"fecha": db.hoy(), "precio": e_costo, "precio_anterior": ins.get("costo", 0)})
                            upd["historial_precios"] = hist
                        upd["costo"] = e_costo
                        db.update_insumo(ins["id"], upd)
                        st.success("✅ Insumo actualizado")
                        reload()
                    if col_del.form_submit_button("🗑️ Eliminar", use_container_width=True, type="secondary"):
                        db.delete_insumo(ins["id"])
                        st.warning(f"Insumo '{ins['nombre']}' eliminado")
                        reload()
        else:
            st.info("Sin insumos. Agrega el primero en la pestaña ➕")


# ─────────────────────────────────────────────────────────────────────────────
#  RECETAS
# ─────────────────────────────────────────────────────────────────────────────
elif current == "recetas":
    st.title("📋 Recetas")

    tab1, tab2, tab3 = st.tabs(["📋 Listado", "➕ Nueva receta", "⚙️ Costos fijos"])

    with tab3:
        st.subheader("Costos fijos de cocina")
        st.markdown("Porcentaje adicional sobre el costo de ingredientes para cubrir gas, electricidad, mano de obra indirecta, etc.")
        with st.form("form_cf"):
            val_cf = st.number_input("% Costos fijos", min_value=0.0, max_value=100.0,
                                      value=costos_fijos, step=0.5)
            if st.form_submit_button("💾 Guardar"):
                db.update_config(val_cf, umbral_precio)
                st.success(f"✅ Costos fijos: {val_cf}%")
                reload()

        if recetas:
            st.subheader("Vista comparativa de recetas")
            rows = []
            for r in recetas[:10]:
                ci = calc.costo_ingredientes_receta(r, insumos, subrecetas)
                ct = calc.costo_receta(r, insumos, subrecetas, costos_fijos)
                m  = calc.margen_receta(r, insumos, subrecetas, costos_fijos)
                rows.append({
                    "Receta": r["nombre"],
                    "Costo ing.": fmt_cop(round(ci)),
                    "Costos fijos": fmt_cop(round(ci * costos_fijos / 100)),
                    "Costo total": fmt_cop(round(ct)),
                    "Precio venta": fmt_cop(r.get("precio", 0)),
                    "Margen": f"{m:.1f}%" if m is not None else "—",
                })
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    with tab2:
        if not insumos and not subrecetas:
            st.warning("Agrega insumos primero antes de crear recetas.")
        else:
            st.subheader("Nueva receta")
            nombre_r = st.text_input("Nombre de la receta *")
            c1, c2, c3 = st.columns(3)
            cat_r   = c1.selectbox("Categoría", ["Plato Principal", "Entrada", "Postre", "Bebida", "Brunch", "Especial"])
            porc_r  = c2.number_input("Porciones", min_value=1, value=1)
            precio_r = c3.number_input("Precio de venta (COP)", min_value=0.0, step=1000.0)

            st.markdown("**Ingredientes**")
            if "ing_rows" not in st.session_state:
                st.session_state.ing_rows = [{"ref_id": "", "cantidad": 0.0, "merma": 0.0}]

            opciones_ing = {}
            for i in insumos:
                opciones_ing[f"📦 {i['nombre']} ({i.get('unidad','')})" ] = f"ins:{i['id']}"
            for s in subrecetas:
                opciones_ing[f"🧪 {s['nombre']} ({s.get('unidad_rendimiento','')})" ] = f"sub:{s['id']}"
            labels_ing = list(opciones_ing.keys())

            ing_data = []
            for idx, row in enumerate(st.session_state.ing_rows):
                ci1, ci2, ci3, ci4 = st.columns([4, 1.5, 1.5, 0.5])
                sel_label = ci1.selectbox("Ingrediente", ["— Selecciona —"] + labels_ing, key=f"ri_sel_{idx}")
                cant  = ci2.number_input("Cant. neta", min_value=0.0, step=0.01, key=f"ri_cant_{idx}")
                merma = ci3.number_input("Merma %", min_value=0.0, max_value=99.0, step=0.5, key=f"ri_merma_{idx}")
                if ci4.button("✕", key=f"ri_del_{idx}"):
                    st.session_state.ing_rows.pop(idx)
                    st.rerun()
                if sel_label != "— Selecciona —":
                    ing_data.append({
                        "ref_id": opciones_ing[sel_label],
                        "cantidad": cant,
                        "merma": merma,
                    })

            if st.button("➕ Agregar ingrediente"):
                st.session_state.ing_rows.append({"ref_id": "", "cantidad": 0.0, "merma": 0.0})
                st.rerun()

            if ing_data:
                ci_calc = sum(
                    calc.costo_ingrediente(ing["ref_id"], ing["cantidad"], ing["merma"], insumos, subrecetas)
                    for ing in ing_data
                )
                ct_calc = ci_calc * (1 + costos_fijos / 100)
                margen_calc = (precio_r - ct_calc) / precio_r * 100 if precio_r > 0 else None
                st.info(
                    f"💰 Costo ingredientes: **{fmt_cop(round(ci_calc))}** | "
                    f"Costo total: **{fmt_cop(round(ct_calc))}** | "
                    f"Margen: **{f'{margen_calc:.1f}%' if margen_calc is not None else '—'}**"
                )

            if st.button("💾 Guardar receta", type="primary"):
                if not nombre_r.strip():
                    st.error("El nombre es obligatorio")
                elif not ing_data:
                    st.error("Agrega al menos un ingrediente")
                else:
                    db.add_receta({
                        "nombre": nombre_r.strip(),
                        "categoria": cat_r,
                        "porciones": porc_r,
                        "precio": precio_r,
                        "ingredientes": ing_data,
                    })
                    st.session_state.ing_rows = [{"ref_id": "", "cantidad": 0.0, "merma": 0.0}]
                    st.success(f"✅ Receta guardada: {nombre_r}")
                    reload()

    with tab1:
        if not recetas:
            st.info("Sin recetas. Crea la primera en ➕ Nueva receta.")
        else:
            busq_r = st.text_input("🔍 Buscar receta")
            lista_r = [r for r in recetas if not busq_r or busq_r.lower() in r["nombre"].lower()]

            rows_r = []
            for r in lista_r:
                ci = calc.costo_ingredientes_receta(r, insumos, subrecetas)
                ct = calc.costo_receta(r, insumos, subrecetas, costos_fijos)
                m  = calc.margen_receta(r, insumos, subrecetas, costos_fijos)
                rows_r.append({
                    "Receta": r["nombre"],
                    "Categoría": r.get("categoria", ""),
                    "Porciones": r.get("porciones", 1),
                    "Precio venta": fmt_cop(r.get("precio", 0)),
                    "Costo total": fmt_cop(round(ct)),
                    "Margen": f"{m:.1f}%" if m is not None else "—",
                    "Ingredientes": len(r.get("ingredientes", [])),
                    "_id": r["id"],
                })
            st.dataframe(pd.DataFrame(rows_r).drop(columns=["_id"]),
                          hide_index=True, use_container_width=True)

            st.markdown("---")
            sel_r = st.selectbox("Ver / eliminar receta", ["— Selecciona —"] + [r["nombre"] for r in lista_r])
            if sel_r != "— Selecciona —":
                rec = next(r for r in lista_r if r["nombre"] == sel_r)
                st.subheader(f"📋 {rec['nombre']}")
                if rec.get("ingredientes"):
                    ing_rows_disp = []
                    for ing in rec["ingredientes"]:
                        ref = calc.resolve_ref(ing.get("ref_id", ""), insumos, subrecetas)
                        bruta = calc.cant_bruta(ing.get("cantidad", 0), ing.get("merma", 0))
                        costo_ing = ref["costo_unit"] * bruta
                        ing_rows_disp.append({
                            "Ingrediente": ref["nombre"],
                            "Cant. neta": ing.get("cantidad", 0),
                            "Merma %": ing.get("merma", 0),
                            "Cant. bruta": round(bruta, 3),
                            "Unidad": ref["unidad"],
                            "Costo": fmt_cop(round(costo_ing)),
                        })
                    st.dataframe(pd.DataFrame(ing_rows_disp), hide_index=True, use_container_width=True)
                if st.button(f"🗑️ Eliminar receta '{sel_r}'", type="secondary"):
                    db.delete_receta(rec["id"])
                    st.warning("Receta eliminada")
                    reload()


# ─────────────────────────────────────────────────────────────────────────────
#  SUB-RECETAS
# ─────────────────────────────────────────────────────────────────────────────
elif current == "subrecetas":
    st.title("🧪 Sub-recetas")
    tab1, tab2 = st.tabs(["📋 Listado", "➕ Nueva sub-receta"])

    with tab2:
        if not insumos:
            st.warning("Agrega insumos primero.")
        else:
            nombre_s = st.text_input("Nombre de la sub-receta *")
            c1, c2, c3 = st.columns(3)
            cat_s  = c1.selectbox("Categoría", ["Base", "Salsa", "Aliño", "Masa", "Relleno", "Otros"])
            rend_s = c2.number_input("Rendimiento", min_value=0.01, step=1.0)
            u_rend = c3.selectbox("Unidad rendimiento", UNIDADES)

            st.markdown("**Ingredientes**")
            if "sub_ing_rows" not in st.session_state:
                st.session_state.sub_ing_rows = [{}]

            opts_s = {f"📦 {i['nombre']} ({i.get('unidad','')})" : f"ins:{i['id']}" for i in insumos}
            labels_s = list(opts_s.keys())
            sub_ing_data = []
            for idx in range(len(st.session_state.sub_ing_rows)):
                si1, si2, si3, si4 = st.columns([4, 1.5, 1.5, 0.5])
                sel_s = si1.selectbox("Ingrediente", ["— Selecciona —"] + labels_s, key=f"si_sel_{idx}")
                cant_s = si2.number_input("Cant.", min_value=0.0, step=0.01, key=f"si_cant_{idx}")
                merma_s = si3.number_input("Merma %", min_value=0.0, max_value=99.0, key=f"si_merma_{idx}")
                if si4.button("✕", key=f"si_del_{idx}"):
                    st.session_state.sub_ing_rows.pop(idx)
                    st.rerun()
                if sel_s != "— Selecciona —":
                    sub_ing_data.append({"ref_id": opts_s[sel_s], "cantidad": cant_s, "merma": merma_s})

            if st.button("➕ Agregar ingrediente", key="sub_add"):
                st.session_state.sub_ing_rows.append({})
                st.rerun()

            if st.button("💾 Guardar sub-receta", type="primary"):
                if not nombre_s.strip():
                    st.error("El nombre es obligatorio")
                elif rend_s <= 0:
                    st.error("Define el rendimiento")
                elif not sub_ing_data:
                    st.error("Agrega al menos un ingrediente")
                else:
                    db.add_subreceta({
                        "nombre": nombre_s.strip(),
                        "categoria": cat_s,
                        "rendimiento": rend_s,
                        "unidad_rendimiento": u_rend,
                        "ingredientes": sub_ing_data,
                    })
                    st.session_state.sub_ing_rows = [{}]
                    st.success(f"✅ Sub-receta guardada: {nombre_s}")
                    reload()

    with tab1:
        if not subrecetas:
            st.info("Sin sub-recetas aún.")
        else:
            rows_s = []
            for s in subrecetas:
                ct_s = calc.costo_subreceta(s, insumos, subrecetas)
                rend = s.get("rendimiento", 1) or 1
                rows_s.append({
                    "Nombre": s["nombre"],
                    "Categoría": s.get("categoria", ""),
                    "Rendimiento": f"{rend} {s.get('unidad_rendimiento','')}",
                    "Costo elaboración": fmt_cop(round(ct_s)),
                    "Costo / unidad": fmt_cop(round(ct_s / rend)),
                    "Ingredientes": len(s.get("ingredientes", [])),
                    "_id": s["id"],
                })
            st.dataframe(pd.DataFrame(rows_s).drop(columns=["_id"]),
                          hide_index=True, use_container_width=True)
            sel_s2 = st.selectbox("Eliminar sub-receta", ["— Selecciona —"] + [s["nombre"] for s in subrecetas])
            if sel_s2 != "— Selecciona —":
                if st.button(f"🗑️ Eliminar '{sel_s2}'", type="secondary"):
                    s_obj = next(s for s in subrecetas if s["nombre"] == sel_s2)
                    db.delete_subreceta(s_obj["id"])
                    st.warning("Sub-receta eliminada")
                    reload()


# ─────────────────────────────────────────────────────────────────────────────
#  MOVIMIENTOS
# ─────────────────────────────────────────────────────────────────────────────
elif current == "movimientos":
    st.title("↕️ Movimientos")
    tab_e, tab_s, tab_v, tab_l = st.tabs(["📥 Entrada", "📤 Salida", "🍽️ Venta", "📋 Historial"])

    with tab_e:
        st.subheader("Registrar entrada de insumo")
        if not insumos:
            st.warning("No hay insumos registrados.")
        else:
            with st.form("form_entrada", clear_on_submit=True):
                opts_e = {f"{i['nombre']} (stock: {fmt_n(i.get('stock',0))} {i.get('unidad','')})": i for i in insumos}
                sel_e = st.selectbox("Insumo *", ["— Selecciona —"] + list(opts_e.keys()))
                c1, c2 = st.columns(2)
                cant_e  = c1.number_input("Cantidad *", min_value=0.01, step=0.5)
                costo_e = c2.number_input("Costo por unidad (COP, 0 = sin cambio)", min_value=0.0, step=100.0)
                c3, c4 = st.columns(2)
                fecha_e = c3.date_input("Fecha", value=date.today())
                resp_e  = c4.text_input("Responsable")
                prov_e  = st.text_input("Proveedor")
                nota_e  = st.text_input("Nota")
                if st.form_submit_button("💾 Registrar entrada", use_container_width=True):
                    if sel_e == "— Selecciona —":
                        st.error("Selecciona un insumo")
                    else:
                        ins_e = opts_e[sel_e]
                        nuevo_costo = costo_e if costo_e > 0 else ins_e.get("costo", 0)
                        upd_ins = {"stock": ins_e.get("stock", 0) + cant_e, "ultima_entrada": str(fecha_e)}
                        if costo_e > 0 and costo_e != ins_e.get("costo", 0):
                            hist = ins_e.get("historial_precios") or []
                            hist.append({"fecha": str(fecha_e), "precio": costo_e, "precio_anterior": ins_e.get("costo", 0)})
                            upd_ins["costo"] = costo_e
                            upd_ins["historial_precios"] = hist
                        db.update_insumo(ins_e["id"], upd_ins)
                        db.add_movimiento({
                            "tipo": "entrada",
                            "insumo_id": ins_e["id"],
                            "nombre": ins_e["nombre"],
                            "cantidad": cant_e,
                            "costo_unit": nuevo_costo,
                            "fecha": str(fecha_e),
                            "responsable": resp_e or "—",
                            "nota": nota_e,
                            "proveedor": prov_e,
                        })
                        st.success(f"✅ Entrada: +{cant_e} {ins_e.get('unidad','')} de {ins_e['nombre']}")
                        reload()

    with tab_s:
        st.subheader("Registrar salida de insumo")
        if not insumos:
            st.warning("No hay insumos registrados.")
        else:
            with st.form("form_salida", clear_on_submit=True):
                opts_s2 = {f"{i['nombre']} (stock: {fmt_n(i.get('stock',0))} {i.get('unidad','')})": i for i in insumos}
                sel_s2 = st.selectbox("Insumo *", ["— Selecciona —"] + list(opts_s2.keys()))
                c1, c2 = st.columns(2)
                cant_s2 = c1.number_input("Cantidad *", min_value=0.01, step=0.5)
                fecha_s2 = c2.date_input("Fecha", value=date.today())
                c3, c4 = st.columns(2)
                resp_s2  = c3.text_input("Responsable")
                motivo_s = c4.selectbox("Motivo", ["Consumo cocina", "Merma", "Transferencia", "Otro"])
                nota_s2  = st.text_input("Nota adicional")
                if st.form_submit_button("💾 Registrar salida", use_container_width=True):
                    if sel_s2 == "— Selecciona —":
                        st.error("Selecciona un insumo")
                    else:
                        ins_s2 = opts_s2[sel_s2]
                        if cant_s2 > ins_s2.get("stock", 0):
                            st.error(f"Stock insuficiente. Disponible: {fmt_n(ins_s2.get('stock',0))} {ins_s2.get('unidad','')}")
                        else:
                            db.update_insumo(ins_s2["id"], {"stock": ins_s2.get("stock", 0) - cant_s2})
                            db.add_movimiento({
                                "tipo": "salida",
                                "insumo_id": ins_s2["id"],
                                "nombre": ins_s2["nombre"],
                                "cantidad": cant_s2,
                                "costo_unit": ins_s2.get("costo", 0),
                                "fecha": str(fecha_s2),
                                "responsable": resp_s2 or "—",
                                "nota": f"{motivo_s} · {nota_s2}".strip(" ·"),
                            })
                            st.success(f"✅ Salida: -{cant_s2} {ins_s2.get('unidad','')} de {ins_s2['nombre']}")
                            reload()

    with tab_v:
        st.subheader("Registrar venta (descuenta ingredientes)")
        if not recetas:
            st.warning("No hay recetas registradas.")
        else:
            with st.form("form_venta", clear_on_submit=True):
                opts_v = {r["nombre"]: r for r in recetas}
                sel_v = st.selectbox("Receta *", ["— Selecciona —"] + list(opts_v.keys()))
                c1, c2, c3 = st.columns(3)
                cant_v   = c1.number_input("Cantidad de porciones", min_value=1, step=1, value=1)
                fecha_v  = c2.date_input("Fecha", value=date.today())
                resp_v   = c3.text_input("Responsable")
                if sel_v != "— Selecciona —":
                    rec_v = opts_v[sel_v]
                    st.markdown("**Ingredientes que se descontarán:**")
                    ok = True
                    for ing in rec_v.get("ingredientes", []):
                        ref = calc.resolve_ref(ing.get("ref_id", ""), insumos, subrecetas)
                        need = ing.get("cantidad", 0) * cant_v
                        if ing.get("ref_id", "").startswith("ins:"):
                            ins_id = ing["ref_id"][4:]
                            ins_v = next((i for i in insumos if i["id"] == ins_id), None)
                            if ins_v:
                                disp = ins_v.get("stock", 0)
                                estado = "✓" if disp >= need else "⚠️ INSUFICIENTE"
                                color = "green" if disp >= need else "red"
                                if disp < need:
                                    ok = False
                                st.markdown(f":{color}[{estado}] **{ref['nombre']}**: -{fmt_n(need)} {ref['unidad']} (disponible: {fmt_n(disp)})")
                if st.form_submit_button("💾 Registrar venta", use_container_width=True):
                    if sel_v == "— Selecciona —":
                        st.error("Selecciona una receta")
                    else:
                        rec_v2 = opts_v[sel_v]
                        sin_stock = []
                        for ing in rec_v2.get("ingredientes", []):
                            if ing.get("ref_id", "").startswith("ins:"):
                                ins_id = ing["ref_id"][4:]
                                ins_obj = next((i for i in insumos if i["id"] == ins_id), None)
                                if ins_obj and ins_obj.get("stock", 0) < ing.get("cantidad", 0) * cant_v:
                                    sin_stock.append(ins_obj["nombre"])
                        if sin_stock:
                            st.error(f"Stock insuficiente: {', '.join(sin_stock)}")
                        else:
                            for ing in rec_v2.get("ingredientes", []):
                                if ing.get("ref_id", "").startswith("ins:"):
                                    ins_id = ing["ref_id"][4:]
                                    ins_obj = next((i for i in insumos if i["id"] == ins_id), None)
                                    if ins_obj:
                                        db.update_insumo(ins_id, {"stock": ins_obj.get("stock", 0) - ing.get("cantidad", 0) * cant_v})
                            db.add_movimiento({
                                "tipo": "venta",
                                "receta_id": rec_v2["id"],
                                "nombre": f"{rec_v2['nombre']}" + (f" x{cant_v}" if cant_v > 1 else ""),
                                "cantidad": cant_v,
                                "fecha": str(fecha_v),
                                "responsable": resp_v or "—",
                                "nota": "Venta registrada",
                            })
                            st.success(f"✅ Venta registrada: {cant_v} × {rec_v2['nombre']}")
                            reload()

    with tab_l:
        st.subheader("Historial de movimientos")
        c1, c2, c3 = st.columns(3)
        busq_m = c1.text_input("🔍 Buscar")
        filtro_tipo = c2.selectbox("Tipo", ["Todos", "entrada", "salida", "venta", "baja"])
        filtro_fecha_m = c3.date_input("Fecha exacta (opcional)", value=None)

        lista_m = movs
        if busq_m:
            lista_m = [m for m in lista_m if busq_m.lower() in (m.get("nombre") or "").lower()]
        if filtro_tipo != "Todos":
            lista_m = [m for m in lista_m if m.get("tipo") == filtro_tipo]
        if filtro_fecha_m:
            lista_m = [m for m in lista_m if m.get("fecha") == str(filtro_fecha_m)]

        if lista_m:
            df_m = pd.DataFrame([{
                "Fecha": m.get("fecha"),
                "Tipo": m.get("tipo"),
                "Insumo / Plato": m.get("nombre") or "—",
                "Cantidad": m.get("cantidad"),
                "Costo unit.": fmt_cop(m.get("costo_unit")),
                "Responsable": m.get("responsable") or "—",
                "Nota": m.get("nota") or "—",
            } for m in lista_m[:300]])
            st.dataframe(df_m, hide_index=True, use_container_width=True)
        else:
            st.info("Sin movimientos.")


# ─────────────────────────────────────────────────────────────────────────────
#  KARDEX
# ─────────────────────────────────────────────────────────────────────────────
elif current == "kardex":
    st.title("📒 Kardex — Trazabilidad")
    if not insumos:
        st.info("Sin insumos registrados.")
    else:
        col_k1, col_k2, col_k3 = st.columns([3, 2, 2])
        opts_k = {i["nombre"]: i for i in insumos}
        sel_k = col_k1.selectbox("Insumo", ["— Selecciona —"] + list(opts_k.keys()))
        desde_k = col_k2.date_input("Desde", value=date.today() - timedelta(days=30))
        hasta_k = col_k3.date_input("Hasta", value=date.today())

        if sel_k != "— Selecciona —":
            ins_k = opts_k[sel_k]
            st.markdown(f"### 📒 {ins_k['nombre']}")
            st.markdown(
                f"**Categoría:** {ins_k.get('categoria','')} | "
                f"**Unidad:** {ins_k.get('unidad','')} | "
                f"**Costo unit.:** {fmt_cop(ins_k.get('costo',0))} | "
                f"**Stock actual:** {fmt_n(ins_k.get('stock',0))} {ins_k.get('unidad','')}"
            )

            desde_str = str(desde_k)
            hasta_str = str(hasta_k)

            movs_k = [
                m for m in movs
                if m.get("insumo_id") == ins_k["id"]
                and desde_str <= (m.get("fecha") or "") <= hasta_str
            ]
            ventas_k = []
            for m in movs:
                if m.get("tipo") != "venta":
                    continue
                if not (desde_str <= (m.get("fecha") or "") <= hasta_str):
                    continue
                rec_v = next((r for r in recetas if r["id"] == m.get("receta_id")), None)
                if not rec_v:
                    continue
                for ing in rec_v.get("ingredientes", []):
                    ref_id = ing.get("ref_id", "")
                    if ref_id == f"ins:{ins_k['id']}" or ref_id == ins_k["id"]:
                        ventas_k.append({
                            "tipo": "venta",
                            "nombre": f"Venta: {rec_v['nombre']}",
                            "cantidad": ing.get("cantidad", 0) * m.get("cantidad", 1),
                            "costo_unit": ins_k.get("costo", 0),
                            "fecha": m.get("fecha"),
                            "responsable": m.get("responsable") or "—",
                            "signo": -1,
                        })

            all_movs_k = sorted(
                [dict(m, signo=1 if m.get("tipo") == "entrada" else -1) for m in movs_k] + ventas_k,
                key=lambda m: m.get("fecha", "")
            )

            entradas_t = sum(m["cantidad"] for m in all_movs_k if m.get("tipo") == "entrada")
            salidas_t  = sum(m["cantidad"] for m in all_movs_k if m.get("tipo") == "salida")
            ventas_t   = sum(m["cantidad"] for m in all_movs_k if m.get("tipo") == "venta")
            bajas_t    = sum(m["cantidad"] for m in all_movs_k if m.get("tipo") == "baja")

            c1k, c2k, c3k, c4k = st.columns(4)
            c1k.metric("Entradas", fmt_n(entradas_t))
            c2k.metric("Salidas", fmt_n(salidas_t))
            c3k.metric("Ventas", fmt_n(ventas_t))
            c4k.metric("Bajas", fmt_n(bajas_t))

            if all_movs_k:
                balance = 0.0
                rows_k = []
                for m in all_movs_k:
                    entrada = m["cantidad"] if m.get("signo", 1) > 0 else None
                    salida  = m["cantidad"] if m.get("signo", 1) < 0 else None
                    balance += (entrada or 0) - (salida or 0)
                    rows_k.append({
                        "Fecha": m.get("fecha"),
                        "Tipo": m.get("tipo"),
                        "Descripción": m.get("nombre") or "—",
                        "Entrada": f"+{fmt_n(entrada)}" if entrada else "—",
                        "Salida": f"-{fmt_n(salida)}" if salida else "—",
                        "Saldo": fmt_n(max(0, balance)),
                        "Costo unit.": fmt_cop(m.get("costo_unit", ins_k.get("costo", 0))),
                        "Responsable": m.get("responsable") or "—",
                    })
                st.dataframe(pd.DataFrame(rows_k), hide_index=True, use_container_width=True)

                if ins_k.get("historial_precios"):
                    st.subheader("📊 Historial de precios")
                    df_hp = pd.DataFrame(ins_k["historial_precios"])
                    fig_hp = px.line(df_hp, x="fecha", y="precio",
                                     title=f"Evolución precio — {ins_k['nombre']}",
                                     markers=True, color_discrete_sequence=["#2d6a4f"])
                    fig_hp.update_layout(height=250, margin=dict(t=40, b=10))
                    st.plotly_chart(fig_hp, use_container_width=True)
            else:
                st.info("Sin movimientos en el período seleccionado.")


# ─────────────────────────────────────────────────────────────────────────────
#  BAJAS
# ─────────────────────────────────────────────────────────────────────────────
elif current == "bajas":
    st.title("🗑️ Control de Bajas")
    tab1, tab2 = st.tabs(["➕ Registrar baja", "📋 Historial y resumen"])

    with tab1:
        if not insumos:
            st.warning("Sin insumos registrados.")
        else:
            with st.form("form_baja", clear_on_submit=True):
                opts_b = {f"{i['nombre']} (stock: {fmt_n(i.get('stock',0))} {i.get('unidad','')})": i for i in insumos}
                sel_b = st.selectbox("Insumo *", ["— Selecciona —"] + list(opts_b.keys()))
                c1, c2 = st.columns(2)
                cant_b  = c1.number_input("Cantidad *", min_value=0.01, step=0.5)
                fecha_b = c2.date_input("Fecha", value=date.today())
                c3, c4 = st.columns(2)
                causa_b  = c3.selectbox("Causa", CAUSAS_BAJA)
                turno_b  = c4.selectbox("Turno", TURNOS)
                c5, c6 = st.columns(2)
                resp_b   = c5.text_input("Responsable")
                autor_b  = c6.text_input("Autoriza")
                accion_b = st.text_input("Acción correctiva")
                if st.form_submit_button("💾 Registrar baja", use_container_width=True):
                    if sel_b == "— Selecciona —":
                        st.error("Selecciona un insumo")
                    else:
                        ins_b = opts_b[sel_b]
                        if cant_b > ins_b.get("stock", 0):
                            st.error(f"Cantidad mayor al stock disponible: {fmt_n(ins_b.get('stock',0))}")
                        else:
                            db.update_insumo(ins_b["id"], {"stock": ins_b.get("stock", 0) - cant_b})
                            costo_total = ins_b.get("costo", 0) * cant_b
                            db.add_baja({
                                "insumo_id": ins_b["id"],
                                "nombre": ins_b["nombre"],
                                "unidad": ins_b.get("unidad", ""),
                                "cantidad": cant_b,
                                "costo_unit": ins_b.get("costo", 0),
                                "costo_total": costo_total,
                                "causa": causa_b,
                                "turno": turno_b,
                                "fecha": str(fecha_b),
                                "responsable": resp_b or "—",
                                "autoriza": autor_b or "—",
                                "accion": accion_b,
                            })
                            db.add_movimiento({
                                "tipo": "baja",
                                "insumo_id": ins_b["id"],
                                "nombre": ins_b["nombre"],
                                "cantidad": cant_b,
                                "costo_unit": ins_b.get("costo", 0),
                                "fecha": str(fecha_b),
                                "responsable": resp_b or "—",
                                "nota": f"BAJA: {causa_b}",
                            })
                            st.success(f"✅ Baja registrada: {cant_b} {ins_b.get('unidad','')} de {ins_b['nombre']} — {fmt_cop(round(costo_total))}")
                            reload()

    with tab2:
        lunes = date.today() - timedelta(days=date.today().weekday())
        bajas_sem = [b for b in bajas if b.get("fecha", "") >= str(lunes)]
        total_sem = sum(b.get("costo_total", 0) for b in bajas_sem)
        c1b, c2b = st.columns(2)
        c1b.metric("Total bajas esta semana", fmt_cop(round(total_sem)))
        c2b.metric("Registros", len(bajas_sem))

        if bajas_sem:
            resumen_causa = {}
            for c in CAUSAS_BAJA:
                resumen_causa[c] = sum(b.get("costo_total", 0) for b in bajas_sem if b.get("causa") == c)
            df_rc = pd.DataFrame([
                {"Causa": c, "Total COP": fmt_cop(round(v)), "Registros": sum(1 for b in bajas_sem if b.get("causa") == c)}
                for c, v in resumen_causa.items() if v > 0
            ])
            if not df_rc.empty:
                st.dataframe(df_rc, hide_index=True, use_container_width=True)

        filtro_causa_b = st.selectbox("Filtrar por causa", ["Todas"] + CAUSAS_BAJA)
        lista_b = bajas
        if filtro_causa_b != "Todas":
            lista_b = [b for b in lista_b if b.get("causa") == filtro_causa_b]

        if lista_b:
            df_b = pd.DataFrame([{
                "Fecha": b.get("fecha"),
                "Turno": b.get("turno"),
                "Insumo": b.get("nombre"),
                "Cantidad": f"{fmt_n(b.get('cantidad',0))} {b.get('unidad','')}",
                "Costo total": fmt_cop(round(b.get("costo_total", 0))),
                "Causa": b.get("causa"),
                "Responsable": b.get("responsable"),
                "Autoriza": b.get("autoriza"),
            } for b in lista_b[:300]])
            st.dataframe(df_b, hide_index=True, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
#  ALERTAS
# ─────────────────────────────────────────────────────────────────────────────
elif current == "alertas":
    st.title("🔔 Alertas")

    # Stock bajo
    st.subheader("📦 Stock bajo el mínimo")
    bajo_a = [i for i in insumos if i.get("minimo", 0) > 0 and i.get("stock", 0) <= i["minimo"]]
    if bajo_a:
        df_bajo = pd.DataFrame([{
            "Insumo": i["nombre"],
            "Categoría": i.get("categoria"),
            "Stock actual": fmt_n(i.get("stock", 0)),
            "Stock mínimo": fmt_n(i.get("minimo", 0)),
            "Faltante": fmt_n(max(0, i.get("minimo", 0) - i.get("stock", 0))),
            "Unidad": i.get("unidad"),
            "Proveedor": i.get("proveedor") or "—",
        } for i in bajo_a])
        st.dataframe(df_bajo, hide_index=True, use_container_width=True)
    else:
        st.success("✅ Todo el stock está sobre el mínimo")

    st.markdown("---")

    # Vencimientos próximos
    st.subheader("⏰ Vencimientos próximos (≤ 3 días)")
    hoy_d = date.today()
    proximos = []
    for i in insumos:
        if not i.get("vida_util") or not i.get("ultima_entrada"):
            continue
        try:
            ult = date.fromisoformat(i["ultima_entrada"])
        except Exception:
            continue
        vence = ult + timedelta(days=int(i["vida_util"]))
        dias = (vence - hoy_d).days
        if dias <= 3:
            proximos.append({
                "Insumo": i["nombre"],
                "Vida útil": f"{i['vida_util']}d",
                "Última entrada": str(ult),
                "Vence": str(vence),
                "Estado": "VENCIDO" if dias < 0 else ("HOY" if dias == 0 else f"En {dias}d"),
            })
    if proximos:
        st.dataframe(pd.DataFrame(proximos), hide_index=True, use_container_width=True)
    else:
        st.success("✅ Ninguna preparación próxima a vencer")

    st.markdown("---")

    # Fluctuaciones de precio
    st.subheader("💲 Fluctuaciones de precio")
    fluctuaciones = []
    for i in insumos:
        hist = i.get("historial_precios") or []
        if len(hist) < 2:
            continue
        for j in range(len(hist) - 1, 0, -1):
            ant = hist[j - 1].get("precio", 0)
            act = hist[j].get("precio", 0)
            if not ant or ant <= 0:
                continue
            pct = (act - ant) / ant * 100
            if pct >= umbral_precio:
                fluctuaciones.append({
                    "Insumo": i["nombre"],
                    "Categoría": i.get("categoria"),
                    "Precio anterior": fmt_cop(ant),
                    "Precio nuevo": fmt_cop(act),
                    "Variación": f"▲ {pct:.1f}%",
                    "Fecha cambio": hist[j].get("fecha"),
                    "Proveedor": i.get("proveedor") or "—",
                })
                break
    if fluctuaciones:
        st.warning(f"{len(fluctuaciones)} insumo(s) con aumento de precio ≥ {umbral_precio}%")
        st.dataframe(pd.DataFrame(fluctuaciones), hide_index=True, use_container_width=True)
    else:
        st.success(f"✅ Sin fluctuaciones de precio ≥ {umbral_precio}%")

    st.markdown(f"*Umbral de alerta de precio: **{umbral_precio}%** — ajustar en ⚙️ Configuración*")


# ─────────────────────────────────────────────────────────────────────────────
#  REPORTES
# ─────────────────────────────────────────────────────────────────────────────
elif current == "reportes":
    st.title("📈 Reportes")

    tab_inv, tab_bajas, tab_cons = st.tabs(["📦 Inventario", "🗑️ Bajas", "📊 Consumo"])

    with tab_inv:
        st.subheader(f"Inventario al {date.today().strftime('%d/%m/%Y')}")
        if insumos:
            total_val = sum(i.get("stock", 0) * i.get("costo", 0) for i in insumos)
            st.metric("Valor total inventario", fmt_cop(round(total_val)))
            cats_unicas = sorted(set(i.get("categoria", "Otros") for i in insumos))
            cat_sel = st.selectbox("Filtrar por categoría", ["Todas"] + cats_unicas)
            lista_inv = insumos if cat_sel == "Todas" else [i for i in insumos if i.get("categoria") == cat_sel]
            df_inv = pd.DataFrame([{
                "Insumo": i["nombre"],
                "Categoría": i.get("categoria"),
                "Stock": i.get("stock", 0),
                "Unidad": i.get("unidad"),
                "Mínimo": i.get("minimo", 0),
                "Costo unit.": fmt_cop(i.get("costo", 0)),
                "Valor total": fmt_cop(round(i.get("stock", 0) * i.get("costo", 0))),
                "Estado": "⚠️ Bajo" if i.get("minimo", 0) > 0 and i.get("stock", 0) <= i["minimo"] else "✓ OK",
            } for i in lista_inv])
            st.dataframe(df_inv, hide_index=True, use_container_width=True)

            cats_data = {}
            for i in insumos:
                cats_data[i.get("categoria", "Otros")] = cats_data.get(i.get("categoria", "Otros"), 0) + i.get("stock", 0) * i.get("costo", 0)
            fig_cat = px.bar(
                x=list(cats_data.keys()),
                y=[round(v / 1000) for v in cats_data.values()],
                labels={"x": "Categoría", "y": "Valor (miles COP)"},
                color_discrete_sequence=["#2d6a4f"],
            )
            fig_cat.update_layout(height=280, margin=dict(t=10, b=10))
            st.plotly_chart(fig_cat, use_container_width=True)

    with tab_bajas:
        st.subheader("Análisis de bajas")
        if bajas:
            semanas_data = []
            hoy_d2 = date.today()
            for w in range(7, -1, -1):
                lun = hoy_d2 - timedelta(days=hoy_d2.weekday() + w * 7)
                dom = lun + timedelta(days=6)
                total_w = sum(b.get("costo_total", 0) for b in bajas if str(lun) <= (b.get("fecha") or "") <= str(dom))
                semanas_data.append({"Semana": f"S-{w}", "Bajas (COP)": round(total_w / 1000)})
            fig_sem = px.line(pd.DataFrame(semanas_data), x="Semana", y="Bajas (COP)",
                               markers=True, color_discrete_sequence=["#ef4444"])
            fig_sem.update_layout(height=250, margin=dict(t=10, b=10))
            st.plotly_chart(fig_sem, use_container_width=True)

            causa_tots = {c: sum(b.get("costo_total", 0) for b in bajas if b.get("causa") == c) for c in CAUSAS_BAJA}
            fig_cau = px.pie(values=list(causa_tots.values()), names=list(causa_tots.keys()),
                              color_discrete_sequence=px.colors.qualitative.Set2)
            fig_cau.update_layout(height=300, margin=dict(t=10, b=10))
            st.plotly_chart(fig_cau, use_container_width=True)
        else:
            st.info("Sin bajas registradas.")

    with tab_cons:
        st.subheader("Top 10 ingredientes más consumidos")
        consumo = {}
        for m in movs:
            if m.get("tipo") == "venta":
                rec_v = next((r for r in recetas if r["id"] == m.get("receta_id")), None)
                if rec_v:
                    for ing in rec_v.get("ingredientes", []):
                        ref = calc.resolve_ref(ing.get("ref_id", ""), insumos, subrecetas)
                        consumo[ref["nombre"]] = consumo.get(ref["nombre"], 0) + ing.get("cantidad", 0) * m.get("cantidad", 1)
            elif m.get("tipo") == "salida":
                consumo[m.get("nombre", "?")] = consumo.get(m.get("nombre", "?"), 0) + m.get("cantidad", 0)
        top = sorted(consumo.items(), key=lambda x: x[1], reverse=True)[:10]
        if top:
            fig_top = px.bar(x=[t[1] for t in top], y=[t[0] for t in top],
                              orientation="h", color_discrete_sequence=["#40916c"])
            fig_top.update_layout(height=350, margin=dict(t=10, b=10), xaxis_title="Unidades consumidas")
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("Sin datos de consumo aún.")


# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────────────────
elif current == "config":
    st.title("⚙️ Configuración")

    with st.form("form_config"):
        st.subheader("Parámetros del sistema")
        cf_val = st.number_input("% Costos fijos de cocina", min_value=0.0, max_value=100.0,
                                  value=costos_fijos, step=0.5,
                                  help="Gas, electricidad, mano de obra indirecta, etc.")
        up_val = st.number_input("% Umbral alerta de precio", min_value=0.1, max_value=100.0,
                                  value=umbral_precio, step=0.5,
                                  help="Alerta cuando un insumo sube su precio por encima de este %")
        if st.form_submit_button("💾 Guardar configuración", use_container_width=True):
            db.update_config(cf_val, up_val)
            st.success(f"✅ Configuración guardada: costos fijos {cf_val}%, umbral precio {up_val}%")
            reload()

    st.markdown("---")
    st.subheader("🔄 Actualizar datos")
    st.markdown("Si los datos no se actualizan, pulsa este botón para recargar desde la base de datos.")
    if st.button("🔄 Recargar datos ahora"):
        reload()
