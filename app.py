# app.py
from modules import introducao, escopo1, escopo2, escopo3, relatorios

import streamlit as st
from modules import introducao, escopo1, escopo2, escopo3, relatorios

# Configuração da Página
st.set_page_config(page_title="Sistema GHG Protocol", layout="wide", page_icon="🌎")

# Inicializa Session State Global se não existir
if 'empresa_dados' not in st.session_state:
    st.session_state['empresa_dados'] = {}
if 'inventario' not in st.session_state:
    st.session_state['inventario'] = []

def main():
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2964/2964514.png", width=50)
    st.sidebar.title("Menu GHG")
    
    # Menu Principal
    menu = st.sidebar.radio(
        "Navegação",
        ["🏠 Introdução", "🏭 Escopo 1", "⚡ Escopo 2", "🚚 Escopo 3", "📊 Relatórios & Download"]
    )

    st.sidebar.markdown("---")
    
    # Mostra qual empresa está logada na barra lateral
    if st.session_state['empresa_dados'].get('nome'):
        st.sidebar.info(f"Inventário de: **{st.session_state['empresa_dados']['nome']}**")
        st.sidebar.caption(f"Ano Base: {st.session_state['empresa_dados'].get('ano')}")

    # Roteador de Páginas
    if menu == "🏠 Introdução":
        introducao.render()
    elif menu == "🏭 Escopo 1":
        escopo1.render()
    elif menu == "⚡ Escopo 2":
        escopo2.render()
    elif menu == "🚚 Escopo 3":
        escopo3.render()
    elif menu == "📊 Relatórios & Download":
        relatorios.render()

if __name__ == "__main__":
    main()