import streamlit as st
from layout import render_layout
from processamento import processar_planilha

st.set_page_config(page_title="Envio de Transações CAF", layout="centered")

# Inicializar os estados se não existirem
for key in ["iniciar_envio", "envio_em_andamento", "interromper"]:
    if key not in st.session_state:
        st.session_state[key] = False

# Renderiza interface
render_layout()

# Processa planilha se necessário
processar_planilha(
    arquivo=st.session_state.get("arquivo"),
    auth_token=st.session_state.get("auth_token"),
    template_id=st.session_state.get("template_id")
)
