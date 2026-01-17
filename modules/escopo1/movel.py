import streamlit as st
import pandas as pd
from src.calculadora import GHGCalculator

def get_calculator():
    return GHGCalculator()

calc = get_calculator()

def render():
    st.markdown("### 🚚 Combustão Móvel")
    st.markdown("Emissões de veículos da frota própria ou controlada.")

    # 1. Seleção do Modal
    modais = ["Rodoviário", "Ferroviário", "Hidroviário", "Aéreo", "Outros"]
    modal = st.selectbox("Tipo de Transporte:", modais)

    if modal != "Rodoviário":
        st.info("🚧 Apenas o modal 'Rodoviário' está implementado neste protótipo.")
        return

    # 2. Abas das Opções
    tab1, tab2, tab3 = st.tabs([
        "Opção 1 (Veículo + Ano)", 
        "Opção 2 (Combustível)", 
        "Opção 3 (Distância)"
    ])

    # Inicializa sessão
    if 'inventario_movel' not in st.session_state:
        st.session_state['inventario_movel'] = []

    # --- OPÇÃO 1: VEÍCULO + ANO ---
    with tab1:
        st.caption("Utilize caso possua o tipo e o ano de fabricação.")
        with st.form("form_movel_op1", clear_on_submit=True):
            c1, c2 = st.columns(2)
            reg = c1.text_input("Registro da Frota (Placa/ID)")
            desc = c2.text_input("Descrição")
            
            tipo_veiculo = st.selectbox("Tipo da Frota:", calc.get_tipos_veiculos(), key="op1_tipo")
            
            # Lógica de Bloqueio do Ano
            habilita_ano = calc.verifica_ano_habilitado(tipo_veiculo)
            anos = calc.get_anos_frota()
            ano_selecionado = st.selectbox("Ano da Frota:", anos, disabled=not habilita_ano, key="op1_ano")
            if not habilita_ano:
                st.caption(" * Ano desabilitado para este tipo de veículo (Base DEFRA).")

            # Input de Consumo (Mensal ou Anual simplificado num campo só)
            qtd = st.number_input("Consumo Total (Litros/m³)", min_value=0.0, key="op1_qtd")
            periodo = st.radio("Período do Dado:", ["Anual", "Mensal"], horizontal=True, key="op1_per")

            if st.form_submit_button("Calcular Opção 1", type="primary"):
                res = calc.calcular_movel(1, {
                    'tipo_veiculo': tipo_veiculo,
                    'ano': ano_selecionado if habilita_ano else "N/A",
                    'qtd': qtd
                })
                salvar_resultado(res, reg, desc, tipo_veiculo, f"Opção 1 ({periodo})")

    # --- OPÇÃO 2: COMBUSTÍVEL ---
    with tab2:
        st.caption("Utilize caso possua apenas o tipo e quantidade de combustível.")
        with st.form("form_movel_op2", clear_on_submit=True):
            c1, c2 = st.columns(2)
            reg = c1.text_input("Registro da Frota")
            desc = c2.text_input("Descrição")
            
            # Lista de combustíveis (reusa a da estacionária ou cria nova lista móvel)
            lista_comb = ["Gasolina C (Brasileira)", "Óleo Diesel (comercial)", "Etanol Hidratado"] 
            comb_direto = st.selectbox("Combustível:", lista_comb, key="op2_comb")
            
            qtd = st.number_input("Consumo Total (Litros/m³)", min_value=0.0, key="op2_qtd")
            
            if st.form_submit_button("Calcular Opção 2", type="primary"):
                res = calc.calcular_movel(2, {
                    'combustivel_direto': comb_direto,
                    'qtd': qtd
                })
                salvar_resultado(res, reg, desc, "Diversos", "Opção 2")

    # --- OPÇÃO 3: DISTÂNCIA ---
    with tab3:
        st.caption("Utilize caso possua apenas a distância percorrida (km).")
        with st.form("form_movel_op3", clear_on_submit=True):
            c1, c2 = st.columns(2)
            reg = c1.text_input("Registro da Frota")
            desc = c2.text_input("Descrição")
            
            tipo_veiculo = st.selectbox("Tipo da Frota:", calc.get_tipos_veiculos(), key="op3_tipo")
            habilita_ano = calc.verifica_ano_habilitado(tipo_veiculo)
            ano_selecionado = st.selectbox("Ano da Frota:", calc.get_anos_frota(), disabled=not habilita_ano, key="op3_ano")
            
            dist = st.number_input("Distância Percorrida (km)", min_value=0.0, key="op3_dist")
            
            if st.form_submit_button("Calcular Opção 3", type="primary"):
                res = calc.calcular_movel(3, {
                    'tipo_veiculo': tipo_veiculo,
                    'ano': ano_selecionado if habilita_ano else "N/A",
                    'qtd': dist
                })
                
                # Feedback extra da Opção 3
                st.info(f"⛽ Conversão Estimada: {dist} km ÷ {res['consumo_medio_usado']} km/l = {res['consumo_calculado_litros']:.2f} Litros de {res['combustivel_utilizado']}")
                
                salvar_resultado(res, reg, desc, tipo_veiculo, "Opção 3")

    # --- TABELA DE RESULTADOS ---
    st.divider()
    st.subheader("📊 Inventário de Emissões Móveis")
    
    if st.session_state['inventario_movel']:
        df = pd.DataFrame(st.session_state['inventario_movel'])
        
        # Formatação das colunas solicitadas
        cols_config = {
            "Emissões totais (t CO2e)": st.column_config.NumberColumn(format="%.4f"),
            "Emissões de CO2 biogênico (t)": st.column_config.NumberColumn(format="%.4f"),
            "Qtd Combustível Fóssil": st.column_config.NumberColumn(format="%.2f"),
            "FE Fóssil CO2 (kg/l)": st.column_config.NumberColumn(format="%.4f"),
        }
        
        st.dataframe(df, use_container_width=True, column_config=cols_config)
    else:
        st.info("Nenhum registro móvel.")

def salvar_resultado(res, reg, desc, tipo, metodo):
    """Função auxiliar para formatar a saída exatamente como pedido"""
    novo = {
        # Identificação
        "Registro": reg, "Descrição": desc, "Tipo Veículo": tipo, "Método": metodo,
        
        # Unidades e Composição
        "Unidades": res['unidade_entrada'],
        "Combustível Base": res['combustivel_utilizado'],
        "Comp. Fóssil": res['comp_fossil'],
        "Comp. Bio": res['comp_bio'],
        
        # Quantidades (A grande sacada da Opção 3 é gerar isso)
        "Qtd Combustível Fóssil": res['qtd_fossil'],
        "Qtd Biocombustível": res['qtd_bio'],
        
        # Fatores (Separados por Gás)
        "FE Fóssil CO2 (kg/l)": res['fatores_fossil']['CO2'],
        "FE Bio CO2 (kg/l)": res['fatores_bio']['CO2'],
        "FE Comercial CH4 (kg/l)": res['fatores_fossil']['CH4'], # Simplificado
        "FE Comercial N2O (kg/l)": res['fatores_fossil']['N2O'], # Simplificado
        
        # Emissões em Toneladas
        "Emissões de CO2 fóssil (t)": res['emis_fossil']['CO2'] / 1000,
        "Emissões de CH4 (t)": (res['emis_fossil']['CH4'] + res['emis_bio']['CH4']) / 1000,
        "Emissões de N2O (t)": (res['emis_fossil']['N2O'] + res['emis_bio']['N2O']) / 1000,
        
        # Totais
        "Emissões totais (t CO2e)": res['total_gee'],
        "Emissões de CO2 biogênico (t)": res['total_bio']
    }
    st.session_state['inventario_movel'].append(novo)
    st.success("Adicionado com sucesso!")