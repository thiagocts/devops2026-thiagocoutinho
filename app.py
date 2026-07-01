# Aqui estamos importando as ferramentas que o Python vai usar para construir o sistema
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask, request, jsonify, render_template 

# Definimos onde o nosso banco de dados (o arquivo que guarda as informações) vai ficar salvo
CAMINHO_BD = "sqlite:///banco.db"

# Uma configuração padrão que o banco de dados precisa para começar a funcionar
class BaseModel(DeclarativeBase): 
    pass

# Criamos o nosso "gerente do banco". É ele quem vai ler, salvar e apagar as coisas para nós
BD = SQLAlchemy(model_class=BaseModel)

# =========================================================================
# A MODEL (A Ficha do Livro)
# Aqui dizemos ao sistema como deve ser a "ficha de cadastro" de cada livro
# =========================================================================
class Livro(BD.Model):
    __tablename__ = "livros" # O nome da tabela que vai ser criada dentro do arquivo do banco

    # Abaixo estão os campos que cada livro DEVE ter na ficha:
    id = BD.Column(BD.Integer, primary_key=True)  # O número de identificação único de cada livro (gerado sozinho)
    titulo = BD.Column(BD.String, nullable=False) # O título do livro (texto obrigatório)
    autor = BD.Column(BD.String, nullable=False)  # O nome do autor (texto obrigatório)
    issn = BD.Column(BD.String, nullable=False)   # O código de registro do livro (texto obrigatório)
    
    # Guarda o dia e a hora exata em que o livro foi cadastrado (preenchido sozinho com o horário atual)
    data_publicacao = BD.Column(BD.DateTime, nullable=False, default=datetime.utcnow) 
    
    paginas = BD.Column(BD.Integer, nullable=False) # A quantidade de páginas (número inteiro obrigatório)


# Inicializamos o Flask, que é o "motor do site" que atende os pedidos na internet
APP = Flask(__name__)

# Conectamos o motor do site ao nosso arquivo de banco de dados
APP.config['SQLALCHEMY_DATABASE_URI'] = CAMINHO_BD
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Desativa um aviso visual para o código rodar mais rápido
BD.init_app(APP) # Dizemos ao banco de dados: "Agora você trabalha junto com o Flask"


# =========================================================================
# ROTA 1: Página Inicial (Endereço: http://127.0.0.1:5000/)
# =========================================================================
@APP.route("/")
def index():
    # Quando alguém entra na página principal, o Flask vai até a pasta 'templates',
    # lê o arquivo 'index.html' e mostra o conteúdo dele (o nome do aluno) na tela do usuário.
    return render_template('index.html')


# =========================================================================
# ROTA 2: Gerenciar Livros (Endereço: http://127.0.0.1:5000/livros)
# =========================================================================
@APP.route("/livros", methods=['GET', 'POST'])
def livros():
    
    # --- SE O USUÁRIO QUISER APENAS VER OS LIVROS (Método GET) ---
    if request.method == 'GET':
        livros_db = Livro.query.all() # O gerente do banco vai lá e pega todos os livros salvos
        
        # O sistema organiza os livros em uma lista limpa e bonita (formato JSON) para enviar de volta
        return jsonify([
            {
                "titulo": livro.titulo,
                "autor": livro.autor,
                "issn": livro.issn,
                "data_publicacao": livro.data_publicacao.strftime("%Y-%m-%d"),
                "paginas": livro.paginas
            }
            for livro in livros_db
        ]), 200 # Código 200 significa: "Sucesso! Aqui estão os dados."

    # --- SE O USUÁRIO ENVIAR DADOS PARA CADASTRAR UM LIVRO NOVO (Método POST) ---
    if request.method == 'POST':
        dados = request.json # O Flask pega o pacotinho de texto que o usuário enviou e lê as informações
        
        # Preenchemos uma nova ficha de livro com o que o usuário mandou no pacote
        livro = Livro(
            titulo=dados['titulo'],
            autor=dados['autor'],
            issn=dados['issn'],
            paginas=dados['paginas']
        )

        BD.session.add(livro)    # Coloca o livro na fila para salvar
        BD.session.commit()     # Salva definitivamente no arquivo de banco de dados

        # Devolve uma mensagem avisando quem enviou que deu tudo certo
        return jsonify({"mensagem": "Livro cadastrado"}), 201 # Código 210 significa: "Criado com sucesso!"


# =========================================================================
# ROTA 3: Remover Livro (Endereço: http://127.0.0.1:5000/livros/NUMERO_DO_ID)
# =========================================================================
@APP.route("/livros/<int:id>", methods=['DELETE'])
def deletar_livro(id):
    # O gerente procura no banco se existe algum livro com o número de ID enviado na URL
    livro = Livro.query.get(id)
    
    # Se o ID não existir (por exemplo, tentar apagar o ID 999 que não foi cadastrado):
    if livro is None:
        return jsonify({"erro": "Livro não encontrado"}), 404 # Código 404 significa: "Não encontrado!"

    # Se o livro existir, o gerente faz a remoção:
    BD.session.delete(livro) # Coloca o livro na fila de exclusão
    BD.session.commit()      # Apaga definitivamente do arquivo do banco

    # Devolve uma mensagem confirmando a exclusão
    return jsonify({"mensagem": "Livro removido com sucesso"}), 200 # Código 200 significa: "Sucesso!"


# =========================================================================
# INICIALIZAÇÃO DO SISTEMA
# =========================================================================
if __name__ == '__main__':
    # Antes do site ligar, entramos no contexto do aplicativo para preparar o terreno
    with APP.app_context():
        BD.create_all() # Verifica o arquivo. Se as tabelas do banco ainda não existirem, ele cria elas do zero automaticamente.
    
    # Liga o servidor do site no seu computador (com o modo debug ativado para mostrar erros detalhados se algo quebrar)
    APP.run(debug=True)