import streamlit as st

def render_layout():
    st.markdown(
        '''
        <style>
            .main {
                background-color: #0f0f0f;
                color: white;
            }
            h1, h2, h3 {
                color: #00ffd4;
            }
            .stButton>button {
                background-color: #00ffd4;
                color: black;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
        </style>
        ''',
        unsafe_allow_html=True
    )

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

    st.subheader("📄 Exemplo da planilha esperada:")
    colunas_selecionadas = [campo for campo, marcado in campos.items() if marcado]
    st.code("\t".join(colunas_selecionadas), language="text")

    st.subheader("2️⃣ Informações da Requisição")

    auth_token = st.text_input("Authorization (coloque o token completo):", type="password", key="auth_token")
    template_id = st.text_input("ID do Modelo (templateId):", key="template_id")

    col1, col2 = st.columns(2)
    with col1:
        frequencia = st.number_input("Quantidade de requisições", min_value=1, value=2, key="frequencia")
    with col2:
        unidade_tempo = st.selectbox("Por...", options=["segundo", "minuto"], key="unidade_tempo")

    st.subheader("3️⃣ Upload da planilha")
    arquivo = st.file_uploader("Envie um arquivo Excel (.xlsx)", type=["xlsx"], key="arquivo")

    iniciar_envio = st.button("🚀 Iniciar envio")

    if "interromper" not in st.session_state:
        st.session_state.interromper = False

    if st.session_state.get("envio_em_andamento"):
        if st.button("🛑 Interromper envio"):
            st.session_state.interromper = True

    return {
        "campos": campos,
        "colunas_selecionadas": colunas_selecionadas,
        "auth_token": auth_token,
        "template_id": template_id,
        "frequencia": frequencia,
        "unidade_tempo": unidade_tempo,
        "arquivo": arquivo,
        "iniciar_envio": iniciar_envio,
    }
