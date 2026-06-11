# -*- coding: utf-8 -*-
"""
Genera el manual de usuario de La Ocasion - Sistema de Inventarios v2.0
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)

OUTPUT = r"C:\Users\LATITUDE 3400\Desktop\INGENIERIA DE MENÚ LA OCASION\inventarios_python\manual_usuario.pdf"

CAFE_OSCURO = colors.HexColor("#3B1A0A")
CAFE_MEDIO  = colors.HexColor("#7C4A1E")
CAFE_ACENTO = colors.HexColor("#C17F3E")
CREMA       = colors.HexColor("#F5EFE0")
CREMA_CARD  = colors.HexColor("#fff8f0")
VERDE_OK    = colors.HexColor("#2d7a2d")
ROJO        = colors.HexColor("#b00020")

styles = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

estilo_portada_titulo = S("PT", fontSize=36, leading=44, textColor=CREMA,
    alignment=TA_CENTER, fontName="Helvetica-Bold")
estilo_portada_sub    = S("PS", fontSize=14, leading=20, textColor=CAFE_ACENTO,
    alignment=TA_CENTER, fontName="Helvetica")
estilo_portada_mini   = S("PM", fontSize=10, leading=14, textColor=CREMA,
    alignment=TA_CENTER, fontName="Helvetica")
estilo_h1  = S("H1", fontSize=20, leading=26, textColor=CAFE_OSCURO,
    fontName="Helvetica-Bold", spaceAfter=6, spaceBefore=18)
estilo_h2  = S("H2", fontSize=13, leading=18, textColor=CAFE_MEDIO,
    fontName="Helvetica-Bold", spaceAfter=4, spaceBefore=10)
estilo_h3  = S("H3", fontSize=11, leading=15, textColor=CAFE_OSCURO,
    fontName="Helvetica-BoldOblique", spaceAfter=3, spaceBefore=6)
estilo_body   = S("BD", fontSize=10, leading=15, textColor=CAFE_OSCURO,
    fontName="Helvetica", alignment=TA_JUSTIFY, spaceAfter=4)
estilo_bullet = S("BL", fontSize=10, leading=14, textColor=CAFE_OSCURO,
    fontName="Helvetica", leftIndent=16, spaceAfter=2)
estilo_nota   = S("NT", fontSize=9, leading=13, textColor=CAFE_MEDIO,
    fontName="Helvetica-Oblique", leftIndent=12, spaceAfter=4)
estilo_indice = S("IX", fontSize=11, leading=18, textColor=CAFE_OSCURO, fontName="Helvetica")
estilo_indice_item = S("IXI", fontSize=10, leading=16, textColor=CAFE_MEDIO,
    fontName="Helvetica", leftIndent=20)
estilo_tip = S("TIP", fontSize=9, leading=13, textColor=VERDE_OK,
    fontName="Helvetica-Bold", leftIndent=12, spaceAfter=3)

def titulo_seccion(texto, icono=""):
    return [
        HRFlowable(width="100%", thickness=2, color=CAFE_ACENTO, spaceAfter=6),
        Paragraph(f"{icono}  {texto}" if icono else texto, estilo_h1),
        HRFlowable(width="100%", thickness=0.5, color=CAFE_ACENTO, spaceAfter=8),
    ]

def subtitulo(texto):     return Paragraph(texto, estilo_h2)
def subtitulo3(texto):    return Paragraph(texto, estilo_h3)
def paso(texto):          return Paragraph(f"<bullet>&bull;</bullet> {texto}", estilo_bullet)
def nota(texto):          return Paragraph(f"<i>Nota: {texto}</i>", estilo_nota)
def tip(texto):           return Paragraph(f"Tip: {texto}", estilo_tip)
def cuerpo(texto):        return Paragraph(texto, estilo_body)
def espacio(h=0.3):       return Spacer(1, h * cm)

def tabla_info(datos, col_widths=None):
    t = Table(datos, colWidths=col_widths or [5*cm, 11*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (0,-1), CREMA),
        ("BACKGROUND",   (1,0), (1,-1), CREMA_CARD),
        ("TEXTCOLOR",    (0,0), (-1,-1), CAFE_OSCURO),
        ("FONTNAME",     (0,0), (0,-1),  "Helvetica-Bold"),
        ("FONTNAME",     (1,0), (1,-1),  "Helvetica"),
        ("FONTSIZE",     (0,0), (-1,-1), 9),
        ("LEADING",      (0,0), (-1,-1), 13),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [CREMA, CREMA_CARD]),
        ("GRID",         (0,0), (-1,-1), 0.3, CAFE_ACENTO),
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING",   (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
    ]))
    return t

def tabla_acciones(datos):
    """tabla de 3 col: Boton | Color | Que hace"""
    t = Table(datos, colWidths=[4*cm, 2.5*cm, 9.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), CAFE_OSCURO),
        ("TEXTCOLOR",    (0,0), (-1,0), CREMA),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 9),
        ("LEADING",      (0,0), (-1,-1), 13),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [CREMA, CREMA_CARD]),
        ("TEXTCOLOR",    (0,1), (-1,-1), CAFE_OSCURO),
        ("FONTNAME",     (0,1), (-1,-1), "Helvetica"),
        ("GRID",         (0,0), (-1,-1), 0.3, CAFE_ACENTO),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING",   (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
    ]))
    return t

# ════════════════════════════════════════════════════════════════════
doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=2.2*cm, rightMargin=2.2*cm,
    topMargin=2.5*cm,  bottomMargin=2.5*cm,
    title="La Ocasion - Manual de Usuario v2",
    author="Ingenieria de Menu La Ocasion",
)
story = []
W, H = A4

# ── PORTADA ────────────────────────────────────────────────────────
story.append(Spacer(1, 3.5*cm))
story.append(Paragraph("la Ocasion", estilo_portada_titulo))
story.append(Spacer(1, 0.4*cm))
story.append(Paragraph("Sistema de Inventarios", estilo_portada_sub))
story.append(Spacer(1, 0.5*cm))
story.append(HRFlowable(width="60%", thickness=1.5, color=CAFE_ACENTO, hAlign="CENTER", spaceAfter=10))
story.append(Spacer(1, 0.4*cm))
story.append(Paragraph("Manual de Usuario", S("mv", fontSize=16, alignment=TA_CENTER,
    textColor=CREMA, fontName="Helvetica-Bold")))
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph("Version 2.0  |  2025", estilo_portada_mini))
story.append(Spacer(1, 3.5*cm))
story.append(Paragraph(
    "Ingenieria de Menu &amp; Gestion de Costos",
    S("x1", fontSize=10, alignment=TA_CENTER, textColor=CAFE_ACENTO, fontName="Helvetica")))
story.append(PageBreak())

# ── INDICE ─────────────────────────────────────────────────────────
story += titulo_seccion("Contenido")
story.append(espacio(0.3))
indice_items = [
    ("1.",    "Dashboard — Vision general del inventario"),
    ("2.",    "Insumos — Gestion de ingredientes"),
    ("  2.1", "Listado y edicion directa en tabla"),
    ("  2.2", "Stock inicial"),
    ("  2.3", "Minimos y alertas"),
    ("  2.4", "Agregar insumo"),
    ("  2.5", "Importar / Exportar CSV"),
    ("3.",    "Recetas — Platos de carta"),
    ("  3.1", "Nueva receta"),
    ("  3.2", "Listado desplegable con edicion de ingredientes"),
    ("  3.3", "Costos y margenes"),
    ("  3.4", "Importar / Exportar JSON"),
    ("4.",    "Sub-recetas — Preparaciones base"),
    ("  4.1", "Nueva sub-receta"),
    ("  4.2", "Listado desplegable con edicion de ingredientes"),
    ("5.",    "Movimientos — Entradas, Salidas y Ventas"),
    ("  5.1", "Registrar entrada"),
    ("  5.2", "Registrar salida"),
    ("  5.3", "Registrar venta / despacho"),
    ("  5.4", "Historial: editar y eliminar movimientos"),
    ("6.",    "Kardex — Trazabilidad por insumo"),
    ("7.",    "Bajas — Control de perdidas"),
    ("8.",    "Alertas — Listas desplegables por tipo"),
    ("9.",    "Reportes — Graficas e indicadores"),
    ("10.",   "Proyeccion de Produccion Semanal"),
    ("  10.1","Plan manual: insumos a comprar y sub-recetas a preparar"),
    ("  10.2","Sugerida por ventas"),
    ("11.",   "Configuracion del sistema"),
]
for num, tit in indice_items:
    es = estilo_indice if not num.startswith("  ") else estilo_indice_item
    story.append(Paragraph(f"{num}&nbsp;&nbsp;&nbsp;{tit}", es))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════
#  1. DASHBOARD
# ════════════════════════════════════════════════════════════════════
story += titulo_seccion("1. Dashboard")
story.append(cuerpo(
    "El Dashboard es la pantalla principal. Muestra un resumen en tiempo real "
    "del estado del inventario: KPIs, graficas, alertas criticas y ultimos movimientos."
))
story.append(espacio())
story.append(subtitulo("Indicadores (KPIs)"))
story.append(tabla_info([
    ["Insumos registrados",  "Total de ingredientes en el sistema."],
    ["Stock critico",        "Insumos cuyo stock actual es igual o menor al minimo."],
    ["Recetas activas",      "Total de platos registrados."],
    ["Bajas esta semana",    "Valor en COP de insumos dados de baja en los ultimos 7 dias."],
    ["Movimientos hoy",      "Entradas, salidas y ventas registradas hoy."],
    ["Valor inventario",     "Suma de stock x costo unitario de todos los insumos."],
]))
story.append(espacio())
story.append(subtitulo("Graficas"))
story.append(paso("Stock vs Minimo: Barras de los 12 insumos mas criticos. Rojo = bajo el minimo."))
story.append(paso("Movimientos ultimos 7 dias: Lineas de entradas, ventas y bajas por dia."))
story.append(espacio())
story.append(subtitulo("Panel inferior"))
story.append(paso("Listado de insumos con stock bajo el minimo (enlace directo a Alertas)."))
story.append(paso("Tabla con los 8 movimientos mas recientes."))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════
#  2. INSUMOS
# ════════════════════════════════════════════════════════════════════
story += titulo_seccion("2. Insumos")
story.append(cuerpo(
    "Los insumos son todos los ingredientes y materias primas del restaurante. "
    "El modulo tiene 6 pestanas: Listado, Stock inicial, Minimos/Alertas, "
    "Agregar, Importar CSV y Exportar CSV."
))
story.append(espacio())

story.append(subtitulo("2.1 Listado y edicion directa en tabla"))
story.append(cuerpo("La pestana <b>Listado</b> muestra todos los insumos en una tabla editable:"))
story.append(paso("Haz doble clic en cualquier celda para editarla directamente."))
story.append(paso("Puedes cambiar: nombre, categoria, unidad, stock, minimo, costo, proveedor y vida util."))
story.append(paso("Al terminar, haz clic en <b>Guardar cambios</b> para guardar solo las filas modificadas."))
story.append(paso("Usa el buscador para filtrar por nombre."))
story.append(nota("Si cambias el costo, el precio anterior se guarda en el historial de precios automaticamente."))
story.append(espacio())

story.append(subtitulo("2.2 Stock inicial"))
story.append(cuerpo(
    "La pestana <b>Stock inicial</b> permite registrar el inventario fisico de apertura. "
    "Usa esta pestana cuando empiezas a usar el sistema o despues de un conteo fisico:"
))
story.append(paso("Ingresa la cantidad actual de cada insumo en la tabla."))
story.append(paso("Haz clic en <b>Guardar stock inicial</b> para actualizar todos los valores."))
story.append(nota("El stock inicial sobreescribe el stock actual. Usalo con cuidado despues del primer conteo fisico."))
story.append(espacio())

story.append(subtitulo("2.3 Minimos y alertas"))
story.append(cuerpo(
    "La pestana <b>Minimos / Alertas</b> permite definir el nivel minimo de stock "
    "para cada insumo. Cuando el stock cae a ese nivel, se genera una alerta automatica:"
))
story.append(paso("Ingresa el stock minimo de cada insumo en la tabla."))
story.append(paso("Haz clic en <b>Guardar minimos</b>."))
story.append(paso("Los insumos con stock igual o menor al minimo apareceran en el modulo de Alertas con icono rojo."))
story.append(espacio())

story.append(subtitulo("2.4 Agregar insumo"))
story.append(cuerpo("Ve a la pestana <b>+ Agregar</b> y llena el formulario:"))
story.append(tabla_info([
    ["Nombre *",         "Nombre del ingrediente. Obligatorio."],
    ["Categoria",        "Proteinas, Lacteos, Verduras, Frutas, Harinas, Bebidas, etc."],
    ["Unidad",           "g, kg, ml, L, unidad, porcion, cucharada, etc."],
    ["Stock inicial",    "Cantidad disponible al registrar."],
    ["Stock minimo",     "Nivel minimo. Si el stock baja aqui se activa alerta."],
    ["Costo por unidad", "Precio de compra por unidad en pesos colombianos (COP)."],
    ["Proveedor",        "Nombre del proveedor habitual."],
    ["Vida util (dias)", "Dias de duracion. 0 = sin vencimiento."],
]))
story.append(espacio())

story.append(subtitulo("2.5 Importar / Exportar CSV"))
story.append(paso("Importar: Sube un archivo CSV con los insumos. Si ya existen, se actualizan."))
story.append(paso("Exportar: Descarga el inventario completo en CSV para trabajar en Excel."))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════
#  3. RECETAS
# ════════════════════════════════════════════════════════════════════
story += titulo_seccion("3. Recetas")
story.append(cuerpo(
    "Las recetas son los platos de la carta. Cada receta tiene un precio de venta "
    "y una lista de ingredientes. El sistema calcula automaticamente el costo total "
    "y el margen de ganancia."
))
story.append(espacio())

story.append(subtitulo("3.1 Nueva receta"))
story.append(tabla_info([
    ["Nombre *",        "Nombre del plato. Obligatorio."],
    ["Categoria",       "Plato Principal, Entrada, Postre, Bebida, Panaderia, etc."],
    ["Porciones",       "Numero de porciones que rinde la receta."],
    ["Precio de venta", "Precio al publico en pesos colombianos."],
]))
story.append(espacio(0.2))
story.append(cuerpo("<b>Para agregar ingredientes:</b>"))
story.append(paso("Haz clic en <b>+ Agregar ingrediente</b> para cada componente."))
story.append(paso("Selecciona el ingrediente: puede ser un insumo (icono caja) o una sub-receta (icono tubo de ensayo)."))
story.append(paso("Ingresa la <b>cantidad neta</b> que necesita la receta."))
story.append(paso("Ingresa el <b>% de merma</b>: porcentaje que se pierde en la preparacion."))
story.append(paso("El sistema calcula automaticamente la cantidad bruta y el costo."))
story.append(nota("Cantidad bruta = Cantidad neta / (1 - merma/100). Ejemplo: 100g con 20% merma = necesitas comprar 125g."))
story.append(espacio())

story.append(subtitulo("3.2 Listado desplegable con edicion de ingredientes"))
story.append(cuerpo(
    "En la pestana <b>Listado</b> las recetas se muestran agrupadas por categoria "
    "como tarjetas desplegables. Haz clic en cualquier receta para ver su detalle completo:"
))
story.append(paso("Se muestra: precio, costo de ingredientes, costo total y margen."))
story.append(paso("Dentro del card aparece la tabla de ingredientes directamente editable."))
story.append(espacio(0.2))
story.append(subtitulo3("Acciones sobre ingredientes:"))
story.append(tabla_acciones([
    ["Accion",                    "Donde",             "Como hacerlo"],
    ["Editar cantidad",           "Cant. neta",        "Clic directo en la celda y escribe el nuevo valor."],
    ["Editar merma",              "Merma %",           "Clic directo en la celda y escribe el porcentaje."],
    ["Cambiar ingrediente",       "Ingrediente",       "Clic en la celda: aparece un menu desplegable con todos los insumos y sub-recetas disponibles."],
    ["Agregar ingrediente nuevo", "Ultima fila",       "Clic en el boton + al final de la tabla para agregar una fila vacia."],
    ["Eliminar ingrediente",      "Fila de la tabla",  "Selecciona la fila y haz clic en el icono de borrar (X) a la derecha."],
    ["Guardar todos los cambios", "Boton cafe",        "Clic en 'Guardar ingredientes' para guardar en la base de datos."],
    ["Eliminar receta completa",  "Boton rojo",        "Clic en 'Eliminar receta'. Esta accion no se puede deshacer."],
]))
story.append(espacio())

story.append(subtitulo("3.3 Costos y margenes"))
story.append(tabla_info([
    ["Costo ingredientes", "Suma del costo de todos los ingredientes segun cantidad bruta."],
    ["Costos fijos (%)",   "Porcentaje adicional para cubrir arriendo, servicios, nomina, etc. Se configura en el modulo Configuracion."],
    ["Costo total",        "Costo ingredientes x (1 + % costos fijos / 100)."],
    ["Margen",             "(Precio venta - Costo total) / Precio venta x 100%."],
]))
story.append(espacio())

story.append(subtitulo("3.4 Importar / Exportar JSON"))
story.append(paso("Exportar: Descarga todas las recetas en JSON para respaldo."))
story.append(paso("Importar: Sube un JSON exportado previamente. Las recetas existentes se omiten."))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════
#  4. SUB-RECETAS
# ════════════════════════════════════════════════════════════════════
story += titulo_seccion("4. Sub-recetas")
story.append(cuerpo(
    "Las sub-recetas son preparaciones intermedias que se reutilizan en varias recetas. "
    "Ejemplos: masa de pan, salsa pesto, alioli, mermelada casera, caldo base, rellenos."
))
story.append(espacio())

story.append(subtitulo("4.1 Nueva sub-receta"))
story.append(tabla_info([
    ["Nombre *",           "Nombre de la preparacion. Obligatorio."],
    ["Categoria",          "Base, Salsa, Aliño, Masa, Relleno, Panaderia, etc."],
    ["Rendimiento",        "Cantidad total que produce la sub-receta (ej: 800 para 800g de pesto)."],
    ["Unidad rendimiento", "Unidad del rendimiento: g, kg, ml, L, unidad, etc."],
]))
story.append(cuerpo(
    "El sistema calcula el <b>costo por unidad de rendimiento</b>: "
    "divide el costo total entre el rendimiento. "
    "Cuando una receta usa esta sub-receta, el costo se integra automaticamente."
))
story.append(espacio())

story.append(subtitulo("4.2 Listado desplegable con edicion de ingredientes"))
story.append(cuerpo(
    "En la pestana <b>Listado</b> las sub-recetas se muestran agrupadas por categoria. "
    "Haz clic en cualquier sub-receta para ver su detalle:"
))
story.append(paso("Se muestran: rendimiento, costo de elaboracion y costo por unidad."))
story.append(paso("Dentro del card aparece la tabla de ingredientes directamente editable."))
story.append(paso("Las acciones de edicion son identicas a las de Recetas (ver seccion 3.2)."))
story.append(nota("Las sub-recetas solo pueden usar insumos como ingredientes (no otras sub-recetas anidadas)."))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════
#  5. MOVIMIENTOS
# ════════════════════════════════════════════════════════════════════
story += titulo_seccion("5. Movimientos")
story.append(cuerpo(
    "Los movimientos registran cada cambio en el inventario. "
    "Hay cuatro pestanas: Entrada, Salida, Venta/Despacho e Historial."
))
story.append(espacio())

story.append(subtitulo("5.1 Registrar entrada"))
story.append(cuerpo("Cuando llega una compra o un insumo entra al inventario:"))
story.append(paso("Selecciona el insumo."))
story.append(paso("Ingresa la cantidad que entro."))
story.append(paso("Ingresa el costo por unidad de esta compra (0 = mantener costo actual)."))
story.append(paso("Llena fecha, responsable, proveedor y nota (todos opcionales)."))
story.append(paso("Haz clic en <b>Registrar entrada</b>. El stock se suma automaticamente."))
story.append(nota("Si el precio es diferente al anterior, se guarda en el historial de precios y puede activar una alerta de fluctuacion."))
story.append(espacio())

story.append(subtitulo("5.2 Registrar salida"))
story.append(cuerpo("Para descontar insumos usados fuera de una venta (consumo cocina, merma, transferencia):"))
story.append(paso("Selecciona el insumo."))
story.append(paso("Ingresa la cantidad que sale."))
story.append(paso("Selecciona el motivo: Consumo cocina, Merma, Transferencia u Otro."))
story.append(paso("El stock se descuenta automaticamente."))
story.append(espacio())

story.append(subtitulo("5.3 Registrar venta / despacho"))
story.append(cuerpo(
    "Cuando se vende un plato, el sistema descuenta automaticamente todos sus ingredientes:"
))
story.append(paso("Selecciona la receta vendida."))
story.append(paso("Ingresa el numero de porciones."))
story.append(paso("El sistema muestra los insumos que se descontaran y si hay stock suficiente (verde = OK, rojo = falta)."))
story.append(paso("Haz clic en <b>Registrar venta</b>."))
story.append(nota("Si algun insumo no tiene stock suficiente, el sistema lo advierte y bloquea el registro."))
story.append(espacio())

story.append(subtitulo("5.4 Historial: editar y eliminar movimientos"))
story.append(cuerpo(
    "La pestana <b>Historial</b> muestra todos los movimientos como tarjetas desplegables. "
    "Puedes filtrar por tipo, fecha o buscar por nombre. "
    "Cada movimiento tiene dos acciones disponibles:"
))
story.append(espacio(0.2))
story.append(tabla_acciones([
    ["Accion",                            "Boton",             "Descripcion"],
    ["Editar nota, fecha o responsable",  "Guardar cambios",   "Corrige datos del movimiento sin afectar el stock. Util para errores de escritura o fecha incorrecta."],
    ["Eliminar y revertir stock",         "Eliminar y revertir","Borra el movimiento Y revierte el stock al estado anterior. Usar para cancelar registros equivocados."],
]))
story.append(espacio(0.2))
story.append(subtitulo3("Que pasa con el stock al eliminar:"))
story.append(tabla_info([
    ["Entrada eliminada",  "El stock del insumo disminuye la cantidad que habia entrado."],
    ["Salida eliminada",   "El stock del insumo aumenta la cantidad que habia salido."],
    ["Venta eliminada",    "El stock de todos los ingredientes de la receta se devuelve segun las cantidades consumidas."],
]))
story.append(nota("Si eliminas una venta, los ingredientes de la receta vuelven al inventario como si la venta no hubiera ocurrido."))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════
#  6. KARDEX
# ════════════════════════════════════════════════════════════════════
story += titulo_seccion("6. Kardex")
story.append(cuerpo(
    "El Kardex muestra la trazabilidad completa de un insumo especifico: "
    "todas sus entradas, salidas y ventas en orden cronologico, "
    "con el saldo acumulado despues de cada movimiento."
))
story.append(espacio())
story.append(paso("Selecciona el insumo que quieres revisar."))
story.append(paso("Filtra por rango de fechas si necesitas un periodo especifico."))
story.append(paso("La tabla muestra: fecha, tipo, descripcion, entrada, salida, saldo y costo."))
story.append(paso("Si el insumo tiene historial de precios, se muestra una grafica de evolucion de precio."))
story.append(nota("El kardex es util para auditorias, detectar inconsistencias y revisar el comportamiento de un insumo a lo largo del tiempo."))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════
#  7. BAJAS
# ════════════════════════════════════════════════════════════════════
story += titulo_seccion("7. Bajas")
story.append(cuerpo(
    "Las bajas registran los insumos que se pierden sin generar venta: "
    "vencimientos, contaminacion, accidentes, errores de porcion."
))
story.append(espacio())
story.append(tabla_info([
    ["Insumo *",      "Ingrediente que se da de baja."],
    ["Cantidad *",    "Cuanto se pierde."],
    ["Causa *",       "Vencimiento, Contaminacion, Error de preparacion, Accidente, etc."],
    ["Turno",         "Manana, Tarde, Noche."],
    ["Responsable",   "Quien reporta la baja."],
    ["Autoriza",      "Quien autoriza (jefe de cocina, administrador)."],
    ["Accion tomada", "Que se hizo al respecto."],
]))
story.append(espacio())
story.append(paso("El stock del insumo se descuenta automaticamente."))
story.append(paso("En el Dashboard aparece el valor total de bajas de la semana."))
story.append(paso("En Reportes puedes ver graficas de bajas por causa."))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════
#  8. ALERTAS
# ════════════════════════════════════════════════════════════════════
story += titulo_seccion("8. Alertas")
story.append(cuerpo(
    "El modulo de Alertas detecta automaticamente situaciones criticas y las muestra "
    "en tres secciones desplegables. En la parte superior hay tres KPIs que muestran "
    "el numero de alertas activas de cada tipo."
))
story.append(espacio())

story.append(subtitulo("Seccion 1 — Stock bajo el minimo"))
story.append(cuerpo(
    "Muestra los insumos cuyo stock actual esta igual o por debajo del minimo definido. "
    "Los insumos se agrupan por categoria."
))
story.append(tabla_info([
    ["Icono rojo (Rojo)",   "El stock es menor o igual al 50% del minimo. Situacion critica."],
    ["Icono naranja",       "El stock esta entre el 50% y el 100% del minimo. Necesita atencion."],
]))
story.append(paso("Haz clic en cualquier insumo para ver: stock actual, minimo, faltante y proveedor."))
story.append(espacio())

story.append(subtitulo("Seccion 2 — Vencimientos proximos"))
story.append(cuerpo(
    "Muestra los insumos que vencen en los proximos 7 dias. "
    "Solo aparecen insumos con vida util y fecha de ultima entrada definidas."
))
story.append(tabla_info([
    ["Rojo - VENCIDO",  "El insumo ya vencio. Retirar inmediatamente."],
    ["Rojo - HOY",      "El insumo vence hoy."],
    ["Naranja - En X dias", "El insumo vence pronto. Planifica su uso o descarte."],
]))
story.append(paso("Haz clic en cada item para ver: stock actual, vida util y fecha de ultima entrada."))
story.append(espacio())

story.append(subtitulo("Seccion 3 — Fluctuaciones de precio"))
story.append(cuerpo(
    "Muestra los insumos cuyo precio subio mas del umbral configurado entre dos compras consecutivas. "
    "Los items se ordenan de mayor a menor porcentaje de aumento."
))
story.append(paso("Haz clic en cada item para ver: precio anterior, precio nuevo, variacion % y proveedor."))
story.append(nota("El umbral de alerta de precio se configura en el modulo de Configuracion (por defecto 3%)."))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════
#  9. REPORTES
# ════════════════════════════════════════════════════════════════════
story += titulo_seccion("9. Reportes")
story.append(cuerpo(
    "El modulo de Reportes ofrece visualizaciones graficas para analizar el desempeno del inventario."
))
story.append(espacio())
story.append(tabla_info([
    ["Top insumos por valor",  "Cuales insumos representan mayor valor en el inventario (Pareto)."],
    ["Bajas por causa",        "Distribucion de perdidas por tipo de causa."],
    ["Consumo semanal",        "Cantidad y costo de insumos consumidos en la semana actual."],
    ["Ventas por receta",      "Cuantas veces se ha vendido cada plato en el periodo."],
    ["Margen por receta",      "Comparacion de margenes de ganancia de todas las recetas."],
]))
story.append(espacio())
story.append(tip("Puedes guardar cualquier grafica como imagen haciendo clic derecho sobre ella."))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════
#  10. PROYECCION
# ════════════════════════════════════════════════════════════════════
story += titulo_seccion("10. Proyeccion de Produccion Semanal")
story.append(cuerpo(
    "Este modulo calcula cuanto producir durante la semana, "
    "que insumos necesitas comprar y que sub-recetas debes preparar. "
    "Tiene dos pestanas: Plan Manual y Sugerida por Ventas."
))
story.append(espacio())

story.append(subtitulo("10.1 Plan manual"))
story.append(paso("Filtra por categoria (Panaderia, Pasteleria, Platos, etc.) si lo deseas."))
story.append(paso("Para cada receta, ingresa cuantas porciones quieres producir esta semana."))
story.append(paso("El sistema calcula automaticamente los insumos necesarios vs el stock actual."))
story.append(espacio(0.2))
story.append(subtitulo3("Tabla de insumos necesarios vs stock"))
story.append(cuerpo(
    "Muestra todos los insumos requeridos (incluyendo los de las sub-recetas descompuestas). "
    "Cada fila indica cuanto necesitas, cuanto tienes y cuanto te falta."
))
story.append(espacio(0.2))
story.append(subtitulo3("Seccion: Insumos a COMPRAR"))
story.append(cuerpo(
    "Solo los insumos con faltante mayor a cero. Cada uno aparece como una tarjeta desplegable "
    "con la cantidad exacta a comprar y el costo estimado. "
    "Puedes descargar la lista completa en CSV."
))
story.append(espacio(0.2))
story.append(subtitulo3("Seccion: Sub-recetas a PREPARAR"))
story.append(cuerpo(
    "Cuando las recetas planeadas usan sub-recetas, el sistema calcula cuantas "
    "<b>tandas</b> de cada sub-receta debes preparar:"
))
story.append(tabla_info([
    ["Total necesario",     "Cantidad total de la sub-receta que necesitan todas las recetas planeadas."],
    ["Rend. por tanda",     "Cuanto produce una sola preparacion de la sub-receta."],
    ["Tandas a preparar",   "Total necesario / Rendimiento por tanda. Puede ser decimal (ej: 3.5 tandas)."],
]))
story.append(paso("Ejemplo: Si necesitas 2.8 kg de pesto y el pesto rinde 800g por tanda, necesitas preparar 3.5 tandas."))
story.append(paso("Puedes descargar el plan de sub-recetas en CSV."))
story.append(espacio())

story.append(subtitulo("10.2 Sugerida por ventas"))
story.append(cuerpo(
    "El sistema analiza las ventas pasadas para sugerir cuanto producir:"
))
story.append(paso("Selecciona el periodo de referencia (Desde / Hasta)."))
story.append(paso("Ajusta el <b>Factor de ajuste</b>: 100% = igual que el promedio, 120% = 20% mas."))
story.append(paso("El sistema calcula el promedio diario de ventas por receta y lo proyecta a 7 dias."))
story.append(paso("Haz clic en <b>Usar esta sugerencia como plan de produccion</b> para cargarla en el Plan Manual."))
story.append(paso("La misma vista de <b>Insumos a comprar</b> y <b>Sub-recetas a preparar</b> aparece aqui tambien."))
story.append(nota("Si no hay ventas en el periodo seleccionado, la sugerencia sera 0 para todas las recetas. Registra ventas en Movimientos para obtener sugerencias utiles."))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════
#  11. CONFIGURACION
# ════════════════════════════════════════════════════════════════════
story += titulo_seccion("11. Configuracion")
story.append(cuerpo(
    "El modulo de Configuracion permite ajustar los parametros globales del sistema."
))
story.append(espacio())
story.append(tabla_info([
    ["% Costos fijos",          "Porcentaje de gastos fijos (arriendo, servicios, nomina, etc.) que se suma al costo de ingredientes de cada receta. Por defecto: 15%. Afecta el margen de TODAS las recetas."],
    ["% Umbral alerta precio",  "Si el precio de un insumo sube mas de este % entre dos compras, se genera una alerta en el modulo de Alertas. Por defecto: 3%."],
]))
story.append(espacio())
story.append(nota("Cambiar los costos fijos actualiza los margenes de todas las recetas inmediatamente."))
story.append(espacio(2))

# ── PIE ────────────────────────────────────────────────────────────
story.append(HRFlowable(width="100%", thickness=1.5, color=CAFE_ACENTO, spaceAfter=10))
story.append(Paragraph(
    "la Ocasion &bull; Sistema de Inventarios &bull; Version 2.0 &bull; 2025",
    S("pie", fontSize=9, alignment=TA_CENTER, textColor=CAFE_MEDIO, fontName="Helvetica")))
story.append(Paragraph(
    "Para soporte contacta a tu consultor de ingenieria de menu.",
    S("pie2", fontSize=8, alignment=TA_CENTER, textColor=CAFE_ACENTO, fontName="Helvetica-Oblique")))

# ── Encabezado / pie en cada pagina ────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(CAFE_OSCURO)
    canvas.rect(0, H - 0.8*cm, W, 0.8*cm, fill=1, stroke=0)
    canvas.rect(0, 0, W, 0.7*cm, fill=1, stroke=0)
    canvas.setFillColor(CREMA)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(W/2, 0.22*cm, f"Pagina {doc.page}")
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(CAFE_ACENTO)
    canvas.drawString(2.2*cm, H - 0.55*cm, "la Ocasion")
    canvas.setFillColor(CREMA)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(W - 2.2*cm, H - 0.55*cm, "Manual de Usuario v2.0")
    canvas.restoreState()

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print("Manual generado:", OUTPUT)
