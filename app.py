import streamlit as st
from layout import render_layout
from processamento import processar_planilha

st.set_page_config(page_title="Envio de Transações CAF", layout="centered")

# Inicializa os estados obrigatórios
for key in ["iniciar_envio", "envio_em_andamento", "interromper", "arquivo", "auth_token", "template_id"]:
    if key not in st.session_state:
        st.session_state[key] = None if key == "arquivo" else False

# Renderiza a interface
render_layout()

# Só chama processamento se todos os campos estiverem preenchidos
if (
    st.session_state["iniciar_envio"]
    and st.session_state["arquivo"]
    and st.session_state["auth_token"]
    and st.session_state["template_id"]
):
    processar_planilha(
        arquivo=st.session_state["arquivo"],
        auth_token=st.session_state["auth_token"],
        template_id=st.session_state["template_id"]
    )
