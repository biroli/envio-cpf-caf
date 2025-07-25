import streamlit as st

def render_layout():
    st.title("📤 Envio de Transações para a CAF")

    st.subheader("1️⃣ Selecione os campos que estarão na planilha:")
    campos = {
        "CPF": st.checkbox("CPF", value=True),
        "NOME": st.checkbox("NOME"),
        "DATA_NASC": st.checkbox("DATA_NASC"),
        "NOME_MAE": st.checkbox("NOME_MAE"),
        "CEP": st.checkbox("CEP"),
        "EMAIL": st.checkbox("EMAIL"),
        "TEL": st.checkbox("TEL"),
        "PLACA": st.checkbox("PLACA"),
        "SELFIE": st.checkbox("SELFIE"),
        "FRENTE_DOC": st.checkbox("FRENTE_DOC"),
        "VERSO_DOC": st.checkbox("VERSO_DOC"),
    }
    st.session_state["campos"] = campos

    st.subheader("📄 Exemplo da planilha esperada:")
    colunas = [campo for campo, marcado in campos.items() if marcado]
    st.code("\t".join(colunas), language="text")

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

    if st.session_state.get("envio_em_andamento"):
        if st.button("🛑 Interromper envio"):
            st.session_state["interromper"] = True

    if st.button("🚀 Iniciar envio"):
        st.session_state["iniciar_envio"] = True
        st.session_state["interromper"] = False
