import streamlit as st
import pandas as pd
import requests
import time
import re
from config import CAMPOS_DISPONIVEIS

def processar_planilha(arquivo, auth_token, template_id):
    try:
        df = pd.read_excel(arquivo)
    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo: {e}")
        return

    total = len(df)
    progresso = st.progress(0, text="Aguardando início...")
    log_area = st.empty()
    logs = []

    st.session_state["envio_em_andamento"] = True
    st.session_state["interromper"] = False

    frequencia = st.session_state.get("frequencia", 1)
    unidade_tempo = st.session_state.get("unidade_tempo", "segundo")
    intervalo = 1 / frequencia if unidade_tempo == "segundo" else 60 / frequencia

    for i, linha in df.iterrows():
        if st.session_state.get("interromper"):
            st.warning("⛔ Envio interrompido pelo usuário.")
            break

        payload = {"templateId": template_id, "attributes": {}, "files": []}
        input_debug = {}

        for campo in CAMPOS_DISPONIVEIS:
            if campo in linha and not pd.isna(linha[campo]):
                valor = str(linha[campo]).strip()
                input_debug[campo] = valor

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
                    valor = valor.replace(" ", "")
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
            msg = response.text
            cpf_log = payload['attributes'].get("cpf", "")
            logs.append(f"{cpf_log},{status},\"{msg}\"")
            log_area.text(f"{i+1}/{total} → Status: {status} | CPF: {cpf_log}")
        except Exception as e:
            cpf_log = payload['attributes'].get("cpf", "")
            logs.append(f"{cpf_log},ERROR,\"{str(e)}\"")
            log_area.text(f"{i+1}/{total} → Erro: {str(e)}")

        progresso.progress((i+1)/total, text=f"{i+1} de {total} enviados")
        time.sleep(intervalo)

    st.session_state["envio_em_andamento"] = False
    st.session_state["iniciar_envio"] = False

    if logs:
        df_log = pd.DataFrame([x.split(",", 2) for x in logs], columns=["cpf", "status", "mensagem"])
        csv = df_log.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Baixar relatório", data=csv, file_name="relatorio_envio.csv", mime="text/csv")

    progresso.empty()
