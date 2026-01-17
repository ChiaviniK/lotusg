# modules/introducao.py
import streamlit as st
from datetime import date

def render():
    st.title("📋 Identificação da Organização")
    st.markdown("Preencha os dados institucionais para compor o cabeçalho do Inventário.")

    with st.form("form_intro"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome da Organização", value=st.session_state['empresa_dados'].get('nome', ''))
            endereco = st.text_area("Endereço Completo", value=st.session_state['empresa_dados'].get('endereco', ''))
            ano = st.selectbox("Ano Inventariado", [2023, 2024, 2025], index=0)
        
        with col2:
            responsavel = st.text_input("Nome do Responsável", value=st.session_state['empresa_dados'].get('responsavel', ''))
            telefone = st.text_input("Telefone/Contato", value=st.session_state['empresa_dados'].get('telefone', ''))
            data_preenchimento = st.date_input("Data de Preenchimento", value=date.today())

        st.markdown("---")
        submitted = st.form_submit_button("Salvar Dados da Empresa", type="primary")

        if submitted:
            st.session_state['empresa_dados'] = {
                "nome": nome,
                "endereco": endereco,
                "ano": ano,
                "responsavel": responsavel,
                "telefone": telefone,
                "data": data_preenchimento
            }
            st.success("Dados institucionais salvos com sucesso! Avance para os Escopos.")