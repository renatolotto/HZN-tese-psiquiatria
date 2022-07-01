1- Como nosso scrapng go Google Places não retorna com uma chave única, André sugeriu guardar todas as respostas possíveis do scraping para cada input no ELASTIC SEARCH (banco open source orientado a documentos), assim a ideia é fazer uma anotação de dado dentro do elastic search e o prório rankeamento...processo de "Learning to Rank"

2- Para comparação de strings, recomendou a seguinte sequência:
    1-comapara por distância de Jakar
    2-comparar por distância de Levestein
    3- Usar ML: MOdelo Word to Vect (GLOVE), que é em nível de palavra - digitar no google GLOVE NILC (repositório de palavras com representação vetorial da USP SC)
    Assim podemos usar similaridade de cossenos comparar as palavras
    4-Pesquisar sobre o S_Bert, que é um modelo já orientado a sentença, porém pode ser matar uma mosca com bazooka

3-Para comparação de endereços, usar api de geolocalização que retorna LAT,LON com base no string do endereço e aplicar testar de 2 endereços estão no mesmo quadrado, usando a lib do uber/h3, que define hexagonos de tamanhos variados, assim podemos conluir se ambos endere~ços estão no mesmo hexagono, eles são o mesmo endereço.
ver: https://github.com/uber/h3