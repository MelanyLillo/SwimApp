import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Registro Natación Avanzado", layout="centered")

distancias = [50, 100, 150, 200, 250, 300, 350, 400]

# --- Estado Inicial ---
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "nadadores" not in st.session_state:
    st.session_state.nadadores = {}

st.title("🏊‍♂️ Registro de Natación Avanzado")

# --- Lista de Nadadores ---
nombres_input = st.text_input("Ingrese nombres de nadadores separados por coma:")
if nombres_input:
    nombres = [n.strip() for n in nombres_input.split(",")]
    for n in nombres:
        if n not in st.session_state.nadadores:
            st.session_state.nadadores[n] = {d: {"tiempo": None, "fb": None} for d in distancias}

# --- Botón Global de Inicio ---
if st.button("🚦 Iniciar Cronómetro Global"):
    st.session_state.start_time = time.time()
    st.success("Cronómetro global iniciado.")

# --- Panel de Nadadores ---
for nadador, registros in st.session_state.nadadores.items():
    st.subheader(f"🏅 {nadador}")
    for d in distancias:
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button(f"Detener {d}m ({nadador})", key=f"stop_{nadador}_{d}"):
                if st.session_state.start_time:
                    elapsed = round(time.time() - st.session_state.start_time, 2)
                    st.session_state.nadadores[nadador][d]["tiempo"] = elapsed
                    st.success(f"{nadador} - {d}m: {elapsed}s")
                else:
                    st.warning("Primero debes iniciar el cronómetro.")
        with col2:
            fb_val = st.number_input(f"FB {d}m ({nadador})", min_value=0.0, step=0.1, format="%.1f", key=f"fb_{nadador}_{d}")
            st.session_state.nadadores[nadador][d]["fb"] = fb_val

# --- Mostrar Resultados ---
mostrar_tabla = True
for nadador, registros in st.session_state.nadadores.items():
    for d in distancias:
        if registros[d]["tiempo"] is None or registros[d]["fb"] is None or registros[d]["fb"] == 0:
            mostrar_tabla = False
            break

if mostrar_tabla:
    st.subheader("📊 Resultados Completos")

    for nadador, registros in st.session_state.nadadores.items():
        st.markdown(f"### 🏊‍♂️ {nadador}")

        resultados = []
        tps_acumulado = 0
        tiempos_100m = []

        for idx, d in enumerate(distancias):
            if idx == 0:
                p50s = registros[d]["tiempo"]
            else:
                p50s = registros[d]["tiempo"] - registros[distancias[idx - 1]]["tiempo"]

            tps_acumulado += p50s
            fb = registros[d]["fb"]

            # Fórmulas 
            v = (50 / p50s) / 86400 * 0.96 if p50s != 0 else 0
            lb = (v * 60) / fb if fb != 0 else 0
            n_ciclos = (50 / lb) - 5 if lb != 0 else 0
            t_ciclo = lb / v if v != 0 else 0
            indice = lb * v

            resultados.append({
                "Metros": d,
                "P50s": round(p50s, 2),
                "Tps": round(tps_acumulado, 2),
                "FB": fb,
                "V": round(v, 6),
                "LB": round(lb, 3),
                "N° Ciclos": round(n_ciclos, 2),
                "T(Ciclo)": round(t_ciclo, 2),
                "IN": round(indice, 3)
            })

            if d % 100 == 0:
                tiempos_100m.append(tps_acumulado)

        # Calcular caídas entre intervalos de 100m
        caidas = [round(tiempos_100m[i] - tiempos_100m[i-1], 2) for i in range(1, len(tiempos_100m))]

        df_resultados = pd.DataFrame(resultados)
        st.dataframe(df_resultados, use_container_width=True)

        # Mostrar intervalos de 100m y caídas
        st.markdown("#### ⏱️ Tiempos por 100m")
        df_100m = pd.DataFrame({
            "Intervalo (m)": [100, 200, 300, 400][:len(tiempos_100m)],
            "Tiempo Acumulado": tiempos_100m
        })
        st.dataframe(df_100m, use_container_width=True)

        st.markdown("#### 📉 Caídas entre intervalos")
        if caidas:
            df_caidas = pd.DataFrame({
                "Intervalo": [f"{(i+2)-1}00m - {(i+1)-1}00m" for i in range(len(caidas))],
                "Caída (s)": caidas
            })
            st.dataframe(df_caidas, use_container_width=True)
else:
    st.info("Cuando todos los tiempos y FB estén completos, se mostrará la tabla de resultados.")
