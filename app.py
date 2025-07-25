import streamlit as st
from layout import render_layout
from processamento import processar_planilha

st.set_page_config(page_title="Envio de Transações CAF", layout="centered")
render_layout()

auth_token = st.session_state.get("auth_token")
template_id = st.session_state.get("template_id")
arquivo = st.session_state.get("arquivo")

if arquivo and auth_token and template_id:
    processar_planilha(arquivo, auth_token, template_id)