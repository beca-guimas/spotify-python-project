from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import sessionmaker
from modelos import engine, Musica, Cidade, HistoricoRanking

# 1. Instanciar a nossa aplicação FastAPI
app = FastAPI(
    title="API Garimpo Indie",
    description="API para explorar e descobrir fenômenos e resiliências da cena musical regional brasileira.",
    version="1.0.0"
)

# 2. Configure a fábrica de sessões do banco de dados
Session = sessionmaker(bind=engine)


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
def listar_cidades():
    session = Session()
    # Buscamos todas as linhas da tabela Cidade
    todas_cidades = session.query(Cidade).all()
    session.close()

    # Retornamos os dados em formato de lista pura
    return [{"id": c.id_cidade, "nome": c.nome_cidade} for c in todas_cidades]


# Rota de Garimpo: Traz as músicas mais resilientes de uma cidade específica
@app.get("/garimpo/resiliencia/{id_cidade}")
def garimpar_resiliencia(id_cidade: int, limite: int = 10):
    session = Session()

    # 1. Verificar se a cidade informada existe no nosso cadastro
    cidade_existe = session.query(Cidade).filter(Cidade.id_cidade == id_cidade).first()
    if not cidade_existe:
        session.close()
        raise HTTPException(status_code=404, detail="Cidade não encontrada no banco do Garimpo Indie.")

    # 2. Fazer uma query avançada no banco:
    # Buscar o histórico de rankings daquela cidade onde o pico NUNCA foi #1 (peak > 1)
    # Ordenar pelo maior streak (resiliência) de forma decrescente
    rankings = (
        session.query(HistoricoRanking)
        .filter(HistoricoRanking.fk_cidade == id_cidade)
        .filter(HistoricoRanking.peak > 1)
        .order_by(HistoricoRanking.streak.desc())
        .limit(limite)
        .all()
    )

    # 3. Monta a resposta estruturada contendo as informações da música vinculada (a FK funcionando na prática!)
    resultado = []
    for r in rankings:
        resultado.append({
            "posicao_na_semana": r.rank,
            "semana": r.semana,
            "maior_resiliencia_semanal(streak)": r.streak,
            "melhor_pico_alcancado": r.peak,
            "musica": r.musica.track_name,  # O SQLAlchemy busca na tabela musicas usando a FK automaticamente!
            "artistas": r.musica.artist_names
        })

    session.close()
    return {
        "cidade": cidade_existe.nome_cidade,
        "criterio": "Músicas mais resilientes que nunca atingiram o topo de massa (#1)",
        "quantidade_encontrada": len(resultado),
        "dados": resultado
    }
