import streamlit as st
from config import CAMPOS_DISPONIVEIS

def render_layout():
    st.markdown("""
    <style>
        .main { background-color: #0f0f0f; color: white; }
        h1, h2, h3 { color: #00ffd4; }
        .stButton>button {
            background-color: #00ffd4; color: black; font-weight: bold;
            border-radius: 8px; padding: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("📤 Envio de Transações para a CAF")

    st.subheader("1️⃣ Selecione os campos que estarão na planilha:")
    for campo in CAMPOS_DISPONIVEIS:
        st.session_state[campo] = st.checkbox(campo, value=(campo == "CPF"))

    st.subheader("📄 Exemplo da planilha esperada:")
    colunas = [c for c in CAMPOS_DISPONIVEIS if st.session_state.get(c)]
    st.code("\t".join(colunas), language="text")

    st.subheader("2️⃣ Informações da Requisição")
    st.session_state["auth_token"] = st.text_input("Authorization (coloque o token completo):", type="password")
    st.session_state["template_id"] = st.text_input("ID do Modelo (templateId):")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state["frequencia"] = st.number_input("Quantidade de requisições", min_value=1, value=2)
    with col2:
        st.session_state["unidade_tempo"] = st.selectbox("Por...", options=["segundo", "minuto"])

    st.subheader("3️⃣ Upload da planilha")
    st.session_state["arquivo"] = st.file_uploader("Envie um arquivo Excel (.xlsx)", type=["xlsx"])

    st.session_state["iniciar_envio"] = st.button("🚀 Iniciar envio")
