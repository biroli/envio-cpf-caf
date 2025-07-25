import streamlit as st
import pandas as pd
import requests
import time
import re
from io import StringIO

def processar_planilha(arquivo, auth_token, template_id, frequencia, unidade_tempo, campos_selecionados):
    df = pd.read_excel(arquivo)
    total = len(df)
    intervalo = 1 / frequencia if unidade_tempo == "segundo" else 60 / frequencia

    progresso = st.progress(0, text="Iniciando envio...")
    log_area = st.empty()
    st.session_state["interromper_envio"] = False
    interromperamento = st.empty()

    if interromperamento.button("🛑 Interromper envio"):
        st.session_state["interromper_envio"] = True

    logs = []
    for i, linha in df.iterrows():
        if st.session_state.get("interromper_envio"):
            st.warning("Envio interrompido pelo usuário.")
            break

        payload = {"templateId": template_id, "attributes": {}, "files": []}
        for campo in campos_selecionados:
            if campo in linha and not pd.isna(linha[campo]):
                valor = str(linha[campo]).strip()
                if campo == "CPF":
                    valor = re.sub(r"\D", "", valor).zfill(11)
                    payload["attributes"]["cpf"] = valor
                elif campo == "NOME":
                    payload["attributes"]["name"] = valor
                elif campo == "DATA_NASC":
                    payload["attributes"]["birthDate"] = valor
                elif campo == "NOME_MAE":
                    payload["attributes"]["motherName"] = valor
                elif campo == "CEP":
                    valor = re.sub(r"\D", "", valor).zfill(8)
                    payload["attributes"]["cep"] = valor
                elif campo == "EMAIL":
                    payload["attributes"]["email"] = valor
                elif campo == "TEL":
                    payload["attributes"]["phoneNumber"] = valor
                elif campo == "PLACA":
                    valor = valor.replace(" ", "").upper()
                    payload["attributes"]["plate"] = valor
                elif campo == "SELFIE":
                    payload["files"].append({"data": valor, "type": "SELFIE"})
                elif campo in ["FRENTE_DOC", "VERSO_DOC"]:
                    payload["files"].append({"data": valor, "type": "OTHERS"})

        try:
            response = requests.post(
                url="https://api.combateafraude.com/v1/transactions?origin=TRUST",
                headers={
                    "Authorization": auth_token,
                    "Content-Type": "application/json"
                },
                json=payload
            )
            status = response.status_code
            resp_text = response.text.replace("\n", "").replace("\r", "")
            logs.append(f'{payload["attributes"].get("cpf", "")},{status},"{resp_text}"')
            log_area.text(f"{i+1}/{total} → Status: {status} | CPF: {payload["attributes"].get("cpf", "")}")
        except Exception as e:
            logs.append(f'{payload["attributes"].get("cpf", "")},error,"{str(e)}"')
            log_area.text(f"{i+1}/{total} → Erro: {str(e)}")

        progresso.progress((i+1)/total, text=f"{i+1} de {total} enviados")
        time.sleep(intervalo)

    output = "cpf,status,mensagem\n" + "\n".join(logs)
    st.download_button("📥 Baixar relatório", data=output, file_name="relatorio_envio.csv", mime="text/csv")
    if not st.session_state.get("interromper_envio"):
        st.success("✅ Processamento concluído.")
