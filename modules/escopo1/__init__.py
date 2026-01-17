import streamlit as st
from . import estacionaria, movel  # <--- Importe o novo arquivo movel

def render():
    st.title("🏭 Escopo 1: Emissões Diretas")
    
    abas = st.tabs([
        "Combustão Estacionária", 
        "Combustão Móvel", 
        "Emissões Fugitivas", 
        "Processos Industriais",
        "Resíduos Sólidos"
    ])

    with abas[0]:
        estacionaria.render()
        
    with abas[1]:
        # Agora chamamos o render() do módulo movel
        movel.render()
        
    with abas[2]:
        st.info("🚧 Emissões Fugitivas em construção...")