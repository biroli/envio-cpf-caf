
import streamlit as st
import pandas as pd
import time
import requests

# Configurações iniciais
st.set_page_config(page_title="Envio de Transações CAF", layout="wide")

# Sidebar de preferências
with st.sidebar:
    st.markdown("### ⚙️ Preferências")
    idioma = st.radio("Idioma / Language", ["Português", "English"])
    tema = st.radio("Tema", ["Claro", "Escuro"])
    if tema == "Escuro":
        st.markdown("""
            <style>
            body, .stApp {
                background-color: #111 !important;
                color: #eee !important;
            }
            </style>
        """, unsafe_allow_html=True)

# Título principal
st.title("📄 Envio de Transações - CAF")

st.markdown("#### Selecione os campos que estarão na sua planilha")

# Campos disponíveis
campos_disponiveis = {
    "CPF": "cpf",
    "NOME": "name",
    "DATA_NASC": "birthDate",
    "NOME_MAE": "motherName",
    "CEP": "cep",
    "EMAIL": "email",
    "TEL": "phoneNumber",
    "PLACA": "plate",
    "SELFIE": "selfie",
    "FRENTE_DOC": "frente_doc",
    "VERSO_DOC": "verso_doc"
}

# Seletor de campos
col1, col2, col3 = st.columns(3)
selecionados = []
for i, campo in enumerate(campos_disponiveis):
    with [col1, col2, col3][i % 3]:
        if st.checkbox(campo, value=True if campo == "CPF" else False):
            selecionados.append(campo)

# Exemplo de planilha
if selecionados:
    st.markdown("#### Exemplo de estrutura esperada da planilha")
    exemplo = pd.DataFrame({campo: ["exemplo"] for campo in selecionados})
    st.dataframe(exemplo, use_container_width=True)

st.markdown("---")
st.markdown("### 📤 Envio de arquivo e dados da requisição")

# Upload da planilha
arquivo = st.file_uploader("Faça upload da planilha com os dados", type=["xlsx", "csv"])

# Inputs adicionais
authorization = st.text_input("Authorization (cole o token completo)", type="password")
template_id = st.text_input("ID do modelo de consulta (templateId)")
frequencia = st.number_input("Quantidade de requisições", min_value=1, value=2)
modo = st.radio("Tempo entre requisições", ["Por segundo", "Por minuto"])

# Processar planilha e enviar
if st.button("🚀 Enviar Transações") and arquivo and authorization and template_id:
    if arquivo.name.endswith(".csv"):
        df = pd.read_csv(arquivo)
    else:
        df = pd.read_excel(arquivo)

    col_map = {campo: campos_disponiveis[campo] for campo in selecionados}
    df.columns = df.columns.str.strip().str.upper()
    df = df[[col for col in df.columns if col in selecionados]]

    total = len(df)
    sucesso = 0

    barra = st.progress(0)
    status_area = st.empty()

    for i, row in df.iterrows():
        payload = {"templateId": template_id}

        attributes = {}
        files = []

        for col in selecionados:
            valor = str(row.get(col, "")).strip()
            if col == "CPF":
                valor = valor.replace(".", "").replace("-", "").zfill(11)
            if col == "SELFIE":
                files.append({"data": valor, "type": "SELFIE"})
            elif col == "FRENTE_DOC":
                files.append({"data": valor, "type": "OTHERS"})
            elif col == "VERSO_DOC":
                files.append({"data": valor, "type": "OTHERS"})
            elif col in campos_disponiveis:
                key = campos_disponiveis[col]
                if key not in ["selfie", "frente_doc", "verso_doc"]:
                    attributes[key] = valor

        if attributes:
            payload["attributes"] = attributes
        if files:
            payload["files"] = files

        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json"
        }

        r = requests.post("https://api.combateafraude.com/v1/transactions?origin=TRUST",
                          json=payload, headers=headers)

        if r.status_code == 200 or r.status_code == 201:
            sucesso += 1

        barra.progress((i+1)/total)
        status_area.markdown(f"**{i+1}/{total} enviados** - Status: {r.status_code}")

        delay = 60/frequencia if modo == "Por minuto" else 1/frequencia
        time.sleep(delay)

    st.success(f"✅ Envio finalizado: {sucesso} de {total} enviados com sucesso.")
