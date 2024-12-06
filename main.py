from flask import Flask, request, render_template, flash, redirect, url_for, session
import os
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import secrets
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github
app = Flask(__name__)
app.secret_key = 'peixefrito123'

# Configuração para autenticação com o Google
google_bp = make_google_blueprint(
    client_id="SEU_GOOGLE_CLIENT_ID",
    client_secret="SEU_GOOGLE_CLIENT_SECRET",
    redirect_to="google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

# Configuração para autenticação com o GitHub
github_bp = make_github_blueprint(
    client_id="Ov23liGunVmtbGYth4Rv",
    client_secret="0496405b06a8dedbe843f27591c2fc7f86abf7c2",
    redirect_to="github_login"
)
app.register_blueprint(github_bp, url_prefix="/login/github")

# Salvar imagens de produtos
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_db():
    conn = sqlite3.connect('banco.db')
    conn.row_factory = sqlite3.Row
    return conn

# Cadastro de produtos da loja
@app.route('/adminloja', methods=['GET', 'POST'])
def adminloja():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        imagem = request.files['imagem']

        if imagem:
            filename = secure_filename(imagem.filename)
            imagem_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagem.save(imagem_path)

            cursor.execute(
                'INSERT INTO produtos (nome, descricao, imagem) VALUES (?, ?, ?)',
                (nome, descricao, imagem_path)
            )
            conn.commit()

            flash('Produto cadastrado com sucesso!', 'success')
        else:
            flash('Erro ao cadastrar produto: a imagem é obrigatória.', 'danger')

    # Listagem de produtos
    cursor.execute('SELECT * FROM produtos ORDER BY created_at DESC')
    produtos = cursor.fetchall()
    conn.close()

    return render_template('adminloja.html', produtos=produtos)

# Rota para apagar produto
@app.route('/adminloja/delete/<int:id>', methods=['POST'])
def delete_produto(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM produtos WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Produto apagado com sucesso!', 'success')
    return redirect(url_for('adminloja'))

# Rota para login com Google
@app.route('/login/google')
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    user_info = resp.json()
    session['google_user'] = user_info
    flash(f"Logado com Google como {user_info['email']}", "success")
    return redirect(url_for("loja"))

# Rota para login com GitHub
@app.route('/login/github')
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    assert resp.ok, resp.text
    user_info = resp.json()
    session['github_user'] = user_info
    flash(f"Logado com GitHub como {user_info['login']}", "success")
    return redirect(url_for("loja"))

# Configuração do banco de dados SQLite3
DATABASE = 'database.db'

# Configuração do servidor de e-mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'gustavoprado641@gmail.com'
app.config['MAIL_PASSWORD'] = 'qlif zytt sukc pqwj'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# Serializador para gerar os tokens seguros
s = URLSafeTimedSerializer(app.secret_key)

# Conectar ao BD
def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


# Criar a tabela de dados
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
            db.commit()
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

        cursor.execute('SELECT * FROM usuarios WHERE login = ?', (login,))
        user = cursor.fetchone()

        if user and check_password_hash(user['senha'], senha):
            if login == 'administrador@gmail.com' and senha == 'admin123':
                # Credenciais específicas do administrador
                flash('Bem-vindo, Administrador!', 'success')
                return redirect(url_for('adminloja'))
            elif user['status'] == 1:  # 1 é ativo, 2 é inativo
                flash('Login bem-sucedido!', 'success')
                return redirect(url_for('loja'))
            else:
                flash('Conta inativa.', 'danger')
        else:
            flash('Login ou senha inválidos.', 'danger')

        conn.close()

    return render_template('login.html')


# Rota para solicitar redefinição de senha
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        token = s.dumps(email, salt='password_recovery')
        msg = Message('Redefinição de senha', sender='gustavoprado641@gmail.com', recipients=[email])
        link = url_for('reset_password', token=token, _external=True)
        msg.body = f'Clique no link para redefinir sua senha: {link}'
        mail.send(msg)

        flash('Um link de recuperação de senha foi enviado para o seu email', category='success')

        return redirect(url_for('login'))

    return render_template('forgot_password.html')

# Rota para redefinir a senha
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password_recovery', max_age=3600)  # 1 hora
    except SignatureExpired:
        return '<h1> O link de redefinição de senha expirou!!!</h1>'
    except BadSignature:
        return '<h1> Token inválido!!! </h1>'

    if request.method == 'POST':
        new_password = request.form['password']
        hashed_password = generate_password_hash(new_password)

        # Conectar ao banco e atualizar a senha
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE usuarios SET senha = ?, reset_token = NULL, reset_token_expiry = NULL WHERE login = ?',
            (hashed_password, email)
        )
        conn.commit()
        conn.close()

        flash('Sua senha foi redefinida com sucesso!', category='success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)


# Rota para loja
@app.route('/loja')
def loja():
    conn = get_db()
    cursor = conn.cursor()

    # Configuração de paginação
    page = request.args.get('page', 1, type=int)  # Página atual
    per_page = 4  # Produtos por página
    offset = (page - 1) * per_page  # Índice inicial

    cursor.execute('SELECT * FROM produtos ORDER BY created_at DESC LIMIT ? OFFSET ?', (per_page, offset))
    produtos = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) FROM produtos')
    total_produtos = cursor.fetchone()[0]
    total_pages = -(-total_produtos // per_page)  # Arredondamento para cima

    conn.close()

    return render_template(
        'loja.html',
        produtos=produtos,
        current_page=page,
        total_pages=total_pages,
    )



# Rota para cadastro de usuários
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        login = request.form['login']
        senha = generate_password_hash(request.form['senha'])
        nome_completo = request.form['nome_completo']
        status = request.form['status']

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM usuarios WHERE login = ?', (login,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Login já cadastrado. Tente outro.', 'danger')
        else:
            cursor.execute(
                'INSERT INTO usuarios (login, senha, nome_completo, status, created, modified) VALUES (?, ?, ?, ?, ?, ?)',
                (login, senha, nome_completo, status, datetime.now(), datetime.now())
            )
            conn.commit()
            flash('Usuário cadastrado com sucesso!', 'success')

        conn.close()
        return redirect(url_for('cadastro'))

    # Paginação
    page = int(request.args.get('page', 1))
    limit = 10
    offset = (page - 1) * limit

    conn = get_db()
    cursor = conn.cursor()

    # Total de usuários para calcular páginas
    total_usuarios = cursor.execute('SELECT COUNT(*) FROM usuarios').fetchone()[0]
    total_pages = (total_usuarios + limit - 1) // limit  # Arredondar para cima

    usuarios = cursor.execute(
        'SELECT * FROM usuarios LIMIT ? OFFSET ?', (limit, offset)
    ).fetchall()

    conn.close()

    return render_template('cadastro.html', usuarios=usuarios, page=page, total_pages=total_pages)



# Rota para edição de usuários
@app.route('/editar_usuario/<int:id>', methods=['POST'])
def editar_usuario(id):
    nome_completo = request.form['nome_completo']
    login = request.form['login']
    status = request.form['status']

    conn = get_db()
    conn.execute(
        'UPDATE usuarios SET nome_completo = ?, login = ?, status = ?, modified = ? WHERE id = ?',
        (nome_completo, login, status, datetime.now(), id)
    )
    conn.commit()
    conn.close()

    flash('Usuário atualizado com sucesso!', 'success')
    return redirect(url_for('cadastro'))

# Inicializar a aplicação Flask
if __name__ == '__main__':
    app.run(debug=True, port=5002)