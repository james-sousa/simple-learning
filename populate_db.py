"""
Script para popular o banco com dados de exemplo
Execute: python manage.py shell < populate_db.py
"""

from django.contrib.auth.models import User
from cursos.models import Course, Lesson, Enrollment, Material
from cursos.progress import ProgressManager
from datetime import datetime, timedelta

print("Criando dados de exemplo...")

# Limpar dados anteriores (opcional)
# Course.objects.all().delete()
# User.objects.filter(is_superuser=False).delete()

# Criar usuários
users = []
for i in range(1, 4):
    user, created = User.objects.get_or_create(
        username=f'aluno{i}',
        defaults={
            'email': f'aluno{i}@example.com',
            'first_name': f'Aluno',
            'last_name': f'{i}'
        }
    )
    if created:
        user.set_password('senha123')
        user.save()
        print(f"✓ Usuário criado: aluno{i} (senha: senha123)")
    users.append(user)

# Criar cursos
cursos_data = [
    {
        'name': 'Python para Iniciantes',
        'slug': 'python-iniciantes',
        'description': 'Aprenda Python do zero. Curso completo com exercícios práticos.',
        'about': 'Neste curso você aprenderá os fundamentos da linguagem Python, desde variáveis até programação orientada a objetos.',
        'aulas': [
            'Introdução ao Python',
            'Variáveis e Tipos de Dados',
            'Estruturas de Controle',
            'Funções e Módulos',
            'Orientação a Objetos'
        ]
    },
    {
        'name': 'Django Avançado',
        'slug': 'django-avancado',
        'description': 'Domine o framework Django criando aplicações web completas.',
        'about': 'Curso avançado de Django cobrindo models, views, templates, REST APIs e deploy.',
        'aulas': [
            'Arquitetura MTV',
            'Models e ORM',
            'Views e URLs',
            'Templates e Formulários',
            'Django REST Framework',
            'Deploy em Produção'
        ]
    },
    {
        'name': 'JavaScript Moderno',
        'slug': 'javascript-moderno',
        'description': 'ES6+, Async/Await, Promises e muito mais.',
        'about': 'Aprenda JavaScript moderno com as últimas features da linguagem.',
        'aulas': [
            'ES6 - Let, Const e Arrow Functions',
            'Destructuring e Spread Operator',
            'Promises e Async/Await',
            'Módulos ES6',
            'Fetch API e AJAX'
        ]
    },
    {
        'name': 'Git e GitHub',
        'slug': 'git-github',
        'description': 'Controle de versão profissional.',
        'about': 'Domine Git e GitHub para trabalhar em equipe de forma eficiente.',
        'aulas': [
            'Introdução ao Git',
            'Commits e Branches',
            'Merge e Rebase',
            'GitHub - Push e Pull',
            'Pull Requests e Code Review'
        ]
    }
]

cursos = []
for curso_data in cursos_data:
    course, created = Course.objects.get_or_create(
        slug=curso_data['slug'],
        defaults={
            'name': curso_data['name'],
            'description': curso_data['description'],
            'about': curso_data['about'],
            'start_date': datetime.now().date()
        }
    )
    if created:
        print(f"✓ Curso criado: {course.name}")
        
        # Criar aulas
        for idx, aula_nome in enumerate(curso_data['aulas'], 1):
            lesson = Lesson.objects.create(
                name=aula_nome,
                course=course,
                number=idx,
                description=f'Conteúdo da aula {aula_nome}',
                release_date=datetime.now().date()
            )
            
            # Adicionar material
            Material.objects.create(
                name=f'Slides - {aula_nome}',
                lesson=lesson,
                file=None
            )
            
        print(f"  → {len(curso_data['aulas'])} aulas criadas")
    cursos.append(course)

# Matricular usuários nos cursos
matriculas_config = [
    # aluno1: matriculado em Python e Django, progresso parcial
    (users[0], [cursos[0], cursos[1]], [3, 2]),  # 3 aulas em Python, 2 em Django
    # aluno2: matriculado em JavaScript e Git, progresso completo em Git
    (users[1], [cursos[2], cursos[3]], [2, 5]),  # 2 aulas em JS, 5 em Git (completo)
    # aluno3: matriculado apenas em Python, nenhuma aula completa
    (users[2], [cursos[0]], [0]),
]

for user, user_courses, progress_list in matriculas_config:
    for course, num_aulas in zip(user_courses, progress_list):
        enrollment, created = Enrollment.objects.get_or_create(
            user=user,
            course=course
        )
        
        if created:
            print(f"✓ Matrícula criada: {user.username} → {course.name}")
            
            # Inicializar progresso
            ProgressManager.initialize_course_progress(user, enrollment)
            
            # Completar aulas
            lessons = list(course.lessons.all().order_by('number')[:num_aulas])
            for lesson in lessons:
                ProgressManager.mark_lesson_complete(user, lesson)
            
            if num_aulas > 0:
                progress = ProgressManager.get_course_progress(user, course)
                print(f"  → Progresso: {progress.progress_percentage:.0f}%")
                
                # Se completou 100%, certificado já foi gerado automaticamente
                if progress.progress_percentage == 100:
                    from cursos.models import Certificate
                    cert = Certificate.objects.get(user=user, course=course)
                    print(f"  → Certificado gerado: {cert.certificate_number}")

print("\n" + "="*50)
print("DADOS CRIADOS COM SUCESSO!")
print("="*50)
print("\nUsuários criados:")
print("  - aluno1 / senha123 (progresso parcial em 2 cursos)")
print("  - aluno2 / senha123 (1 certificado completo)")
print("  - aluno3 / senha123 (matriculado, sem progresso)")
print("\nCursos criados:")
for curso in cursos:
    print(f"  - {curso.name} ({curso.lessons.count()} aulas)")
print("\nAcesse: http://127.0.0.1:8000/")
print("Admin: http://127.0.0.1:8000/admin/")
