import streamlit as st
import pandas as pd
import time
import requests
import re

st.set_page_config(page_title="Envio de Transações CAF", layout="centered")

st.markdown("""
<style>
    .main {
        background-color: #0f0f0f;
        color: white;
    }
    h1, h2, h3 {
        color: #00ffd4;
    }
    .css-1v3fvcr {
        background-color: #0f0f0f;
    }
    .stButton>button {
        background-color: #00ffd4;
        color: black;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📤 Envio de Transações para a CAF")

st.subheader("1️⃣ Selecione os campos que estarão na planilha:")
campos = {
    "CPF": st.checkbox("CPF", value=True),
    "NOME": st.checkbox("NOME"),
    "DATA_NASC": st.checkbox("DATA_NASC"),
    "NOME_MAE": st.checkbox("NOME_MAE"),
    "CEP": st.checkbox("CEP"),
    "EMAIL": st.checkbox("EMAIL"),
    "TEL": st.checkbox("TEL"),
    "PLACA": st.checkbox("PLACA"),
    "SELFIE": st.checkbox("SELFIE"),
    "FRENTE_DOC": st.checkbox("FRENTE_DOC"),
    "VERSO_DOC": st.checkbox("VERSO_DOC"),
}

st.subheader("📄 Exemplo da planilha esperada:")
colunas_selecionadas = [campo for campo, marcado in campos.items() if marcado]
st.code("\t".join(colunas_selecionadas), language="text")

st.subheader("2️⃣ Informações da Requisição")
auth_token = st.text_input("Authorization (coloque o token completo):", type="password")
template_id = st.text_input("ID do Modelo (templateId):")

col1, col2 = st.columns(2)
with col1:
    frequencia = st.number_input("Quantidade de requisições", min_value=1, value=2)
with col2:
    unidade_tempo = st.selectbox("Por...", options=["segundo", "minuto"])

intervalo = 1 / frequencia if unidade_tempo == "segundo" else 60 / frequencia

st.subheader("3️⃣ Upload da planilha")
arquivo = st.file_uploader("Envie um arquivo Excel (.xlsx)", type=["xlsx"])

interromper_btn = st.empty()
interromper = False
resultados = []

def reset_interromper():
    global interromper
    interromper = False

if arquivo and auth_token and template_id:
    df = pd.read_excel(arquivo)
    total = len(df)
    progresso = st.progress(0, text="Aguardando início...")
    log_area = st.empty()

    if st.button("🚀 Enviar Transações"):
        reset_interromper()
        show_stop = True

        for i, linha in df.iterrows():
            if show_stop:
                if interromper_btn.button("🛑 Interromper Envio", key="btn_stop"):
                    interromper = True
                    show_stop = False

            if interromper:
                st.warning("Envio interrompido pelo usuário.")
                break

            payload = {"templateId": template_id, "attributes": {}, "files": []}
            cpf_log = ""

            for campo in campos:
                if campo in linha and not pd.isna(linha[campo]):
                    valor = str(linha[campo]).strip()
                    if campo == "CPF":
                        valor = re.sub(r"\D", "", valor).zfill(11)
                        payload["attributes"]["cpf"] = valor
                        cpf_log = valor
                    elif campo == "NOME":
                        payload["attributes"]["name"] = valor
                    elif campo == "DATA_NASC":
                        payload["attributes"]["birthDate"] = valor
                    elif campo == "NOME_MAE":
                        payload["attributes"]["motherName"] = valor
                    elif campo == "CEP":
                        payload["attributes"]["cep"] = valor
                    elif campo == "EMAIL":
                        payload["attributes"]["email"] = valor
                    elif campo == "TEL":
                        payload["attributes"]["phoneNumber"] = valor
                    elif campo == "PLACA":
                        payload["attributes"]["plate"] = valor
                    elif campo == "SELFIE":
                        payload["files"].append({"data": valor, "type": "SELFIE"})
                    elif campo in ["FRENTE_DOC", "VERSO_DOC"]:
                        payload["files"].append({"data": valor, "type": "OTHERS"})

            try:
                response = requests.post(
                    url="https://api.combateafraude.com/v1/transactions?origin=TRUST",
                    headers={
                        "Authorization": auth_token,
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                status = f"{response.status_code} | {response.reason}"
                log_area.text(f"{i+1}/{total} → CPF: {cpf_log} → {status}")
                resultados.append({"CPF": cpf_log, "Status": response.status_code, "Resultado": response.text})
            except Exception as e:
                erro = str(e)
                log_area.text(f"{i+1}/{total} → CPF: {cpf_log} → ERRO: {erro}")
                resultados.append({"CPF": cpf_log, "Status": "ERROR", "Resultado": erro})

            progresso.progress((i+1)/total, text=f"{i+1} de {total} enviados")
            time.sleep(intervalo)

        st.success("✅ Processamento concluído.")

        if resultados:
            st.subheader("📄 Baixar Relatório Final")
            df_result = pd.DataFrame(resultados)
            csv = df_result.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Baixar .csv com resultado", data=csv, file_name="resumo_transacoes.csv", mime="text/csv")
