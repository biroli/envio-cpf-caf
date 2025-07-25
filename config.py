import streamlit as st

def init_session_state():
    defaults = {
        "auth_token": "",
        "template_id": "",
        "frequencia": 2,
        "unidade_tempo": "segundo",
        "arquivo": None,
        "campos_selecionados": [],
        "iniciar_envio": False,
        "interromper_envio": False
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default
