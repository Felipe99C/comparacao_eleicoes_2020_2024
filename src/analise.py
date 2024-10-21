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
resultado_2016.info()

#%%
## Pega os dados dos partidos dentro do espectro politico

partidos = pd.read_csv(arquivo_partidos_2024, sep=';')

espec_type = pd.CategoricalDtype(categories=['direita', 'centro', 'esquerda'], ordered=True)
partidos['Espectro'] = partidos['Espectro'].astype(espec_type)
#%%
partidos.info()

#%%
# Carrega os dados da geolocalizacao
geo_df = gpd.read_file(arquivo_BR_municipios_shapefile)

if LOCAL != 'BRASIL':
  geo_df = geo_df[geo_df.SIGLA_UF == LOCAL]

geo_df['NM_MUN'] = geo_df['NM_MUN'].str.upper()
geo_df

#%%
###################################### Analise dos espectros vais votados no primeiro turno nas eleições #####################################################

# Faz o merge dos partidos com o espectro politico

resultado_2024 = resultado_2024.\
merge(partidos[['NR_PARTIDO','Espectro']], left_on='NR_PARTIDO', right_on='NR_PARTIDO', suffixes=('', '_partido'))

votos_espectro_2024 = resultado_2024[(resultado_2024['DS_CARGO']== TIPO_CANDIDATO)&(resultado_2024['NR_TURNO']==1)].groupby(['CD_MUNICIPIO','Espectro']).agg({'NM_MUNICIPIO':'first','SG_UF':'first','QT_VOTOS_NOMINAIS_VALIDOS':'sum'}).reset_index()
espectro_mais_votado_2024 = votos_espectro_2024.loc[votos_espectro_2024.groupby('CD_MUNICIPIO')['QT_VOTOS_NOMINAIS_VALIDOS'].idxmax()].reset_index(drop=True)
espectro_mais_votado_2024

resultado_2020 = resultado_2020.\
merge(partidos[['NR_PARTIDO','Espectro']], left_on='NR_PARTIDO', right_on='NR_PARTIDO',suffixes=('', '_partido'))

votos_espectro_2020 = resultado_2020[(resultado_2020['DS_CARGO']== TIPO_CANDIDATO)&(resultado_2020['NR_TURNO']==1)].groupby(['CD_MUNICIPIO','Espectro']).agg({'NM_MUNICIPIO':'first','SG_UF':'first','QT_VOTOS_NOMINAIS_VALIDOS':'sum'}).reset_index()
espectro_mais_votado_2020 = votos_espectro_2020.loc[votos_espectro_2020.groupby('CD_MUNICIPIO')['QT_VOTOS_NOMINAIS_VALIDOS'].idxmax()].reset_index(drop=True)
espectro_mais_votado_2020

resultado_2016 = resultado_2016.\
merge(partidos[['NR_PARTIDO','Espectro']], left_on='NR_PARTIDO', right_on='NR_PARTIDO',suffixes=('', '_partido'))

resultado_2012 = resultado_2012.\
merge(partidos[['NR_PARTIDO','Espectro']], left_on='NR_PARTIDO', right_on='NR_PARTIDO',suffixes=('', '_partido'))


#%%

# Grafico comparando os espectros mais votados em 2020 e 2024
espectro_mais_votado_2024_geo_df = geo_df.merge(espectro_mais_votado_2024, left_on='NM_MUN', right_on='NM_MUNICIPIO')
espectro_mais_votado_2020_geo_df = geo_df.merge(espectro_mais_votado_2020, left_on='NM_MUN', right_on='NM_MUNICIPIO')

fig, ax = plt.subplots(1,2,figsize=(28,10))
ax[0].set_title(f'Espectro Mais Votado {LOCAL} 2020 ({TIPO_CANDIDATO})', color='black', size=16)
ax[1].set_title(f'Espectro Mais Votado {LOCAL} 2024 ({TIPO_CANDIDATO})', color='black', size=16)

espectro_mais_votado_2020_geo_df.plot(column='Espectro', legend=True, cmap='coolwarm', ax=ax[0])
espectro_mais_votado_2024_geo_df.plot(column='Espectro', legend=True, cmap='coolwarm', ax=ax[1])


#%%

############################ Analise do espectro dos candidatos mais votados ######################################################
candidatos_mais_votados_2024 = resultado_2024[(resultado_2024['DS_CARGO']== TIPO_CANDIDATO)&(resultado_2024['NR_TURNO']== 1)]\
.groupby(['NR_CANDIDATO','NM_UE'])\
.agg({'Espectro' :'first','NM_URNA_CANDIDATO' :'first', 'NM_MUNICIPIO' :'first', 'CD_MUNICIPIO' :'first',
      'DS_SIT_TOT_TURNO' :'first', 'NR_PARTIDO' :'first',
      'SG_PARTIDO' :'first','QT_VOTOS_NOMINAIS' : 'sum' })\
      .sort_values(by='QT_VOTOS_NOMINAIS',ascending=False)\
      .drop_duplicates(subset=['CD_MUNICIPIO'],keep='first')


candidatos_mais_votados_2020 = resultado_2020[(resultado_2020['DS_CARGO']== TIPO_CANDIDATO) & (resultado_2020['NR_TURNO']== 1)]\
.groupby(['NR_CANDIDATO','NM_UE'])\
.agg({'Espectro' :'first','NM_URNA_CANDIDATO' :'first', 'NM_MUNICIPIO' :'first', 'CD_MUNICIPIO' :'first',
      'DS_SIT_TOT_TURNO' :'first', 'NR_PARTIDO' :'first',
      'SG_PARTIDO' :'first','QT_VOTOS_NOMINAIS' : 'sum' })\
      .sort_values(by='QT_VOTOS_NOMINAIS',ascending=False)\
      .drop_duplicates(subset=['CD_MUNICIPIO'],keep='first')

candidatos_mais_votados_2016 = resultado_2016[(resultado_2016['DS_CARGO']==TIPO_CANDIDATO)&(resultado_2016['NR_TURNO']== 1)]\
.groupby(['NR_CANDIDATO','NM_UE'])\
.agg({'Espectro' :'first','NM_URNA_CANDIDATO' :'first', 'NM_MUNICIPIO' :'first', 'CD_MUNICIPIO' :'first',
      'DS_SIT_TOT_TURNO' :'first', 'NR_PARTIDO' :'first',
      'SG_PARTIDO' :'first','QT_VOTOS_NOMINAIS' : 'sum' })\
      .sort_values(by='QT_VOTOS_NOMINAIS',ascending=False)\
      .drop_duplicates(subset=['CD_MUNICIPIO'],keep='first')

candidatos_mais_votados_2012 = resultado_2012[(resultado_2012['DS_CARGO']==TIPO_CANDIDATO)&(resultado_2012['NR_TURNO']== 1)]\
.groupby(['NR_CANDIDATO','NM_UE'])\
.agg({'Espectro' :'first','NM_URNA_CANDIDATO' :'first', 'NM_MUNICIPIO' :'first', 'CD_MUNICIPIO' :'first',
      'DS_SIT_TOT_TURNO' :'first', 'NR_PARTIDO' :'first',
      'SG_PARTIDO' :'first','QT_VOTOS_NOMINAIS' : 'sum' })\
      .sort_values(by='QT_VOTOS_NOMINAIS',ascending=False)\
      .drop_duplicates(subset=['CD_MUNICIPIO'],keep='first')
#%%

# Analisa a qtd de candidatos votados por partidos de 2012 a 2024 

#candidatos_mais_votados_2024.SG_PARTIDO.value_counts().plot(kind='bar',title=f'Partido Mais Votados {LOCAL} 2024 ({TIPO_CANDIDATO})')

#candidatos_mais_votados_2020.SG_PARTIDO.value_counts().plot(kind='bar',title=f'Partido Mais Votado {LOCAL} 2020 ({TIPO_CANDIDATO})')

#candidatos_mais_votados_2016.SG_PARTIDO.value_counts().plot(kind='bar', title=f'Partido Mais Votado {LOCAL} 2016 ({TIPO_CANDIDATO})')

candidatos_mais_votados_2012.SG_PARTIDO.value_counts().plot(kind='bar', title=f'Partido Mais Votado {LOCAL} 2012 ({TIPO_CANDIDATO})')

#%%
candidatos_mais_votados_2024_geo_df = geo_df.merge(candidatos_mais_votados_2024, left_on='NM_MUN', right_on='NM_MUNICIPIO')
candidatos_mais_votados_2020_geo_df = geo_df.merge(candidatos_mais_votados_2020, left_on='NM_MUN', right_on='NM_MUNICIPIO')
candidatos_mais_votados_2016_geo_df = geo_df.merge(candidatos_mais_votados_2016, left_on='NM_MUN', right_on='NM_MUNICIPIO')
candidatos_mais_votados_2012_geo_df = geo_df.merge(candidatos_mais_votados_2012, left_on='NM_MUN', right_on='NM_MUNICIPIO')

fig, ax = plt.subplots(1,2,figsize=(28,10))
ax[0].set_title(f'Espectro Candidato Mais Votado {LOCAL} 2020 ({TIPO_CANDIDATO})', color='black', size=16)
ax[1].set_title(f'Espectro Candidato Mais Votado {LOCAL} 2024 ({TIPO_CANDIDATO})', color='black', size=16)

candidatos_mais_votados_2020_geo_df.plot(column='Espectro', legend=True, cmap='coolwarm', ax=ax[0])
candidatos_mais_votados_2024_geo_df.plot(column='Espectro', legend=True, cmap='coolwarm', ax=ax[1])
#%%

fig, ax = plt.subplots(1,4,figsize=(28,10))

# Definindo títulos para os subplots
ax[0].set_title(f'Espectro Mais Votados {LOCAL} 2012 ({TIPO_CANDIDATO})', color='black', size=16)
ax[1].set_title(f'Espectro Mais Votados {LOCAL} 2016 ({TIPO_CANDIDATO})', color='black', size=16)
ax[2].set_title(f'Espectro Mais Votados {LOCAL} 2020 ({TIPO_CANDIDATO})', color='black', size=16)
ax[3].set_title(f'Espectro Mais Votados {LOCAL} 2024 ({TIPO_CANDIDATO})', color='black', size=16)

# Plotando os dados nos subplots corretos
candidatos_mais_votados_2012_geo_df.plot(column='Espectro', legend=True, cmap='coolwarm', ax=ax[0])
candidatos_mais_votados_2016_geo_df.plot(column='Espectro', legend=True, cmap='coolwarm', ax=ax[1])
candidatos_mais_votados_2020_geo_df.plot(column='Espectro', legend=True, cmap='coolwarm', ax=ax[2])
candidatos_mais_votados_2024_geo_df.plot(column='Espectro', legend=True, cmap='coolwarm', ax=ax[3])

# Ajustando o layout para evitar sobreposição
plt.tight_layout()
plt.show()