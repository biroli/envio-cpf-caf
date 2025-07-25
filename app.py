import streamlit as st
from layout import render_layout
from processamento import processar_planilha

st.set_page_config(page_title="Envio de Transações para a CAF", layout="centered", page_icon="📤")

render_layout()

if "iniciar_envio" in st.session_state and st.session_state["iniciar_envio"]:
    processar_planilha(
        arquivo=st.session_state["arquivo"],
        auth_token=st.session_state["auth_token"],
        template_id=st.session_state["template_id"],
        frequencia=st.session_state["frequencia"],
        unidade_tempo=st.session_state["unidade_tempo"],
        campos_selecionados=st.session_state["campos_selecionados"]
    )
