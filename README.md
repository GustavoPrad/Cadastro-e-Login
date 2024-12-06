# Sistema de Cadastro e Login de Usuários e Produtos

# IMPORTANTE
Para aplicação rodar primeiramente fazer a criação do banco de dados utilizando o /initdb. Após isso fazer o cadastro de usuário (isso é necessário pois ele verifica se o email existe no banco antes de enviar link para recuperação de senha.) 

# CONTROLE DE ACESSO
Há dois tipos de usuários, o admin e o usuário comum, a tela de login é a mesma, porém quando autenticado com as credenciais do admin, ele abre uma tela onde ele pode adicionar e remover produtos de uma loja. E quando autenticado com um usuario comum, ele abre a página da loja.
Credenciais para teste:

Usuario comum: 
login: usuariocomum@gmail.com 
senha: usuariocomum

Administrador:
login: administrador@gmail.com
senha: admin123

# PAGINAÇÃO
Há duas páginas que utilizam paginação, a tela de cadastro de usuários, que pode ser acessada clicando no botão "Cadastrar e Gerenciar Usuarios" e também a tela da loja, que pode ser acessada após você logar na aplicação utilizando credenciais previamente cadastradas.

# INTERNACIONALIZAÇÃO
Não foi implementada devido a erros.


Este é um sistema de cadastro e login de usuários e produtos desenvolvido com Flask e SQLite3. O sistema permite criar, editar e visualizar usuários. Os usuários podem ser ativados ou desativados, mas a exclusão não é permitida. Usuários desativados não podem acessar o sistema.

## Funcionalidades

- **Cadastro de usuários**: Permite o cadastro de novos usuários com login, senha, nome completo e status (ativo ou inativo).
- **Login de usuários**: Apenas usuários ativos podem se logar no sistema.
- **Login de usuários via google e Github**: 
- **Gerenciamento de status**: Administradores podem modificar o status de um usuário (ativo ou inativo).
- **Segurança**: As senhas são armazenadas de forma segura usando hashing (`werkzeug.security`).
- **Banco de dados**: Para iniciar banco de dados, acessar página utilizando /initdb no final.
- **Recuperação de senha**: Recuperação de senha.

## Requisitos para Rodar a Aplicação

Para rodar esta aplicação em sua máquina local, siga os passos abaixo:

### 1. Pré-requisitos

- **Python 3.7+**: Certifique-se de ter o Python instalado em sua máquina. Você pode baixar a versão mais recente [aqui](https://www.python.org/downloads/).

### 2. Instalação de Dependências

Clone o repositório e instale as bibliotecas necessárias.

```bash
# Clone o repositório
git clone https://github.com/seu_usuario/sistema-cadastro-login.git
cd sistema-cadastro-login

# (Opcional) Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Para Linux/Mac
venv\Scripts\activate  # Para Windows

# Instale as dependências
pip install -r requirements.txt
