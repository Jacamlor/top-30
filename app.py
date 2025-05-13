
import streamlit as st
import pandas as pd
import os
import tempfile

st.set_page_config(page_title="Top 30 por Tienda y Zonas", layout="wide")
st.title("🏬 Top 30 productos más vendidos por tienda y zonas")

# === Grupos de tiendas por zona ===
ZONAS = {
    "Zona Alex":   ["V04", "V06", "V09", "V11", "V12", "V13", "V26", "V27", "V28", "V31", "V35"],
    "Zona Alberto": ["V37"],
    "Zona Leticia": ["V01", "V02", "V07", "V15", "V16", "V17", "V24", "V29", "V38"],
    "Zona Roberto": ["V03", "V05", "V21", "V22", "V25", "V33", "V36", "V39", "V41", "V42"]
}

archivo = st.file_uploader("📂 Sube el archivo TXT de stock y ventas", type=["txt"])

if archivo:
    try:
        df = pd.read_csv(archivo, sep="\t", encoding="utf-8", decimal=",")
        columnas_ventas = [col for col in df.columns if col.startswith("V")]

        # Asegurar valores numéricos
        df[columnas_ventas] = df[columnas_ventas].apply(pd.to_numeric, errors="coerce")

        tmpdir = tempfile.mkdtemp()

        # === 1. Generar archivo por tienda individual ===
        st.subheader("📁 Archivos Excel por tienda individual")

        with pd.ExcelWriter(os.path.join(tmpdir, "top_30_por_tienda.xlsx"), engine="xlsxwriter") as writer:
            for col in columnas_ventas:
                top_tienda = df[["CODIGO", "ARTICULO", "DESCRIPCION", col]].copy()
                top_tienda = top_tienda.rename(columns={col: "Ventas"}).sort_values(by="Ventas", ascending=False).head(30)
                top_tienda.to_excel(writer, sheet_name=col, index=False)

        with open(os.path.join(tmpdir, "top_30_por_tienda.xlsx"), "rb") as f:
            st.download_button("⬇️ Descargar Excel por tienda", f, file_name="top_30_por_tienda.xlsx")

        # === 2. Generar archivo por zonas ===
        st.subheader("📘 Archivo Excel por zonas agrupadas")

        with pd.ExcelWriter(os.path.join(tmpdir, "top_30_por_zona.xlsx"), engine="xlsxwriter") as writer:
            for zona, tiendas in ZONAS.items():
                columnas_zona = [tienda for tienda in tiendas if tienda in df.columns]
                if columnas_zona:
                    df_zona = df.copy()
                    df_zona["Ventas_Zona"] = df_zona[columnas_zona].sum(axis=1)
                    top_30_zona = df_zona[["CODIGO", "ARTICULO", "DESCRIPCION", "Ventas_Zona"]].sort_values(by="Ventas_Zona", ascending=False).head(30)
                    for tienda in columnas_zona:
                        top_30_zona[tienda] = df[tienda]
                    for tienda in columnas_zona:
                        columnas = ["CODIGO", "ARTICULO", "DESCRIPCION", "Ventas_Zona", tienda]
                        hoja = top_30_zona[columnas].copy()
                        hoja.to_excel(writer, sheet_name=tienda, index=False)

        with open(os.path.join(tmpdir, "top_30_por_zona.xlsx"), "rb") as f:
            st.download_button("⬇️ Descargar Excel por zonas", f, file_name="top_30_por_zona.xlsx")

    except Exception as e:
        st.error(f"❌ Error procesando el archivo: {e}")
