
import streamlit as st
import pandas as pd
import requests
import time
import re

st.set_page_config(page_title="Envio de CPFs para a CAF", layout="centered")

st.title("📤 Envio de CPFs para a API da CAF")
st.markdown("Envie uma planilha com os CPFs (sem título) na coluna **A**. O script irá normalizar os CPFs, realizar as requisições e exibir os resultados.")

uploaded_file = st.file_uploader("📄 Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"])
auth_token = st.text_input("🔐 Authorization (Bearer token)")
template_id = st.text_input("📌 ID do modelo de consulta (templateId)")
rps = st.number_input("🚀 Requisições por segundo (RPS)", min_value=0.1, max_value=10.0, value=2.0, step=0.1)

def normaliza_cpf(cpf):
    if pd.isna(cpf):
        return ""
    return re.sub(r"\D", "", str(cpf)).zfill(11)

if st.button("🚀 Iniciar envio"):
    if uploaded_file and auth_token and template_id:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file, header=None)
            else:
                df = pd.read_excel(uploaded_file, header=None)
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            st.stop()

        cpfs = df.iloc[:, 0].dropna().apply(normaliza_cpf).tolist()
        total = len(cpfs)
        delay = 1 / rps
        resultados = []

        st.info(f"📦 {total} CPFs detectados. Enviando {rps:.1f} requisições por segundo...")

        progress_bar = st.progress(0)
        log_area = st.empty()

        for i, cpf in enumerate(cpfs):
            payload = {
                "templateId": template_id,
                "attributes": {
                    "cpf": cpf
                }
            }

            try:
                response = requests.post(
                    "https://api.combateafraude.com/v1/transactions?origin=TRUST",
                    headers={
                        "Authorization": auth_token,
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                status = response.status_code
                text = response.text
            except Exception as e:
                status = "ERROR"
                text = str(e)

            resultados.append({
                "cpf": cpf,
                "status": status,
                "resposta": text
            })

            log_area.text(f"[{i+1}/{total}] CPF: {cpf} | Status: {status}")
            progress_bar.progress((i+1) / total)
            time.sleep(delay)

        df_resultado = pd.DataFrame(resultados)
        st.success("✅ Processamento finalizado.")
        st.dataframe(df_resultado)

        from io import BytesIO
        output = BytesIO()
        df_resultado.to_excel(output, index=False)
        st.download_button("📥 Baixar resultado (.xlsx)", data=output.getvalue(), file_name="resultado_envio_cpf.xlsx")
    else:
        st.warning("Por favor, preencha todos os campos e envie um arquivo.")
