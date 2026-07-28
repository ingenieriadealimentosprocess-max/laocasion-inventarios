"""
db.py — Capa de datos con Supabase para La Ocasión Inventarios
"""
import streamlit as st
from supabase import create_client, Client
from datetime import date
import uuid
import re


@st.cache_resource
def get_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def uid():
    return uuid.uuid4().hex[:16]


def hoy():
    return str(date.today())


def _missing_column(err, data):
    """Si el error de Supabase/PostgREST es por una columna inexistente que está
    en `data`, devuelve el dict sin esa columna. Si no aplica, devuelve None."""
    msg = str(err)
    m = re.search(r"'([^']+)' column", msg) or re.search(r'column "([^"]+)"', msg)
    if not m:
        return None
    col = m.group(1)
    if col in data:
        return {k: v for k, v in data.items() if k != col}
    return None


def _safe_write(fn, data):
    """Ejecuta fn(data). Si PostgREST rechaza por una columna que aún no existe
    en la base (ej. una columna nueva sin migrar), la quita y reintenta, de modo
    que el guardado no falle. Cualquier otro error se propaga normalmente."""
    while True:
        try:
            return fn(data)
        except Exception as e:
            reduced = _missing_column(e, data)
            if reduced is None:
                raise
            data = reduced


# ── INSUMOS ──────────────────────────────────────────────────────────────────

def get_insumos():
    return get_client().table("insumos").select("*").order("nombre").execute().data or []


def add_insumo(data: dict):
    data["id"] = uid()
    data.setdefault("creado_en", hoy())
    data.setdefault("historial_precios", [])
    _safe_write(lambda d: get_client().table("insumos").insert(d).execute(), data)


def update_insumo(id: str, data: dict):
    _safe_write(lambda d: get_client().table("insumos").update(d).eq("id", id).execute(), data)


def delete_insumo(id: str):
    get_client().table("insumos").delete().eq("id", id).execute()


# ── RECETAS ───────────────────────────────────────────────────────────────────

def get_recetas():
    return get_client().table("recetas").select("*").order("nombre").execute().data or []


def add_receta(data: dict):
    data.setdefault("id", uid())
    data.setdefault("creado_en", hoy())
    data.setdefault("ingredientes", [])
    _safe_write(lambda d: get_client().table("recetas").insert(d).execute(), data)


def update_receta(id: str, data: dict):
    _safe_write(lambda d: get_client().table("recetas").update(d).eq("id", id).execute(), data)


def delete_receta(id: str):
    get_client().table("recetas").delete().eq("id", id).execute()


# ── SUBRECETAS ────────────────────────────────────────────────────────────────

def get_subrecetas():
    return get_client().table("subrecetas").select("*").order("nombre").execute().data or []


def add_subreceta(data: dict):
    data.setdefault("id", uid())
    data.setdefault("creado_en", hoy())
    data.setdefault("ingredientes", [])
    _safe_write(lambda d: get_client().table("subrecetas").insert(d).execute(), data)


def update_subreceta(id: str, data: dict):
    _safe_write(lambda d: get_client().table("subrecetas").update(d).eq("id", id).execute(), data)


def delete_subreceta(id: str):
    get_client().table("subrecetas").delete().eq("id", id).execute()


# ── MOVIMIENTOS ───────────────────────────────────────────────────────────────

def get_movimientos(limit=500):
    return (
        get_client()
        .table("movimientos")
        .select("*")
        .order("fecha", desc=True)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
        .data or []
    )


def add_movimiento(data: dict):
    data["id"] = uid()
    data.setdefault("fecha", hoy())
    _safe_write(lambda d: get_client().table("movimientos").insert(d).execute(), data)


def update_movimiento(id: str, data: dict):
    get_client().table("movimientos").update(data).eq("id", id).execute()


def delete_movimiento(id: str):
    get_client().table("movimientos").delete().eq("id", id).execute()


# ── BAJAS ─────────────────────────────────────────────────────────────────────

def get_bajas():
    return (
        get_client()
        .table("bajas")
        .select("*")
        .order("fecha", desc=True)
        .execute()
        .data or []
    )


def add_baja(data: dict):
    data["id"] = uid()
    data.setdefault("fecha", hoy())
    get_client().table("bajas").insert(data).execute()


# ── CONFIG ────────────────────────────────────────────────────────────────────

def get_config():
    rows = get_client().table("config").select("*").eq("id", 1).execute().data
    return rows[0] if rows else {"costos_fijos": 15.0, "umbral_precio": 3.0, "ventas_esperadas": 0}


def update_config(costos_fijos: float, umbral_precio: float, ventas_esperadas: float = 0):
    get_client().table("config").upsert({
        "id": 1,
        "costos_fijos": costos_fijos,
        "umbral_precio": umbral_precio,
        "ventas_esperadas": ventas_esperadas,
    }).execute()


def set_alerta_import(texto: str):
    """Guarda (o limpia) la última alerta de importación (JSON) para mostrarla en Alertas."""
    _safe_write(lambda d: get_client().table("config").upsert(d).execute(),
                {"id": 1, "alertas_import": texto})


# ── COSTOS FIJOS ITEMS ────────────────────────────────────────────────────────

def get_costos_fijos_items():
    """Retorna la lista de costos fijos.
    None  -> la tabla no existe / no es accesible (falta correr el SQL)
    []    -> la tabla existe pero está vacía
    [...] -> hay rubros registrados"""
    try:
        return get_client().table("costos_fijos_items").select("*").order("nombre").execute().data or []
    except Exception:
        return None


def add_costo_fijo(data: dict):
    data["id"] = uid()
    get_client().table("costos_fijos_items").insert(data).execute()


def update_costo_fijo(id: str, data: dict):
    get_client().table("costos_fijos_items").update(data).eq("id", id).execute()


def delete_costo_fijo(id: str):
    get_client().table("costos_fijos_items").delete().eq("id", id).execute()
