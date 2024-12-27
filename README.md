# simple-learning
# Documentação do Projeto de Site para Curso Online


## Introdução
Este é um projeto de site para cursos online desenvolvido utilizando o framework Django. O projeto oferece funcionalidades para gerenciar cursos, instrutores, alunos e matrículas, além de permitir a interação entre estudantes e conteúdos.

## Tecnologias Utilizadas

- **Framework**: Django
- **Linguagem de Programação**: Python 3.8+
- **Banco de Dados**: SQLite (padrão do Django)
- **Frontend**: HTML, CSS e JavaScript
- **Outras Dependências**: Django REST Framework (DRF) para APIs, Bootstrap para estilização

## Guia de Instalação

Siga os passos abaixo para configurar e executar o projeto localmente:

### 1. Pré-requisitos

Certifique-se de ter os seguintes itens instalados em sua máquina:
- Python 3.8 ou superior
- Git

### 2. Clonar o Repositório

Clone este repositório para sua máquina local:
```bash
git clone https://github.com/james-sousa/simple-learning.git
cd simple-learning
```

### 3. Configurar o Ambiente Virtual

Crie e ative um ambiente virtual para o projeto:
```bash
python -m venv venv
source venv/bin/activate
No Windows: venv\Scripts\activate
```


### 4. Configurar o Banco de Dados

Por padrão, o Django utiliza o SQLite como banco de dados. Não é necessário configurar credenciais adicionais. O arquivo do banco será criado automaticamente no diretório do projeto.

Se desejar usar outro banco de dados (como PostgreSQL), atualize as configurações no arquivo `settings.py`.

### 5. Aplicar Migrações

Execute as migrações para criar as tabelas no banco de dados:
```bash
pip install django
python manage.py migrate
```

### 6. Criar um Superusuário

Crie um superusuário para acessar a área administrativa do Django:
```bash
python manage.py createsuperuser
```

### 7. Executar o Servidor de Desenvolvimento

Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

Acesse o projeto no navegador em [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Funcionalidades Principais

- Gerenciamento de cursos, alunos e instrutores
- API REST para integração com sistemas externos
- Interface responsiva com Bootstrap

---
Este projeto foi desenvolvido para facilitar a criação e gerenciamento de cursos online de forma simples e escalável.

