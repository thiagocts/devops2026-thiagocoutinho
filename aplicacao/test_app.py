# Testes unitários da aplicação Flask
import pytest
from app import APP, BD

# =========================================================================
# A CONFIGURAÇÃO DO ROBÔ (Fixture)
# Uma "fixture" prepara o terreno antes dos testes rodarem e limpa tudo depois
# =========================================================================
@pytest.fixture()
def client():
    # Ligamos o modo de teste e criamos um banco de dados "fantasma" (em memória).
    # Esse banco só existe enquanto o teste roda, para não misturar com o banco real.
    APP.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    # Entramos nos bastidores do nosso aplicativo Flask
    with APP.app_context():
        BD.create_all()  # PREPARAÇÃO: O robô cria as tabelas limpas no banco fantasma antes de começar
        
        yield APP.test_client() # EXECUÇÃO: O robô simula um navegador de internet para testar as páginas
        
        BD.drop_all()    # LIMPEZA: Depois que todos os testes terminam, o robô apaga o banco fantasma

# =========================================================================
# TESTES DA ROTA / (Página Inicial)
# O robô vai testar a página que deveria mostrar o nome do integrante
# =========================================================================

def test_index(client):
    """Teste 1: Garante que o texto e a estrutura da página inicial estão corretos"""
    resposta = client.get("/") # O robô finge que entrou no endereço "/" do site
    conteudo_da_resposta = resposta.text # O robô lê todo o texto/HTML que o site devolveu
    
    # O robô define o que ele espera encontrar lá dentro
    conteudo_esperado = "<h1>Integrantes</h1>\n<br>\nThiago Coutinho Da Silva"
    
    # Ele confere: "O conteúdo esperado está dentro da resposta do site?"
    assert conteudo_esperado in conteudo_da_resposta

def test_index_status(client):
    """Teste 2: Garante que a página inicial está no ar e funcionando (Status 200)"""
    resposta = client.get("/") # O robô acessa a página
    # O código 200 na internet significa "OK/Sucesso". Se der 404 ou 500, o teste falha.
    assert resposta.status_code == 200

def test_index_integrantes(client):
    """Teste 3: Garante que a palavra 'Integrantes' está escrita em algum lugar da página"""
    resposta = client.get("/") # O robô acessa a página
    # Ele confere se a palavra específica "Integrantes" existe dentro do texto do site
    assert "Integrantes" in resposta.text


# =========================================================================
# TESTES DA ROTA /livros (Gerenciamento de Livros)
# O robô vai testar a listagem de livros
# =========================================================================

def test_livros(client):
    """Teste 4: Garante que o sistema começa com a lista de livros totalmente vazia"""
    resposta = client.get("/livros") # O robô acessa a página de livros
    # Como o banco de dados fantasma acabou de ser criado, ele precisa retornar uma lista vazia: []
    assert resposta.json == []

def test_livros_status(client):
    """Teste 5: Garante que a página de livros está no ar e respondendo (Status 200)"""
    resposta = client.get("/livros") # O robô acessa a página
    # Confere se a resposta foi de sucesso (Código 200)
    assert resposta.status_code == 200

def test_livros_json(client):
    """Teste 6: Garante que o formato que o site responde é o formato JSON (dados organizados)"""
    resposta = client.get("/livros") # O robô acessa a página
    # O robô confere se o site está devolvendo os dados organizados em JSON (e não uma página de texto comum)
    assert resposta.is_json