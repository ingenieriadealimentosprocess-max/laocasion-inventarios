"""
db.py — Capa de datos con Supabase para La Ocasión Inventarios
"""
import streamlit as st
from supabase import create_client, Client
from datetime import date
import uuid


@st.cache_resource
def get_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def uid():
    return uuid.uuid4().hex[:16]


def hoy():
    return str(date.today())


# ── INSUMOS ──────────────────────────────────────────────────────────────────

def get_insumos():
    return get_client().table("insumos").select("*").order("nombre").execute().data or []


def add_insumo(data: dict):
    data["id"] = uid()
    data.setdefault("creado_en", hoy())
    data.setdefault("historial_precios", [])
    get_client().table("insumos").insert(data).execute()


def update_insumo(id: str, data: dict):
    get_client().table("insumos").update(data).eq("id", id).execute()


def delete_insumo(id: str):
    get_client().table("insumos").delete().eq("id", id).execute()


# ── RECETAS ───────────────────────────────────────────────────────────────────

def get_recetas():
    return get_client().table("recetas").select("*").order("nombre").execute().data or []


def add_receta(data: dict):
    data["id"] = uid()
    data.setdefault("creado_en", hoy())
    data.setdefault("ingredientes", [])
    get_client().table("recetas").insert(data).execute()


def update_receta(id: str, data: dict):
    get_client().table("recetas").update(data).eq("id", id).execute()


def delete_receta(id: str):
    get_client().table("recetas").delete().eq("id", id).execute()


# ── SUBRECETAS ────────────────────────────────────────────────────────────────

def get_subrecetas():
    return get_client().table("subrecetas").select("*").order("nombre").execute().data or []


def add_subreceta(data: dict):
    data["id"] = uid()
    data.setdefault("creado_en", hoy())
    data.setdefault("ingredientes", [])
    get_client().table("subrecetas").insert(data).execute()


def update_subreceta(id: str, data: dict):
    get_client().table("subrecetas").update(data).eq("id", id).execute()


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
    get_client().table("movimientos").insert(data).execute()


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


# ── COSTOS FIJOS ITEMS ────────────────────────────────────────────────────────

def get_costos_fijos_items():
    try:
        return get_client().table("costos_fijos_items").select("*").order("nombre").execute().data or []
    except Exception:
        return []


def add_costo_fijo(data: dict):
    data["id"] = uid()
    get_client().table("costos_fijos_items").insert(data).execute()


def update_costo_fijo(id: str, data: dict):
    get_client().table("costos_fijos_items").update(data).eq("id", id).execute()


def delete_costo_fijo(id: str):
    get_client().table("costos_fijos_items").delete().eq("id", id).execute()
