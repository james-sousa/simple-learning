# Setup Inicial do Sistema de Progresso e Certificados

Este arquivo documenta como configurar inicialmente o sistema de progresso e certificados.

## Passo 1: Instalar Dependências

```bash
pip install -r requirements.txt
```

ou especificamente para certificados:

```bash
pip install reportlab
```

## Passo 2: Executar Migrações

Crie as migrações dos novos modelos:

```bash
python manage.py makemigrations cursos
```

Você verá algo como:

```
Migrations for 'cursos':
  cursos/migrations/XXXX_lesson_progress.py
    - Create model LessonProgress
    - Create model CourseProgress
    - Create model Certificate
```

Aplique as migrações:

```bash
python manage.py migrate cursos
```

## Passo 3: Verificar Modelos no Admin

1. Acesse: http://127.0.0.1:8000/admin/
2. Você verá os novos modelos:
   - LessonProgress (Progresso da Aula)
   - CourseProgress (Progresso do Curso)
   - Certificate (Certificado)

## Passo 4: Testar o Sistema

### Via Django Shell

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from cursos.models import Course, Enrollment
from cursos.progress import ProgressManager, CertificateManager

# Obter usuário e curso
user = User.objects.first()
course = Course.objects.first()

# Criar matrícula
enrollment = Enrollment.objects.create(user=user, course=course, status=1)

# Inicializar progresso
ProgressManager.initialize_course_progress(user, enrollment)

# Completar todas as aulas
for lesson in course.lessons.all():
    ProgressManager.mark_lesson_complete(user, lesson)

# Gerar certificado
cert = CertificateManager.check_and_generate_certificate(user, course)
print(f"Certificado: {cert.certificate_number}")
```

### Via Página Web

1. Acesse: http://127.0.0.1:8000/cursos/
2. Matricule-se em um curso
3. Acesse as aulas e marque como concluídas
4. Ao completar todas as aulas, o certificado será gerado automaticamente
5. Baixe o certificado em "Meus Certificados"

## Passo 5: Estrutura de Arquivos

Confirme que os seguintes arquivos foram criados/modificados:

```
✓ cursos/models.py              (Modificado - novos modelos)
✓ cursos/views.py               (Novo - 11 views novas)
✓ cursos/progress.py            (Modificado - gerenciadores)
✓ cursos/urls.py                (Modificado - novas rotas)
✓ cursos/admin.py               (Modificado - registros admin)
✓ cursos/exemplos.py            (Novo - exemplos de uso)
✓ requirements.txt              (Novo - dependências)
✓ DOCUMENTACAO_PROGRESSO.md     (Novo - documentação completa)
✓ SETUP.md                      (Este arquivo)
```

## Passo 6: Configurações Opcionais

### settings.py

Se desejar adicionar configurações customizadas, adicione ao final de `settings.py`:

```python
# Configurações de Certificado
CERTIFICATE_SETTINGS = {
    'CERTIFICATE_EXPIRY_DAYS': None,  # Sem expiração se None
    'GENERATE_PDF': True,  # Gerar PDF automaticamente
    'INSTITUTION_NAME': 'Simple Learning',
    'INSTITUTION_LOGO': 'path/to/logo.png',
}

# Pasta de mídia para certificados
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'simplemooc' / 'media'
```

### urls.py (Projeto Principal)

Confirme que a seguinte configuração está em `simplemooc/urls.py`:

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include('accounts.urls', namespace='accounts')),
    path('cursos/', include('cursos.urls', namespace='cursos')),
    path('', include('core.urls', namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Troubleshooting

### Erro: "No module named 'reportlab'"

```bash
pip install reportlab
```

### Erro: "django.db.utils.OperationalError: no such table"

Execute:
```bash
python manage.py migrate
```

### Certificado PDF não é gerado

1. Confirme que reportlab está instalado: `pip install reportlab`
2. Verifique se o progresso do curso é 100%
3. Confirme que a pasta `media/certificates/` existe e tem permissões de escrita

## Próximos Passos

1. Criar templates para exibir progresso (dashboard, página de aula)
2. Criar JavaScript para marcar aulas como concluídas via AJAX
3. Personalizar design do certificado
4. Adicionar notificações/emails ao completar cursos
5. Criar relatórios de progresso para instrutores

## Suporte

Para dúvidas ou problemas, consulte:
- DOCUMENTACAO_PROGRESSO.md - Documentação completa do sistema
- cursos/exemplos.py - Exemplos de código
- Django Shell para testes interativos

## Versão

Sistema de Progresso e Certificados - v1.0
Data: 13 de Novembro de 2025
