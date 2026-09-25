# Garimpo Indie: Engenharia de Dados e Analise do Monopólio Cultural Musical

O Garimpo Indie é um projeto de Back-End, Engenharia e Análise de Dados desenvolvido para investigar o consumo musical nas capitais brasileiras, contrapondo o ecossistema cultural regional ao algoritmo de massa do eixo tradicional Rio de Janeiro - Sao Paulo (RJ-SP).

A aplicação processa um histórico massivo de mais de 201.000 linhas de rankings semanais do Spotify (compreendendo os anos de 2021 a 2024), extrai insights socioculturais, além de estruturar um banco de dados relacional robusto e expõe os resultados através de uma API estável construida com FastAPI.

---

## Roteiro do Projeto e Arquitetura Tecnologica

O projeto foi executado seguindo tres etapas de maturidade de engenharia de software:

1. **Analise de Dados e ETL (1_analise_e_consolidacao.ipynb):** Varredura automatizada de centenas de arquivos semanais isolados em pastas regionais, tratamento de codificação de texto e cruzamento massivo de tabelas.
2. **Modelagem Relacional (modelos.py e popular_banco.py):** Arquitetura SQL estruturada via ORM (SQLAlchemy), normalizando dados brutos em relacionamentos de chaves primarias e estrangeiras para garantir performance de leitura.
3. **Exposição de Dados via API (api.py):** Construção de endpoints escalaveis usando FastAPI e Uvicorn para servir as analises diretamente do banco indexado.

---

## Linha do Tempo da Analise, Hipóteses e Tomadas de Decisão

O desenvolvimento do projeto foi marcado por uma investigação minuciosa dos dados brutos, onde cada barreira tecnica ou comportamento inesperado gerou uma nova solucao de engenharia:

### 1. Primeira Hipótese: A Resiliência do Underground
Busquei identificar quais as músicas que demonstraram uma força extrema de permanência (alto streak), mas que nunca atingiram o topo absoluto (#1) controlado pelas grandes engrenagens de marketing pop. 
* **Resultado:** Encontrei o projeto independente "Poesia Acustica #6", que sustentou uma resiliência de 118 semanas seguidas dentro dos rankings regionais sem nunca alcancar o primeiro lugar. Isso provou a tese de que movimentos de nicho constroem ecossistemas autonomos e fieis de ouvintes.

### 2. Segunda Hipótese: A Busca pela Autonomia no Top 10 e o Filtro de Ruido Comercial
A intenção era isolar mísicas que alcancaram o Top 10 em capitais com forte identidade cultural regional, mas que passaram longe do eixo tradicional (pior que a posicao #85 ou inexistentes) no Sudeste.

* **O Desafio do Sertanejo:** Ao abrir a analise para multiplas cidades do interior e centro-oeste, o mega-mainstream do Sertanejo Universitario inundou os resultados. Ele distorceu a busca, pois esses hits comerciais dominavam os rankings com comportamentos puramente corporativos e de radio.
* **O Refinamento de Escopo:** Para limpar o ruido comercial e isolar o garimpo de nicho, o escopo foi reduzido estritamente para as capitais Recife e Belo Horizonte.

### 3. Terceira Hipótese: O impacto do algoritmo em Manaus e o resultado que me surpreendeu
Tentamos aplicar o mesmo filtro estrito (Top 10 local vs abaixo de #60 ou ausente no Sudeste) alterando as variaveis para estudar a capital Manaus e Belo Horizonte.
* **O Resultado Vazio:** Para a nossa surpresa, a consulta retornou uma tabela completamente vazia. 
* **O Insight Critico:** Esse resultado "vazio" foi, na verdade, uma das maiores revelacoes do projeto. Ele provou empiricamente o peso esmagador do monopolio cultural e da padronizacao do algoritmo do Spotify. Os dados mostraram que o mercado de massa nacional e tao centralizado que e matematicamente impossivel uma musica alcancar o topo maximo (Top 10) de capitais como Manaus ou Belo Horizonte sem ser arrastada e injetada nas paradas de Sao Paulo e Rio de Janeiro de forma simultanea.

### 4. Quarta Hipótese: A Validação do Sucesso Autônomo em Recife
Ajustando o filtro para um cenario de equilibrio e focando a busca especificamente na capital de Recife, a analise finalmente isolou o comportamento de resistencia cultural que procuravamos. Conseguimos extrair os seguintes dados:
* **"Cadê Seu Namorado Moça?" (Thales Lessa) e "Duas" (Nadson O Ferinha):** Bateram o Top 10 regional em Recife (posicoes #9 e #10), enquanto no eixo RJ-SP figuravam na posicao 101 (completamente inexistentes nas paradas).
* **"A Gente Se Entrega" (NATTAN):** Alcancou a posicao #7 em Recife e permaneceu em 101 no eixo central.
* **"Coisas Que Eu Sei" (Felipe Amorim):** Bateu o pico de #4 em Recife, figurando escondido na posicao #89 no Sudeste.

Estes dados validaram a existencia de um ecossistema musical regional autossuficiente e bilionario no Nordeste, que se movimenta e consome em alta escala de forma independente do aval ou timing das mídias centrais do Sudeste.

### 5. Solução do Bug Tecnico de Encoding (Belm)
Durante a unificacao das mais de 200 mil linhas, a codificacao de texto antiga gerada pelo sistema operacional corrompeu o caractere especial da cidade de Belem, transformando a string em um formato corrompido em memoria. No script de populacao final (popular_banco.py), criamos um algoritmo de tratamento de string que interceptou o padrao quebrado e forcou a gravacao limpa da palavra "Belém" antes de realizar o insert no banco de dados.

---

## Dicionario de Dados do Banco Relacional

Para normalizar a base bruta de planilhas CSV e garantir consultas de historico em milissegundos, estruturamos o seguinte modelo de tabelas SQL:

### Tabela: musicas
*   uri (PK - String): Codigo unico identificador do Spotify (utilizado como o RG unico da faixa).
*   track_name (String): Nome oficial da musica.
*   artist_names (String): Nome dos artistas ou bandas envolvidas.

### Tabela: cidades
*   id_cidade (PK - Integer - Autoincrement): Identificador numerico gerado automaticamente.
*   nome_cidade (String - Unique): Nome da capital brasileira mapeada.

### Tabela: historico_rankings
*   id_ranking (PK - Integer - Autoincrement): Identificador do registro de historico.
*   rank (Integer): Posicao da musica no Top 100 daquela semana especifica (1 a 100).
*   semana (String): Periodo temporal correspondente ao ranking.
*   peak (Integer): Melhor posicao historica que a musica atingiu ate aquela data.
*   streak (Integer): Quantidade de semanas seguidas que a musica se manteve no Top 100.
*   fk_musica (FK - String): Aponta para o campo uri da tabela musicas.
*   fk_cidade (FK - Integer): Aponta para o campo id_cidade da tabela cidades.

---

## Como Executar o Projeto Localmente

1. Configurar o ambiente virtual (.venv) e instalar as dependencias:
```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install pandas notebook openpyxl sqlalchemy fastapi uvicorn
```

2. Executar o mapeamento das tabelas e o processo de migracao de dados (ETL):
```bash
python modelos.py
python popular_banco.py
```

3. Iniciar o servidor Back-End:
```bash
uvicorn api:app --reload
```
Acesse a documentacao interativa gerada automaticamente pelo FastAPI no seu navegador atraves do endereço: http://localhost:8000/docs.
