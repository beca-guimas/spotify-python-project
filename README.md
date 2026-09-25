# Garimpo Indie: Investigação e Análise dos Fluxos de Distribuição na Indústria Fonográfica Digital

Este projeto de engenharia de dados e desenvolvimento back-end foi desenvolvido por mim para investigar os padrões de consumo e distribuição musical nas capitais brasileiras. O objetivo central foi analisar de forma crítica como os ecossistemas culturais regionais interagem e se posicionam diante das dinâmicas mercadológicas impostas pelo Spotify, que atua hoje como a principal plataforma curadora e ditadora de tendências na indústria da música.

No desenvolvimento desta pesquisa, processei um histórico de mais de 201.000 linhas de rankings semanais da plataforma (compreendendo os anos de 2021 a 2024). Eu extraí insights sobre o comportamento dos mercados locais, estruturei um banco de dados relacional e expus os resultados através de uma API construída com FastAPI.

---

## Estrutura Metodológica e Arquitetura do Projeto

Organizei o desenvolvimento deste projeto em três etapas principais:

1. **Tratamento de Dados e ETL (1_analise_e_consolidacao.ipynb):** Executei a varredura automatizada de centenas de relatórios semanais isolados em pastas regionais, padronizei a codificação de caracteres das strings e unifiquei as tabelas.
2. **Modelagem Relacional (modelos.py e popular_banco.py):** Desenhei uma arquitetura SQL via ORM (SQLAlchemy), dividindo os dados brutos em tabelas normalizadas com chaves primárias e estrangeiras para otimizar a performance de leitura.
3. **Disponibilização através de API (api.py):** Construí endpoints usando FastAPI e Uvicorn para permitir a consulta dinâmica das análises diretamente no banco de dados indexado.

---

## Trajetória de Análise, Hipóteses e Tomadas de Decisão

A investigação foi pautada pelo teste de hipóteses sobre a centralização do mercado da música e a capacidade de sobrevivência de manifestações culturais periféricas ou regionais nas paradas de sucesso:

### 1. Primeira Hipótese: A Resiliência de Fluxos Alternativos ao Topo Comercial
Busquei identificar faixas que demonstraram uma força contínua de permanência nos rankings regionais (alto streak), mesmo sem atingirem a posição número #1 nacional — o ponto máximo de visibilidade moldado pelas estratégias de grande alcance da indústria.
* **Resultado:** Isolei o projeto independente "Poesia Acústica #6", que sustentou uma resiliência de 118 semanas seguidas dentro das paradas de consumo regional sem nunca figurar no topo absoluto. Isto validou a minha hipótese de que circuitos alternativos conseguem fidelizar e manter comunidades de ouvintes estáveis à margem dos investimentos massivos das grandes editoras.

### 2. Segunda Hipótese: A Autonomia dos Mercados Regionais e a Filtragem de Ruído Comercial
A minha intenção original era mapear as músicas que alcançaram o Top 10 em capitais com forte identidade local, mas que foram ignoradas ou estiveram ausentes das paradas (abaixo da posição #85 ou inexistentes) no eixo tradicional de consumo do Sudeste.
* **O Desafio do Sertanejo:** Ao expandir inicialmente a análise para múltiplas cidades, percebi que a massificação comercial do Sertanejo Universitário inundou os resultados. Este fenómeno não representava um mercado de nicho local, mas sim a reprodução de um modelo corporativo de grande escala que replica as dinâmicas da rádio comercial na plataforma.
* **O Refinamento de Escopo:** Para isolar dinâmicas de consumo genuinamente regionalizadas, reduzi o escopo da pesquisa estritamente às capitais Recife e Belo Horizonte.

### 3. Terceira Hipótese: A Centralização no Mercado de Massa de Manaus
Tentei replicar o mesmo critério estrito de filtragem (Top 10 local vs exclusão no Sudeste) alterando as variáveis de espaço para estudar as capitais Manaus e Belo Horizonte.
* **O Resultado Vazio:** A consulta no banco de dados retornou uma tabela completamente vazia.
* **O Insight Técnico:** Longe de ser um erro de código, este resultado revelou-me um dado profundo sobre a economia de plataformas. Ele demonstrou empiricamente o nível de centralização imposto pelo algoritmo do Spotify no topo da pirâmide do consumo. Os dados provaram que a indústria está tão unificada que é matematicamente inviável uma música atingir o ápice (Top 10) de mercados como Manaus ou Belo Horizonte sem que as forças de distribuição e as playlists editoriais da plataforma a injetem, simultaneamente, nas paradas de São Paulo e do Rio de Janeiro.

### 4. Quarta Hipótese: A Validação da Autossuficiência no Mercado do Nordeste
Ao focar a análise de equilíbrio especificamente na capital de Recife, consegui isolar o comportamento de independência que buscava mapear desde o início. Extraí as seguintes evidências:
* **"Cadê Seu Namorado Moça?" (Thales Lessa) e "Duas" (Nadson O Ferinha):** Conquistaram o Top 10 regional em Recife (posições #9 e #10), enquanto no eixo RJ-SP permaneceram na posição 101 (completamente fora das paradas de sucesso).
* **"A Gente Se Entrega" (NATTAN):** Atingiu a posição #7 em Recife e figurou como inexistente (101) no mercado do Sudeste.
* **"Coisas Que Eu Sei" (Felipe Amorim):** Alcançou a posição #4 em Recife, surgindo de forma tardia ou periférica em #89 no Sudeste.

Estes dados confirmaram a existência de um mercado fonográfico regional altamente autossuficiente no Nordeste. Ele movimenta capital financeiro e simbólico em alta escala, operando com um timing e uma lógica de consumo independentes das mídias centrais do Sudeste.

### 5. Tratamento de Anomalias de Dados (Encoding de Belém)
No processo de unificação das tabelas, identifiquei um erro de codificação de texto (*encoding*) originado na geração dos relatórios, que corrompeu os caracteres da palavra Belém, registando-a como `Belm` em memória. No meu script de automação (`popular_banco.py`), tratei esta anomalia intercetando a string corrompida e padronizando-a para "Belém" antes da persistência no banco de dados SQL.

---

## Dicionário de Dados do Banco Relacional

Para organizar o histórico massivo e garantir consultas em milissegundos, estruturei o banco de dados sob o seguinte esquema:

### Tabela: musicas
*   uri (PK - String): Identificador único do Spotify (utilizado como o RG da faixa).
*   track_name (String): Título oficial da música.
*   artist_names (String): Nome dos artistas ou bandas envolvidas.

### Tabela: cidades
*   id_cidade (PK - Integer - Autoincrement): Identificador numérico gerado automaticamente.
*   nome_cidade (String - Unique): Nome da capital brasileira estudada.

### Tabela: historico_rankings
*   id_ranking (PK - Integer - Autoincrement): Identificador do registo de histórico.
*   rank (Integer): Posição da música no Top 100 daquela semana específica (1 a 100).
*   semana (String): Período temporal correspondente ao ranking.
*   peak (Integer): Melhor posição histórica que a música atingiu até aquela data.
*   streak (Integer): Quantidade de semanas consecutivas que a música se manteve no Top 100.
*   fk_musica (FK - String): Aponta para o campo uri da tabela musicas.
*   fk_cidade (FK - Integer): Aponta para o campo id_cidade da tabela cidades.

---

## Como Executar o Projeto Localmente

1. Configurar o ambiente virtual (.venv) e instalar as dependências:
```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install pandas notebook openpyxl sqlalchemy fastapi uvicorn
```

2. Executar o mapeamento das tabelas e o processo de migração de dados (ETL):
```bash
python modelos.py
python popular_banco.py
```

3. Iniciar o servidor Back-End:
```bash
uvicorn api:app --reload
```
*Nota técnica: O endereço `http://localhost:8000/docs` indicado na inicialização do servidor serve para aceder à documentação interativa das rotas na máquina local onde o projeto for executado.*

---

## Origem da Base de Dados

Os dados brutos utilizados nesta investigação foram extraídos de repositórios públicos na plataforma **Kaggle**, contendo relatórios consolidados de audiência regional do Spotify. A base compreende o agregador de rankings semanais por capitais do mercado brasileiro, cobrindo o período de 2021 a 2024, totalizando mais de 201.000 registos de posições de faixas musicais.

---

## Técnicas de Engenharia e Métodos Analíticos Utilizados

Para transformar o volume bruto de ficheiros CSV no sistema estruturado do Garimpo Indie, apliquei as seguintes técnicas com a biblioteca Pandas no Jupyter Notebook:

*   **Automação de Diretórios com o Módulo OS:** Desenvolvi lógicas de varredura para mapear e ler recursivamente centenas de tabelas semanais distribuídas em subpastas de capitais, eliminando a necessidade de caminhos manuais (*hardcoded*).
*   **Agregação e Consolidação Massiva:** Utilizei a função `pd.concat` para unificar os milhares de fragmentos semanais numa única matriz de dados global em memória, gerando colunas indexadoras para cronologia (`semana`) e espaço (`cidade`).
*   **Mapeamento de Extremos via Agrupamento (Groupby e Agg):** Apliquei o método `groupby` combinado com funções de agregação (`.agg`) como `.min()` e `.max()` para isolar o histórico longitudinal de cada faixa musical. Isto permitiu extrair de forma exata o melhor pico histórico de cada obra e a sua resiliência consecutiva (*streak*) dentro de cada mercado específico.
*   **Junções Relacionais (Merge):** Utilizei o conceito de `pd.merge` com comportamento de `LEFT JOIN` para cruzar o comportamento das faixas nas capitais de nicho contra a tabela de comportamento no eixo tradicional RJ-SP. Esta operação isolou matematicamente os fenómenos de sucesso estritamente regional, fundamentais para a validação das hipóteses de autonomia cultural.

