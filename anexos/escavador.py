import requests
import sqlite3
import pandas as pd

cnx = sqlite3.connect('psiquiatria.db')

df = pd.read_sql_query("SELECT *,(leitos_saude_mental + leitos_hospital_dia + leitos_psiquiatria + leitos_neurologia + leitos_geriatria + leitos_geriatria_dia) as leitos_interesse, ([MEDICO NEUROLOGISTA] + [MEDICO PSIQUIATRA] + [MEDICO NEUROFISIOLOGISTA CLINICO] + [PSICOLOGO EDUCACIONAL] + [PSICOLOGO CLINICO] + [PSICOLOGO HOSPITALAR] + [PSICOLOGO SOCIAL] + [PSICOLOGO DO TRABALHO] + [NEUROPSICOLOGO] + PSICANALISTA + [PSICOLOGO ACUPUNTURISTA]) AS funci_interesse from data where (leitos_interesse >= 1 or funci_interesse >= 1) and [Natureza Jurídica] in (2,3) and [Motitivo desabilitação] is null", cnx)

print(df.shape)

url = 'https://api.escavador.com/api/v1/busca'


headers = {
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiYjg4MzA0YzUzMGUyYzc0ZjVjYWEwMmQ4NTA2ZGE5MDdkMWU4ZTQyMTVmY2MwOTVjNGI1M2ZmZDIyZTcwZjc0NDExN2JhOGQxYzI3NWM4NjQiLCJpYXQiOjE2NDg2NzQwNDIsIm5iZiI6MTY0ODY3NDA0MiwiZXhwIjoxOTY0MjkzMjQyLCJzdWIiOiIxMTU3NDgzIiwic2NvcGVzIjpbImFjZXNzYXJfYXBpX3BhZ2EiXX0.oxID0e5hX69sR8sJwk7fcOh9dfVQdrp4AwxzO2Hv7g-TvLSTLFqbzZjy3hmnvHhau6HlI0-LYIX9HJQWCXcXZ5B4L_keU6en-bJyCfCHLitIo8ccB4UzMPn1DGD9S44U2BQ2CSUto_XrgnV3difnEd9kF6GwqTtQO8e-oBvilPbIq92xQY83_pY8df_jkJaF3jLDpU5rEv0pdXVMhHMNq9YCnu1mgOIRAmPPduvfj7SD0Z33HEhaScr2bKzHhC9Cw9rQIMb3WrsgtudezZLo26Ii3F9NScN0qjxMGXW5XxHp6DXp9pQNeVw63tFoQh3E2pRzQc-4EMF4zHUfL1K-KTUHa3zUDU4EQ17VDgzNX0BlclUSynX3ObwXrrH2XAV_HWV79vw38s-BYL4qN8V5uIt36fRqb4HQujJkc7aZoWlzdBDdXACnL61i6rzNN1FZwADaotIq1I2kxDrWQyuMVaXByAmd-TCHO2RMBl9zcw401rqTy6Wp2NjrhXxwSwrMgoz_oq2tq8OkpsXR45MvZQ03REoe1ZTj-A7Txsoac1hP6VTgxstKuJT6XTILd-IWsCMFgTZLS6SkkapzPrG-wCnbXdRdZYu3SvfDfQAbbHiS8zL9koNA-Lw_hBeNvG9RyuhH9jHTNkDAIndv12x5u2v1MtUsxdlhq3g0B038T4Q',
    'X-Requested-With': 'XMLHttpRequest'
}

for i, rows in df.iterrows():
	try:
		params = {
	    'q': '"'+rows['Razão Social']+'"',  
	    'qo': 'i',
	    'limit': '100',  
	    'page': '1'}
		response = requests.get(url, headers=headers, params=params)
		data = response.json()['items'][0]
		nome = data['nome']
		resumo = data['resumo']
		quantidade = data['quantidade_processos']
	except:
		nome = rows['Razão Social']
		quantidade = '0'
		resumo = 'Sem processos'
	print(nome,quantidade)
	conn = sqlite3.connect("psiquiatria.db")
	cursor = conn.cursor()
	cursor.execute('INSERT INTO escavador (id_cnes, nome, processos, resumo) VALUES (?,?,?,?)',(rows['id'],nome,quantidade,resumo))
	conn.commit()
	print('inserted')