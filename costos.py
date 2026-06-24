"""
costos.py — Cálculos de merma y costos de recetas / sub-recetas
"""


def cant_bruta(cant_neta: float, merma_pct: float) -> float:
    """Cantidad bruta considerando % de merma."""
    if merma_pct > 0 and merma_pct < 100:
        return cant_neta / (1 - merma_pct / 100)
    return cant_neta


def rend_efectivo(sub: dict) -> float:
    """Rendimiento REAL de una sub-receta tras la merma por cocción.
    Si la sub-receta pierde peso/volumen al cocinarse (lo que entra no es lo
    que sale), el rendimiento utilizable baja y el costo por unidad sube."""
    rend = sub.get("rendimiento", 1) or 1
    mc = sub.get("merma_coccion", 0) or 0
    if 0 < mc < 100:
        return rend * (1 - mc / 100)
    return rend


def resolve_ref(ref_id: str, insumos: list, subrecetas: list) -> dict:
    """Devuelve nombre, unidad y costo_unit de un ingrediente (insumo o sub-receta)."""
    if not ref_id:
        return {"nombre": "(desconocido)", "unidad": "—", "costo_unit": 0}
    if ref_id.startswith("sub:"):
        sub_id = ref_id[4:]
        sub = next((s for s in subrecetas if s["id"] == sub_id), None)
        if not sub:
            return {"nombre": "(sub-receta eliminada)", "unidad": "—", "costo_unit": 0}
        ct = costo_subreceta(sub, insumos, subrecetas)
        rend = rend_efectivo(sub)
        return {
            "nombre": "🧪 " + sub["nombre"],
            "unidad": sub.get("unidad_rendimiento", ""),
            "costo_unit": ct / rend,
        }
    raw_id = ref_id[4:] if ref_id.startswith("ins:") else ref_id
    ins = next((i for i in insumos if i["id"] == raw_id), None)

    # Fallback para refs __UNKNOWN__: buscar por nombre en sub-recetas e insumos
    if not ins and raw_id.startswith("__UNKNOWN__"):
        nombre_buscado = raw_id[11:].lower().strip()
        # Intentar sub-receta primero (sub-XXXgr suele ser sub-receta)
        sub = next(
            (s for s in subrecetas
             if nombre_buscado in s["nombre"].lower() or s["nombre"].lower() in nombre_buscado),
            None
        )
        if sub:
            ct = costo_subreceta(sub, insumos, subrecetas)
            rend = rend_efectivo(sub)
            return {"nombre": "🧪 " + sub["nombre"],
                    "unidad": sub.get("unidad_rendimiento", ""),
                    "costo_unit": ct / rend}
        # Intentar insumo por nombre parcial
        ins = next(
            (i for i in insumos
             if nombre_buscado in i["nombre"].lower() or i["nombre"].lower() in nombre_buscado),
            None
        )

    if not ins:
        return {"nombre": f"⚠️ {raw_id[11:] if raw_id.startswith('__UNKNOWN__') else raw_id}",
                "unidad": "—", "costo_unit": 0}
    return {"nombre": ins["nombre"], "unidad": ins.get("unidad", ""), "costo_unit": ins.get("costo", 0)}


def costo_ingrediente(ref_id: str, cant_neta: float, merma_pct: float,
                       insumos: list, subrecetas: list) -> float:
    ref = resolve_ref(ref_id, insumos, subrecetas)
    bruta = cant_bruta(cant_neta, merma_pct)
    return ref["costo_unit"] * bruta


def costo_subreceta(sub: dict, insumos: list, subrecetas: list) -> float:
    total = 0.0
    for ing in sub.get("ingredientes", []):
        ref_id = ing.get("ref_id") or ("ins:" + ing.get("insumo_id", ""))
        total += costo_ingrediente(
            ref_id,
            ing.get("cantidad", ing.get("cant_neta", 0)),
            ing.get("merma", 0),
            insumos, subrecetas
        )
    return total


def costo_ingredientes_receta(receta: dict, insumos: list, subrecetas: list) -> float:
    total = 0.0
    for ing in receta.get("ingredientes", []):
        ref_id = ing.get("ref_id") or ("ins:" + ing.get("insumo_id", ""))
        total += costo_ingrediente(
            ref_id,
            ing.get("cantidad", ing.get("cant_neta", 0)),
            ing.get("merma", 0),
            insumos, subrecetas
        )
    return total


def costo_receta(receta: dict, insumos: list, subrecetas: list, costos_fijos_pct: float) -> float:
    ci = costo_ingredientes_receta(receta, insumos, subrecetas)
    return ci * (1 + costos_fijos_pct / 100)


def margen_receta(receta: dict, insumos: list, subrecetas: list, costos_fijos_pct: float) -> float:
    precio = receta.get("precio", 0) or 0
    if precio <= 0:
        return None
    ct = costo_receta(receta, insumos, subrecetas, costos_fijos_pct)
    return (precio - ct) / precio * 100
