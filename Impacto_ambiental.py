import streamlit as st
import pandas as pd

# Título de la app
st.title("🌿 Evaluador de Impacto Ambiental - Bonos Verdes ICMA")
st.write("Selecciona una categoría ICMA y marca los requisitos que tu proyecto cumple.")

def cargar_excel():
    xls = pd.ExcelFile("Requisitos_ICMA.xlsx")
    return xls

# Leer archivo
try:
    xls = cargar_excel()
    hojas = xls.sheet_names
    st.success("✅ Excel cargado exitosamente")
except Exception as e:
    st.error(f"❌ Error al cargar el archivo Excel: {e}")
    st.stop()

# Selección de categoría
categoria = st.selectbox("Selecciona una categoría:", hojas)

# Leer hoja seleccionada
df = xls.parse(categoria)

# Limpiar y preparar los datos
if 'Unnamed: 1' not in df.columns:
    st.error("❌ La hoja seleccionada no tiene la estructura esperada.")
    st.stop()

df_clean = df.dropna(subset=['Unnamed: 1'])
df_clean = df_clean.rename(columns={'Unnamed: 1': 'Requisito', 'Indicadores': 'ID'})
df_clean = df_clean.reset_index(drop=True)

# Mostrar checklist de requisitos
st.subheader(f"📋 Requisitos en categoría: {categoria}")
cumplidos = []
for i, row in df_clean.iterrows():
    cumple = st.checkbox(row['Requisito'], key=f"req_{i}")
    cumplidos.append(1 if cumple else 0)

# Cálculo del resultado
total = len(cumplidos)
cumplidos_total = sum(cumplidos)
porcentaje = (cumplidos_total / total) * 100 if total > 0 else 0

st.markdown(f"### ✅ Cumples con el **{porcentaje:.1f}%** de los requisitos.")

if porcentaje >= 70:
    st.success("¡Tu proyecto cumple con los criterios ambientales para un bono verde! 🌱")
else:
    st.warning("Tu proyecto aún no cumple con los criterios suficientes. Sigue mejorando 💪")

# Agregar columna de cumplimiento y exportar CSV
df_clean["Cumple"] = cumplidos
csv = df_clean.to_csv(index=False).encode('utf-8')
st.download_button("📥 Descargar resultados en CSV", data=csv, file_name="impacto_ambiental_resultado.csv", mime="text/csv")
