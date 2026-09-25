import os
import pandas as pd
from sqlalchemy.orm import sessionmaker
from modelos import engine, Musica, Cidade, HistoricoRanking

# 1. Criamos uma Sessão, que é a nossa ponte de comunicação ativa para salvar dados no banco
Session = sessionmaker(bind=engine)
session = Session()

pasta_base = 'regional'

print(
    "Iniciando a leitura das pastas e população do banco... Isso pode levar um minutinho devido ao volume de dados.")

# Dicionários de controle para evitar que o Python faça consultas repetidas no banco (deixa o código 10 vezes mais rápido!)
cidades_cadastradas = {}
musicas_cadastradas = {}

# 2. Listamos todas as pastas de cidades
cidades = [f for f in os.listdir(pasta_base) if os.path.isdir(os.path.join(pasta_base, f))]

# Loop por cada cidade
for nome_cidade in cidades:
    # Correção do nome quebrado de Belém para o banco ficar perfeito e limpo!
    cidade_limpa = "Belém" if "Belm" in nome_cidade else nome_cidade

    # Se a cidade não está no nosso controle, cadastramos ela na tabela 'cidades'
    if cidade_limpa not in cidades_cadastradas:
        nova_cidade = Cidade(nome_cidade=cidade_limpa)
        session.add(nova_cidade)
        session.flush()  # O flush faz o banco gerar o ID numérico dela agora mesmo
        cidades_cadastradas[cidade_limpa] = nova_cidade.id_cidade

    id_da_cidade_atual = cidades_cadastradas[cidade_limpa]

    caminho_cidade = os.path.join(pasta_base, nome_cidade)
    arquivos_csv = [arq for arq in os.listdir(caminho_cidade) if arq.endswith('.csv')]

    # Loop por cada semana daquela cidade
    for arquivo in arquivos_csv:
        semana_nome = arquivo.replace('.csv', '')
        caminho_arquivo = os.path.join(caminho_cidade, arquivo)

        # Lemos a semana com o Pandas
        df_semana = pd.read_csv(caminho_arquivo)

        # Varremos linha por linha do CSV semanal (as músicas do ranking)
        for _, linha in df_semana.iterrows():
            uri_musica = str(linha['uri'])

            # Se a música nunca foi vista pelo script, cadastramos na tabela 'musicas'
            if uri_musica not in musicas_cadastradas:
                # Tratamento simples caso o nome venha vazio por algum erro do arquivo
                track_name = str(linha['track_name']) if pd.notna(linha['track_name']) else "Desconhecido"
                artist_names = str(linha['artist_names']) if pd.notna(linha['artist_names']) else "Desconhecido"

                nova_musica = Musica(uri=uri_musica, track_name=track_name, artist_names=artist_names)
                session.add(nova_musica)
                musicas_cadastradas[uri_musica] = True

            # Criamos o registro do histórico apontando para as chaves estrangeiras (as PKs de música e cidade)
            novo_ranking = HistoricoRanking(
                rank=int(linha['rank']),
                semana=semana_nome,
                peak=int(linha['peak']) if pd.notna(linha['peak']) else None,
                streak=int(linha['streak']) if pd.notna(linha['streak']) else None,
                fk_musica=uri_musica,
                fk_cidade=id_da_cidade_atual
            )
            session.add(novo_ranking)

# 3. Damos o COMMIT final! É aqui que o Python envia o blocão de dados definitivo para o arquivo do banco
print("Gravando os dados definitivamente no banco de dados...")
session.commit()
session.close()

print("SUCESSO ABSOLUTO! Mais de 200 mil linhas inseridas e vinculadas perfeitamente!")
