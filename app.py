import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

# Configuración de la página web
st.set_page_config(page_title="Evaluador de Bonos Verdes", layout="wide")
st.title("🌱 Evaluador de Proyectos para Bonos Verdes")

# Menú de navegación
seccion = st.sidebar.radio("Navega por la aplicación:", [
    "Análisis Financiero",
    "Evaluación Ambiental ICMA",
    "Resultado Final"
])

# Variables globales (guardar resultados entre secciones)
for key in ["van", "tir", "roi", "payback", "cumplimiento_ambiental"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "cumplimiento_ambiental" else 0

# Función para calcular indicadores financieros
def calcular_indicadores(fcl, tasa_descuento=0.10):
    van = np.npv(tasa_descuento, fcl)
    tir = np.irr(fcl)
    inversion = abs(fcl[0])
    ganancia_neta = sum(fcl[1:])
    roi = (ganancia_neta / inversion) * 100

    acumulado = 0
    payback = None
    for i, valor in enumerate(fcl):
        acumulado += valor
        if acumulado >= 0:
            payback = i
            break
    return van, tir, roi, payback

# Sección 1: Análisis Financiero
if seccion == "Análisis Financiero":
    st.subheader("📊 Análisis Financiero")

    archivo = st.file_uploader("Sube tu archivo Excel con el flujo de caja (debe contener una fila llamada 'FCL')", type=["xlsx"])
    if archivo is not None:
        df = pd.read_excel(archivo, header=None)
        st.write("Vista previa del archivo cargado:")
        st.dataframe(df)

        # Buscar la fila con "FCL"
        fila_fcl = df[df.apply(lambda row: row.astype(str).str.contains("FCL", case=False).any(), axis=1)]
        if not fila_fcl.empty:
            fila_fcl_valores = fila_fcl.iloc[0].dropna().tolist()
            try:
                idx = next(i for i, x in enumerate(fila_fcl_valores) if "FCL" in str(x))
                fcl = [float(str(v).replace("$", "").replace(",", "")) for v in fila_fcl_valores[idx + 1:]]
                st.write("💰 Flujo de caja libre (FCL) identificado:", fcl)

                van, tir, roi, payback = calcular_indicadores(fcl)
                st.session_state.van = van
                st.session_state.tir = tir
                st.session_state.roi = roi
                st.session_state.payback = payback

                st.success("✅ Indicadores calculados automáticamente:")
                st.write(f"**VAN:** ${van:,.2f}")
                st.write(f"**TIR:** {tir*100:.2f}%")
                st.write(f"**ROI:** {roi:.2f}%")
                st.write(f"**Payback:** {payback} años")

            except Exception as e:
                st.error("Error al procesar la fila FCL. Revisa el formato del archivo.")
                st.exception(e)
        else:
            st.error("No se encontró ninguna fila que contenga 'FCL'.")

# Sección 2: Evaluación Ambiental ICMA
elif seccion == "Evaluación Ambiental ICMA":
    st.subheader("🌍 Evaluación Ambiental según ICMA")
    categoria = st.selectbox("Selecciona la categoría ICMA", [
        "Energía renovable",
        "Eficiencia energética",
        "Gestión de residuos",
        "Gestión del agua",
        "Reutilización de suelos",
        "Transporte limpio",
        "Prevención de contaminación",
        "Edificaciones verdes",
        "Conservación de biodiversidad",
        "Agricultura sostenible",
        "Adaptación climática"
    ])

    cumplimiento = 0
    if categoria == "Eficiencia energética":
        energia_total = st.number_input("Consumo energético del proyecto (kWh)", min_value=0.0)
        energia_base = st.number_input("Consumo energético de referencia (kWh)", min_value=0.0)
        if energia_base > 0:
            eficiencia = (1 - energia_total / energia_base) * 100
            cumplimiento = min(eficiencia, 100)
            st.write(f"Eficiencia energética mejorada en un {eficiencia:.2f}%")

    elif categoria == "Gestión del agua":
        agua_total = st.number_input("Agua total utilizada (m³)", min_value=0.0)
        agua_reutilizada = st.number_input("Agua reutilizada (m³)", min_value=0.0)
        if agua_total > 0:
            porcentaje = (agua_reutilizada / agua_total) * 100
            cumplimiento = min(porcentaje, 100)
            st.write(f"Porcentaje de agua reutilizada: {porcentaje:.2f}%")

    elif categoria == "Gestión de residuos":
        residuos_total = st.number_input("Residuos totales generados (kg)", min_value=0.0)
        residuos_reciclados = st.number_input("Residuos reciclados (kg)", min_value=0.0)
        if residuos_total > 0:
            porcentaje = (residuos_reciclados / residuos_total) * 100
            cumplimiento = min(porcentaje, 100)
            st.write(f"Porcentaje de residuos reciclados: {porcentaje:.2f}%")

    elif categoria == "Reutilización de suelos":
        reutiliza = st.selectbox("¿El proyecto contempla reutilización de terrenos ya intervenidos?", ["Sí", "No"])
        cumplimiento = 100 if reutiliza == "Sí" else 0

    elif categoria == "Energía renovable":
        co2_ev = st.number_input("CO₂ evitado (toneladas)", min_value=0.0)
        cumplimiento = min(co2_ev * 10, 100)

    st.session_state.cumplimiento_ambiental = cumplimiento

# Sección 3: Resultado Final
elif seccion == "Resultado Final":
    st.subheader("📈 Resultado Final del Proyecto")

    st.write("### Indicadores Financieros")
    st.write(f"**VAN:** {st.session_state.van}")
    st.write(f"**TIR:** {st.session_state.tir}")
    st.write(f"**ROI:** {st.session_state.roi}")
    st.write(f"**Payback:** {st.session_state.payback}")

    st.write("### Cumplimiento Ambiental")
    st.write(f"**Porcentaje de cumplimiento ambiental:** {st.session_state.cumplimiento_ambiental:.2f}%")

    if all(x is not None for x in [st.session_state.van, st.session_state.tir, st.session_state.roi, st.session_state.payback]):
        cumplimiento_total = st.session_state.cumplimiento_ambiental + 50
        st.write(f"### ✅ Puntaje Total de Cumplimiento: **{cumplimiento_total:.2f}%**")

        if cumplimiento_total >= 80:
            st.success("🎯 El proyecto es altamente viable para la emisión de un Bono Verde.")
        elif cumplimiento_total >= 60:
            st.info("🔎 El proyecto es potencialmente viable, pero necesita mejoras.")
        else:
            st.warning("⚠️ El proyecto no cumple con los requisitos mínimos para un Bono Verde.")

        df_resultado = pd.DataFrame({
            "VAN": [st.session_state.van],
            "TIR": [st.session_state.tir],
            "ROI": [st.session_state.roi],
            "Payback": [st.session_state.payback],
            "Cumplimiento Ambiental (%)": [st.session_state.cumplimiento_ambiental],
            "Puntaje Total (%)": [cumplimiento_total]
        })

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_resultado.to_excel(writer, index=False, sheet_name='Resultado')

        st.download_button(
            label="📥 Descargar resultado en Excel",
            data=output.getvalue(),
            file_name=f"resultado_bono_verde_{datetime.today().date()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("❌ Faltan datos financieros. Vuelve a la sección anterior.")
