import streamlit as st
import pandas as pd
import time
import requests
import re

def processar_planilha():
    arquivo = st.session_state.get("arquivo")
    auth_token = st.session_state.get("auth_token")
    template_id = st.session_state.get("template_id")
    campos = st.session_state.get("campos")

    if not all([arquivo, auth_token, template_id, campos]):
        st.error("❌ Preencha todas as informações e envie um arquivo.")
        return

    df = pd.read_excel(arquivo)
    total = len(df)
    progresso = st.progress(0, text="Aguardando início...")
    log_area = st.empty()
    resultados = []

    st.session_state["envio_em_andamento"] = True

    intervalo = 1 / st.session_state["frequencia"] if st.session_state["unidade_tempo"] == "segundo" else 60 / st.session_state["frequencia"]

    for i, linha in df.iterrows():
        if st.session_state.get("interromper"):
            break

        payload = {"templateId": template_id, "attributes": {}, "files": []}

        for campo, chave in campos.items():
            if chave and campo in linha and not pd.isna(linha[campo]):
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
                    valor = valor.replace(" ", "")
                    payload["attributes"]["plate"] = valor
                elif campo == "SELFIE":
                    payload["files"].append({"data": valor, "type": "SELFIE"})
                elif campo in ["FRENTE_DOC", "VERSO_DOC"]:
                    payload["files"].append({"data": valor, "type": "OTHERS"})

        try:
            response = requests.post(
                url="https://api.combateafraude.com/v1/transactions?origin=TRUST",
                headers={"Authorization": auth_token, "Content-Type": "application/json"},
                json=payload
            )
            status = response.status_code
            resultados.append({
                "cpf": payload["attributes"].get("cpf", ""),
                "status": status,
                "mensagem": response.text
            })
            log_area.text(f"{i+1}/{total} → Status: {status}")
        except Exception as e:
            resultados.append({
                "cpf": payload["attributes"].get("cpf", ""),
                "status": "ERRO",
                "mensagem": str(e)
            })
            log_area.text(f"{i+1}/{total} → Erro: {str(e)}")

        progresso.progress((i+1)/total, text=f"{i+1} de {total} enviados")
        time.sleep(intervalo)

    df_log = pd.DataFrame(resultados)
    csv = df_log.to_csv(index=False).encode("utf-8")
    st.download_button("📄 Baixar relatório final (.csv)", csv, "relatorio_transacoes.csv", mime="text/csv")

    if not st.session_state.get("interromper"):
        st.success("✅ Processamento concluído.")
    else:
        st.warning("⛔ Envio interrompido pelo usuário.")

    st.session_state["iniciar_envio"] = False
    st.session_state["envio_em_andamento"] = False
