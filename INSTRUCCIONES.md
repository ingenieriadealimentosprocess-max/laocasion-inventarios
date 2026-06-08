# La Ocasión · Sistema de Inventarios — Guía de instalación

## Pasos para publicar la app (una sola vez)

---

### PASO 1 — Crear las tablas en Supabase

1. Abre **supabase.com** → entra a tu proyecto
2. En el menú izquierdo haz clic en **SQL Editor**
3. Clic en **New query**
4. Abre el archivo `setup_supabase.sql` con el Bloc de notas
5. Copia todo el contenido y pégalo en el editor de Supabase
6. Clic en **Run** (botón verde)
7. Debe aparecer: `Success. No rows returned`

---

### PASO 2 — Obtener tus credenciales de Supabase

1. En Supabase → **Settings** (ícono engranaje) → **API**
2. Copia:
   - **Project URL** → algo como `https://abcdefgh.supabase.co`
   - **anon public key** → empieza con `eyJ...`

---

### PASO 3 — Poner las credenciales en la app

1. Abre el archivo `.streamlit/secrets.toml` con el Bloc de notas
2. Reemplaza `https://XXXX.supabase.co` con tu Project URL
3. Reemplaza `eyJXXXX...` con tu anon key
4. Cambia `laocasion2024` por la contraseña que quieras

---

### PASO 4 — Publicar en Streamlit (gratis, desde cualquier PC)

1. Abre **streamlit.io** → entra a tu cuenta
2. Clic en **New app**
3. Conecta con tu cuenta de GitHub (si no tienes GitHub, crea una en github.com)
4. Sube los archivos de esta carpeta a un repositorio privado de GitHub
5. En Streamlit apunta al archivo `app.py`
6. En **Advanced settings → Secrets** copia el contenido de `secrets.toml`
7. Clic **Deploy** — en 2 minutos tendrás un link como:
   `https://laocasion-inventarios.streamlit.app`

---

### Probar en tu PC primero (opcional)

Si tienes Python instalado, puedes probar localmente:

```
pip install -r requirements.txt
streamlit run app.py
```

---

### Módulos disponibles

| Módulo | Descripción |
|--------|-------------|
| 📊 Dashboard | KPIs, gráficas de stock y movimientos |
| 📦 Insumos | Agregar, editar, eliminar insumos |
| 📋 Recetas | Recetas con costo automático y margen |
| 🧪 Sub-recetas | Preparaciones base reutilizables |
| ↕️ Movimientos | Entradas, salidas y ventas |
| 📒 Kardex | Trazabilidad por insumo con historial de precios |
| 🗑️ Bajas | Control de pérdidas con análisis por causa |
| 🔔 Alertas | Stock bajo, vencimientos, fluctuaciones de precio |
| 📈 Reportes | Gráficas de inventario, bajas y consumo |
| ⚙️ Configuración | % costos fijos y umbral de precio |
