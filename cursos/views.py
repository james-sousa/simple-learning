"""
Views para gerenciar cursos, aulas, progresso e certificados.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages

from .models import Course, Lesson, Material, Enrollment, Announcement, Comment, CourseProgress, LessonProgress, Certificate
from .progress import ProgressManager, CertificateManager
from .forms import CommentForm


def index(request):
    """
    Lista todos os cursos disponíveis.
    """
    template_name = 'courses/index.html'
    courses = Course.objects.all()
    
    # Filtro de busca
    query = request.GET.get('q', '')
    if query:
        courses = Course.objects.search(query)
    
    context = {
        'courses': courses,
        'query': query,
    }
    return render(request, template_name, context)


def details(request, slug):
    """
    Exibe detalhes de um curso específico.
    """
    template_name = 'courses/details.html'
    course = get_object_or_404(Course, slug=slug)
    enrolled = False
    progress = None
    
    if request.user.is_authenticated:
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course)
            enrolled = enrollment.is_approved()
            progress = ProgressManager.get_course_progress(request.user, course)
        except Enrollment.DoesNotExist:
            pass
    
    context = {
        'course': course,
        'enrolled': enrolled,
        'progress': progress,
    }
    return render(request, template_name, context)


@login_required
def enrollment(request, slug):
    """
    Realiza a matrícula do usuário em um curso.
    """
    course = get_object_or_404(Course, slug=slug)
    
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
        if not enrollment.is_approved():
            enrollment.active()
            messages.success(request, 'Você foi matriculado no curso com sucesso!')
    except Enrollment.DoesNotExist:
        enrollment = Enrollment.objects.create(
            user=request.user,
            course=course,
            status=1
        )
        messages.success(request, 'Você foi matriculado no curso com sucesso!')
    
    # Inicializar progresso do curso
    ProgressManager.initialize_course_progress(request.user, enrollment)
    
    return redirect('cursos:details', slug=slug)


@login_required
def undo_enrollment(request, slug):
    """
    Cancela a matrícula do usuário em um curso.
    """
    course = get_object_or_404(Course, slug=slug)
    
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
        enrollment.status = 2  # Cancelado
        enrollment.save()
        messages.success(request, 'Sua matrícula foi cancelada.')
    except Enrollment.DoesNotExist:
        messages.error(request, 'Você não estava matriculado neste curso.')
    
    return redirect('cursos:details', slug=slug)


def announcements(request, slug):
    """
    Lista os anúncios de um curso.
    """
    template_name = 'courses/announcements.html'
    course = get_object_or_404(Course, slug=slug)
    enrolled = False
    
    if request.user.is_authenticated:
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course)
            enrolled = enrollment.is_approved()
        except Enrollment.DoesNotExist:
            pass
    
    announcements = course.announcements.all()
    
    context = {
        'course': course,
        'announcements': announcements,
        'enrolled': enrolled,
    }
    return render(request, template_name, context)


def show_announcement(request, slug, pk):
    """
    Exibe detalhes de um anúncio específico.
    """
    template_name = 'courses/announcement_detail.html'
    course = get_object_or_404(Course, slug=slug)
    announcement = get_object_or_404(Announcement, pk=pk, course=course)
    enrolled = False
    form = CommentForm(request.POST or None)
    
    if request.user.is_authenticated:
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course)
            enrolled = enrollment.is_approved()
        except Enrollment.DoesNotExist:
            pass
        
        if request.method == 'POST' and form.is_valid() and enrolled:
            comment = form.save(commit=False)
            comment.announcement = announcement
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comentário adicionado com sucesso!')
            return redirect('cursos:show_announcement', slug=slug, pk=pk)
    
    comments = announcement.comments.all()
    
    context = {
        'course': course,
        'announcement': announcement,
        'comments': comments,
        'form': form,
        'enrolled': enrolled,
    }
    return render(request, template_name, context)


@login_required
def lessons(request, slug):
    """
    Lista as aulas de um curso.
    """
    template_name = 'courses/lessons.html'
    course = get_object_or_404(Course, slug=slug)
    enrolled = False
    progress = None
    
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
        enrolled = enrollment.is_approved()
        progress = ProgressManager.get_course_progress(request.user, course)
    except Enrollment.DoesNotExist:
        pass
    
    if not enrolled:
        messages.error(request, 'Você precisa estar matriculado neste curso para acessar as aulas.')
        return redirect('cursos:details', slug=slug)
    
    lessons = course.lessons.all()
    
    context = {
        'course': course,
        'lessons': lessons,
        'progress': progress,
    }
    return render(request, template_name, context)


@login_required
def lesson(request, slug, pk):
    """
    Exibe uma aula específica com seus materiais.
    """
    template_name = 'courses/lesson.html'
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, pk=pk, course=course)
    enrolled = False
    progress = None
    
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
        enrolled = enrollment.is_approved()
        progress = ProgressManager.get_course_progress(request.user, course)
    except Enrollment.DoesNotExist:
        pass
    
    if not enrolled:
        messages.error(request, 'Você precisa estar matriculado neste curso para acessar as aulas.')
        return redirect('cursos:details', slug=slug)
    
    materials = lesson.materials.all()
    lesson_progress = ProgressManager.get_lesson_progress(request.user, lesson)
    
    context = {
        'course': course,
        'lesson': lesson,
        'materials': materials,
        'lesson_progress': lesson_progress,
        'progress': progress,
    }
    return render(request, template_name, context)


@login_required
def material(request, slug, pk):
    """
    Exibe um material específico de uma aula.
    """
    template_name = 'courses/material.html'
    course = get_object_or_404(Course, slug=slug)
    material = get_object_or_404(Material, pk=pk, lesson__course=course)
    lesson = material.lesson
    enrolled = False
    progress = None
    
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
        enrolled = enrollment.is_approved()
        progress = ProgressManager.get_course_progress(request.user, course)
    except Enrollment.DoesNotExist:
        pass
    
    if not enrolled:
        messages.error(request, 'Você precisa estar matriculado neste curso para acessar os materiais.')
        return redirect('cursos:details', slug=slug)
    
    lesson_progress = ProgressManager.get_lesson_progress(request.user, lesson)
    
    context = {
        'course': course,
        'lesson': lesson,
        'material': material,
        'lesson_progress': lesson_progress,
        'progress': progress,
    }
    return render(request, template_name, context)


# VIEWS AJAX/API para Progresso


@login_required
@require_http_methods(["POST"])
def mark_lesson_complete(request, slug, lesson_id):
    """
    API endpoint para marcar uma aula como completa.
    Retorna JSON.
    """
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, pk=lesson_id, course=course)
    
    # Verificar se usuário está inscrito
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
        if not enrollment.is_approved():
            return JsonResponse({'error': 'Não autorizado'}, status=403)
    except Enrollment.DoesNotExist:
        return JsonResponse({'error': 'Não autorizado'}, status=403)
    
    # Marcar aula como completa
    lesson_progress = ProgressManager.mark_lesson_complete(request.user, lesson)
    
    # Atualizar progresso do curso
    course_progress = ProgressManager.get_course_progress(request.user, course)
    course_progress.calculate_progress()
    course_progress.save()
    
    # Verificar se curso foi completado e gerar certificado
    certificate = None
    if course_progress.progress_percentage >= 100:
        certificate = CertificateManager.check_and_generate_certificate(request.user, course)
    
    return JsonResponse({
        'success': True,
        'lesson_progress': {
            'completed': lesson_progress.completed,
            'completed_at': lesson_progress.completed_at.isoformat() if lesson_progress.completed_at else None,
        },
        'course_progress': {
            'completed_lessons': course_progress.completed_lessons,
            'total_lessons': course_progress.total_lessons,
            'progress_percentage': course_progress.progress_percentage,
            'completed': course_progress.completed_at is not None,
        },
        'certificate': {
            'generated': certificate is not None,
            'certificate_number': certificate.certificate_number if certificate else None,
        } if certificate or course_progress.progress_percentage >= 100 else None,
    })


@login_required
@require_http_methods(["POST"])
def mark_lesson_incomplete(request, slug, lesson_id):
    """
    API endpoint para marcar uma aula como não completa.
    Retorna JSON.
    """
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, pk=lesson_id, course=course)
    
    # Verificar se usuário está inscrito
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
        if not enrollment.is_approved():
            return JsonResponse({'error': 'Não autorizado'}, status=403)
    except Enrollment.DoesNotExist:
        return JsonResponse({'error': 'Não autorizado'}, status=403)
    
    # Marcar aula como não completa
    lesson_progress = ProgressManager.mark_lesson_incomplete(request.user, lesson)
    
    # Atualizar progresso do curso
    course_progress = ProgressManager.get_course_progress(request.user, course)
    course_progress.calculate_progress()
    course_progress.save()
    
    return JsonResponse({
        'success': True,
        'lesson_progress': {
            'completed': lesson_progress.completed if lesson_progress else False,
            'completed_at': lesson_progress.completed_at.isoformat() if lesson_progress and lesson_progress.completed_at else None,
        },
        'course_progress': {
            'completed_lessons': course_progress.completed_lessons,
            'total_lessons': course_progress.total_lessons,
            'progress_percentage': course_progress.progress_percentage,
            'completed': course_progress.completed_at is not None,
        },
    })


@login_required
def get_course_progress(request, slug):
    """
    API endpoint para obter o progresso atual do usuário em um curso.
    Retorna JSON.
    """
    course = get_object_or_404(Course, slug=slug)
    
    # Verificar se usuário está inscrito
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
        if not enrollment.is_approved():
            return JsonResponse({'error': 'Não autorizado'}, status=403)
    except Enrollment.DoesNotExist:
        return JsonResponse({'error': 'Não autorizado'}, status=403)
    
    progress = ProgressManager.get_course_progress(request.user, course)
    progress.calculate_progress()
    
    return JsonResponse({
        'success': True,
        'course_progress': {
            'completed_lessons': progress.completed_lessons,
            'total_lessons': progress.total_lessons,
            'progress_percentage': progress.progress_percentage,
            'completed': progress.completed_at is not None,
            'completed_at': progress.completed_at.isoformat() if progress.completed_at else None,
        },
    })


@login_required
def dashboard(request):
    """
    Dashboard do usuário com resumo de progresso em todos os cursos.
    """
    template_name = 'accounts/dashboard.html'
    
    user_progress = ProgressManager.get_user_courses_progress(request.user)
    
    # Adicionar certificados
    for progress in user_progress:
        progress.certificate = CertificateManager.get_certificate(request.user, progress.course)
    
    context = {
        'user_progress': user_progress,
    }
    return render(request, template_name, context)


@login_required
def download_certificate(request, slug):
    """
    Download do certificado em PDF.
    """
    course = get_object_or_404(Course, slug=slug)
    certificate = get_object_or_404(Certificate, user=request.user, course=course)
    
    if not certificate.certificate_file:
        raise Http404("Certificado não disponível para download.")
    
    return FileResponse(
        certificate.certificate_file.open('rb'),
        content_type='application/pdf',
        as_attachment=True,
        filename=f'certificado_{certificate.certificate_number}.pdf'
    )


@login_required
def my_certificates(request):
    """
    Lista os certificados do usuário.
    """
    template_name = 'accounts/my_certificates.html'
    
    certificates = Certificate.objects.filter(user=request.user).select_related('course')
    
    context = {
        'certificates': certificates,
    }
    return render(request, template_name, context)
