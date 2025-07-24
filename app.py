# app.py
import streamlit as st
import pandas as pd
import time
import requests
import base64
from io import BytesIO
import threading

st.set_page_config(page_title="Envio de Transações CAF", layout="wide")

st.title("🚀 Envio de Transações CAF")

# Campos disponíveis
campos_disponiveis = [
    "CPF", "NOME", "DATA_NASC", "NOME_MAE",
    "CEP", "EMAIL", "TEL", "PLACA",
    "SELFIE", "FRENTE_DOC", "VERSO_DOC"
]

# Seleção dos campos da planilha
st.subheader("✅ Selecione os campos que estarão na sua planilha")
campos_selecionados = []
cols = st.columns(4)
for idx, campo in enumerate(campos_disponiveis):
    if cols[idx % 4].checkbox(campo, key=f"col_{campo}"):
        campos_selecionados.append(campo)

# Exemplo da planilha esperada
if campos_selecionados:
    st.subheader("📄 Exemplo de estrutura esperada da planilha")
    exemplo = pd.DataFrame([["exemplo"] * len(campos_selecionados)], columns=campos_selecionados)
    st.dataframe(exemplo, use_container_width=True, hide_index=True)

# Upload da planilha
st.subheader("📁 Envie um arquivo Excel (.xlsx)")
arquivo = st.file_uploader("Drag and drop file here", type=["xlsx"], label_visibility="collapsed")

# Inputs de configuração
st.subheader("🔐 Configurações da Requisição")
authorization = st.text_input("Authorization (cole o token completo)", type="password")
template_id = st.text_input("ID do modelo de consulta (templateId)")

# Configuração de velocidade
st.subheader("⚙️ Frequência de requisições")
col1, col2 = st.columns([1, 2])
qtd = col1.number_input("Quantidade", min_value=1, value=1, step=1)
modo = col2.selectbox("Intervalo", options=["por segundo", "por minuto"])
intervalo = 60 / qtd if modo == "por minuto" else 1 / qtd

# Controle de interrupção
stop_event = threading.Event()

def interromper_envio():
    stop_event.set()

# Botão de envio
if st.button("📝 Enviar Transações"):
    if not arquivo:
        st.error("Envie um arquivo Excel.")
    elif not authorization or not template_id:
        st.error("Preencha o Authorization e o templateId.")
    elif not campos_selecionados:
        st.error("Selecione ao menos um campo.")
    else:
        df = pd.read_excel(arquivo)
        total = len(df)
        progresso = st.progress(0)
        status_area = st.empty()
        btn_stop = st.empty()
        resultados = []

        # Mostra botão de interrupção
        if btn_stop.button("🔴 Interromper Envio", key="btn_stop_envio"):
            interromper_envio()

        for i, row in df.iterrows():
            if stop_event.is_set():
                status_area.warning("Envio interrompido pelo usuário.")
                break

            payload = {"templateId": template_id, "attributes": {}, "files": []}
            for campo in campos_selecionados:
                valor = row.get(campo)
                if pd.isna(valor): continue

                if campo == "CPF":
                    cpf = ''.join(filter(str.isdigit, str(valor)))
                    cpf = cpf.zfill(11)
                    payload["attributes"]["cpf"] = cpf
                elif campo in ["SELFIE", "FRENTE_DOC", "VERSO_DOC"]:
                    tipo = "SELFIE" if campo == "SELFIE" else "OTHERS"
                    payload["files"].append({"data": str(valor), "type": tipo})
                else:
                    key_attr = {
                        "NOME": "name",
                        "DATA_NASC": "birthDate",
                        "NOME_MAE": "motherName",
                        "CEP": "cep",
                        "EMAIL": "email",
                        "TEL": "phoneNumber",
                        "PLACA": "plate"
                    }.get(campo, campo.lower())
                    payload["attributes"][key_attr] = str(valor)

            response = requests.post(
                "https://api.combateafraude.com/v1/transactions?origin=TRUST",
                json=payload,
                headers={"Authorization": authorization, "Content-Type": "application/json"}
            )

            resultado = {
                "cpf": payload["attributes"].get("cpf", ""),
                "status_code": response.status_code,
                "resumo": "OK" if response.ok else response.text
            }
            resultados.append(resultado)

            progresso.progress((i + 1) / total)
            status_area.info(f"{i+1}/{total} → CPF: {resultado['cpf']} → {resultado['status_code']} | {resultado['resumo']}")
            time.sleep(intervalo)

        if not stop_event.is_set():
            status_area.success("✅ Envio concluído!")

        # Gerar relatório final
        relatorio = pd.DataFrame(resultados)
        buffer = BytesIO()
        relatorio.to_excel(buffer, index=False)
        buffer.seek(0)
        st.download_button(
            label="📥 Baixar relatório final (.xlsx)",
            data=buffer,
            file_name="relatorio_transacoes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
