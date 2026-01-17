# modules/relatorios.py
import streamlit as st
import pandas as pd
from io import BytesIO

def render():
    st.title("📊 Relatório Final e Exportação")
    
    if not st.session_state['inventario']:
        st.info("Nenhum dado lançado ainda.")
        return

    # Transforma lista de dicionários em DataFrame
    df_dados = pd.DataFrame(st.session_state['inventario'])
    
    st.subheader("Visualização dos Dados")
    st.dataframe(df_dados, use_container_width=True)
    
    # --- Geração do Excel Complexo ---
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        
        # 1. Aba de Introdução (Capa)
        dados_intro = st.session_state['empresa_dados']
        df_intro = pd.DataFrame(list(dados_intro.items()), columns=['Campo', 'Valor'])
        df_intro.to_excel(writer, sheet_name='Introdução', index=False)
        
        # 2. Aba de Inventário (Dados)
        df_dados.to_excel(writer, sheet_name='Inventário Completo', index=False)
        
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Baixar Planilha Completa (XLSX)",
        data=excel_data,
        file_name=f"Inventario_{st.session_state['empresa_dados'].get('nome', 'Empresa')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )