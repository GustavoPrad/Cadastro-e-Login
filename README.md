# Sistema de Cadastro e Login de Usuários

Este é um sistema de cadastro e login de usuários desenvolvido com Flask e SQLite3. O sistema permite criar, editar e visualizar usuários. Os usuários podem ser ativados ou desativados, mas a exclusão não é permitida. Usuários desativados não podem acessar o sistema.

## Funcionalidades

- **Cadastro de usuários**: Permite o cadastro de novos usuários com login, senha, nome completo e status (ativo ou inativo).
- **Login de usuários**: Apenas usuários ativos podem se logar no sistema.
- **Gerenciamento de status**: Administradores podem modificar o status de um usuário (ativo ou inativo).
- **Segurança**: As senhas são armazenadas de forma segura usando hashing (`werkzeug.security`).

## Requisitos para Rodar a Aplicação

Para rodar esta aplicação em sua máquina local, siga os passos abaixo:

### 1. Pré-requisitos

- **Python 3.7+**: Certifique-se de ter o Python instalado em sua máquina. Você pode baixar a versão mais recente [aqui](https://www.python.org/downloads/).
- **Virtualenv** (opcional, mas recomendado): Para criar um ambiente virtual isolado.

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
