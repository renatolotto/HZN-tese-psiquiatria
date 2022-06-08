import requests
import pandas as pd
from time import sleep
import sqlite3

cnx = sqlite3.connect('psiquiatria.db')

df = pd.read_sql_query("SELECT * FROM data", cnx)

df = df[df['id'].isin([3548702069776,3550302077418])]


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
        response = requests.get('https://cnes.datasus.gov.br/services/estabelecimentos-profissionais/'+str(rows['id']), headers=headers)
        print(response)
        print(response.text)
        serv = response.json()
        total = 0
        mn = 0
        mp = 0
        mnc = 0
        pc = 0
        pe = 0
        ph = 0
        ps = 0
        pt = 0
        np = 0
        pca = 0
        pa = 0
        for s in serv:
            if s['cbo'] == '225112':
                mn += 1
            if s['cbo'] == '225133':
                mp += 1
            if s['cbo'] == '225350':
                mnc += 1
            if s['cbo'] == '251505':
                pc += 1
            if s['cbo'] == '251510':
                pe += 1
            if s['cbo'] == '251520':
                ph += 1
            if s['cbo'] == '251530':
                ps += 1
            if s['cbo'] == '251540':
                pt += 1
            if s['cbo'] == '251545':
                np += 1
            if s['cbo'] == '251550':
                pca += 1
            if s['cbo'] == '251555':
                pa += 1
            total += 1
        if total > 0:
            conn = sqlite3.connect("psiquiatria.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE data SET [MEDICO NEUROLOGISTA] = '"+str(mn)+"', [MEDICO PSIQUIATRA] = '"+str(mp)+"', [MEDICO NEUROFISIOLOGISTA CLINICO] = '"+str(mnc)+"', [PSICOLOGO CLINICO] = '"+str(pc)+"', [PSICOLOGO EDUCACIONAL] = "+str(pe)+", [PSICOLOGO HOSPITALAR] = '"+str(ph)+"', [PSICOLOGO SOCIAL] = '"+str(ps)+"', [PSICOLOGO DO TRABALHO] = '"+str(pt)+"', [NEUROPSICOLOGO] = '"+str(np)+"', [PSICANALISTA] = '"+str(pca)+"', [PSICOLOGO ACUPUNTURISTA] = '"+str(pa)+"', [TOTAL FUNCIONARIOS] = '"+str(total)+"' WHERE data.'id' = "+str(rows['id']))
            conn.commit()
            print(total)
            print('inserted')
        else:
            print('sem funci')
        count += 1
        print(100*count/df.shape[0])        
    except Exception as e:
        print(e)
        count += 1
        pass