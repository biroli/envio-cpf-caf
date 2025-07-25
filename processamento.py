import streamlit as st
import pandas as pd
import time
import requests
import re

def processar_planilha(arquivo, auth_token, template_id, intervalo, campos, interromper_key):
    df = pd.read_excel(arquivo)
    total = len(df)
    progresso = st.progress(0, text="Enviando...")
    log_area = st.empty()
    logs = []

    for i, linha in df.iterrows():
        if st.session_state.get(interromper_key):
            st.warning("🚫 Envio interrompido.")
            break

        payload = {"templateId": template_id, "attributes": {}, "files": []}

        for campo in campos:
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
                    valor = re.sub(r"\s+", "", valor)
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
            mensagem = response.text
            cpf_log = payload["attributes"].get("cpf", "N/A")
            log_texto = f"{i+1}/{total} → Status: {status} | CPF: {cpf_log}"
            logs.append({"cpf": cpf_log, "status": status, "mensagem": mensagem})
        except Exception as e:
            log_texto = f"{i+1}/{total} → Erro: {str(e)}"
            logs.append({"cpf": cpf_log, "status": "erro", "mensagem": str(e)})

        log_area.text(log_texto)
        progresso.progress((i+1)/total, text=f"{i+1} de {total} enviados")
        time.sleep(intervalo)

    df_log = pd.DataFrame(logs)
    csv = df_log.to_csv(index=False).encode("utf-8")
    st.download_button("📄 Baixar relatório de envio", csv, file_name="log_envio.csv", mime="text/csv")

    if not st.session_state.get(interromper_key):
        st.success("✅ Processamento concluído.")
