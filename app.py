#!/usr/bin/env python
# coding: utf-8


# In[12]:


import pandas as pd
import os

# === MOSTRAR DIRECTORIO ACTUAL ===
print(f"📁 Directorio actual: {os.getcwd()}")

# === PEDIR NOMBRE DEL ARCHIVO ===
archivo = input("📂 Introduce el nombre o ruta completa del archivo (ej: PRUEBA TOP.txt): ").strip()
if not os.path.isfile(archivo):
    print(f"❌ El archivo '{archivo}' no existe.")
    exit()

# === CONFIGURACIÓN ===
separador = "\t"
decimal = ","
archivo_global = "top_30_global.csv"
archivo_por_tienda_xlsx = "top_30_por_tienda.xlsx"

# === TIENDAS PERMITIDAS ===
tiendas_validas = {
    "01", "02", "03", "04", "05", "06", "07", "09", "11", "12", "13", "15", "16", "17",
    "18", "19", "21", "22", "24", "25", "26", "27", "28", "29", "31", "33", "35", "36",
    "37", "38", "39", "41", "42"
}

# === CARGAR DATOS ===
df = pd.read_csv(archivo, sep=separador, encoding="utf-8", decimal=decimal)

# === ELIMINAR FILAS CON "online hombre" EN CUALQUIER COLUMNA ===
df = df[~df.apply(lambda fila: fila.astype(str).str.lower().str.contains("online hombre").any(), axis=1)]

# === IDENTIFICAR COLUMNAS V y S SEGÚN TIENDAS PERMITIDAS ===
columnas_ventas = [col for col in df.columns if col.startswith("V") and col[1:] in tiendas_validas]
columnas_stock = [col for col in df.columns if col.startswith("S") and col[1:] in tiendas_validas]

# === CONVERTIR A NÚMEROS ===
df[columnas_ventas + columnas_stock] = df[columnas_ventas + columnas_stock].apply(pd.to_numeric, errors='coerce')

# === CALCULAR TOTALES Y TOP 30 ===
df["Total_Ventas"] = df[columnas_ventas].sum(axis=1, skipna=True)
df["Total_Stock"] = df[columnas_stock].sum(axis=1, skipna=True)
top_30 = df.nlargest(30, "Total_Ventas").copy()

# === ARCHIVO 1: GLOBAL ===
top_30_global = top_30[["CODIGO", "ARTICULO", "DESCRIPCION", "Total_Ventas", "Total_Stock"]]
top_30_global.to_csv(archivo_global, index=False, encoding="utf-8-sig", sep=";")

# === ARCHIVO 2: EXCEL CON HOJA "RESUMEN" PRIMERO ===
resumen_data = []

with pd.ExcelWriter(archivo_por_tienda_xlsx, engine="xlsxwriter") as writer:
    # === PRIMERO: hoja "RESUMEN"
    for tienda in columnas_stock:
        productos_sin_stock = top_30[top_30[tienda] <= 0]
        resumen_data.append({"Tienda": tienda, "Productos_sin_stock": len(productos_sin_stock)})

    resumen_df = pd.DataFrame(resumen_data)
    resumen_df.to_excel(writer, sheet_name="RESUMEN", index=False)

    # === DESPUÉS: hojas por tienda si hay productos sin stock
    for tienda in columnas_stock:
        productos_sin_stock = top_30[top_30[tienda] <= 0]
        if not productos_sin_stock.empty:
            columnas_a_mostrar = ["CODIGO", "ARTICULO", "DESCRIPCION", "Total_Ventas", tienda]
            productos_sin_stock[columnas_a_mostrar].to_excel(writer, sheet_name=tienda, index=False)

# === CONFIRMACIÓN ===
print(f"\n✅ Archivos generados correctamente:")
print(f"   📄 {archivo_global}")
print(f"   📄 {archivo_por_tienda_xlsx}")
print("\n📊 La hoja 'RESUMEN' será la primera visible al abrir el archivo Excel.")

