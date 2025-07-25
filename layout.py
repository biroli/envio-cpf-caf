import streamlit as st
from config import CAMPOS_DISPONIVEIS


def render_layout():
    st.markdown("## 1️⃣ Selecione os campos que estarão na planilha:")

    if "campos_selecionados" not in st.session_state:
        st.session_state.campos_selecionados = list(CAMPOS_DISPONIVEIS.keys())

    colunas = list(CAMPOS_DISPONIVEIS.keys())

    selecionados = st.multiselect(
        "Campos disponíveis:", options=colunas, default=st.session_state.campos_selecionados, key="campos_selecionados"
    )

    if not selecionados:
        st.warning("Selecione pelo menos um campo.")

    st.markdown("### 📄 Exemplo da planilha esperada:")
    st.code("\t".join(selecionados), language="text")

    st.markdown("## 2️⃣ Informações da Requisição")

    st.text_input("Authorization (coloque o token completo):", type="password", key="auth_token")
    st.text_input("ID do Modelo (templateId):", key="template_id")

    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Quantidade de requisições", min_value=1, value=1, step=1, key="frequencia")
    with col2:
        st.selectbox("Por...", options=["segundo", "minuto"], key="unidade_tempo")

    st.markdown("## 3️⃣ Upload da planilha")
    st.file_uploader("Envie um arquivo Excel (.xlsx)", type=["xlsx"], key="arquivo")

    if st.session_state.get("enviando"):
        if st.button("🛑 Interromper envio"):
            st.session_state.enviar = False
            st.rerun()
    else:
        if st.button("🚀 Iniciar envio"):
            st.session_state.enviar = True
            st.rerun()
