"""
Exemplos de uso do sistema de Progresso e Certificados

Este arquivo demonstra como usar as funcionalidades de progresso e certificados
através de código Python. Ideal para testes e entendimento do sistema.
"""

# ===========================
# EXEMPLO 1: Inicializar Progresso
# ===========================

from django.contrib.auth.models import User
from cursos.models import Course, Enrollment
from cursos.progress import ProgressManager

# Obter usuário e curso
user = User.objects.get(username='joao')
course = Course.objects.get(slug='python-iniciante')

# Criar matrícula
enrollment = Enrollment.objects.create(
    user=user,
    course=course,
    status=1  # Aprovado
)

# Inicializar progresso
progress = ProgressManager.initialize_course_progress(user, enrollment)
print(f"Progresso inicializado: {progress.progress_percentage}%")


# ===========================
# EXEMPLO 2: Marcar Aulas como Concluídas
# ===========================

from cursos.models import Lesson

# Obter todas as aulas do curso
lessons = course.lessons.all()

# Marcar primeira aula como concluída
lesson1 = lessons.first()
progress_obj = ProgressManager.mark_lesson_complete(user, lesson1)
print(f"Aula '{lesson1.name}' marcada como concluída")

# Verificar progresso atualizado
course_progress = ProgressManager.get_course_progress(user, course)
print(f"Progresso do curso: {course_progress.progress_percentage}%")
print(f"Aulas concluídas: {course_progress.completed_lessons}/{course_progress.total_lessons}")


# ===========================
# EXEMPLO 3: Completar Todas as Aulas
# ===========================

for lesson in lessons:
    ProgressManager.mark_lesson_complete(user, lesson)
    print(f"✓ {lesson.name}")

# Verificar progresso final
course_progress = ProgressManager.get_course_progress(user, course)
print(f"\nProgresso final: {course_progress.progress_percentage}%")


# ===========================
# EXEMPLO 4: Gerar Certificado
# ===========================

from cursos.progress import CertificateManager

# Verificar e gerar certificado (automático)
certificate = CertificateManager.check_and_generate_certificate(user, course)

if certificate:
    print(f"Certificado gerado!")
    print(f"Número: {certificate.certificate_number}")
    print(f"Emitido em: {certificate.issued_at}")
else:
    print("Certificado não gerado (progresso < 100%)")


# ===========================
# EXEMPLO 5: Obter Certificado
# ===========================

# Buscar certificado existente
certificate = CertificateManager.get_certificate(user, course)

if certificate:
    print(f"Certificado encontrado!")
    print(f"Número: {certificate.certificate_number}")
    print(f"Arquivo: {certificate.certificate_file}")
else:
    print("Nenhum certificado para este usuário/curso")


# ===========================
# EXEMPLO 6: Relatório de Progresso do Usuário
# ===========================

# Obter todos os cursos do usuário
all_progress = ProgressManager.get_user_courses_progress(user)

print("\n=== RELATÓRIO DE PROGRESSO ===\n")
for progress in all_progress:
    status = "✓ Completo" if progress.completed_at else "⏳ Em andamento"
    print(f"{progress.course.name}: {progress.progress_percentage}% {status}")
    print(f"  Aulas: {progress.completed_lessons}/{progress.total_lessons}")
    
    # Verificar certificado
    cert = CertificateManager.get_certificate(user, progress.course)
    if cert:
        print(f"  📜 Certificado: {cert.certificate_number}")
    print()


# ===========================
# EXEMPLO 7: Desmarcar Aula como Completa
# ===========================

# Desmarcar primeira aula
ProgressManager.mark_lesson_incomplete(user, lesson1)
print(f"Aula '{lesson1.name}' desmarcada")

# Verificar progresso reduzido
course_progress = ProgressManager.get_course_progress(user, course)
print(f"Novo progresso: {course_progress.progress_percentage}%")


# ===========================
# EXEMPLO 8: Visualizar Aulas Concluídas
# ===========================

# Obter todas as aulas concluídas
completed_lessons = ProgressManager.get_all_lessons_completed(user, course)

print(f"Aulas concluídas ({completed_lessons.count()}):")
for lesson_progress in completed_lessons:
    print(f"  - {lesson_progress.lesson.name} (em {lesson_progress.completed_at})")


# ===========================
# EXEMPLO 9: Usar em uma View Django
# ===========================

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def mark_lesson_complete_example(request, slug, lesson_id):
    """Exemplo de como usar em uma view Django"""
    
    course = Course.objects.get(slug=slug)
    lesson = Lesson.objects.get(id=lesson_id)
    
    # Marcar como completa
    ProgressManager.mark_lesson_complete(request.user, lesson)
    
    # Obter progresso atualizado
    course_progress = ProgressManager.get_course_progress(request.user, course)
    course_progress.calculate_progress()
    course_progress.save()
    
    # Gerar certificado se necessário
    certificate = None
    if course_progress.progress_percentage >= 100:
        certificate = CertificateManager.check_and_generate_certificate(
            request.user, course
        )
    
    return JsonResponse({
        'success': True,
        'progress_percentage': course_progress.progress_percentage,
        'completed_lessons': course_progress.completed_lessons,
        'total_lessons': course_progress.total_lessons,
        'certificate_generated': certificate is not None,
    })


# ===========================
# EXEMPLO 10: Query Avançadas
# ===========================

from django.db.models import Q, F

# Usuários que completaram mais de 50% de um curso
from cursos.models import CourseProgress

advanced_students = CourseProgress.objects.filter(
    course=course,
    progress_percentage__gte=50
).order_by('-progress_percentage')

print(f"Alunos avançados: {advanced_students.count()}")
for progress in advanced_students:
    print(f"  {progress.user.username}: {progress.progress_percentage}%")


# Usuários que completaram o curso
completed_students = CourseProgress.objects.filter(
    course=course,
    completed_at__isnull=False
)

print(f"\nAlunos que completaram: {completed_students.count()}")
for progress in completed_students:
    print(f"  {progress.user.username} - {progress.completed_at}")


# ===========================
# EXEMPLO 11: Importar em manage.py shell
# ===========================

# Execute: python manage.py shell
# >>> from exemplos import *
# >>> # Agora todos os exemplos estão disponíveis

"""
Para usar este arquivo no Django shell:

1. Coloque este arquivo em: cursos/exemplos.py

2. Execute no terminal:
   python manage.py shell

3. No shell do Django:
   >>> from cursos.exemplos import *
   >>> # Todos os exemplos podem ser usados

"""
