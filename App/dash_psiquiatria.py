import pandas as pd 
import streamlit as st
import numpy as np
import plotly.express as px
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb

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
    
    @st.cache
    def load_col():
        col = pd.read_excel('bases_download.xlsx')
        return col
    col=load_col()

    dict_col_name = pd.read_excel('bases_download_novos nomes_220513.xlsx')
    dict_col_name = dict_col_name[(dict_col_name['coluna']!='x')&(dict_col_name['coluna']!=dict_col_name['new name'])&(dict_col_name['coluna'].notna())]
    dict_col_name = dict_col_name.set_index('coluna')['new name'].to_dict()

    options1 = st.selectbox('Escolha o tipo de base que deseja fazer o download',
         ('Dados Entrega','Dados Apresentacao'), 1)

    st.subheader('Etapa 1: Levantamento de Estabelecimentos (CNES)')

    @st.cache
    def load1():
        df1 = pd.read_csv('total.csv', sep = ';', encoding = 'latin1')
        return df1
    st.table(load1())

    st.subheader('Etapa 2: Seleção de Estabelecimentos Ativos (CNES)')

    @st.cache
    def load2():
        df2 = pd.read_csv('total_clean.csv', sep = ';', encoding = 'latin1')
        return df2
    st.table(load2())
    
    st.subheader('Etapa 3: Exclusao de Empresas Publicas e Pessoas Fisicas Seleção de empresas por # de leitos e profissionais SM, exclusão empresas públicas/PFs')

    lm = st.slider('Mínimo # de Leitos Saúde Mental (exSUS)',0,100)

    st.write('ou')

    fm = st.slider('Mínimo # de funcionários Saúde Mental',0,100)

    lsm = st.slider('# de leitos SM exSUS para classificar estabelecimentos',0,100, 10)
    
    @st.cache
    def load_df():
        df = pd.read_csv('base.csv', sep = ';', encoding = 'latin1')
        return df
    df=load_df()

    df = df[col[(col[options1] == 1.0)&(col.coluna != 'x')]['coluna'].to_list()]

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

    df3 = df[(df.funci_interesse >= fm)|(df.leitos_interesse_sus >= lm)]

    leitos = np.where(df3.leitos_interesse_sus  >= lsm , str(lsm)+' Leitos ou mais', 'menos de '+str(lsm)+' Leitos')

    df4 = df3.groupby(leitos).agg({'cnes':'count','leitos_interesse_sus': 'sum', 'funci_interesse': 'sum'}).reset_index().rename(columns = {'cnes':'Estabelecimentos','leitos_interesse_sus': 'Leitos SM exSUS', 'funci_interesse': 'Funcionários SM'})

    df4 = df4.append(pd.DataFrame([['total',df4['Estabelecimentos'].sum(),df4['Leitos SM exSUS'].sum(),df4['Funcionários SM'].sum()]], columns = df4.columns))

    st.table(df4.rename(columns = {'index':'leitos'}))

    st.subheader('Etapa 4: Seleção de Estabelecimentos Ativos (RF)')

    df3 = df[((df.funci_interesse >= fm)|(df.leitos_interesse_sus >= lm))&(df.situacao=='ATIVA')]
    
    df3['percentual_sus'] = 100*df3.leitos_total_SUS/df3.leitos_total

    df3['percentual_sm'] = 100*(df3.leitos_interesse+df3.leitos_sus)/df3.leitos_total
   
    

    df3['leitos'] = np.where(df3.leitos_interesse_sus  >= lsm , str(lsm)+' Leitos ou mais', 'menos de '+str(lsm)+' Leitos')

    df4 = df3.groupby('leitos').agg({'cnes':'count','leitos_interesse_sus': 'sum', 'funci_interesse': 'sum'}).reset_index().rename(columns = {'cnes':'Estabelecimentos','leitos_interesse_sus': 'Leitos SM exSUS', 'funci_interesse': 'Funcionários SM'})

    df4 = df4.append(pd.DataFrame([['total',df4['Estabelecimentos'].sum(),df4['Leitos SM exSUS'].sum(),df4['Funcionários SM'].sum()]], columns = df4.columns))

    st.table(df4)

    st.write('Distribuição dos estabelecimentos ativos')

    fig = px.scatter_mapbox(df3, lat="latitude", lon="longitude", zoom=9, title = 'Distribuição dos estabelecimentos ativos', color ='leitos', hover_name = 'Nome Fantasia', hover_data = ['Município','UF','leitos_interesse','funci_interesse'])

    fig.update_layout(
        mapbox = {'style': "open-street-map", 'center': {'lon': -48.5, 'lat': -14.5}, 'zoom': 3},
        showlegend = True,
        margin = {'l':0, 'r':0, 'b':0, 't':0},
        title = 'Distribuição dos estabelecimentos ativos')

    st.plotly_chart(fig, use_container_width=True)

    # col = pd.read_excel('bases_download.xlsx')
    dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
    df3 = df3.rename(columns=dictfilt(dict_col_name, list(df3.columns)))
    df_xlsx = to_excel(df3.sort_values(by = ['base_referencia_97', '# Leitos SM não SUS'], ascending = [False , False]))
    
    st.download_button(label='📥 Download estabelecimentos SM',
                                    data=df_xlsx ,
                                    file_name= 'estabelecimentos_saude_mental.xlsx')


    st.subheader('Etapa 5A: Seleção de Estabelecimentos com mais de '+str(lsm)+' Leitos SM exSUS (+Dados Google + Transunion + Escavador + Keyword Crawler)')

    mls = st.slider('Máximo % de Leitos SUS',0,100,30)
    mlsm = st.slider('Mínimo % de Leitos Saúde Mental / Total de Leitos',0,100,35)

    df5 = df[(df.leitos_interesse_sus >= lsm)&(df.percentual_sus <= mls)&(df.percentual_sm >= mlsm)&(df.situacao=='ATIVA')]

    df6 = df5.groupby('base_referencia_97').agg({'cnes':'count','leitos_interesse_sus': 'sum', 'funci_interesse': 'sum'}).reset_index().rename(columns = {'cnes':'Estabelecimentos','leitos_interesse_sus': 'Leitos SM exSUS', 'funci_interesse': 'Funcionários SM'})

    df6 = df6.append(pd.DataFrame([['total',df6['Estabelecimentos'].sum(),df6['Leitos SM exSUS'].sum(),df6['Funcionários SM'].sum()]], columns = df6.columns))

    st.table(df6)

    st.write('Distribuição dos estabelecimentos tipo A')

    fig = px.scatter_mapbox(df5, lat="latitude", lon="longitude", zoom=9, title = 'Distribuição dos estabelecimentos ativos', color = 'base_referencia_97', hover_name = 'Nome Fantasia', hover_data = ['Município','UF','leitos_interesse','funci_interesse'])

    fig.update_layout(
        mapbox = {'style': "open-street-map", 'center': {'lon': -48.5, 'lat': -14.5}, 'zoom': 3},
        showlegend = True,
        margin = {'l':0, 'r':0, 'b':0, 't':0},
        title = 'Distribuição dos estabelecimentos ativos')

    st.plotly_chart(fig, use_container_width=True)

    dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
    df5 = df5.rename(columns=dictfilt(dict_col_name, list(df5.columns)))
    df_xlsx = to_excel(df5.sort_values(by = ['base_referencia_97', '# Leitos SM não SUS'], ascending = [False , False]))
    st.download_button(label='📥 Download estabelecimentos tipo A',
                                    data=df_xlsx ,
                                    file_name= 'ativos_A.xlsx')

    st.subheader('Etapa 5B: Seleção de Estabelecimentos com menos de '+str(lsm)+' Leitos SM exSUS (+Dados Google + Transunion + Escavador + Keyword Crawler)')

    options = st.multiselect('Natureza Juridica CNES',
         ['ENTIDADES EMPRESARIAIS','ENTIDADES SEM FINS LUCRATIVOS'],
         ['ENTIDADES EMPRESARIAIS'])

    mps = st.slider('# Minimo Profissionais de SM',0,100,5)
    mp = st.slider('# Minimo Psiquiatras',1,100,1)
    pp = st.slider('Mínimo % Profissionais de SM',1,100,30)
    lp = st.slider('Limite de # de Processos',0,1000,5000)
    df5 = df[(df['Natureza Jurídica'].isin(options))&(df.leitos_interesse_sus <= lsm)&(df.funci_interesse/df['TOTAL FUNCIONARIOS'] >= pp/100)&(df.funci_interesse >= mps)&(df['MEDICO PSIQUIATRA'] >= mp)&(df.processos.apply(lambda x: 0 if type(x) == str else x) <= lp)&(df.situacao=='ATIVA')]

    df6 = df5.groupby('base_referencia_97').agg({'cnes':'count','leitos_interesse_sus': 'sum', 'funci_interesse': 'sum'}).reset_index().rename(columns = {'cnes':'Estabelecimentos','leitos_interesse_sus': 'Leitos SM exSUS', 'funci_interesse': 'Funcionários SM'})

    df6 = df6.append(pd.DataFrame([['total',df6['Estabelecimentos'].sum(),df6['Leitos SM exSUS'].sum(),df6['Funcionários SM'].sum()]], columns = df6.columns))

    st.table(df6)

    st.write('Distribuição dos estabelecimentos tipo B')

    fig = px.scatter_mapbox(df5, lat="latitude", lon="longitude", zoom=9, title = 'Distribuição dos estabelecimentos ativos', color = 'base_referencia_97', hover_name = 'Nome Fantasia', hover_data = ['Município','UF','leitos_interesse','funci_interesse'])

    fig.update_layout(
        mapbox = {'style': "open-street-map", 'center': {'lon': -48.5, 'lat': -14.5}, 'zoom': 3},
        showlegend = True,
        margin = {'l':0, 'r':0, 'b':0, 't':0},
        title = 'Distribuição dos estabelecimentos ativos')

    st.plotly_chart(fig, use_container_width=True)

    dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
    df5 = df5.rename(columns=dictfilt(dict_col_name, list(df5.columns)))
    df_xlsx = to_excel(df5.sort_values(by = ['base_referencia_97', '# Psiquiatras'], ascending = [False, False]))
    st.download_button(label='📥 Download estabelecimentos tipo B',
                                    data=df_xlsx ,
                                    file_name= 'ativos_B.xlsx')

login_blocks = generate_login_block()
password = login(login_blocks)

if is_authenticated(password):
    clean_blocks(login_blocks)
    main()
elif password:
    st.info("Please enter a valid password")






