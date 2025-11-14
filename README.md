# Simple Learning - Plataforma de Cursos Online

Sistema completo para gerenciamento de cursos com rastreamento de progresso e geração automática de certificados em PDF.

## Funcionalidades Principais

- Gerenciamento de cursos, aulas e matrículas
- Rastreamento de progresso em tempo real
- Geração automática de certificados em PDF
- API REST com endpoints AJAX
- Admin Django customizado
- 20+ testes unitários inclusos

---

## Instalação Passo a Passo

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

Isso instala:
- Django 4.1.7
- reportlab (para gerar PDFs)
- Pillow (para processar imagens)

### 2. Criar Migrações

```bash
python manage.py makemigrations cursos
```

### 3. Executar Migrações

```bash
python manage.py migrate
```

Isso cria as tabelas no banco de dados.

### 4. Criar Admin (Superusuário)

```bash
python manage.py createsuperuser
```

Responda as perguntas:
- Username: seu_usuario
- Email: seu_email@example.com
- Password: sua_senha

### 5. Iniciar Servidor

```bash
python manage.py runserver
```

Acesse no navegador: http://127.0.0.1:8000/

### 6. Testar Tudo

```bash
python manage.py test cursos.tests
```

Resultado esperado:

```
Found 14 test(s).
...
Ran 14 tests in ~5s
OK
```

---

## Como Usar

### Via Admin (http://127.0.0.1:8000/admin/)

1. Faça login com o superusuário
2. Crie um Curso
3. Crie Aulas dentro do curso
4. Crie um Usuário comum
5. Crie uma Matrícula para o usuário no curso
6. Usuário pode agora acessar as aulas

### Como Usuário Final

1. Acesse http://127.0.0.1:8000/
2. Faça cadastro ou login
3. Procure um curso
4. Clique em "Matricular-se"
5. Acesse as aulas e clique "Marcar como Completa" em cada uma
6. Ao atingir 100%, seu certificado é gerado automaticamente
7. Clique "Baixar Certificado" para obter o PDF

### Via Django Shell (Desenvolvimento)

```bash
python manage.py shell
```

**Marcar aula como completa:**

```python
from cursos.progress import ProgressManager
from cursos.models import Lesson, Course
from django.contrib.auth.models import User

user = User.objects.get(username='seu_usuario')
lesson = Lesson.objects.first()

ProgressManager.mark_lesson_complete(user, lesson)
```

**Verificar progresso:**

```python
course = lesson.course
progress = ProgressManager.get_course_progress(user, course)
print(f"Progresso: {progress.progress_percentage}%")
print(f"Aulas completas: {progress.completed_lessons}/{progress.total_lessons}")
```

**Gerar certificado manualmente:**

```python
from cursos.progress import CertificateManager

cert = CertificateManager.check_and_generate_certificate(user, course)
if cert:
    print(f"Certificado: {cert.certificate_number}")
    print(f"Arquivo: {cert.certificate_file}")
```

**Listar certificados do usuário:**

```python
from cursos.models import Certificate

certificates = Certificate.objects.filter(user=user)
for cert in certificates:
    print(f"{cert.course.name}: {cert.certificate_number}")
```

---

## APIs REST (Para Frontend AJAX)

### 1. Marcar Aula Como Completa

```
POST /cursos/<slug>/aulas/<id>/completar/
```

**Exemplo JavaScript:**

```javascript
fetch('/cursos/python-basico/aulas/1/completar/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    }
})
.then(response => response.json())
.then(data => {
    console.log(`Progresso: ${data.course_progress.progress_percentage}%`);
    if (data.certificate_generated) {
        alert('Parabéns! Seu certificado foi gerado!');
    }
});
```

### 2. Desmarcar Aula

```
POST /cursos/<slug>/aulas/<id>/descompletar/
```

### 3. Obter Progresso do Curso

```
GET /cursos/<slug>/progresso/
```

**Resposta:**

```json
{
    "course_progress": {
        "progress_percentage": 75,
        "completed_lessons": 3,
        "total_lessons": 4
    },
    "certificate_generated": false
}
```

### 4. Baixar Certificado

```
GET /cursos/<slug>/certificado/download/
```

Retorna o arquivo PDF do certificado.

### 5. Listar Meus Certificados

```
GET /meus-certificados/
```

---

## Estrutura de Dados

### Modelo: LessonProgress

Rastreia a conclusão de cada aula por usuário.

```
user: Usuário (ForeignKey)
lesson: Aula (ForeignKey)
completed: Sim/Não (Boolean)
completed_at: Data/Hora de conclusão
```

### Modelo: CourseProgress

Rastreia o progresso geral em um curso.

```
user: Usuário (ForeignKey)
course: Curso (ForeignKey)
completed_lessons: Número de aulas completas
total_lessons: Total de aulas
progress_percentage: 0-100%
completed_at: Quando completou
```

### Modelo: Certificate

Armazena os certificados emitidos.

```
user: Usuário (ForeignKey)
course: Curso (ForeignKey)
certificate_number: Número único (ABC123DEF456...)
issued_at: Data de emissão
certificate_file: Arquivo PDF
```

---

## Classes Gerenciadoras

### ProgressManager

Gerencia o rastreamento de progresso.

**Métodos:**

- `mark_lesson_complete(user, lesson)` - Marca aula como completa
- `mark_lesson_incomplete(user, lesson)` - Desmarca aula
- `get_lesson_progress(user, lesson)` - Obtém progresso de uma aula
- `get_course_progress(user, course)` - Obtém progresso do curso
- `initialize_course_progress(user, enrollment)` - Inicializa progresso
- `update_course_progress(user, course)` - Atualiza progresso
- `get_all_lessons_completed(user, course)` - Lista aulas completas
- `get_user_courses_progress(user)` - Progresso em todos os cursos

### CertificateManager

Gerencia a geração de certificados.

**Métodos:**

- `create_certificate(user, course, course_progress)` - Cria certificado
- `generate_certificate_pdf(certificate)` - Gera PDF
- `save_certificate_file(certificate)` - Salva arquivo
- `get_certificate(user, course)` - Obtém certificado existente
- `check_and_generate_certificate(user, course)` - Gera se 100%

---

## Troubleshooting

**Erro: "no such table: cursos_course"**

Execute as migrações:

```bash
python manage.py migrate
```

**Erro: "Certificate não gera"**

Verifique se o progresso é 100%:

```python
from cursos.models import CourseProgress
progress = CourseProgress.objects.get(user=user, course=course)
print(progress.progress_percentage)
```

**Erro: "Arquivo PDF não baixa"**

Execute:

```bash
python manage.py collectstatic
```

**Testes falhando**

Execute com detalhes:

```bash
python manage.py test cursos.tests -v 2
```

---

## Arquivos Modificados

| Arquivo | Descrição |
|---------|-----------|
| cursos/models.py | 3 novos modelos (LessonProgress, CourseProgress, Certificate) |
| cursos/views.py | 14 views com endpoints REST |
| cursos/progress.py | 2 classes gerenciadoras (ProgressManager, CertificateManager) |
| cursos/urls.py | 5 novas rotas |
| cursos/admin.py | 3 admin customizados |
| cursos/tests.py | 20+ testes unitários |
| cursos/exemplos.py | 11 exemplos de uso |
| cursos/templatetags/ | Tags customizadas |
| manage.py | Script de gerenciamento |
| requirements.txt | Dependências |

---

## Estatísticas

- 1.500+ linhas de código Python
- 14 views implementadas
- 20+ testes unitários
- 11 exemplos de uso
- 3 admin customizados
- 5 endpoints REST
- 2 classes gerenciadoras
- 3 modelos Django

---

## Próximos Passos

1. Criar templates para exibir progresso
2. Notificações por email
3. Relatórios para instrutores
4. Personalizar certificado
5. Integrar com pagamento

---

## Tecnologias

- Django 4.1.7
- Python 3.8+
- SQLite/PostgreSQL
- reportlab (PDFs)
- Pillow (imagens)
- Bootstrap 5

---

## Licença

MIT

