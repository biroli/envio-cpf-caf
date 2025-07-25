import streamlit as st
from config import CAMPOS_DISPONIVEIS

def render_layout():
    st.title("📤 Envio de Transações para a CAF")

    st.subheader("1️⃣ Selecione os campos que estarão na planilha:")
    for campo in CAMPOS_DISPONIVEIS:
        st.session_state[campo] = st.checkbox(campo, value=(campo == "CPF"))

    st.subheader("📄 Exemplo da planilha esperada:")
    campos_selecionados = [campo for campo in CAMPOS_DISPONIVEIS if st.session_state.get(campo)]
    st.code("\t".join(campos_selecionados), language="text")

    st.subheader("2️⃣ Informações da Requisição")
    st.text_input("Authorization (coloque o token completo):", type="password", key="auth_token")
    st.text_input("ID do Modelo (templateId):", key="template_id")

    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Quantidade de requisições", min_value=1, value=2, key="frequencia")
    with col2:
        st.selectbox("Por...", options=["segundo", "minuto"], key="unidade_tempo")

    st.subheader("3️⃣ Upload da planilha")
    st.file_uploader("Envie um arquivo Excel (.xlsx)", type=["xlsx"], key="arquivo")

    if not st.session_state["enviar"]:
        if st.button("🚀 Iniciar envio"):
            st.session_state["enviar"] = True
            st.experimental_rerun()
    else:
        if st.button("🛑 Interromper envio"):
            st.session_state["interromper"] = True
