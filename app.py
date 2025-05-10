import streamlit as st
import pandas as pd
import tempfile
import os

# --- Configuración de la interfaz ---
st.set_page_config(page_title="Top 30 Stock", layout="wide")
st.title("📊 Análisis de Top 30 productos y stock por tienda")

# --- Tiendas válidas ---
TIENDAS_VALIDAS = {
    "01", "02", "03", "04", "05", "06", "07", "09", "11", "12", "13", "15", "16", "17",
    "18", "19", "21", "22", "24", "25", "26", "27", "28", "29", "31", "33", "35", "36",
    "37", "38", "39", "41", "42"
}

# --- Subida del archivo ---
archivo = st.file_uploader("📂 Sube el archivo TXT de stock y ventas", type=["txt"])

if archivo:
    try:
        # --- Lectura del archivo ---
        df = pd.read_csv(archivo, sep="\t", encoding="utf-8", decimal=",")

        # --- Limpieza de 'online hombre' ---
        df = df[~df.apply(lambda row: row.astype(str).str.lower().str.contains("online hombre").any(), axis=1)]

        # --- Detección de columnas ---
        columnas_ventas = [col for col in df.columns if col.startswith("V") and col[1:] in TIENDAS_VALIDAS]
        columnas_stock = [col for col in df.columns if col.startswith("S") and col[1:] in TIENDAS_VALIDAS]

        # --- Conversión a numérico ---
        df[columnas_ventas + columnas_stock] = df[columnas_ventas + columnas_stock].apply(pd.to_numeric, errors='coerce')

        # --- Cálculo de totales ---
        df["Total_Ventas"] = df[columnas_ventas].sum(axis=1, skipna=True)
        df["Total_Stock"] = df[columnas_stock].sum(axis=1, skipna=True)
        top_30 = df.nlargest(30, "Total_Ventas").copy()

        # --- Mostrar en pantalla el resumen global ---
        resumen_global = top_30[["CODIGO", "ARTICULO", "DESCRIPCION", "Total_Ventas", "Total_Stock"]]
        st.subheader("🔝 Top 30 productos por ventas")
        st.dataframe(resumen_global)

        # --- Crear archivo CSV global ---
        tmpdir = tempfile.mkdtemp()
        csv_path = os.path.join(tmpdir, "top_30_global.csv")
        resumen_global.to_csv(csv_path, index=False, encoding="utf-8-sig", sep=";")

        # --- Crear Excel con hojas por tienda ---
        resumen_data = []
        hojas_por_tienda = {}

        for tienda in columnas_stock:
            sin_stock = top_30[top_30[tienda] <= 0]
            resumen_data.append({
                "Tienda": tienda,
                "Productos_sin_stock": len(sin_stock),
                "Porcentaje": f"{len(sin_stock)/30:.0%}"
            })
            if not sin_stock.empty:
                columnas_a_mostrar = ["CODIGO", "ARTICULO", "DESCRIPCION", "Total_Ventas", tienda]
                hojas_por_tienda[tienda] = sin_stock[columnas_a_mostrar]

        resumen_df = pd.DataFrame(resumen_data)
        excel_path = os.path.join(tmpdir, "top_30_por_tienda.xlsx")
        with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
            resumen_df.to_excel(writer, sheet_name="RESUMEN", index=False)
            for tienda, df_tienda in hojas_por_tienda.items():
                df_tienda.to_excel(writer, sheet_name=tienda, index=False)

        # --- Botones para descargar archivos ---
        st.subheader("📥 Descarga de archivos")

        with open(csv_path, "rb") as f:
            st.download_button("⬇️ Descargar Top 30 Global (.csv)", f, file_name="top_30_global.csv")

        with open(excel_path, "rb") as f:
            st.download_button("⬇️ Descargar Excel por Tienda (.xlsx)", f, file_name="top_30_por_tienda.xlsx")

    except Exception as e:
        st.error(f"❌ Error procesando el archivo: {e}")
