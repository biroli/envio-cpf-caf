import streamlit as st
from layout import render_layout
from processamento import processar_planilha

st.set_page_config(page_title="Envio de Transações CAF", layout="centered")

if "enviar" not in st.session_state:
    st.session_state["enviar"] = False
if "interromper" not in st.session_state:
    st.session_state["interromper"] = False

render_layout()

if st.session_state["enviar"] and not st.session_state["interromper"]:
    processar_planilha()
