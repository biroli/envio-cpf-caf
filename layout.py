import streamlit as st
from config import CAMPOS_DISPONIVEIS

def render_layout():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

        html, body, .main {
            background-color: #0F0F1C;
            color: #F0F0F5;
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: linear-gradient(145deg, #0F0F1C 0%, #1A133F 100%) !important;
        }

        h1, h2, h3 {
            color: #7B61FF;
            font-weight: 600;
        }

        .step-card {
            background-color: #1B1B2E;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.3);
            margin-bottom: 2rem;
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

        .logo-container {
            text-align: center;
            margin-bottom: 30px;
        }

        .logo-container img {
            max-height: 60px;
        }

        .stAlert {
            background-color: #1E1E2F;
            border-left: 4px solid #F39C12;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="logo-container"><img src="https://uploads-ssl.webflow.com/6127f0cf7b3c241b35b82ef5/612804c6435c0210a842b9b6_caf-logo-white.svg" alt="CAF Logo"/></div>',
        unsafe_allow_html=True
    )

    with st.container():
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.subheader("1️⃣ Selecione os campos que estarão na planilha (obrigatório):")
        for campo in CAMPOS_DISPONIVEIS:
            if campo not in st.session_state:
                st.session_state[campo] = campo == "CPF"
            st.session_state[campo] = st.checkbox(campo, value=st.session_state[campo])
        colunas = [c for c in CAMPOS_DISPONIVEIS if st.session_state.get(c)]

        if not colunas:
            st.warning("⚠️ Você deve selecionar pelo menos um campo para continuar.")
            st.markdown('</div>', unsafe_allow_html=True)
            return

        st.markdown("#### 📄 Copie e cole na primeira linha da sua planilha:")
        st.code("\t".join(colunas), language="text")
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.subheader("2️⃣ 🔐 Informações da Requisição")
        st.session_state["auth_token"] = st.text_input("🔑 Authorization (coloque o token completo):", type="password")
        st.session_state["template_id"] = st.text_input("🧬 ID do Modelo (templateId):")

        col1, col2 = st.columns(2)
        with col1:
            st.session_state["frequencia"] = st.number_input("📊 Quantidade de requisições", min_value=1, value=2)
        with col2:
            st.session_state["unidade_tempo"] = st.selectbox("⏱️ Por...", options=["segundo", "minuto"])
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.subheader("3️⃣ 🧾 Upload da planilha")
        st.session_state["arquivo"] = st.file_uploader("📎 Envie um arquivo Excel (.xlsx)", type=["xlsx"])
        st.session_state["iniciar_envio"] = st.button("🚀 Iniciar envio")
        st.markdown('</div>', unsafe_allow_html=True)