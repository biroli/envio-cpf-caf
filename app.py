import streamlit as st
from layout import render_layout
from processamento import processar_planilha

st.set_page_config(page_title="Envio de Transações CAF", layout="centered")

if "iniciar_envio" not in st.session_state:
    st.session_state["iniciar_envio"] = False
if "interromper" not in st.session_state:
    st.session_state["interromper"] = False
if "envio_em_andamento" not in st.session_state:
    st.session_state["envio_em_andamento"] = False

render_layout()

if st.session_state["iniciar_envio"]:
    processar_planilha()
