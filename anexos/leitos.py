import requests
import pandas as pd
from time import sleep
import sqlite3

cnx = sqlite3.connect('psiquiatria.db')

df = pd.read_sql_query("SELECT * FROM data", cnx)

ind = df[df['id']==3129402136139].index.values[0]

print(ind)

df = df[df.index > ind]

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
        response = requests.get('https://cnes.datasus.gov.br/services/estabelecimentos-hospitalar/'+str(rows['id']), headers=headers)
        print(response)
        print(response.text)
        serv = response.json()
        total = 0
        total_sus = 0
        mental = 0
        mental_sus = 0
        dia = 0
        dia_sus = 0
        psiq = 0 
        psiq_sus = 0
        neuro = 0
        neuro_sus = 0
        geri = 0
        geri_sus = 0
        geri_dia = 0
        geri_dia_sus = 0
        for s in serv:
            if s['coLeito'] == '87':
                mental = mental + int(s['qtExistente']) 
                mental_sus = mental_sus + int(s['qtSus'])
            if s['coLeito'] == '73':
                dia = dia + int(s['qtExistente']) 
                dia_sus = dia_sus + int(s['qtSus'])
            if s['coLeito'] == '47':
                psiq = psiq + int(s['qtExistente']) 
                psiq_sus = psiq_sus + int(s['qtSus'])
            if s['coLeito'] == '42':
                neuro = neuro + int(s['qtExistente']) 
                neuro_sus = neuro_sus + int(s['qtSus'])
            if s['coLeito'] == '72':
                geri = geri + int(s['qtExistente']) 
                geri_sus = geri_sus + int(s['qtSus'])
            if s['coLeito'] == '36':
                geri_dia = geri_dia + int(s['qtExistente']) 
                geri_dia_sus = geri_dia_sus + int(s['qtSus'])
            total = total + int(s['qtExistente'])
            total_sus = total_sus + int(s['qtSus'])
        if total > 0:
            conn = sqlite3.connect("psiquiatria.db")
            cursor = conn.cursor()
            print("UPDATE data SET 'leitos_saude_mental' = "+str(mental)+", 'leitos_saude_mental_SUS' = "+str(mental_sus)+", 'leitos_total' = "+str(total)+", 'leitos_total_SUS' = "+str(total_sus)+", 'leitos_hospital_dia' = "+str(dia)+", 'leitos_hospital_dia_SUS' = "+str(dia_sus)+", 'leitos_psiquiatria' = "+str(psiq)+", 'leitos_psiquiatria_SUS' = "+str(psiq_sus)+", 'leitos_neurologia' = "+str(neuro)+", 'leitos_neurologia_SUS' = "+str(neuro_sus)+", 'leitos_geriatria' = "+str(geri)+", 'leitos_geriatria_SUS' = "+str(geri_sus)+", 'leitos_geriatria_dia' = "+str(geri_dia)+", 'leitos_geriatria_dia_SUS' = "+str(geri_dia_sus)+" WHERE 'id' = "+str(rows['id']))
            cursor.execute("UPDATE data SET 'leitos_saude_mental' = "+str(mental)+", 'leitos_saude_mental_SUS' = "+str(mental_sus)+", 'leitos_total' = "+str(total)+", 'leitos_total_SUS' = "+str(total_sus)+", 'leitos_hospital_dia' = "+str(dia)+", 'leitos_hospital_dia_SUS' = "+str(dia_sus)+", 'leitos_psiquiatria' = "+str(psiq)+", 'leitos_psiquiatria_SUS' = "+str(psiq_sus)+", 'leitos_neurologia' = "+str(neuro)+", 'leitos_neurologia_SUS' = "+str(neuro_sus)+", 'leitos_geriatria' = "+str(geri)+", 'leitos_geriatria_SUS' = "+str(geri_sus)+", 'leitos_geriatria_dia' = "+str(geri_dia)+", 'leitos_geriatria_dia_SUS' = "+str(geri_dia_sus)+" WHERE data.'id' = "+str(rows['id']))
            conn.commit()
            print(total)
            print('inserted')
        else:
            print('sem leitos')
        count += 1
        print(100*count/df.shape[0])        
    except Exception as e:
        print(e)
        count += 1
        pass