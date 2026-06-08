-- ═══════════════════════════════════════════════════════════════════════
--  La Ocasión · Inventarios — Tablas Supabase
--  Ejecutar en: Supabase → SQL Editor → New query → Pegar y ejecutar
-- ═══════════════════════════════════════════════════════════════════════

-- INSUMOS
CREATE TABLE IF NOT EXISTS insumos (
  id                TEXT PRIMARY KEY,
  nombre            TEXT NOT NULL,
  categoria         TEXT DEFAULT 'Otros',
  unidad            TEXT DEFAULT 'unidad',
  stock             FLOAT DEFAULT 0,
  minimo            FLOAT DEFAULT 0,
  costo             FLOAT DEFAULT 0,
  proveedor         TEXT DEFAULT '',
  vida_util         INT DEFAULT 0,
  ultima_entrada    DATE,
  creado_en         DATE,
  historial_precios JSONB DEFAULT '[]',
  precio_alerta_visto DATE
);

-- RECETAS
CREATE TABLE IF NOT EXISTS recetas (
  id          TEXT PRIMARY KEY,
  nombre      TEXT NOT NULL,
  categoria   TEXT DEFAULT 'Plato Principal',
  porciones   INT DEFAULT 1,
  precio      FLOAT DEFAULT 0,
  ingredientes JSONB DEFAULT '[]',
  creado_en   DATE
);

-- SUB-RECETAS
CREATE TABLE IF NOT EXISTS subrecetas (
  id                 TEXT PRIMARY KEY,
  nombre             TEXT NOT NULL,
  categoria          TEXT DEFAULT 'Base',
  rendimiento        FLOAT DEFAULT 1,
  unidad_rendimiento TEXT DEFAULT 'g',
  ingredientes       JSONB DEFAULT '[]',
  creado_en          DATE
);

-- MOVIMIENTOS
CREATE TABLE IF NOT EXISTS movimientos (
  id           TEXT PRIMARY KEY,
  tipo         TEXT NOT NULL,
  insumo_id    TEXT,
  receta_id    TEXT,
  nombre       TEXT,
  cantidad     FLOAT DEFAULT 0,
  costo_unit   FLOAT DEFAULT 0,
  fecha        DATE,
  responsable  TEXT DEFAULT '',
  nota         TEXT DEFAULT '',
  proveedor    TEXT DEFAULT '',
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- BAJAS
CREATE TABLE IF NOT EXISTS bajas (
  id           TEXT PRIMARY KEY,
  insumo_id    TEXT,
  nombre       TEXT,
  unidad       TEXT,
  cantidad     FLOAT DEFAULT 0,
  costo_unit   FLOAT DEFAULT 0,
  costo_total  FLOAT DEFAULT 0,
  causa        TEXT,
  turno        TEXT,
  fecha        DATE,
  responsable  TEXT DEFAULT '',
  autoriza     TEXT DEFAULT '',
  accion       TEXT DEFAULT ''
);

-- CONFIG (una sola fila)
CREATE TABLE IF NOT EXISTS config (
  id              INT PRIMARY KEY DEFAULT 1,
  costos_fijos    FLOAT DEFAULT 15,
  umbral_precio   FLOAT DEFAULT 3
);

INSERT INTO config (id, costos_fijos, umbral_precio)
VALUES (1, 15, 3)
ON CONFLICT (id) DO NOTHING;

-- ── Habilitar Row Level Security (recomendado) ──────────────────────────────
ALTER TABLE insumos    ENABLE ROW LEVEL SECURITY;
ALTER TABLE recetas    ENABLE ROW LEVEL SECURITY;
ALTER TABLE subrecetas ENABLE ROW LEVEL SECURITY;
ALTER TABLE movimientos ENABLE ROW LEVEL SECURITY;
ALTER TABLE bajas      ENABLE ROW LEVEL SECURITY;
ALTER TABLE config     ENABLE ROW LEVEL SECURITY;

-- Permitir todas las operaciones con la clave anon (la app usa autenticación propia)
CREATE POLICY "allow_all_insumos"    ON insumos    FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_recetas"    ON recetas    FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_subrecetas" ON subrecetas FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_movimientos" ON movimientos FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_bajas"      ON bajas      FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_config"     ON config     FOR ALL USING (true) WITH CHECK (true);
