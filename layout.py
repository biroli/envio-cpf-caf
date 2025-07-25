import streamlit as st
import time

def render_layout():
    st.title("📤 Envio de Transações para a CAF")

    st.subheader("1️⃣ Selecione os campos que estarão na planilha:")
    campos_disponiveis = ["CPF", "NOME", "DATA_NASC", "NOME_MAE", "CEP", "EMAIL", "TEL", "PLACA", "SELFIE", "FRENTE_DOC", "VERSO_DOC"]
    campos = st.multiselect("Campos disponíveis:", campos_disponiveis, default=campos_disponiveis)

    st.subheader("📄 Exemplo da planilha esperada:")
    st.code("\t".join(campos), language="text")

    st.subheader("2️⃣ Informações da Requisição")
    auth_token = st.text_input("Authorization (coloque o token completo):", type="password", key="auth_token")
    template_id = st.text_input("ID do Modelo (templateId):", key="template_id")

    col1, col2 = st.columns(2)
    with col1:
        frequencia = st.number_input("Quantidade de requisições", min_value=1, value=2)
    with col2:
        unidade_tempo = st.selectbox("Por...", options=["segundo", "minuto"])

    intervalo = 1 / frequencia if unidade_tempo == "segundo" else 60 / frequencia

    st.subheader("3️⃣ Upload da planilha")
    arquivo = st.file_uploader("Envie um arquivo Excel (.xlsx)", type=["xlsx"], key="arquivo")

    start = st.button("🚀 Iniciar envio")

    # Exibe botão de interrupção se estiver enviando
    if st.session_state.get("enviando", False):
        if st.button("🛑 Interromper envio"):
            st.session_state["interromper"] = True

    return {
        "campos": campos,
        "intervalo": intervalo,
        "start": start
    }
