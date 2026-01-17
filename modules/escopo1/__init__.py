import streamlit as st
# O ponto (.) significa "desta mesma pasta, importe estacionaria"
from . import estacionaria

def render():
    st.title("🏭 Escopo 1: Emissões Diretas")
    
    # Abas para separar as categorias do Escopo 1
    abas = st.tabs([
        "Combustão Estacionária", 
        "Combustão Móvel", 
        "Emissões Fugitivas", 
        "Processos Industriais",
        "Resíduos Sólidos"
    ])

    # Aba 1: Chama o arquivo estacionaria.py
    with abas[0]:
        estacionaria.render()
        
    # Outras abas (placeholders por enquanto)
    with abas[1]:
        st.info("🚧 Módulo de Combustão Móvel em construção...")
        
    with abas[2]:
        st.info("🚧 Módulo de Emissões Fugitivas em construção...")