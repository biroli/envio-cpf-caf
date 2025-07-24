
import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="Envio de Transações CAF", layout="centered")

st.title("📤 Envio de Transações para a CAF")

st.markdown("### 1️⃣ Selecione os campos que estarão presentes na sua planilha:")

campos_disponiveis = {
    "cpf": "CPF",
    "name": "Nome completo",
    "birthDate": "Data de nascimento",
    "motherName": "Nome da mãe",
    "cep": "CEP",
    "email": "Email",
    "phoneNumber": "Telefone",
    "plate": "Placa do carro",
    "selfie": "URL da selfie",
    "doc_front": "URL frente do documento",
    "doc_back": "URL verso do documento"
}

colunas_selecionadas = st.multiselect("Campos incluídos na planilha", options=list(campos_disponiveis.keys()),
                                      format_func=lambda x: campos_disponiveis[x])

if colunas_selecionadas:
    st.markdown("### 🧾 Exemplo da planilha esperada:")
    df_exemplo = pd.DataFrame({campos_disponiveis[c]: [f"exemplo_{i+1}"] for i, c in enumerate(colunas_selecionadas)})
    st.dataframe(df_exemplo)

    st.markdown("### 2️⃣ Envie a planilha com os dados reais:")
    arquivo = st.file_uploader("Escolha o arquivo Excel (.xlsx)", type=["xlsx"])

    if arquivo:
        df = pd.read_excel(arquivo)
        st.success("Planilha carregada com sucesso!")

        st.markdown("### 3️⃣ Preencha as informações da requisição:")
        authorization = st.text_input("Authorization (Bearer token)", type="password")
        template_id = st.text_input("ID do modelo de consulta (templateId)")
        rps = st.number_input("Requisições por segundo", min_value=1, max_value=10, value=1)

        if st.button("🚀 Enviar transações"):
            total = len(df)
            progresso = st.progress(0)
            resultados = []

            for idx, row in df.iterrows():
                payload = {
                    "templateId": template_id,
                    "attributes": {},
                    "files": []
                }

                for campo in colunas_selecionadas:
                    valor = row.get(campos_disponiveis[campo], None)
                    if pd.isna(valor):
                        continue
                    if campo in ["selfie", "doc_front", "doc_back"]:
                        tipo = "SELFIE" if campo == "selfie" else "OTHERS"
                        payload["files"].append({"data": valor, "type": tipo})
                    else:
                        if campo == "cpf":
                            valor = str(valor).zfill(11).replace(".", "").replace("-", "").replace(" ", "")
                        payload["attributes"][campo] = valor

                headers = {
                    "Authorization": f"Bearer {authorization}",
                    "Content-Type": "application/json"
                }

                try:
                    response = requests.post(
                        "https://api.combateafraude.com/v1/transactions?origin=TRUST",
                        headers=headers,
                        json=payload
                    )
                    resultados.append(f"Linha {idx + 1}: {response.status_code} - {response.text[:100]}")
                except Exception as e:
                    resultados.append(f"Linha {idx + 1}: ERRO - {str(e)}")

                progresso.progress((idx + 1) / total)
                time.sleep(1 / rps)

            st.markdown("### ✅ Resultados:")
            for r in resultados:
                st.write(r)
