import streamlit as st
from config import CAMPOS_DISPONIVEIS

def render_layout():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    .main {
        background-color: #0F0F1C;
        color: #F0F0F5;
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        color: #7B61FF;
        font-weight: 600;
    }

    .stButton>button {
        background-color: #7B61FF;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 600;
        transition: background-color 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #5C45E3;
    }

    .stAlert {
        background-color: #1E1E2F;
        border-left: 4px solid #F39C12;
    }
</style>
    """, unsafe_allow_html=True)

    st.title("📤 Envio de Transações para a CAF")

    st.subheader("1️⃣ Selecione os campos que estarão na planilha (obrigatório):")
    for campo in CAMPOS_DISPONIVEIS:
        if campo not in st.session_state:
            st.session_state[campo] = campo == "CPF"
        st.session_state[campo] = st.checkbox(campo, value=st.session_state[campo])

    colunas = [c for c in CAMPOS_DISPONIVEIS if st.session_state.get(c)]

    if not colunas:
        st.warning("⚠️ Você deve selecionar pelo menos um campo para continuar.")
        return  # Para a execução aqui se não tiver campo selecionado

    st.subheader("📄 Copie e cole na primeira linha da sua planilha:")
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
