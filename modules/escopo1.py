import streamlit as st
import pandas as pd
from src.calculadora import GHGCalculator

# Removendo cache para garantir atualização durante desenvolvimento
def get_calculator():
    return GHGCalculator()

calc = get_calculator()

def render():
    st.title("🏭 Escopo 1: Combustão Estacionária")
    st.markdown("Preencha as informações da Fonte.")

    # 1. Seleção de Setor e Combustível
    col_topo1, col_topo2 = st.columns(2)
    with col_topo1:
        setor = st.selectbox("Fatores de emissão para o setor:", calc.get_setores())
    with col_topo2:
        lista_combustiveis = calc.get_combustiveis_estacionaria()
        combustivel_selecionado = st.selectbox("Combustível Utilizado:", lista_combustiveis)
        unidade_atual = calc.get_unidade(combustivel_selecionado)

    st.divider()

    # 2. Formulário
    st.subheader("Registro da Fonte")
    with st.form("form_estacionaria", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1: reg_fonte = st.text_input("Registro da Fonte (ID)")
        with c2: desc_fonte = st.text_input("Descrição da Fonte")
        with c3: quantidade = st.number_input(f"Quantidade ({unidade_atual})", min_value=0.0)

        submitted = st.form_submit_button("➕ Adicionar à Tabela 1", type="primary")

        if submitted and quantidade > 0:
            res = calc.calcular_estacionaria(combustivel_selecionado, quantidade)
            
            # --- MAPEAMENTO COMPLETO DA TABELA 1 ---
            novo_lancamento = {
                "Registro": reg_fonte,
                "Descrição": desc_fonte,
                "Combustível": combustivel_selecionado,
                "Unidade": unidade_atual,
                "Quantidade Total": quantidade,

                # Formação do Combustível (Nomes)
                "Comp. Fóssil": res['componente_fossil'],
                "Comp. Bio": res['componente_bio'],

                # Quantidades Consumidas (Separadas)
                "Qtd Fóssil": res['qtd_fossil'],
                "Qtd Bio": res['qtd_bio'],

                # Fatores de Emissão - Fóssil
                "FE Fóssil CO2 (kg/un)": res['fatores_fossil']['CO2'],
                "FE Fóssil CH4 (kg/un)": res['fatores_fossil']['CH4'],
                "FE Fóssil N2O (kg/un)": res['fatores_fossil']['N2O'],

                # Fatores de Emissão - Bio
                "FE Bio CO2 (kg/un)": res['fatores_bio']['CO2'],
                "FE Bio CH4 (kg/un)": res['fatores_bio']['CH4'],
                "FE Bio N2O (kg/un)": res['fatores_bio']['N2O'],

                # Emissões Fósseis (em Toneladas)
                "Emis. Fóssil CO2 (t)": res['emis_fossil']['CO2'] / 1000,
                "Emis. Fóssil CH4 (t)": res['emis_fossil']['CH4'] / 1000,
                "Emis. Fóssil N2O (t)": res['emis_fossil']['N2O'] / 1000,

                # Emissões Bio (em Toneladas)
                "Emis. Bio CO2 (t)": res['emis_bio']['CO2'] / 1000,
                "Emis. Bio CH4 (t)": res['emis_bio']['CH4'] / 1000,
                "Emis. Bio N2O (t)": res['emis_bio']['N2O'] / 1000,

                # Resultados Finais
                "Total GEE (tCO2e)": res['total_gee'],
                "Biogênicas (tCO2)": res['total_biogenico']
            }
            
            st.session_state['inventario'].append(novo_lancamento)
            st.success("Fonte adicionada com sucesso!")

    # 3. Visualização da Tabela 1 (Completa)
    st.write("---")
    st.subheader("Tabela 1. Inventário de Emissões (Detalhada)")
    
    if len(st.session_state['inventario']) > 0:
        df = pd.DataFrame(st.session_state['inventario'])
        
        # Aqui configuramos para mostrar TUDO o que o usuário pediu
        # Usamos column_config para formatar números com muitas casas decimais
        st.dataframe(
            df, 
            use_container_width=True,
            column_config={
                "Quantidade Total": st.column_config.NumberColumn(format="%.2f"),
                "Qtd Fóssil": st.column_config.NumberColumn(format="%.2f"),
                "Qtd Bio": st.column_config.NumberColumn(format="%.2f"),
                "Total GEE (tCO2e)": st.column_config.NumberColumn(format="%.4f"),
                "Biogênicas (tCO2)": st.column_config.NumberColumn(format="%.4f"),
                # Formatações para fatores (geralmente pequenos)
                "FE Fóssil CH4 (kg/un)": st.column_config.NumberColumn(format="%.5f"),
                "FE Bio CH4 (kg/un)": st.column_config.NumberColumn(format="%.5f"),
            }
        )
    else:
        st.info("Nenhum registro ainda.")

    # 4. Visualização da Tabela 2 (Resumo)
    st.write("##")
    st.subheader("Tabela 2. Resumo por Tipo de Combustível")
    try:
        dados_t2_fossil, dados_t2_bio = calc.gerar_tabela_2(st.session_state['inventario'], setor)
        
        c_t2_1, c_t2_2 = st.columns(2)
        with c_t2_1:
            st.markdown("**Combustíveis Fósseis**")
            st.dataframe(pd.DataFrame(dados_t2_fossil), use_container_width=True, hide_index=True)
        with c_t2_2:
            st.markdown("**Biocombustíveis**")
            st.dataframe(pd.DataFrame(dados_t2_bio), use_container_width=True, hide_index=True)
    except Exception as e:
        st.warning(f"Ainda não há dados suficientes para gerar a Tabela 2. ({str(e)})")