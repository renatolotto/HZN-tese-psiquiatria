import requests
import pandas as pd
from time import sleep
import sqlite3

df = pd.read_csv('saude.csv', sep = ';')
df['numero'] = df['CO_MUNICIPIO_GESTOR'].astype(str) + df['CO_CNES'].astype(str) 
cne = df['numero'].to_list()
cne = cne[100000:200000]

headers = {'Accept': 'application/json, text/plain, */*',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
'Connection': 'keep-alive',
'Host': 'cnes.datasus.gov.br',
'Referer': 'https://cnes.datasus.gov.br/pages/estabelecimentos/consulta.jsp',
'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
'sec-ch-ua-mobile': '?0',
'sec-ch-ua-platform': '"Windows"',
'Sec-Fetch-Dest': 'empty',
'Sec-Fetch-Mode': 'cors',
'Sec-Fetch-Site': 'same-origin',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'}

con=sqlite3.connect('psiquiatria.db')

df1 = pd.read_sql('select * from data', con)
lista = df1['id'].to_list()

count = 0
for cad in cne:
    if cad in lista:
        count += 1
    else:
        try:
            print(cad)
            response = requests.get('https://cnes.datasus.gov.br/services/estabelecimentos/'+str(cad), headers=headers)
            print(response)
            print(response.text)
            c = response.json()
            id = c['id']
            cnes = c['cnes']
            noFantasia = c['noFantasia']
            noEmpresarial = c['noEmpresarial']
            natJuridica = c['natJuridica']
            natJuridicaMant = c['natJuridicaMant']
            cnpj = c['cnpj']
            tpPessoa = c['tpPessoa']
            nvDependencia = c['nvDependencia']
            nuAlvara = c['nuAlvara']
            dtExpAlvara = c['dtExpAlvara']
            orgExpAlvara = c['orgExpAlvara']
            dsTpUnidade = c['dsTpUnidade']
            dsStpUnidade = c['dsStpUnidade']
            noLogradouro = c['noLogradouro']
            nuEndereco = c['nuEndereco']
            cep = c['cep']
            regionalSaude = c['regionalSaude']
            bairro = c['bairro']
            noComplemento = c['noComplemento']
            municipio = c['municipio']
            noMunicipio = c['noMunicipio']
            uf = c['uf']
            tpGestao = c['tpGestao']
            nuTelefone = c['nuTelefone']
            tpSempreAberto = c['tpSempreAberto']
            coMotivoDesab = c['coMotivoDesab']
            dsMotivoDesab = c['dsMotivoDesab']
            cpfDiretorCln = c['cpfDiretorCln']
            stContratoFormalizado = c['stContratoFormalizado']
            nuCompDesab = c['nuCompDesab']
            dtCarga = c['dtCarga']
            dtAtualizacaoOrigem = c['dtAtualizacaoOrigem']
            dtAtualizacao = c['dtAtualizacao']
            conn = sqlite3.connect("psiquiatria.db")
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO data (id,cnes                           
    ,[Nome Fantasia]                    
    ,[Razão Social]                     
    ,[Natureza Jurídica]            
    ,[Natureza Jurídica Mantenedora]    
    ,CNPJ                           
    ,[Tipo de Pessoa]               
    ,[Nível de dependência]         
    ,[Número do Alvará]                 
    ,[Data de expedição do Alvará]      
    ,[Orgão expedidor Alvará]           
    ,[Tipo de Unidade]                  
    ,[Subtipo de Unidade]               
    ,Logradouro                         
    ,[Número do endereço]               
    ,CEP                            
    ,[Regional de Saude]                
    ,Bairro                             
    ,Complemento                        
    ,[Cod. Município]               
    ,Município                          
    ,UF                                 
    ,[Tipo de Gestão]                   
    ,Telefone                           
    ,[Sempre aberto?]                   
    ,[cód Motivo Desabilitação]         
    ,[Motitivo desabilitação]           
    ,[CPF Diretor]                      
    ,[Situação contrato formalizado]    
    ,[Número de Desabilitação]          
    ,[Data da Carga]                    
    ,[Data da origem da atualização]    
    ,[Data da Atualização]) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (id, cnes, noFantasia, noEmpresarial, natJuridica, natJuridicaMant, cnpj, tpPessoa, nvDependencia, nuAlvara, dtExpAlvara, orgExpAlvara, dsTpUnidade, dsStpUnidade, noLogradouro, nuEndereco, cep, regionalSaude, bairro, noComplemento, municipio, noMunicipio, uf, tpGestao, nuTelefone, tpSempreAberto, coMotivoDesab, dsMotivoDesab, cpfDiretorCln, stContratoFormalizado, nuCompDesab, dtCarga, dtAtualizacaoOrigem, dtAtualizacao))
            conn.commit()
            count += 1
            print(100*count/len(cne))        
        except Exception as e:
            print(e)
            count += 1
            pass

