import streamlit as st
import pandas as pd
import requests
import time
import re
from config import CAMPOS_DISPONIVEIS
from io import StringIO

def processar_planilha(arquivo, auth_token, template_id):
    if st.session_state.get("iniciar_envio") and st.session_state.get("arquivo") and st.session_state.get("auth_token") and st.session_state.get("template_id"):
        df = pd.read_excel(arquivo)
        total = len(df)
        progresso = st.progress(0, text="Aguardando início...")
        log_area = st.empty()

        # Ativa estado de envio e limpa interrupção
        st.session_state["envio_em_andamento"] = True
        st.session_state["interromper"] = False

        intervalo = 1 / st.session_state["frequencia"] if st.session_state["unidade_tempo"] == "segundo" else 60 / st.session_state["frequencia"]
        resultados = []

        for i, linha in df.iterrows():
            if st.session_state.get("interromper"):
                st.warning("🛑 Envio interrompido pelo usuário.")
                break

            payload = {"templateId": template_id, "attributes": {}, "files": []}
            entrada_placa = ""

            for campo, tipo in CAMPOS_DISPONIVEIS.items():
                if st.session_state.get(campo) and campo in linha and not pd.isna(linha[campo]):
                    valor = str(linha[campo]).strip()
                    if campo == "CPF":
                        valor = re.sub(r"\D", "", valor).zfill(11)
                        payload["attributes"][tipo] = valor
                    elif campo == "CEP":
                        valor = re.sub(r"\D", "", valor).zfill(8)
                        payload["attributes"][tipo] = valor
                    elif campo == "PLACA":
                        valor = re.sub(r"[^A-Z0-9]", "", valor.upper())
                        entrada_placa = valor
                        payload["attributes"][tipo] = valor
                    elif campo in ["SELFIE", "FRENTE_DOC", "VERSO_DOC"]:
                        payload["files"].append({"data": valor, "type": tipo})
                    else:
                        payload["attributes"][tipo] = valor

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
                log_area.text(f"{i+1}/{total} → Status: {status} | CPF: {payload['attributes'].get('cpf', '')}")
                resultados.append({
                    "cpf": payload["attributes"].get("cpf", ""),
                    "placa_enviada": entrada_placa,
                    "status": status,
                    "mensagem": response.text if status != 201 else "OK"
                })
            except Exception as e:
                log_area.text(f"{i+1}/{total} → Erro: {str(e)}")
                resultados.append({
                    "cpf": payload["attributes"].get("cpf", ""),
                    "placa_enviada": entrada_placa,
                    "status": "ERRO",
                    "mensagem": str(e)
                })

            progresso.progress((i+1)/total, text=f"{i+1} de {total} enviados")
            time.sleep(intervalo)

        st.success("✅ Processamento concluído.")
        st.session_state["envio_em_andamento"] = False

        relatorio_df = pd.DataFrame(resultados)
        csv = relatorio_df.to_csv(index=False).encode("utf-8")
        st.download_button("📄 Baixar relatório final (.csv)", csv, "relatorio_transacoes.csv", mime="text/csv")
