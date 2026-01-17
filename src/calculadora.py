import json
import pandas as pd
import os

class GHGCalculator:
    def __init__(self, data_path='data/fatores.json', csv_path='data/lista_comb.csv'):
        # 1. Carrega Fatores
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                self.db = json.load(f)
        else:
            self.db = {
                "gwp": {"CO2": 1, "CH4": 28, "N2O": 265},
                "combustao_estacionaria": {},
                "fatores_base": {}
            }
        
        # 2. Carrega CSV
        try:
            self.df_comb = pd.read_csv(csv_path, encoding='utf-8')
        except UnicodeDecodeError:
            self.df_comb = pd.read_csv(csv_path, encoding='latin1')
        except FileNotFoundError:
            self.df_comb = pd.DataFrame(columns=['Combustível', 'Unidade', 'Combustível fóssil', 'biocombustível'])
            
        self.gwp = self.db.get('gwp', {"CO2": 1, "CH4": 28, "N2O": 265})

    def get_setores(self):
        return [
            "Energia",
            "Manufatura ou Construção",
            "Comercial ou Institucional",
            "Residencial, Agricultura, Florestal ou Pesca"
        ]

    def get_combustiveis_estacionaria(self):
        if not self.df_comb.empty:
            return self.df_comb['Combustível'].unique().tolist()
        return []

    def get_unidade(self, nome_combustivel):
        if not self.df_comb.empty:
            item = self.df_comb[self.df_comb['Combustível'] == nome_combustivel]
            if not item.empty:
                return item.iloc[0]['Unidade']
        return "unidade"

    def _get_fator_do_db(self, nome_tecnico):
        if nome_tecnico == "-" or 'fatores_base' not in self.db or nome_tecnico not in self.db['fatores_base']:
            return {"CO2": 0, "CH4": 0, "N2O": 0}
        return self.db['fatores_base'][nome_tecnico]

    def calcular_estacionaria(self, nome_comercial, quantidade):
        # 1. Definição do CSV
        item = self.df_comb[self.df_comb['Combustível'] == nome_comercial].iloc[0]
        comp_fossil = item['Combustível fóssil']
        comp_bio = item['biocombustível']
        
        # 2. Frações (Mistura)
        dados_mistura = self.db.get('combustao_estacionaria', {}).get(nome_comercial)
        if dados_mistura and 'fracao_fossil' in dados_mistura:
            fracao_f = dados_mistura['fracao_fossil']
            fracao_b = dados_mistura['fracao_bio']
        else:
            tem_fossil = comp_fossil != "-"
            tem_bio = comp_bio != "-"
            if tem_fossil and tem_bio:
                fracao_f = 0.88; fracao_b = 0.12 
            elif tem_fossil:
                fracao_f = 1.0; fracao_b = 0.0
            elif tem_bio:
                fracao_f = 0.0; fracao_b = 1.0
            else:
                fracao_f = 0.0; fracao_b = 0.0

        # 3. Quantidades Reais
        qtd_fossil = quantidade * fracao_f
        qtd_bio = quantidade * fracao_b
        
        # 4. Busca Fatores
        fator_f = self._get_fator_do_db(comp_fossil)
        fator_b = self._get_fator_do_db(comp_bio)
        
        # 5. Cálculo Emissões
        emis_fossil = {
            "CO2": qtd_fossil * fator_f['CO2'],
            "CH4": qtd_fossil * fator_f['CH4'],
            "N2O": qtd_fossil * fator_f['N2O']
        }
        emis_bio = {
            "CO2": qtd_bio * fator_b['CO2'],
            "CH4": qtd_bio * fator_b['CH4'],
            "N2O": qtd_bio * fator_b['N2O']
        }
        
        # 6. Totalização tCO2e
        tco2e_total = (
            (emis_fossil['CO2']*self.gwp['CO2']) + 
            (emis_fossil['CH4']*self.gwp['CH4']) + 
            (emis_fossil['N2O']*self.gwp['N2O']) +
            (emis_bio['CH4']*self.gwp['CH4']) +   
            (emis_bio['N2O']*self.gwp['N2O'])     
        ) / 1000.0
        
        tco2_biogenico = (emis_bio['CO2'] * self.gwp['CO2']) / 1000.0

        return {
            "qtd_fossil": qtd_fossil, "qtd_bio": qtd_bio,
            "emis_fossil": emis_fossil, "emis_bio": emis_bio,
            "fatores_fossil": fator_f, "fatores_bio": fator_b,
            "total_gee": tco2e_total, "total_biogenico": tco2_biogenico,
            "componente_fossil": comp_fossil, "componente_bio": comp_bio
        }

    def get_lista_tabela2_ref(self):
        # Mantenha sua lista completa aqui. Estou colocando a abreviada apenas para exemplo.
        # USE A LISTA COMPLETA QUE JÁ TEMOS.
        frosseis = [{"id": 25, "nome": "Gasolina Automotiva (pura)", "unidade": "Litros"}, {"id": 32, "nome": "Óleo Diesel (puro)", "unidade": "Litros"}] 
        bios = [{"id": 49, "nome": "Etanol Anidro", "unidade": "Litros"}, {"id": 52, "nome": "Biodiesel (B100)", "unidade": "Litros"}]
        return frosseis, bios

    def gerar_tabela_2(self, lista_inventario, setor_selecionado):
        ref_fossil, ref_bio = self.get_lista_tabela2_ref()
        acumulado = {}
        for item in lista_inventario:
            nf = item.get('componente_fossil'); qf = item.get('Qtd Fóssil', 0)
            if nf and nf != "-": acumulado[nf] = acumulado.get(nf, 0.0) + qf
            nb = item.get('componente_bio'); qb = item.get('Qtd Bio', 0)
            if nb and nb != "-": acumulado[nb] = acumulado.get(nb, 0.0) + qb
            
        def monta_linhas(referencias):
            linhas = []
            for ref in referencias:
                c = acumulado.get(ref['nome'], 0.0)
                f = self._get_fator_do_db(ref['nome'])
                linhas.append({
                    "Nº ref": ref['id'], "Tipo de combustível": ref['nome'], "Unidade": ref['unidade'],
                    "Consumo Total": c, "Fator CO2 (kg/un)": f.get('CO2',0), "Fator CH4": f.get('CH4',0), "Fator N2O": f.get('N2O',0)
                })
            return linhas
        return monta_linhas(ref_fossil), monta_linhas(ref_bio)

    # --- NOVO MÉTODO PARA TABELA 3 ---
    def calcular_tabela3_inputs_diretos(self, co2_fossil, ch4, n2o):
        """
        Calcula o tCO2e total baseado nos inputs diretos em toneladas.
        Fórmula: Soma(EmissãoGás * GWP)
        """
        total_gee = (
            (co2_fossil * self.gwp['CO2']) +
            (ch4 * self.gwp['CH4']) +
            (n2o * self.gwp['N2O'])
        )
        return total_gee