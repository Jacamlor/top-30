# 🧮 Top 30 Productos con Stock por Tienda

Esta es una aplicación interna desarrollada con [Streamlit](https://streamlit.io) para analizar los productos más vendidos y su stock por tienda.

## 🚀 ¿Qué hace esta app?

- Permite subir un archivo `.txt` con columnas de stock (`Sxx`) y ventas (`Vxx`).
- Filtra las tiendas permitidas (S01 a S42 según configuración).
- Elimina productos como `"online hombre"`.
- Genera:
  - Un archivo `.csv` con el **Top 30 productos por ventas totales**.
  - Un archivo `.xlsx` con:
    - Una hoja `RESUMEN` (productos sin stock por tienda).
    - Una hoja por tienda (productos del top 30 con stock ≤ 0).

## 🛠 Requisitos

- Python 3.8+
- Streamlit
- Pandas
- XlsxWriter

Instalación local (opcional):

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🌐 Despliegue en Streamlit Cloud

1. Sube este repositorio a GitHub.
2. Ve a [https://streamlit.io/cloud](https://streamlit.io/cloud) y conéctalo.
3. Selecciona `app.py` como archivo principal.
4. Haz clic en **Deploy**.
