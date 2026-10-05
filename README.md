# 🎧 Garimpo Indie API

**API REST com banco relacional sobre 201 mil rankings semanais do Spotify Brasil (2021–2023).**
Construída com Python, SQLAlchemy e FastAPI, e usada para investigar se mercados musicais regionais (Recife, BH) funcionam de forma independente do eixo RJ-SP.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red)
![Pandas](https://img.shields.io/badge/Pandas-ETL-150458)

<!-- Coloque aqui um print do Swagger (http://localhost:8000/docs) -->

---

## Visão geral

O projeto tem duas partes que se alimentam:

- **Backend:** pipeline de ETL, modelagem relacional e API REST para consultar os rankings.
- **Análise:** perguntas de pesquisa respondidas em cima desse banco, e algumas delas viraram endpoints.

```
CSVs semanais (Kaggle)
        │
        ▼
1_analise_e_consolidacao.ipynb   →  leitura, limpeza e consolidação (Pandas)
        │
        ▼
modelos.py + popular_banco.py    →  schema SQLAlchemy + carga no banco
        │
        ▼
api.py (FastAPI + Uvicorn)       →  API REST com docs automática (Swagger)
```

## Stack

Python · FastAPI · Uvicorn · SQLAlchemy (ORM) · Pandas · Jupyter · PyCharm

---

## Banco de dados

Normalizei os dados em 3 tabelas, com chaves primárias e estrangeiras:

| Tabela | Colunas |
|---|---|
| `musicas` | `uri` (PK), `track_name`, `artist_names` |
| `cidades` | `id_cidade` (PK), `nome_cidade` (único) |
| `historico_rankings` | `id_ranking` (PK), `rank`, `semana`, `peak`, `streak`, `fk_musica` → `musicas.uri`, `fk_cidade` → `cidades.id_cidade` |

**Pipeline de carga (`popular_banco.py`):**
- Lê centenas de relatórios semanais organizados em subpastas por capital, sem caminhos fixos no código.
- Corrige um problema de encoding nos arquivos de origem (`Belém` chegava como `Belm`) antes de gravar.
- Popula as tabelas respeitando as relações entre elas.

## API

Com o servidor rodando, a documentação interativa fica em **http://localhost:8000/docs**.

| Método | Rota | O que retorna |
|---|---|---|
| GET | `/cidades` | Capitais disponíveis e seus ids |
| GET | `/musicas?busca=&limite=` | Busca músicas por trecho do título ou do artista |
| GET | `/historico?uri=&id_cidade=` | Trajetória semanal de uma música |
| GET | `/garimpo/resiliencia/{id_cidade}` | Músicas com maior sequência de semanas no ranking da cidade, sem nunca chegar ao #1 nela |
| GET | `/garimpo/exclusivas/{id_cidade}?top=&corte=` | Músicas que chegaram ao Top N da cidade e ficaram fora do RJ-SP |

Exemplo:

```bash
curl "http://localhost:8000/garimpo/exclusivas/1?top=10&corte=85"
```

---

## Como rodar

**Pré-requisito:** Python 3.10+

```bash
git clone https://github.com/beca-guimas/spotify-python-project.git
cd spotify-python-project

python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\activate

pip install pandas notebook openpyxl sqlalchemy fastapi uvicorn

python modelos.py                # cria as tabelas
python popular_banco.py          # carrega os dados
uvicorn api:app --reload         # sobe a API
```

---

## O que a análise mostrou

A análise foi feita com Pandas no Jupyter Notebook e reproduzida nas consultas ao banco. O critério foi: Top 10 na capital regional e posição acima de #85 (ou ausência) no RJ-SP.

**Recife tem hits que o Sudeste não enxerga:**

| Música | Artista | Melhor posição em Recife | Posição no RJ-SP |
|---|---|---|---|
| Coisas Que Eu Sei | Felipe Amorim | #4 | #89 |
| A Gente Se Entrega | NATTAN | #7 | fora do Top 100 |
| Cadê Seu Namorado Moça? | Thales Lessa | #9 | fora do Top 100 |
| Duas | Nadson O Ferinha | #10 | fora do Top 100 |

**Outros achados:**
- "Poesia Acústica #6" ficou **118 semanas consecutivas** nos rankings regionais sem chegar ao #1 da cidade.
- Em Manaus e Belo Horizonte, o mesmo filtro não retornou nenhuma faixa, o que sugere forte centralização no topo dessas capitais.
- Na primeira rodada, o sertanejo universitário dominou os resultados por seguir um modelo de distribuição em larga escala. Por isso restringi o escopo a Recife e BH.

**Limitações:** o ranking mostra posição, não volume de streams; o corte de #85 é uma escolha minha e pode alterar os resultados; e a influência de playlists editoriais é uma hipótese, não algo medido nos dados.

---

## Fonte dos dados

[Brazil Regional Spotify Charts (Kaggle, filipeasm)](https://www.kaggle.com/datasets/filipeasm/brazil-regional-spotify-charts): rankings semanais por capital, 2021–2023, com mais de 201 mil registros.

## Próximos passos

- [ ] Testes automatizados dos endpoints (pytest + TestClient)
- [ ] Migrar de SQLite para PostgreSQL
- [ ] Dockerizar e publicar a API online
- [ ] Testar a sensibilidade da análise variando o corte de posição

## Autor

**Beca Guimas** · [LinkedIn](https://www.linkedin.com/in/becaguimas/)
