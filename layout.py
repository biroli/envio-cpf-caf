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

    return campos
