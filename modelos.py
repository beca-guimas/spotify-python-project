from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# 1. O Base é a classe pai que gerencia todas as nossas tabelas
Base = declarative_base()


# 2. Tabela de Músicas
class Musica(Base):
    __tablename__ = 'musicas'

    # A URI do Spotify é o RG perfeito da música (Chave Primária)
    uri = Column(String, primary_key=True)
    track_name = Column(String, nullable=False)
    artist_names = Column(String, nullable=False)

    # Cria uma relação para o Python conseguir puxar os rankings dessa música facilmente
    rankings = relationship("HistoricoRanking", back_populates="musica")


# 3. Tabela de Cidades
class Cidade(Base):
    __tablename__ = 'cidades'

    # Um ID numérico sequencial (1, 2, 3...) como Chave Primária
    id_cidade = Column(Integer, primary_key=True, autoincrement=True)
    nome_cidade = Column(String, nullable=False, unique=True)

    # Relação para puxar os rankings atrelados a essa cidade
    rankings = relationship("HistoricoRanking", back_populates="cidade")


# 4. Tabela de Histórico (Recebe as +200 mil linhas)
class HistoricoRanking(Base):
    __tablename__ = 'historico_rankings'

    id_ranking = Column(Integer, primary_key=True, autoincrement=True)
    rank = Column(Integer, nullable=False)
    semana = Column(String, nullable=False)
    peak = Column(Integer)
    streak = Column(Integer)

    # As Chaves Estrangeiras (As pontes!)
    # ForeignKey('nome_da_tabela.coluna_alvo')
    fk_musica = Column(String, ForeignKey('musicas.uri'), nullable=False)
    fk_cidade = Column(Integer, ForeignKey('cidades.id_cidade'), nullable=False)

    # Conexões internas do Python para navegação entre objetos
    musica = relationship("Musica", back_populates="rankings")
    cidade = relationship("Cidade", back_populates="rankings")


# 5. Criador do Banco de Dados (Vamos criar um banco local leve chamado 'garimpo_indie.db')
engine = create_engine('sqlite:///garimpo_indie.db', echo=True)


# 6. Função para criar as tabelas no arquivo de banco de verdade
def criar_banco():
    Base.metadata.create_all(engine)
    print("🚀 Banco de dados e tabelas do Garimpo Indie criados com sucesso!")


# Se rodarmos esse arquivo direto, ele cria o banco
if __name__ == "__main__":
    criar_banco()

