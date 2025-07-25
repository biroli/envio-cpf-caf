import streamlit as st
import pandas as pd
import requests
import time
import re
from config import CAMPOS_DISPONIVEIS
from io import StringIO

def processar_planilha(arquivo, auth_token, template_id):
    campos_selecionados = {c: CAMPOS_DISPONIVEIS[c] for c in CAMPOS_DISPONIVEIS if st.session_state.get(c)}
    df = pd.read_excel(arquivo)
    total = len(df)
    progresso = st.progress(0, text="Iniciando...")
    log_area = st.empty()
    intervalo = 1 / st.session_state["frequencia"] if st.session_state["unidade_tempo"] == "segundo" else 60 / st.session_state["frequencia"]

    resultados = []

    for i, linha in df.iterrows():
        payload = {"templateId": template_id, "attributes": {}, "files": []}
        for campo, tipo in campos_selecionados.items():
            if campo in linha and not pd.isna(linha[campo]):
                valor = str(linha[campo]).strip()
                if campo == "CPF":
                    valor = re.sub(r"\D", "", valor).zfill(11)
                    payload["attributes"][tipo] = valor
                elif campo == "CEP":
                    valor = re.sub(r"\D", "", valor).zfill(8)
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
                "status": status,
                "mensagem": response.text if status != 201 else "OK"
            })
        except Exception as e:
            log_area.text(f"{i+1}/{total} → Erro: {str(e)}")
            resultados.append({
                "cpf": payload["attributes"].get("cpf", ""),
                "status": "ERRO",
                "mensagem": str(e)
            })

        progresso.progress((i+1)/total, text=f"{i+1} de {total} enviados")
        time.sleep(intervalo)

    st.success("✅ Processamento concluído.")

    # Geração de relatório CSV
    relatorio_df = pd.DataFrame(resultados)
    csv = relatorio_df.to_csv(index=False).encode("utf-8")
    st.download_button("📄 Baixar relatório final (.csv)", csv, "relatorio_transacoes.csv", mime="text/csv")
