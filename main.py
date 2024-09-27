from flask import Flask, request, render_template, flash, redirect, url_for
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash     #converte dados em senha, sem reversão

# Configuração da aplicação Flask
app = Flask(__name__)
app.secret_key = 'chave_secreta'

# Configuração do banco de dados SQLite3
DATABASE = 'database.db'

# Conectar ao BD
def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

# Criar a tabela de dados, se ainda não existir
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
            db.commit()

# Rota para inicializar o banco de dados
@app.route('/initdb')
def initialize_database():
    init_db()
    flash('Banco de dados inicializado com sucesso', 'success')
    return redirect(url_for('home'))

# Rota raiz para renderizar o template HTML
@app.route('/')
def home():
    return render_template('base.html')

# Rota para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']

        conn = get_db()
        cursor = conn.cursor()

        # Verificação de credencais
        cursor.execute('SELECT * FROM usuarios WHERE login = ?', (login,))
        user = cursor.fetchone()

        if user and check_password_hash(user['senha'], senha):
            # Verificação se usuário é ativo
            if user['status'] == 1:  # 1 é ativo, 2 é inativo
                flash('Login bem-sucedido!', 'success')
                return redirect(url_for('loja'))  # Redirecionar para a página loja.html
            else:
                flash('Conta inativa.', 'danger')

        else:
            flash('Login ou senha inválidos.', 'danger')

        conn.close()

    return render_template('login.html')  # Renderize a página de login

# Rota para loja
@app.route('/loja')
def loja():
    return render_template('loja.html')

# Rota para cadastro de usuários
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        login = request.form['login']
        senha = generate_password_hash(request.form['senha'])
        nome_completo = request.form['nome_completo']
        status = request.form['status']  # 1 para ativo ou 0 para inativo

        # Conexão ao banco de dados
        conn = get_db()
        cursor = conn.cursor()

        # Verificando se o login já existe
        cursor.execute('SELECT * FROM usuarios WHERE login = ?', (login,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Login já cadastrado. Tente outro.', 'danger')
        else:
            # Inserindo novo usuário com a data de criação
            cursor.execute(
                'INSERT INTO usuarios (login, senha, nome_completo, status, created, modified) VALUES (?, ?, ?, ?, ?, ?)',
                (login, senha, nome_completo, status, datetime.now(), datetime.now()))
            conn.commit()
            flash('Usuário cadastrado com sucesso!', 'success')

        conn.close()
        return redirect(url_for('cadastro'))

    # Tabela com todos usuários cadastrados
    conn = get_db()
    usuarios = conn.execute('SELECT * FROM usuarios').fetchall()
    conn.close()
    return render_template('cadastro.html', usuarios=usuarios)

# Rota para edição de usuários (não exclui usuário, apenas muda de ativo p/ inativo)
@app.route('/editar_usuario/<int:id>', methods=['POST'])
def editar_usuario(id):
    nome_completo = request.form['nome_completo']
    login = request.form['login']
    status = request.form['status']

    conn = get_db()
    conn.execute('UPDATE usuarios SET nome_completo = ?, login = ?, status = ?, modified = ? WHERE id = ?',
                 (nome_completo, login, status, datetime.now(), id))
    conn.commit()
    conn.close()

    flash('Usuário atualizado com sucesso!', 'success')
    return redirect(url_for('cadastro'))

# Inicializar a aplicação Flask
if __name__ == '__main__':
    app.run(debug=True, port=5002)
