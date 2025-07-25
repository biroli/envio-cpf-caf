import streamlit as st
from config import init_session_state

def render_layout():
    init_session_state()

    st.markdown("<h1 style='font-size: 2.5rem;'>📤 Envio de Transações para a CAF</h1>", unsafe_allow_html=True)

    st.markdown("### 1️⃣ Selecione os campos que estarão na planilha:")
    opcoes = ["CPF", "NOME", "DATA_NASC", "NOME_MAE", "CEP", "EMAIL", "TEL", "PLACA", "SELFIE", "FRENTE_DOC", "VERSO_DOC"]
    campos = st.multiselect("Campos disponíveis:", options=opcoes, default=opcoes)
    st.session_state["campos_selecionados"] = campos

    st.markdown("### 🧾 Exemplo da planilha esperada:")
    st.code("\t".join(campos), language="text")

    st.markdown("### 2️⃣ Informações da Requisição")
    st.session_state["auth_token"] = st.text_input("Authorization (coloque o token completo):", type="password")
    st.session_state["template_id"] = st.text_input("ID do Modelo (templateId):")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state["frequencia"] = st.number_input("Quantidade de requisições", min_value=1, value=2)
    with col2:
        st.session_state["unidade_tempo"] = st.selectbox("Por...", options=["segundo", "minuto"])

    st.markdown("### 3️⃣ Upload da planilha")
    st.session_state["arquivo"] = st.file_uploader("Envie um arquivo Excel (.xlsx)", type=["xlsx"])

    if st.session_state["arquivo"] and st.session_state["auth_token"] and st.session_state["template_id"]:
        if st.button("🚀 Iniciar envio"):
            st.session_state["iniciar_envio"] = True
            st.experimental_rerun()
