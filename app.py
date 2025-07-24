import streamlit as st
import pandas as pd
import time
import requests
from io import BytesIO

st.set_page_config(page_title="Envio de Transações CAF", layout="centered")

st.title("🚀 Envio de Transações CAF")

# Sessão de estado para controle de envio
if "interromper" not in st.session_state:
    st.session_state.interromper = False
if "enviando" not in st.session_state:
    st.session_state.enviando = False

st.markdown("### Envie um arquivo Excel (.xlsx)")
uploaded_file = st.file_uploader("Drag and drop file here", type=["xlsx"])

# Inputs
authorization = st.text_input("Cole seu token Authorization completo (começando com Bearer...)", type="password")
template_id = st.text_input("Informe o ID do modelo de consulta (templateId)")
frequencia = st.number_input("Quantas requisições deseja enviar por vez?", min_value=1, value=1)
unidade = st.selectbox("Intervalo de tempo entre requisições", ["por segundo", "por minuto"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if "CPF" not in df.columns:
        st.error("A coluna obrigatória 'CPF' não foi encontrada na planilha.")
    else:
        # Mostrar botão de envio
        if st.button("🚀 Enviar Transações"):
            st.session_state.interromper = False
            st.session_state.enviando = True

            # Calcular delay entre envios
            delay = 60 / frequencia if unidade == "por minuto" else 1 / frequencia

            responses = []
            total = len(df)
            progress = st.progress(0)
            status_area = st.empty()

            # Botão de interrupção visível durante envio
            with st.container():
                if st.button("🛑 Interromper Envio", key=f"btn_stop_{int(time.time())}"):
                    st.session_state.interromper = True

            for idx, row in df.iterrows():
                if st.session_state.interromper:
                    status_area.error("Envio interrompido pelo usuário.")
                    break

                cpf = str(row["CPF"]).zfill(11).replace(".", "").replace("-", "").replace(" ", "")
                payload = {
                    "templateId": template_id,
                    "attributes": {"cpf": cpf},
                }

                try:
                    response = requests.post(
                        "https://api.combateafraude.com/v1/transactions?origin=TRUST",
                        headers={"Authorization": authorization, "Content-Type": "application/json"},
                        json=payload,
                    )
                    status = f"{response.status_code} | {response.reason}"
                except Exception as e:
                    status = f"ERROR | {e}"

                responses.append({
                    "CPF": cpf,
                    "Status": status
                })

                status_area.info(f"{idx + 1}/{total} → CPF: {cpf} → {status}")
                progress.progress((idx + 1) / total)
                time.sleep(delay)

            # Gerar relatório CSV final
            st.success("✅ Envio concluído!")
            df_resultado = pd.DataFrame(responses)
            buffer = BytesIO()
            df_resultado.to_csv(buffer, index=False)
            buffer.seek(0)
            st.download_button(
                label="📥 Baixar relatório final (.csv)",
                data=buffer,
                file_name="relatorio_envio.csv",
                mime="text/csv"
            )

            st.session_state.enviando = False
