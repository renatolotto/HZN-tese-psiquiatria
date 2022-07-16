import pandas as pd 
import streamlit as st
import numpy as np
import plotly.express as px
from io import BytesIO
# import SessionState
from pyxlsb import open_workbook as open_xlsb
import base64
import io
from fuzzywuzzy import fuzz
from unidecode import unidecode
    
st.set_page_config(page_title='Dashboard SM') #layout="wide",


def is_authenticated(password):
    return password == "hzn123"


def generate_login_block():
    block1 = st.empty()
    block2 = st.empty()

    return block1, block2


def clean_blocks(blocks):
    for block in blocks:
        block.empty()


def login(blocks):
    blocks[0].markdown("""
            <style>
                input {
                    -webkit-text-security: disc;
                }
            </style>
        """, unsafe_allow_html=True)

    return blocks[1].text_input('Password')

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def main():

    st.image('logo (4).png')

    st.title('Tese Saúde Mental')

    st.header('Analytics para Deal Origination')
    
    st.caption('Importante que a equipe da Clínica da Gávea confirme os dados com os responsáveis pelos ativos-alvo antes de tomar decisões de investimento. Há limitações de acuracidade dos dados, já que são provenientes de bases públicas, scraping, cruzamentos entre bases que nem sempre contém chave-única, etapas manuais que podem estar sujeitas a erros.')
    options1 = st.selectbox('2 -Escolha o tipo de base que deseja fazer o download',
         ('Dados Entrega','Dados Apresentacao'), 1)

    # @st.cache
    def load_col():
        col = pd.read_excel('bases_download_novos nomes_220527.xlsx')
        return col
    col=load_col()
    # st.write(col)

    dict_col_name = col[(col['coluna']!='x')&(col['coluna']!=col['new name'])&(col['coluna'].notna())&(col['new name'].notna())]
    dict_col_name = dict_col_name.set_index('coluna')['new name'].to_dict()
    
    ##ETAPA 1
    st.subheader('Etapa 1: Levantamento de Estabelecimentos (CNES)')

    @st.cache
    def load1():
        df1 = pd.read_csv('total.csv', sep = ';', encoding = 'latin1')
        return df1
    st.table(load1())

    ##ETAPA 2
    st.subheader('Etapa 2: Seleção de Estabelecimentos Ativos (CNES)')

    @st.cache
    def load2():
        df2 = pd.read_csv('total_clean.csv', sep = ';', encoding = 'latin1')
        return df2
    st.table(load2())

    @st.cache
    def load_df():
        df = pd.read_csv('base3.csv',dtype={'cnpj': object,'CNPJ': object,'cep': object,'CEP': object,'CNPJ_8_Digitos':object})#, sep = ';', encoding = 'latin1'

        df['leitos_interesse_sus'] = df['leitos_interesse'] - df['leitos_sus']
        df['leitos_interesse'] = df['leitos_interesse'].fillna(0)
        df['leitos_interesse_sus'] = df['leitos_interesse_sus'].fillna(0)
        df['percentual_sus'] = 100*df.leitos_total_SUS/df.leitos_total
        df['percentual_sm'] = 100*(df.leitos_interesse+df.leitos_sus)/df.leitos_total
        df['latitude'] = df['latitude'].str.replace(',','.').astype(float)
        df['longitude'] = df['longitude'].str.replace(',','.').astype(float)
        df = df[df['Natureza Jurídica'].isin(['ENTIDADES EMPRESARIAIS','ENTIDADES SEM FINS LUCRATIVOS'])]
        df = df[df['Motitivo desabilitação'].isna()]
        df['funci_interesse'] = df['funci_interesse'].fillna(0).astype(int)
        return df
    df=load_df()
    df3=df.copy()
    
    #filtering columns, pra processar só o necessário...em cada download tem outro filtro de colunas
    # cols_to_start = col[(col[options1] == 1.0)&(col.coluna != 'x')&(col.coluna != 'grupo leitos')&(col.coluna != 'etapa_filtrado')]['coluna'].to_list()
    # cols_to_start.extend(['leitos_interesse_sus','percentual_sus','funci_interesse'])#,'filtrado motivo: # leitos SM','filtrado motivo: # profissionais SM'
    # df3 = df3[cols_to_start]

    ##ETAPA 3
    st.subheader('Etapa 3: Exclusao de Empresas Públicas e Pessoas Fisicas Seleção de empresas por # de leitos e profissionais SM, exclusão empresas públicas/PFs')
    df3 = df3[df3['Natureza Jurídica'].isin(['ENTIDADES EMPRESARIAIS','ENTIDADES SEM FINS LUCRATIVOS'])]
    
    lm = st.slider('Mínimo # de Leitos Saúde Mental (exSUS)',1,100)
    st.write('ou')
    fm = st.slider('Mínimo # de funcionários Saúde Mental',1,100)

    df3['percentual_sus'] = 100*df3.leitos_total_SUS/df3.leitos_total
    df3['percentual_sm'] = 100*(df3.leitos_interesse+df3.leitos_sus)/df3.leitos_total

    df3_show1 = df3[((df3.funci_interesse >= fm)|(df3.leitos_interesse_sus >= lm))].groupby('Natureza Jurídica').agg({'cnes':'count','leitos_interesse_sus': 'sum', 'funci_interesse': 'sum'}).reset_index().rename(columns = {'cnes':'Estabelecimentos','leitos_interesse_sus': 'Leitos SM exSUS', 'funci_interesse': 'Funcionários SM'})#[((df3.funci_interesse >= fm)|(df3.leitos_interesse_sus >= lm))]
    df3_show1 = df3_show1.append(pd.DataFrame([['TOTAL',df3_show1['Estabelecimentos'].sum(),df3_show1['Leitos SM exSUS'].sum(),df3_show1['Funcionários SM'].sum()]], columns = df3_show1.columns))
    st.table(df3_show1.rename(columns ={'Natureza Jurídica':'Tipo de estabelecimento'} ))

    ##ETAPA 4
    st.subheader('Etapa 4: Seleção de Estabelecimentos Ativos (RF)')
    
    df3 = df3[(df3.situacao=='ATIVA')]

    df3_show = df3[((df3.funci_interesse >= fm)|(df3.leitos_interesse_sus >= lm))].groupby('Natureza Jurídica').agg({'cnes':'count','leitos_interesse_sus': 'sum', 'funci_interesse': 'sum'}).reset_index().rename(columns = {'cnes':'Estabelecimentos','leitos_interesse_sus': 'Leitos SM exSUS', 'funci_interesse': 'Funcionários SM'})#[((df3.funci_interesse >= fm)|(df3.leitos_interesse_sus >= lm))]
    df3_show = df3_show.append(pd.DataFrame([['TOTAL',df3_show['Estabelecimentos'].sum(),df3_show['Leitos SM exSUS'].sum(),df3_show['Funcionários SM'].sum()]], columns = df3_show.columns))
    st.table(df3_show.rename(columns ={'Natureza Jurídica':'Tipo de estabelecimento'} ))

    ##ETAPA 5
    st.subheader('Etapa 5: Divisão de estabelecimentos em grupos A e B')
    st.write('Use o filtro abaixo para dividir os grupos.')
    lsm = st.slider('# de leitos SM exSUS para classificar estabelecimentos',0,100, 10)

    
    df3['grupo leitos'] = np.where(df3.leitos_interesse_sus  >= lsm , str(lsm)+' Leitos ou mais (Grupo A)', 'Menos de '+str(lsm)+' leitos (Grupo B)')
    df3['Grupo'] = np.where(df3.leitos_interesse_sus  >= lsm , 'A', 'B')

    df4 = df3[((df3.funci_interesse >= fm)|(df3.leitos_interesse_sus >= lm))].groupby('grupo leitos').agg({'cnes':'count','leitos_interesse_sus': 'sum', 'funci_interesse': 'sum'}).reset_index().rename(columns = {'cnes':'Estabelecimentos','leitos_interesse_sus': 'Leitos SM exSUS', 'funci_interesse': 'Funcionários SM','grupo leitos':'Leitos'})
    df4 = df4.append(pd.DataFrame([['Total',df4['Estabelecimentos'].sum(),df4['Leitos SM exSUS'].sum(),df4['Funcionários SM'].sum()]], columns = df4.columns))
    st.table(df4.rename(columns = {'index':'Leitos'}))

    #MAPA ETAPA 5
    st.write('Distribuição dos estabelecimentos: Grupos A e B')
    fig = px.scatter_mapbox(df3[((df3.funci_interesse >= fm)|(df3.leitos_interesse_sus >= lm))], lat="latitude", lon="longitude", zoom=9, title = 'Distribuição dos estabelecimentos ativos', color ='grupo leitos', hover_name = 'Nome Fantasia', hover_data = ['Município','UF','leitos_interesse','funci_interesse'])

    fig.update_layout(
        mapbox = {'style': "open-street-map", 'center': {'lon': -48.5, 'lat': -14.5}, 'zoom': 3},
        showlegend = True,
        margin = {'l':0, 'r':0, 'b':0, 't':0},
        title = 'Distribuição dos estabelecimentos ativos')

    st.plotly_chart(fig, use_container_width=True)

    ##DOWNLOAD ETAPA 5
    df_xlsx_filt = df3[((df3.funci_interesse >= fm)|(df3.leitos_interesse_sus >= lm))].sort_values(by = ['base_referencia_97', '# Leitos SM não SUS'], ascending = [False , False])
    #filtrando colunas
    cols_to_show = col[(col[options1] == 1.0)&(col.coluna != 'x')&(col.coluna.notnull())&(col.coluna != 'etapa_filtrado')]['coluna'].to_list()
    df_xlsx_filt = df_xlsx_filt[cols_to_show]
    #renomeando colunas
    dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
    df_xlsx_filt = df_xlsx_filt.rename(columns=dictfilt(dict_col_name, list(df_xlsx_filt.columns)))
    df_xlsx_filt = to_excel(df_xlsx_filt) 

    st.download_button(label='📥 Download estabelecimentos SM',
                                    data=df_xlsx_filt ,
                                    file_name= 'estabelecimentos_saude_mental_filtrado.xlsx')

    ##ETAPA 6A
    st.subheader('Etapa 6A: Seleção de Estabelecimentos com mais de '+str(lsm)+' Leitos SM exSUS (+Dados Google + Transunion + Escavador + Keyword Crawler)')

    mls = st.slider('Máximo % de Leitos SUS',0,100,30)
    mlsm = st.slider('Mínimo % de Leitos Saúde Mental / Total de Leitos',0,100,35)


    df5A = df3[((df3.funci_interesse >= fm)|(df3.leitos_interesse_sus >= lm))& #regra da etapa anterior
        (df3.leitos_interesse_sus >= lsm)&(df3.percentual_sus <= mls)&(df3.percentual_sm >= mlsm)&(df3.situacao=='ATIVA')]#regra da etapa atual
   
    # calculo de encontramento
    # encontramento_RF = 100*df5A['CNPJ'].notnull().sum()/df5A.shape[0]
    # encontramento_GMN = 100*df5A['URL Site'].notnull().sum()/df5A.shape[0]
    # encontramento_Escavador = 100*df5A[df5A['processos']!='Não foi possível identificar processos na base do escavador'].shape[0]/df5A.shape[0]
    # encontramento_Transunion = 100*df5A['faturamento_presumido'].notnull().sum()/df5A.shape[0]
    # st.write('Encontramentos')
    # st.write('df_A_lenght',df5A.shape[0])
    # st.write('RF:',round(encontramento_RF,2),'%')
    # st.write('GMN:',round(encontramento_GMN,2),'%')
    # st.write('Escavador:',round(encontramento_Escavador,2),'%')
    # st.write('Transunion:',round(encontramento_Transunion,2),'%')

    df6 = df5A.groupby('base_referencia_97').agg({'cnes':'count','leitos_interesse_sus': 'sum', 'funci_interesse': 'sum'}).reset_index().rename(columns = {'cnes':'Estabelecimentos','leitos_interesse_sus': 'Leitos SM exSUS', 'funci_interesse': 'Funcionários SM'})
    df6 = df6.append(pd.DataFrame([['total',df6['Estabelecimentos'].sum(),df6['Leitos SM exSUS'].sum(),df6['Funcionários SM'].sum()]], columns = df6.columns))
    st.table(df6)

    st.write('Distribuição dos estabelecimentos tipo A')
    fig = px.scatter_mapbox(df5A, lat="latitude", lon="longitude", zoom=9, title = 'Distribuição dos estabelecimentos ativos', color = 'base_referencia_97', hover_name = 'Nome Fantasia', hover_data = ['Município','UF','leitos_interesse','funci_interesse'])
    fig.update_layout(
        mapbox = {'style': "open-street-map", 'center': {'lon': -48.5, 'lat': -14.5}, 'zoom': 3},
        showlegend = True,
        margin = {'l':0, 'r':0, 'b':0, 't':0},
        title = 'Distribuição dos estabelecimentos ativos')
    st.plotly_chart(fig, use_container_width=True)

    #df etapa 6A
    #filtrando colunas
    cols_to_show = col[(col[options1] == 1.0)&(col.coluna != 'x')&(col.coluna.notnull())&(col.coluna != 'etapa_filtrado')]['coluna'].to_list()
    df5A = df5A[cols_to_show]
    df5A = df5A.rename(columns=dictfilt(dict_col_name, list(df5A.columns)))
    df_xlsx5a = to_excel(df5A.sort_values(by = ['base_referencia_97', '# Leitos SM não SUS'], ascending = [False , False]))
    st.download_button(label='📥 Download estabelecimentos Grupo A',
                                    data=df_xlsx5a ,
                                    file_name= 'ativos_A.xlsx')
    
    ##ETAPA 6B
    st.subheader('Etapa 6B: Seleção de Estabelecimentos com menos de '+str(lsm)+' Leitos SM exSUS (+Dados Google + Transunion + Escavador + Keyword Crawler)')

    options = st.multiselect('Natureza Juridica CNES',
         ['ENTIDADES EMPRESARIAIS','ENTIDADES SEM FINS LUCRATIVOS'],
         ['ENTIDADES EMPRESARIAIS'])

    mps = st.slider('# Minimo Profissionais de SM',0,100,5)
    mp = st.slider('# Minimo Psiquiatras',1,100,1)
    pp = st.slider('Mínimo % Profissionais de SM',1,100,30)
    lp = st.slider('Limite de # de Processos',0,1000,5000)
    df5B = df3[((df3.funci_interesse >= fm)|(df3.leitos_interesse_sus >= lm))& #regra da etapa anterior
        (df3['Natureza Jurídica'].isin(options))&(df3.leitos_interesse_sus <= lsm)&(df3.funci_interesse/df['TOTAL FUNCIONARIOS'] >= pp/100)&(df3.funci_interesse >= mps)&(df3['MEDICO PSIQUIATRA'] >= mp)&(df3.processos.apply(lambda x: 0 if type(x) == str else x) <= lp)&(df3.situacao=='ATIVA')]
    
    # calculo de encontramento
    # encontramento_RF = 100*df5B['CNPJ'].notnull().sum()/df5B.shape[0]
    # encontramento_GMN = 100*df5B['URL Site'].notnull().sum()/df5B.shape[0]
    # encontramento_Escavador = 100*df5B[df5B['processos']!='Não foi possível identificar processos na base do escavador'].shape[0]/df5B.shape[0]
    # encontramento_Transunion = 100*df5B['faturamento_presumido'].notnull().sum()/df5B.shape[0]
    # st.write('Encontramentos')
    # st.write('df_b_lenght',df5B.shape[0])
    # st.write('RF:',round(encontramento_RF,2),'%')
    # st.write('GMN:',round(encontramento_GMN,2),'%')
    # st.write('Escavador:',round(encontramento_Escavador,2),'%')
    # st.write('Transunion:',round(encontramento_Transunion,2),'%')

    df6 = df5B.groupby('base_referencia_97').agg({'cnes':'count','leitos_interesse_sus': 'sum', 'funci_interesse': 'sum'}).reset_index().rename(columns = {'cnes':'Estabelecimentos','leitos_interesse_sus': 'Leitos SM exSUS', 'funci_interesse': 'Funcionários SM'})
    df6 = df6.append(pd.DataFrame([['total',df6['Estabelecimentos'].sum(),df6['Leitos SM exSUS'].sum(),df6['Funcionários SM'].sum()]], columns = df6.columns))
    st.table(df6)

    st.write('Distribuição dos estabelecimentos tipo B')
    fig = px.scatter_mapbox(df5B, lat="latitude", lon="longitude", zoom=9, title = 'Distribuição dos estabelecimentos ativos', color = 'base_referencia_97', hover_name = 'Nome Fantasia', hover_data = ['Município','UF','leitos_interesse','funci_interesse'])
    fig.update_layout(
        mapbox = {'style': "open-street-map", 'center': {'lon': -48.5, 'lat': -14.5}, 'zoom': 3},
        showlegend = True,
        margin = {'l':0, 'r':0, 'b':0, 't':0},
        title = 'Distribuição dos estabelecimentos ativos')
    st.plotly_chart(fig, use_container_width=True)

    #df etapa 6B
    #filtrando colunas
    cols_to_show = col[(col[options1] == 1.0)&(col.coluna != 'x')&(col.coluna.notnull())&(col.coluna != 'etapa_filtrado')]['coluna'].to_list()
    df5B = df5B[cols_to_show]
    df5B = df5B.rename(columns=dictfilt(dict_col_name, list(df5B.columns)))
    df_xlsx = to_excel(df5B.sort_values(by = ['base_referencia_97', '# Psiquiatras'], ascending = [False, False]))
    st.download_button(label='📥 Download estabelecimentos Grupo B',
                                    data=df_xlsx ,
                                    file_name= 'ativos_B.xlsx')

    
    
    # ETAPA 7 - DOWNLOAD DE BASE COMPLETA 19K COM MOTIVOS
    st.subheader('Dowload de base de {} estabelecimentos de sáude mental'.format(df3.shape[0]))

    ##ETAPA QUE ESTAB CHEGOU
    df3['passou_da_3'] = np.where((df3.leitos_interesse_sus >= lm) | (df3.funci_interesse >= fm),'1','0')

    #filtro etapa 3
    df3['parou_etapa_3'] = np.where((df3.leitos_interesse_sus >= lm) | (df3.funci_interesse >= fm),'','3')
    # df3['filtrado motivo: # leitos SM'] = np.where(df3.leitos_interesse_sus >= lm, '', 'Menos que '+str(lm)+' leitos')#str(lm)+' leitos ou mais'
    # df3['filtrado motivo: # profissionais SM'] = np.where(df3.funci_interesse >= fm, '', 'Menos que '+str(fm)+' funcionários')#str(fm)+' funcionários ou mais'
    #filtros etapa 6A
    df3['parou_etapa_6A'] = np.where(((df3.leitos_interesse_sus >= lm) | (df3.funci_interesse >= fm))&#regra etapa anterior
        (df3.percentual_sus  <= mls)&(df3.Grupo=='A')&(df3.percentual_sm  >= mlsm)&(df3.situacao=='ATIVA'),'','6A')#atual
    # df3['filtrado motivo - Máximo % de Leitos SUS (Grupo A)'] = np.where(((df3.leitos_interesse_sus >= lm) | (df3.funci_interesse >= fm))&#regra da etapa anterior
    # (df3.percentual_sus  <= mls)&(df3.Grupo=='A') , ' ', 'Maior que '+str(mls)+'%')#regra da etapa atual
    # df3['filtrado motivo - Mínimo % de Leitos Saúde Mental / Total de Leitos (Grupo A)'] = np.where(
    #     ((df3.leitos_interesse_sus >= lm) | (df3.funci_interesse >= fm))&#regra etapa anterior
    #     (df3.percentual_sm  >= mlsm) &(df3.Grupo=='A'),'' , 'Menor que '+str(mlsm)+'%')#etapa atual
    # filtros etapa 6B
    df3['parou_etapa_6B'] = np.where(((df3.funci_interesse >= fm)|(df3.leitos_interesse_sus >= lm))& #regra da etapa anterior
    (df3['Natureza Jurídica'].isin(options))&(df3.Grupo=='B')&(df3.funci_interesse >= mps)&(df3['MEDICO PSIQUIATRA'] >= mp)&(df3.funci_interesse/df3['TOTAL FUNCIONARIOS'] >= pp/100)&(df3.processos.apply(lambda x: 0 if type(x) == str else x) <= lp),'','6B')
    # df3['filtrado motivo - Natureza Jurídica (Grupo B)'] = np.where((df3['Natureza Jurídica'].isin(options)) &(df3.Grupo=='B'), '', 'Não Atende Natureza Jurídica')#Atende Natureza Jurídica
    # df3['filtrado motivo - # Mínimo Profissionais de SM (Grupo B)'] = np.where((df3.funci_interesse >= mps) &(df3.Grupo=='B'), '', 'Menos que '+str(mps)+' profissionais') #str(mps)+' profissionais ou mais' 
    # df3['filtrado motivo - # Mínimo Psiquiatras (Grupo B)'] = np.where((df3['MEDICO PSIQUIATRA'] >= mp) &(df3.Grupo=='B'), '', 'Menos que '+str(mps)+' psiquiatras')#str(mps)+' psiquiatras ou mais'
    # df3['filtrado motivo - Mínimo % Profissionais de SM (Grupo B)'] = np.where((df3.funci_interesse/df3['TOTAL FUNCIONARIOS'] >= pp/100) &(df3.Grupo=='B'),'' , 'Menor que '+str(mps)+'%')#str(mps)+'% ou mais'
    # df3['filtrado motivo - Limite de # de Processos (Grupo B)'] = np.where((df3.processos.apply(lambda x: 0 if type(x) == str else x) <= lp) &(df3.Grupo=='B'), '', 'Mais que '+str(lp)+' processos')#str(lp)+' processos ou menos'
    
    #coluna com etapa que estab foi filtrado
    def conditions(s):
        if s['parou_etapa_3']=='3':
            return '3'
        elif s['parou_etapa_3']!='3' and s['parou_etapa_6A']=='6A' and s['Grupo']=='A':
            return '6A'
        elif s['parou_etapa_3']!='3' and s['parou_etapa_6B']=='6B'and s['Grupo']=='B':
            return '6B'
    df3['etapa_filtrado'] = df3.apply(conditions,axis=1)
    #ordenando colunas
    df3.drop(columns=['parou_etapa_4','parou_etapa_6A','parou_etapa_6B'],inplace=True)
    # st.write(df3.columns[-14:])

    #Encontrando %s de encontramentos
    # encontramento_RF = 100*df3['CNPJ'].notnull().sum()/df3.shape[0]
    # encontramento_GMN = 100*df3['URL Site'].notnull().sum()/df3.shape[0]
    # encontramento_Escavador = 100*df3[df3['processos']!='Não foi possível identificar processos na base do escavador'].shape[0]/df3.shape[0]
    # encontramento_Transunion = 100*df3['faturamento_presumido'].notnull().sum()/df3.shape[0]
    # st.write('Encontramentos')
    # st.write(df3.shape[0])
    # st.write('RF:',round(encontramento_RF,2),'%')
    # st.write('GMN:',round(encontramento_GMN,2),'%')
    # st.write('Escavador:',round(encontramento_Escavador,2),'%')
    # st.write('Transunion:',round(encontramento_Transunion,2),'%')

    # Fuzzys
    # Nome: CNES vs GMN (OK, coutinho já incluiu na base)
    # 


    #df total (19k explicando qual dado que foi filtrado)        
    df_xlsx = df3.sort_values(by = ['base_referencia_97', '# Leitos SM não SUS'], ascending = [False , False])
    #filtrando colunas
    cols_to_show = col[(col[options1] == 1.0)&(col.coluna != 'x')&(col.coluna.notnull())]['coluna'].to_list()
    # st.write(cols_to_show)
    df_xlsx = df_xlsx[cols_to_show]
    df_xlsx = df_xlsx.rename(columns=dictfilt(dict_col_name, list(df_xlsx.columns)))
    
    df_xlsx = to_excel(df_xlsx)    
    st.download_button(label='📥 Estabelecimentos Saúde Mental',
                                    data=df_xlsx ,
                                    file_name= 'estabelecimentos_saude_mental.xlsx')

    # st.write(df3['cnpj'].sample(20))

login_blocks = generate_login_block()
password = login(login_blocks)

if is_authenticated(password):
    clean_blocks(login_blocks)
    main()
elif password:
    st.info("Please enter a valid password")






