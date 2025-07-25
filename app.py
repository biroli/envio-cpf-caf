import streamlit as st
from layout import render_layout
from processamento import processar_planilha

st.set_page_config(page_title="Envio de Transações CAF", layout="centered")

# Inicializa estados padrão
st.session_state.setdefault("iniciar_envio", False)
st.session_state.setdefault("envio_em_andamento", False)
st.session_state.setdefault("interromper", False)
st.session_state.setdefault("arquivo", None)
st.session_state.setdefault("auth_token", "")
st.session_state.setdefault("template_id", "")
st.session_state.setdefault("frequencia", 1)
st.session_state.setdefault("unidade_tempo", "segundo")

# Renderiza a interface gráfica
render_layout()

# Se o botão de envio foi pressionado, validamos os campos
if st.session_state.get("botao_iniciar"):
    if (
        st.session_state["arquivo"] is not None and
        st.session_state["auth_token"] and
        st.session_state["template_id"]
    ):
        st.session_state["iniciar_envio"] = True
        del st.session_state["botao_iniciar"]
        st.experimental_rerun()
    else:
        st.warning("⚠️ Preencha todos os campos antes de iniciar o envio.")

# Executa o envio somente se tudo estiver preenchido e autorizado
if st.session_state["iniciar_envio"]:
    processar_planilha(
        arquivo=st.session_state["arquivo"],
        auth_token=st.session_state["auth_token"],
        template_id=st.session_state["template_id"]
    )
