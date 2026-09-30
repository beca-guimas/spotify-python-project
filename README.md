# 🎧 Garimpo Indie

**Existe mercado musical regional no Spotify, ou tudo converge para o eixo RJ-SP?**
Análise de 201 mil linhas de rankings semanais (Brasil, 2021–2024) com ETL em Pandas, banco relacional com SQLAlchemy e API em FastAPI.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Pandas](https://img.shields.io/badge/Pandas-ETL-150458)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688)

<!-- Dica: coloque aqui um print da documentação interativa (/docs) ou um gráfico do notebook -->

---

## O que este projeto faz

1. **ETL:** lê centenas de relatórios semanais (CSV) organizados em pastas por capital, corrige problemas de encoding e consolida tudo em uma única base.
2. **Banco de dados:** modela os dados em 3 tabelas normalizadas (SQLAlchemy) com chaves primárias e estrangeiras.
3. **API:** expõe consultas sobre o banco via FastAPI, com documentação interativa automática.
4. **Análise:** usa a base para testar hipóteses sobre centralização e autonomia de mercados regionais.

## Pergunta de pesquisa

> Músicas que estouram em capitais com forte identidade local também aparecem nas paradas do eixo RJ-SP, ou esses mercados funcionam de forma independente?

Para responder, cruzei o desempenho de cada faixa em cada capital com a posição dela no ranking do RJ-SP (valor **101** = fora do Top 100).

---

## Principais achados

### 1. Recife tem hits que o Sudeste não enxerga

| Música | Artista | Melhor posição em Recife | Posição no RJ-SP |
|---|---|---|---|
| Coisas Que Eu Sei | Felipe Amorim | #4 | #89 |
| A Gente Se Entrega | NATTAN | #7 | fora do Top 100 |
| Cadê Seu Namorado Moça? | Thales Lessa | #9 | fora do Top 100 |
| Duas | Nadson O Ferinha | #10 | fora do Top 100 |

Isso indica que o mercado do Nordeste pode operar com lógica e timing próprios, independentes do Sudeste.

### 2. Permanência sem depender do #1

"Poesia Acústica #6" ficou **118 semanas consecutivas** nos rankings regionais sem chegar ao #1 nacional. Sinal de que circuitos alternativos conseguem manter uma base fiel de ouvintes.

### 3. Manaus × Belo Horizonte: a consulta que voltou vazia

Ao aplicar o mesmo filtro (Top 10 local e ausente do RJ-SP), não apareceu nenhuma faixa. Em vez de tratar como erro, interpretei como indício de **forte centralização**: nessas capitais, quem chega ao topo tende a chegar também a SP e RJ.

### 4. Decisão de escopo: por que só Recife e BH

Na primeira rodada, com várias cidades, o sertanejo universitário dominou os resultados. Ele segue um modelo de distribuição em larga escala, não um fenômeno local. Para isolar dinâmicas realmente regionais, restringi a análise a Recife e Belo Horizonte.

---

## Limitações

- O ranking mostra **posição**, não número de streams. Não dá para medir volume real de consumo.
- O corte de "ausente do Sudeste" (posição > 85) é uma escolha minha, e os resultados podem mudar com outros limites.
- RJ-SP é usado como proxy do Sudeste.
- A relação com playlists editoriais e estratégia de gravadoras é uma **hipótese**; os dados não medem isso diretamente.

---

## Arquitetura

```
CSVs semanais (Kaggle)
        │
        ▼
1_analise_e_consolidacao.ipynb   →  limpeza, pd.concat, groupby/agg, merge
        │
        ▼
modelos.py + popular_banco.py    →  schema SQLAlchemy e carga no banco
        │
        ▼
api.py (FastAPI + Uvicorn)       →  consultas via HTTP
```

### Modelo de dados

| Tabela | Colunas |
|---|---|
| `musicas` | `uri` (PK), `track_name`, `artist_names` |
| `cidades` | `id_cidade` (PK), `nome_cidade` (único) |
| `historico_rankings` | `id_ranking` (PK), `rank`, `semana`, `peak`, `streak`, `fk_musica` → `musicas.uri`, `fk_cidade` → `cidades.id_cidade` |

### Técnicas usadas

- **`os`**: varredura recursiva das pastas, sem caminhos fixos no código.
- **`pd.concat`**: unificação dos arquivos semanais, com colunas de `semana` e `cidade`.
- **`groupby` + `agg`**: pico histórico (`min`) e maior sequência (`max`) por faixa e cidade.
- **`pd.merge` (left join)**: cruzamento entre capitais regionais e RJ-SP.
- **Tratamento de encoding**: os relatórios traziam "Belém" corrompido como `Belm`; a string é corrigida em `popular_banco.py` antes de ir pro banco.

---

## Como rodar

**Pré-requisito:** Python 3.10+

```bash
# 1. Clonar e entrar na pasta
git clone https://github.com/beca-guimas/spotify-python-project.git
cd spotify-python-project

# 2. Ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\activate

# 3. Dependências
pip install pandas notebook openpyxl sqlalchemy fastapi uvicorn

# 4. Criar tabelas e carregar os dados
python modelos.py
python popular_banco.py

# 5. Subir a API
uvicorn api:app --reload
```

Depois abra **http://localhost:8000/docs** para testar os endpoints.

### Endpoints

<!-- Preencha com as rotas reais do api.py, por exemplo: -->

| Método | Rota | Descrição |
|---|---|---|
| GET | `/exemplo` | _descreva aqui_ |

---

## Fonte dos dados

Rankings semanais do Spotify por capital brasileira (2021–2024), obtidos no Kaggle: [link do dataset](COLOQUE_O_LINK_AQUI).

## Próximos passos

- [ ] Testar a sensibilidade dos resultados variando o corte de posição (ex.: 50, 85, 100)
- [ ] Incluir mais capitais do Nordeste e do Norte
- [ ] Adicionar testes automatizados para a API
- [ ] Containerizar com Docker e publicar a API online

## Autor

**Beca Guimas** · [LinkedIn](https://www.linkedin.com/in/becaguimas/)
