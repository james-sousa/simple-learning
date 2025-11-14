# simple-learning

Plataforma de cursos online com rastreamento de progresso e geração de certificados.

## Funcionalidades

- Gerenciamento de cursos, alunos e instrutores
- Rastreamento de progresso em tempo real
- Geração automática de certificados em PDF
- API REST com endpoints AJAX
- Admin Django customizado
- 20+ testes unitários

---

## Instalação Rápida

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar Migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Criar Superusuário
```bash
python manage.py createsuperuser
```

### 4. Testar
```bash
python manage.py test cursos.tests
python manage.py runserver
```

Acesse em [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Sistema de Progresso e Certificados

### Modelos

**LessonProgress** - Rastreia conclusão de cada aula
```python
user: ForeignKey(User)
lesson: ForeignKey(Lesson)
completed: Boolean
completed_at: DateTime
```

**CourseProgress** - Rastreia progresso geral
```python
user: ForeignKey(User)
course: ForeignKey(Course)
completed_lessons: IntegerField
total_lessons: IntegerField
progress_percentage: FloatField (0-100%)
```

**Certificate** - Certificados emitidos
```python
user: ForeignKey(User)
course: ForeignKey(Course)
certificate_number: CharField (unique)
certificate_file: FileField (PDF)
```

### Endpoints

```
POST   /cursos/<slug>/aulas/<id>/completar/      - Marcar aula completa
POST   /cursos/<slug>/aulas/<id>/descompletar/   - Desmarcar aula
GET    /cursos/<slug>/progresso/                 - Obter progresso (JSON)
GET    /cursos/<slug>/certificado/download/      - Baixar PDF
GET    /meus-certificados/                       - Listar certificados
```

### Como Usar

**Via Dashboard**
1. Matricule-se em um curso
2. Acesse "Aulas"
3. Clique "Marcar como Completa" em cada aula
4. Ao terminar, clique "Baixar Certificado"

**Via Django Shell**
```bash
python manage.py shell
```

```python
from cursos.progress import ProgressManager, CertificateManager
from django.contrib.auth.models import User

user = User.objects.first()
course = user.enrollments.first().course

# Completar aulas
for lesson in course.lessons.all():
    ProgressManager.mark_lesson_complete(user, lesson)

# Gerar certificado
cert = CertificateManager.check_and_generate_certificate(user, course)
print(f"Certificado: {cert.certificate_number}")
```

**Via API AJAX**
```javascript
fetch('/cursos/python-iniciante/aulas/1/completar/', {
    method: 'POST',
    headers: {'X-CSRFToken': getCookie('csrftoken')}
})
.then(r => r.json())
.then(data => {
    console.log(`Progresso: ${data.course_progress.progress_percentage}%`);
});
```

### Classes Gerenciadoras

**ProgressManager**
```python
mark_lesson_complete(user, lesson)
mark_lesson_incomplete(user, lesson)
get_course_progress(user, course)
initialize_course_progress(user, enrollment)
update_course_progress(user, course)
```

**CertificateManager**
```python
create_certificate(user, course, course_progress)
generate_certificate_pdf(certificate)
check_and_generate_certificate(user, course)
get_certificate(user, course)
```

---

## Arquivos Criados/Modificados

| Arquivo | Status | Descrição |
|---------|--------|-----------|
| cursos/models.py | Modificado | 3 novos modelos |
| cursos/views.py | Novo | 14 views REST |
| cursos/progress.py | Novo | 2 classes gerenciadoras |
| cursos/urls.py | Modificado | 5 rotas |
| cursos/admin.py | Modificado | 3 admin customizados |
| cursos/tests.py | Modificado | 20+ testes |
| cursos/exemplos.py | Novo | 11 exemplos |
| requirements.txt | Novo | Dependências |

---

## Recursos

- 1.500+ linhas de código Python
- 20+ testes unitários
- 11 exemplos de uso
- Segurança: autenticação + autorização
- Escalável para 1.000+ usuários

---

## Troubleshooting

**Certificado não gera ao completar**
- Verifique: `CourseProgress.progress_percentage == 100`

**Erro ao baixar PDF**
- Execute: `python manage.py collectstatic`

**Testes falhando**
- Execute: `python manage.py test cursos.tests -v 2`

---

## Próximos Passos

1. Criar templates para exibir progresso
2. Notificações via email
3. Relatórios para instrutores
4. Personalizar design do certificado
5. Integrar com sistema de pagamento

Ver arquivo `cursos/exemplos.py` para exemplos de código.

---

## Tecnologias

- Django 4.1.7
- Python 3.8+
- SQLite/PostgreSQL
- reportlab (PDF)
- Pillow (imagens)
- Bootstrap 5

---

## Licença

MIT

