import streamlit as st
from layout import render_layout
from processamento import processar_planilha

st.set_page_config(page_title="Envio de Transações CAF", layout="centered")

# Inicialização do estado
if "interromper" not in st.session_state:
    st.session_state["interromper"] = False

if "enviando" not in st.session_state:
    st.session_state["enviando"] = False

# Renderiza o layout e coleta os dados
dados = render_layout()

# Se o botão "Iniciar envio" for clicado
if dados.get("start"):
    st.session_state["enviando"] = True
    st.session_state["interromper"] = False
    processar_planilha(
        arquivo=st.session_state["arquivo"],
        auth_token=st.session_state["auth_token"],
        template_id=st.session_state["template_id"],
        intervalo=dados["intervalo"],
        campos=dados["campos"],
        interromper_key="interromper"
    )
