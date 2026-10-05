from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload, sessionmaker

from modelos import engine, Musica, Cidade, HistoricoRanking

# 1. Instanciar a nossa aplicação FastAPI
app = FastAPI(
    title="API Garimpo Indie",
    description="API para explorar e descobrir fenômenos e resiliências da cena musical regional brasileira.",
    version="1.1.0"
)

# 2. Configure a fábrica de sessões do banco de dados
Session = sessionmaker(bind=engine)


# 3. Dependência: entrega uma sessão para cada requisição e SEMPRE fecha no final.
# Antes, cada rota abria e fechava a sessão na mão. Se desse erro no meio do caminho,
# a sessão podia ficar aberta. Com o yield, o "finally" garante o fechamento.
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


# --- ROTAS DA API (ENDPOINTS) ---

# Rota de Boas-Vindas
@app.get("/")
def home():
    return {
        "mensagem": "Bem-vindo à API oficial do projeto Garimpo Indie!",
        "status": "Servidor rodando e pronto para minerar relíquias musicais"
    }


# Rota para listar todas as cidades cadastradas
@app.get("/cidades")
def listar_cidades(db=Depends(get_db)):
    todas_cidades = db.query(Cidade).order_by(Cidade.nome_cidade).all()
    return [{"id": c.id_cidade, "nome": c.nome_cidade} for c in todas_cidades]


# Rota para procurar músicas por trecho do título ou do artista
@app.get("/musicas")
def buscar_musicas(
    busca: str = Query(..., min_length=2, description="Trecho do título ou do artista"),
    limite: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
):
    padrao = f"%{busca}%"
    musicas = (
        db.query(Musica)
        .filter(or_(Musica.track_name.ilike(padrao), Musica.artist_names.ilike(padrao)))
        .order_by(Musica.track_name)
        .limit(limite)
        .all()
    )
    return [{"uri": m.uri, "musica": m.track_name, "artistas": m.artist_names} for m in musicas]


# Rota com a trajetória semana a semana de uma música (use o uri que veio da busca)
@app.get("/historico")
def historico_da_musica(
    uri: str,
    id_cidade: Optional[int] = None,
    db=Depends(get_db),
):
    musica = db.get(Musica, uri)
    if musica is None:
        raise HTTPException(status_code=404, detail="Música não encontrada.")

    consulta = (
        db.query(HistoricoRanking)
        # joinedload traz a cidade junto na mesma consulta, em vez de uma consulta extra por linha
        .options(joinedload(HistoricoRanking.cidade))
        .filter(HistoricoRanking.fk_musica == uri)
    )
    if id_cidade is not None:
        consulta = consulta.filter(HistoricoRanking.fk_cidade == id_cidade)

    linhas = consulta.order_by(HistoricoRanking.semana).all()
    return {
        "musica": musica.track_name,
        "artistas": musica.artist_names,
        "historico": [
            {
                "cidade": r.cidade.nome_cidade,
                "semana": r.semana,
                "posicao": r.rank,
                "pico": r.peak,
                "streak": r.streak,
            }
            for r in linhas
        ],
    }


# Rota de Garimpo: Traz as músicas mais resilientes de uma cidade específica
@app.get("/garimpo/resiliencia/{id_cidade}")
def garimpar_resiliencia(
    id_cidade: int,
    limite: int = Query(10, ge=1, le=100),
    db=Depends(get_db),
):
    # 1. Verificar se a cidade informada existe no nosso cadastro
    cidade_existe = db.get(Cidade, id_cidade)
    if cidade_existe is None:
        raise HTTPException(status_code=404, detail="Cidade não encontrada no banco do Garimpo Indie.")

    # 2. Agrupar por MÚSICA (e não por linha).
    # Cada música tem uma linha por semana. Antes, a consulta olhava linha por linha, então a
    # mesma música podia aparecer várias vezes no Top 10 (streak 118, 117, 116...).
    # Agora cada música aparece uma vez, com o maior streak e a melhor posição que ela teve.
    # O having(min(rank) > 1) garante que ela nunca foi #1 nessa cidade.
    resultado_bruto = (
        db.query(
            Musica.track_name,
            Musica.artist_names,
            func.max(HistoricoRanking.streak).label("maior_streak"),
            func.min(HistoricoRanking.rank).label("melhor_posicao"),
            func.count(HistoricoRanking.id_ranking).label("semanas_no_ranking"),
        )
        .join(HistoricoRanking, HistoricoRanking.fk_musica == Musica.uri)
        .filter(HistoricoRanking.fk_cidade == id_cidade)
        .group_by(Musica.uri, Musica.track_name, Musica.artist_names)
        .having(func.min(HistoricoRanking.rank) > 1)
        .order_by(func.max(HistoricoRanking.streak).desc())
        .limit(limite)
        .all()
    )

    resultado = [
        {
            "musica": r.track_name,
            "artistas": r.artist_names,
            "maior_streak": r.maior_streak,
            "melhor_posicao": r.melhor_posicao,
            "semanas_no_ranking": r.semanas_no_ranking,
        }
        for r in resultado_bruto
    ]

    return {
        "cidade": cidade_existe.nome_cidade,
        "criterio": "Músicas com maior sequência de semanas no ranking da cidade que nunca chegaram ao #1 nela",
        "quantidade_encontrada": len(resultado),
        "dados": resultado
    }


# Rota de Garimpo: a pergunta central do projeto.
# Quais músicas chegaram ao topo de uma cidade, mas não apareceram (ou ficaram lá embaixo) no eixo RJ-SP?
@app.get("/garimpo/exclusivas/{id_cidade}")
def garimpar_exclusivas(
    id_cidade: int,
    top: int = Query(10, ge=1, le=100, description="Posição máxima na cidade"),
    corte: int = Query(85, ge=1, le=100, description="Posição a partir da qual a música conta como ausente na referência"),
    referencia: list[str] = Query(["Rio de Janeiro", "São Paulo"], description="Nomes exatos das cidades de referência (veja /cidades)"),
    db=Depends(get_db),
):
    cidade = db.get(Cidade, id_cidade)
    if cidade is None:
        raise HTTPException(status_code=404, detail="Cidade não encontrada no banco do Garimpo Indie.")

    # Descobre os ids das cidades de referência a partir dos nomes
    cidades_ref = db.query(Cidade).filter(Cidade.nome_cidade.in_(referencia)).all()
    ids_ref = [c.id_cidade for c in cidades_ref]
    if not ids_ref:
        raise HTTPException(
            status_code=400,
            detail="Nenhuma cidade de referência encontrada. Confira os nomes exatos em /cidades.",
        )
    if id_cidade in ids_ref:
        raise HTTPException(status_code=400, detail="A cidade analisada não pode ser também a referência.")

    # Melhor posição de cada música na cidade analisada (só quem chegou ao Top N)
    pico_local = (
        db.query(
            HistoricoRanking.fk_musica.label("uri"),
            func.min(HistoricoRanking.rank).label("pico_local"),
        )
        .filter(HistoricoRanking.fk_cidade == id_cidade)
        .group_by(HistoricoRanking.fk_musica)
        .having(func.min(HistoricoRanking.rank) <= top)
        .subquery()
    )

    # Melhor posição de cada música nas cidades de referência
    pico_ref = (
        db.query(
            HistoricoRanking.fk_musica.label("uri"),
            func.min(HistoricoRanking.rank).label("pico_ref"),
        )
        .filter(HistoricoRanking.fk_cidade.in_(ids_ref))
        .group_by(HistoricoRanking.fk_musica)
        .subquery()
    )

    # O outerjoin é o "left join" do Pandas: mantém as músicas da cidade mesmo que
    # elas não existam na referência (nesse caso pico_ref vem vazio).
    linhas = (
        db.query(Musica.track_name, Musica.artist_names, pico_local.c.pico_local, pico_ref.c.pico_ref)
        .join(pico_local, pico_local.c.uri == Musica.uri)
        .outerjoin(pico_ref, pico_ref.c.uri == Musica.uri)
        .filter(or_(pico_ref.c.pico_ref.is_(None), pico_ref.c.pico_ref > corte))
        .order_by(pico_local.c.pico_local)
        .all()
    )

    return {
        "cidade": cidade.nome_cidade,
        "referencia": [c.nome_cidade for c in cidades_ref],
        "criterio": f"Chegaram ao Top {top} na cidade e ficaram abaixo da posição {corte} (ou ausentes) na referência",
        "quantidade_encontrada": len(linhas),
        "dados": [
            {
                "musica": r.track_name,
                "artistas": r.artist_names,
                "melhor_posicao_na_cidade": r.pico_local,
                # None significa que a música nunca apareceu nas cidades de referência
                "melhor_posicao_na_referencia": r.pico_ref,
            }
            for r in linhas
        ],
    }
