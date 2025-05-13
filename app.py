import streamlit as st
import pandas as pd
import tempfile
import os

st.set_page_config(page_title="Top 30 Ventas por Tienda y Zona", layout="wide")
st.title("🏪 Top 30 de ventas por tienda, por zona y tiendas dentro de zona")

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
        df[columnas_ventas] = df[columnas_ventas].apply(pd.to_numeric, errors="coerce")

        tmpdir = tempfile.mkdtemp()

        # === 1. Excel por tienda individual ===
        st.subheader("📁 Excel: Top 30 por tienda")
        path_tienda = os.path.join(tmpdir, "top_30_por_tienda.xlsx")
        with pd.ExcelWriter(path_tienda, engine="xlsxwriter") as writer:
            for tienda in columnas_ventas:
                top = df[["CODIGO", "ARTICULO", "DESCRIPCION", tienda]].copy()
                top = top.rename(columns={tienda: "Ventas"}).sort_values(by="Ventas", ascending=False).head(30)
                top.to_excel(writer, sheet_name=tienda[:31], index=False)

        with open(path_tienda, "rb") as f:
            st.download_button("⬇️ Descargar Top 30 por tienda", f, file_name="top_30_por_tienda.xlsx")

        # === 2. Excel con top 30 global por zona ===
        st.subheader("📘 Excel: Top 30 por zona")
        path_zona = os.path.join(tmpdir, "top_30_por_zona.xlsx")
        with pd.ExcelWriter(path_zona, engine="xlsxwriter") as writer:
            for zona, tiendas in ZONAS.items():
                tiendas_validas = [t for t in tiendas if t in df.columns]
                if not tiendas_validas:
                    continue
                df_zona = df.copy()
                df_zona["Ventas_Totales"] = df_zona[tiendas_validas].sum(axis=1)
                top_zona = df_zona[["CODIGO", "ARTICULO", "DESCRIPCION", "Ventas_Totales"]].sort_values(by="Ventas_Totales", ascending=False).head(30)
                top_zona.to_excel(writer, sheet_name=zona[:31], index=False)

        with open(path_zona, "rb") as f:
            st.download_button("⬇️ Descargar Top 30 por zona", f, file_name="top_30_por_zona.xlsx")

        # === 3. Excel por tienda dentro de cada zona ===
        st.subheader("🗂️ Excel: Top 30 por tienda dentro de cada zona")
        path_tienda_en_zona = os.path.join(tmpdir, "top_30_por_tienda_en_zona.xlsx")
        hojas_escritas = 0
        with pd.ExcelWriter(path_tienda_en_zona, engine="xlsxwriter") as writer:
            for zona, tiendas in ZONAS.items():
                for tienda in tiendas:
                    if tienda in df.columns:
                        top = df[["CODIGO", "ARTICULO", "DESCRIPCION", tienda]].copy()
                        top = top.rename(columns={tienda: "Ventas"}).sort_values(by="Ventas", ascending=False).head(30)
                        top.to_excel(writer, sheet_name=nombre_hoja, index=False)
                        hojas_escritas += 1

        if hojas_escritas > 0:
            with open(path_tienda_en_zona, "rb") as f:
                st.download_button("⬇️ Descargar Top 30 por tienda en zona", f, file_name="top_30_por_tienda_en_zona.xlsx")
        else:
            st.warning("⚠️ No se generaron hojas para el archivo por tienda en zona.")

    except Exception as e:
        st.error(f"❌ Error procesando el archivo: {e}")
