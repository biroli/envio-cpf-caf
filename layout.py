import streamlit as st
from config import CAMPOS_DISPONIVEIS

def render_layout():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #0F0F1C;
            color: #F0F0F5;
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

        .stCheckbox>label {
            font-size: 0.95rem;
        }

        .stAlert {
            background-color: #1E1E2F;
            border-left: 4px solid #F39C12;
        }

        .stMarkdown {
            margin-bottom: 1.5rem;
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

    st.markdown("#### 🧾 Exemplo de estrutura da planilha com os campos selecionados:")
    st.dataframe({col: [f"exemplo_{col.lower()}"] for col in colunas})
