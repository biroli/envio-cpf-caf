import streamlit as st
import pandas as pd
import requests
import time
import io
from datetime import datetime

st.set_page_config(
    page_title="Envio de Transações CAF",
    page_icon="🚀",
    layout="centered"
)

st.title("Envio de Transações em Lote para a CAF")

with st.expander("ℹ️ Instruções"):
    st.markdown("""
    - **Monte sua planilha** conforme os campos que deseja utilizar.
    - **Nomes das colunas obrigatoriamente devem ser**:
        - `CPF`, `NOME`, `DATA_NASC`, `NOME_MAE`, `CEP`, `EMAIL`, `TEL`, `PLACA`, `SELFIE`, `FRENTE_DOC`, `VERSO_DOC`
    - Campos com links de imagem (selfie/docs) devem ser URLs acessíveis publicamente.
    """)

# Seleção de campos para a planilha
st.subheader("1. Selecione os campos que serão usados na planilha")
campos_disponiveis = [
    "CPF", "NOME", "DATA_NASC", "NOME_MAE", "CEP", "EMAIL", "TEL", "PLACA",
    "SELFIE", "FRENTE_DOC", "VERSO_DOC"
]
campos_selecionados = []
st.markdown("**Campos Disponíveis:**")
col1, col2, col3 = st.columns(3)
for i, campo in enumerate(campos_disponiveis):
    if i % 3 == 0:
        if col1.checkbox(campo): campos_selecionados.append(campo)
    elif i % 3 == 1:
        if col2.checkbox(campo): campos_selecionados.append(campo)
    else:
        if col3.checkbox(campo): campos_selecionados.append(campo)

if campos_selecionados:
    st.markdown("**Exemplo de estrutura esperada da planilha:**")
    exemplo_df = pd.DataFrame(columns=campos_selecionados)
    st.dataframe(exemplo_df.head(1), use_container_width=True)

# Upload da planilha
st.subheader("2. Faça o upload da planilha preenchida")
arquivo = st.file_uploader("Envie sua planilha Excel (.xlsx)", type=["xlsx"])

# Parâmetros da requisição
st.subheader("3. Parâmetros da Transação")
auth_token = st.text_input("Authorization (ex: Bearer xxxxxx...)", type="password")
template_id = st.text_input("ID do Template")
modo_envio = st.radio("Frequência de envio", ["Por segundo", "Por minuto"], horizontal=True)
qtd_envios = st.number_input("Quantidade de requisições por unidade de tempo selecionada", min_value=1, step=1, value=1)

# Botões de controle
if 'interromper' not in st.session_state:
    st.session_state.interromper = False
if 'enviando' not in st.session_state:
    st.session_state.enviando = False

# Processamento
erros = []
resumo_final = []

def tratar_cpf(cpf):
    if pd.isna(cpf): return ""
    cpf = ''.join(filter(str.isdigit, str(cpf)))
    return cpf.zfill(11)

def enviar_transacoes():
    df = pd.read_excel(arquivo)
    total = len(df)
    delay = 60/qtd_envios if modo_envio == "Por minuto" else 1/qtd_envios

    st.session_state.enviando = True
    barra = st.progress(0)

    for i, row in df.iterrows():
        if st.session_state.interromper:
            st.warning("Envio interrompido pelo usuário.")
            break

        payload = {
            "templateId": template_id,
            "attributes": {},
            "files": [],
            "metadata": {"linha_excel": i+2}
        }

        for campo in campos_selecionados:
            valor = str(row[campo]) if campo in row and pd.notna(row[campo]) else None
            if campo == "CPF":
                payload["attributes"]["cpf"] = tratar_cpf(valor)
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
            elif campo == "SELFIE" and valor:
                payload["files"].append({"data": valor, "type": "SELFIE"})
            elif campo in ["FRENTE_DOC", "VERSO_DOC"] and valor:
                payload["files"].append({"data": valor, "type": "OTHERS"})

        try:
            resp = requests.post(
                url="https://api.combateafraude.com/v1/transactions?origin=TRUST",
                headers={"Authorization": auth_token, "Content-Type": "application/json"},
                json=payload
            )
            resultado = resp.json()
            resumo_final.append({"CPF": payload["attributes"].get("cpf", ""), "status_code": resp.status_code, "response": resultado})
        except Exception as e:
            resumo_final.append({"CPF": payload["attributes"].get("cpf", ""), "status_code": "erro", "response": str(e)})

        barra.progress((i+1)/total)
        time.sleep(delay)

    st.success("Processo finalizado.")
    st.session_state.enviando = False
    st.session_state.interromper = False

    df_resumo = pd.DataFrame(resumo_final)
    st.download_button(
        label="📂 Baixar Relatório Final",
        data=io.BytesIO(df_resumo.to_excel(index=False, engine='openpyxl')),
        file_name=f"resumo_envio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Botão de envio
if st.button("🚀 Enviar Transações") and arquivo:
    enviar_transacoes()

# Botão de interromper envio (só aparece durante o envio)
if st.session_state.get("enviando"):
    if st.button("🛑 Interromper Envio"):
        st.session_state.interromper = True
