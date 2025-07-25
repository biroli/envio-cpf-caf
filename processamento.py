import streamlit as st
import pandas as pd
import requests
import time
import re
from config import CAMPOS_DISPONIVEIS

def processar_planilha():
    df = pd.read_excel(st.session_state["arquivo"])
    total = len(df)
    progresso = st.progress(0, text="Iniciando envio...")
    log_area = st.empty()
    logs = []

    frequencia = st.session_state["frequencia"]
    unidade_tempo = st.session_state["unidade_tempo"]
    intervalo = 1 / frequencia if unidade_tempo == "segundo" else 60 / frequencia

    for i, linha in df.iterrows():
        if st.session_state["interromper"]:
            st.warning("🚫 Envio interrompido pelo usuário.")
            break

        payload = {"templateId": st.session_state["template_id"], "attributes": {}, "files": []}
        for campo in CAMPOS_DISPONIVEIS:
            if st.session_state.get(campo) and campo in linha and not pd.isna(linha[campo]):
                valor = str(linha[campo]).strip()
                if campo == "CPF":
                    valor = re.sub(r"\D", "", valor).zfill(11)
                    payload["attributes"]["cpf"] = valor
                elif campo == "CEP":
                    valor = re.sub(r"\D", "", valor).zfill(8)
                    payload["attributes"]["cep"] = valor
                elif campo == "PLACA":
                    valor = valor.replace(" ", "")
                    payload["attributes"]["plate"] = valor
                elif campo == "SELFIE":
                    payload["files"].append({"data": valor, "type": "SELFIE"})
                elif campo in ["FRENTE_DOC", "VERSO_DOC"]:
                    payload["files"].append({"data": valor, "type": "OTHERS"})
                else:
                    payload["attributes"][CAMPOS_DISPONIVEIS[campo]] = valor

        try:
            response = requests.post(
                url="https://api.combateafraude.com/v1/transactions?origin=TRUST",
                headers={
                    "Authorization": st.session_state["auth_token"],
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

    if st.session_state["interromper"]:
        st.warning("⚠️ Envio interrompido.")
    else:
        st.success("✅ Envio concluído.")

    df_log = pd.DataFrame([x.split(",", 2) for x in logs], columns=["cpf", "status", "mensagem"])
    csv = df_log.to_csv(index=False).encode("utf-8")
    st.download_button("📄 Baixar relatório (.csv)", csv, "relatorio_envio.csv", mime="text/csv")

    st.session_state["enviar"] = False
    st.session_state["interromper"] = False
