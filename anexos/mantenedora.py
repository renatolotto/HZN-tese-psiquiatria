import requests
import pandas as pd
from time import sleep
import sqlite3

cnx = sqlite3.connect('psiquiatria.db ')

df = pd.read_sql_query("SELECT * FROM data where [Natureza Jurídica Mantenedora] is not null", cnx)

#ind = df[df['id']==3129402136139].index.values[0]

#print(ind)

#df = df[df.index > ind]

print(df.shape)

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

count = 0
for i, rows in df.iterrows():
    try:
        response = requests.get('https://cnes.datasus.gov.br/services/estabelecimentos-mantenedora/'+str(rows['id']), headers=headers)
        print(response)
        print(response.text)
        mant = response.json()
        cnpj = mant['cnpjMantenedora']
        name = mant['rzSocial']
        conn = sqlite3.connect("psiquiatria.db")
        cursor = conn.cursor()
        print("UPDATE data SET [CNPJ MANTENEDORA] = '"+str(cnpj)+"', [NOME MANTENEDORA] = "+str(name)+" WHERE 'id' = "+str(rows['id']))
        cursor.execute("UPDATE data SET [CNPJ MANTENEDORA] = '"+str(cnpj)+"', [NOME MANTENEDORA] = '"+str(name)+"' WHERE data.'id' = "+str(rows['id']))
        conn.commit()
        print('inserted')
        count += 1
        print(100*count/df.shape[0])        
    except Exception as e:
        count += 1
        print(e)