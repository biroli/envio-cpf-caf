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
from streamlit.components.v1 import html

# Campo com label acima, mesmo estilo dos outros, e botão de olho funcional
st.markdown("""
<style>
    .password-wrapper {
        position: relative;
    }
    .password-wrapper input {
        padding-right: 40px !important;
    }
    .toggle-eye {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        cursor: pointer;
        color: gray;
    }
</style>
<div class="password-wrapper">
  <input type="password" id="auth_field" placeholder="Authorization (coloque o token completo)" 
         class="stTextInput" oninput="setAuthValue(this.value)">
  <span class="toggle-eye" onclick="togglePassword()">👁️</span>
</div>
<script>
  function togglePassword() {
    var input = document.getElementById("auth_field");
    input.type = input.type === "password" ? "text" : "password";
  }
  function setAuthValue(val) {
    window.parent.postMessage({type: "streamlit:setComponentValue", value: val}, "*");
  }
</script>
""", unsafe_allow_html=True)
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

interromperamento = st.empty()
interromper = False

def reset_interromper():
    global interromper
    interromper = False

if arquivo and auth_token and template_id:
    df = pd.read_excel(arquivo)
    total = len(df)
    progresso = st.progress(0, text="Aguardando início...")
    log_area = st.empty()

    if interromperamento.button("🛑 Interromper Envio"):
        interromper = True

    if st.button("🚀 Enviar Transações"):
        reset_interromper()
        for i, linha in df.iterrows():
            if interromper:
                st.warning("Envio interrompido pelo usuário.")
                break

            payload = {"templateId": template_id, "attributes": {}, "files": []}

            for campo in campos:
                if campo in linha and not pd.isna(linha[campo]):
                    valor = str(linha[campo]).strip()
                    if campo == "CPF":
                        valor = re.sub(r"\D", "", valor).zfill(11)
                        payload["attributes"]["cpf"] = valor
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
                log_area.text(f"{i+1}/{total} → Status: {response.status_code} | CPF: {payload['attributes'].get('cpf', '')}")
            except Exception as e:
                log_area.text(f"{i+1}/{total} → Erro: {str(e)}")

            progresso.progress((i+1)/total, text=f"{i+1} de {total} enviados")
            time.sleep(intervalo)

        st.success("✅ Processamento concluído.")
