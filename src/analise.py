#%%
#Importando pacotes necessários
import os
from zipfile import ZipFile
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

#Caminho para os arquivos utilizados
pasta = r'E:\\Estudos\\Ciência de dados\\Projetos\\TSE_2024\\comparacao_eleicoes_2020_2024\\data'
arquivo_resultado_2024 = os.path.join(pasta, 'votacao_candidato_munzona_2024.zip')
arquivo_resultado_2020 = os.path.join(pasta, 'votacao_candidato_munzona_2020.zip')
arquivo_resultado_2016 = os.path.join(pasta, 'votacao_candidato_munzona_2016.zip')
arquivo_resultado_2012 = os.path.join(pasta, 'votacao_candidato_munzona_2012.zip')
arquivo_partidos_2024 = os.path.join(pasta,'partidos2024.csv')
arquivo_BR_municipios_shapefile = os.path.join(pasta, 'BR_Municipios_2022/BR_Municipios_2022.shp')

#%%
#alterando formato de exibição dos gráficos do Pandas
pd.options.plotting.backend = 'plotly'

#variáveis globais
LOCAL = 'BRASIL' # Recebe a sigla da UF ou BRASIL
TIPO_CANDIDATO = 'Prefeito' #Recebe Vereador pu Prefeito

#Sobe os dados nescessarios

with ZipFile(arquivo_resultado_2024) as z:
  with z.open(f'votacao_candidato_munzona_2024_{LOCAL}.csv') as f:
    resultado_2024 = pd.read_csv(f,sep=';',encoding='ISO-8859-1', decimal=',')

with ZipFile(arquivo_resultado_2020) as z:
  with z.open(f'votacao_candidato_munzona_2020_{LOCAL}.csv') as f:
    resultado_2020 = pd.read_csv(f,sep=';',encoding='ISO-8859-1', decimal=',')

with ZipFile(arquivo_resultado_2016) as z:
  with z.open(f'votacao_candidato_munzona_2016_{LOCAL}.csv') as f:
    resultado_2016 = pd.read_csv(f,sep=';',encoding='ISO-8859-1', decimal=',')

with ZipFile(arquivo_resultado_2012) as z:
  with z.open(f'votacao_candidato_munzona_2012_{LOCAL}.csv') as f:
    resultado_2012 = pd.read_csv(f,sep=';',encoding='ISO-8859-1', decimal=',')


#%%
# mostra todas as colunas e tipos de dados
resultado_2024.info()

#%%
## Pega os dados dos partidos

partidos = pd.read_csv(arquivo_partidos_2024, sep=';')

espec_type = pd.CategoricalDtype(categories=['direita', 'centro', 'esquerda'], ordered=True)
partidos['Espectro'] = partidos['Espectro'].astype(espec_type)

partidos.info()

#%%
# Carrega os dados da geolocalizacao
geo_df = gpd.read_file(arquivo_BR_municipios_shapefile)

if LOCAL != 'BRASIL':
  geo_df = geo_df[geo_df.SIGLA_UF == LOCAL]

geo_df['NM_MUN'] = geo_df['NM_MUN'].str.upper()
geo_df

#%%

 
votos_espectro_2024 = resultado_2024[(resultado_2024['DS_CARGO'] == TIPO_CANDIDATO)&(resultado_2024['NR_TURNO']==1)].groupby(['CD_MUNICIPIO', 'Espectro']).agg({'NM_URNA_CANDIDATO':'first'
                                                                                                                                                               ,'NM_MUNICIPIO':'first'
                                                                                                                                                               ,'SG_UF':'first'
                                                                                                                                                               ,'QT_VOTOS_NOMINAIS_VALIDOS':'sum'}).reset_index()
espectro_mais_votado_2024 = votos_espectro_2024.loc[votos_espectro_2024.groupby('CD_MUNICIPIO')['QT_VOTOS_NOMINAIS_VALIDOS'].idxmax()].reset_index(drop=True)
espectro_mais_votado_2024



#%%

resultado_2024 = resultado_2024.\
merge(partidos[['NR_PARTIDO','Espectro']], left_on='NR_PARTIDO', right_on='NR_PARTIDO')

resultado_2020 = resultado_2020.\
merge(partidos[['NR_PARTIDO','Espectro']], left_on='NR_PARTIDO', right_on='NR_PARTIDO')

resultado_2016 = resultado_2016.\
merge(partidos[['NR_PARTIDO', 'Espectro']], left_on='NR_PARTIDO', right_on='NR_PARTIDO')