import streamlit as st
import pandas as pd
from src.calculadora import GHGCalculator

def get_calculator():
    return GHGCalculator()

calc = get_calculator()

def render():
    st.title("🏭 Escopo 1: Combustão Estacionária")
    st.markdown("Preencha as informações da Fonte.")

    # Inicializa sessão específica para Tabela 3 se não existir
    if 'inventario_t3' not in st.session_state:
        st.session_state['inventario_t3'] = []

    # 1. Seleção de Setor e Combustível (Para Tabela 1)
    col_topo1, col_topo2 = st.columns(2)
    with col_topo1:
        setor = st.selectbox("Fatores de emissão para o setor:", calc.get_setores())
    with col_topo2:
        lista_combustiveis = calc.get_combustiveis_estacionaria()
        combustivel_selecionado = st.selectbox("Combustível Utilizado:", lista_combustiveis)
        unidade_atual = calc.get_unidade(combustivel_selecionado)

    st.divider()

    # ========================================================
    # TABELA 1: CÁLCULO VIA COMBUSTÍVEL
    # ========================================================
    st.subheader("Tabela 1. Inventário (Via Consumo)")
    with st.expander("📝 Adicionar Lançamento por Combustível", expanded=True):
        with st.form("form_estacionaria", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1: reg_fonte = st.text_input("Registro da Fonte (ID)")
            with c2: desc_fonte = st.text_input("Descrição da Fonte")
            with c3: quantidade = st.number_input(f"Quantidade ({unidade_atual})", min_value=0.0)

            submitted = st.form_submit_button("➕ Adicionar à Tabela 1", type="primary")

            if submitted and quantidade > 0:
                res = calc.calcular_estacionaria(combustivel_selecionado, quantidade)
                
                novo_lancamento = {
                    "Registro": reg_fonte, "Descrição": desc_fonte, 
                    "Combustível": combustivel_selecionado, "Unidade": unidade_atual, "Quantidade Total": quantidade,
                    "Comp. Fóssil": res['componente_fossil'], "Comp. Bio": res['componente_bio'],
                    "Qtd Fóssil": res['qtd_fossil'], "Qtd Bio": res['qtd_bio'],
                    "FE Fóssil CO2 (kg/un)": res['fatores_fossil']['CO2'], "FE Fóssil CH4 (kg/un)": res['fatores_fossil']['CH4'], "FE Fóssil N2O (kg/un)": res['fatores_fossil']['N2O'],
                    "FE Bio CO2 (kg/un)": res['fatores_bio']['CO2'], "FE Bio CH4 (kg/un)": res['fatores_bio']['CH4'], "FE Bio N2O (kg/un)": res['fatores_bio']['N2O'],
                    "Emis. Fóssil CO2 (t)": res['emis_fossil']['CO2'] / 1000, "Emis. Fóssil CH4 (t)": res['emis_fossil']['CH4'] / 1000, "Emis. Fóssil N2O (t)": res['emis_fossil']['N2O'] / 1000,
                    "Emis. Bio CO2 (t)": res['emis_bio']['CO2'] / 1000, "Emis. Bio CH4 (t)": res['emis_bio']['CH4'] / 1000, "Emis. Bio N2O (t)": res['emis_bio']['N2O'] / 1000,
                    "Total GEE (tCO2e)": res['total_gee'], "Biogênicas (tCO2)": res['total_biogenico']
                }
                st.session_state['inventario'].append(novo_lancamento)
                st.success("Adicionado à Tabela 1!")

    if len(st.session_state['inventario']) > 0:
        df = pd.DataFrame(st.session_state['inventario'])
        st.dataframe(df, use_container_width=True)

    # ========================================================
    # TABELA 2: RESUMO (AUTOMÁTICA)
    # ========================================================
    st.write("##")
    st.subheader("Tabela 2. Resumo por Tipo de Combustível")
    try:
        dados_t2_fossil, dados_t2_bio = calc.gerar_tabela_2(st.session_state['inventario'], setor)
        c_t2_1, c_t2_2 = st.columns(2)
        with c_t2_1:
            st.caption("Combustíveis Fósseis")
            st.dataframe(pd.DataFrame(dados_t2_fossil), use_container_width=True, hide_index=True)
        with c_t2_2:
            st.caption("Biocombustíveis")
            st.dataframe(pd.DataFrame(dados_t2_bio), use_container_width=True, hide_index=True)
    except Exception as e:
        st.info("Aguardando dados para gerar Tabela 2.")

    st.markdown("---")

    # ========================================================
    # TABELA 3: OUTRAS FERRAMENTAS
    # ========================================================
    st.subheader("Tabela 3. Relato de emissões calculadas em outras ferramentas")
    st.info("Utilize esta tabela caso você já tenha as emissões calculadas em toneladas e queira apenas consolidar o inventário.")

    with st.expander("📝 Adicionar Dados de Outras Ferramentas", expanded=False):
        with st.form("form_tabela3", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                t3_reg = st.text_input("Registro da fonte")
                t3_desc = st.text_input("Descrição da fonte")
            
            st.markdown("**Emissões Diretas (em toneladas):**")
            c_input1, c_input2, c_input3, c_input4 = st.columns(4)
            with c_input1:
                t3_co2f = st.number_input("CO₂ Fóssil (t)", min_value=0.0, format="%.4f")
            with c_input2:
                t3_ch4 = st.number_input("CH₄ (t)", min_value=0.0, format="%.4f")
            with c_input3:
                t3_n2o = st.number_input("N₂O (t)", min_value=0.0, format="%.4f")
            with c_input4:
                t3_co2bio = st.number_input("CO₂ Biogênico (t)", min_value=0.0, format="%.4f")

            submitted_t3 = st.form_submit_button("➕ Adicionar à Tabela 3", type="primary")

            if submitted_t3:
                # Calcula o total GEE usando a função nova
                total_gee_t3 = calc.calcular_tabela3_inputs_diretos(t3_co2f, t3_ch4, t3_n2o)
                
                novo_t3 = {
                    "Registro da fonte": t3_reg,
                    "Descrição da fonte": t3_desc,
                    "Emissões de CO2 fóssil (t)": t3_co2f,
                    "Emissões de CH4 (t)": t3_ch4,
                    "Emissões de N2O (t)": t3_n2o,
                    "Emissões de CO2 biogênico (t)": t3_co2bio,
                    "Emissões de GEE totais (t CO2e)": total_gee_t3
                }
                
                st.session_state['inventario_t3'].append(novo_t3)
                st.success("Adicionado à Tabela 3!")

    # Visualização da Tabela 3
    if len(st.session_state['inventario_t3']) > 0:
        df_t3 = pd.DataFrame(st.session_state['inventario_t3'])
        
        st.dataframe(
            df_t3, 
            use_container_width=True,
            column_config={
                "Emissões de CO2 fóssil (t)": st.column_config.NumberColumn(format="%.4f"),
                "Emissões de CH4 (t)": st.column_config.NumberColumn(format="%.4f"),
                "Emissões de N2O (t)": st.column_config.NumberColumn(format="%.4f"),
                "Emissões de CO2 biogênico (t)": st.column_config.NumberColumn(format="%.4f"),
                "Emissões de GEE totais (t CO2e)": st.column_config.NumberColumn(format="%.4f"),
            }
        )
        
        # Totalizador Rápido da Tabela 3
        total_t3 = df_t3["Emissões de GEE totais (t CO2e)"].sum()
        st.metric("Total Tabela 3 (tCO₂e)", f"{total_t3:.4f}")
    else:
        st.info("Nenhum dado lançado na Tabela 3.")