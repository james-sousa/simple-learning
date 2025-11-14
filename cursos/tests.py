"""
Testes para o sistema de Progresso e Certificados

Execute com: python manage.py test cursos.tests.ProgressManagerTests
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

from cursos.models import (
    Course, Lesson, Material, Enrollment,
    LessonProgress, CourseProgress, Certificate
)
from cursos.progress import ProgressManager, CertificateManager


class ProgressManagerTests(TestCase):
    """Testes para o ProgressManager"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        # Criar usuário
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Criar curso
        self.course = Course.objects.create(
            name='Python Iniciante',
            slug='python-iniciante',
            description='Curso de Python para iniciantes'
        )
        
        # Criar aulas
        self.lesson1 = Lesson.objects.create(
            name='Aula 1: Introdução',
            course=self.course,
            number=1
        )
        self.lesson2 = Lesson.objects.create(
            name='Aula 2: Variáveis',
            course=self.course,
            number=2
        )
        self.lesson3 = Lesson.objects.create(
            name='Aula 3: Funções',
            course=self.course,
            number=3
        )
        
        # Criar matrícula
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status=1
        )
    
    def test_initialize_course_progress(self):
        """Testa inicialização do progresso do curso"""
        progress = ProgressManager.initialize_course_progress(
            self.user, self.enrollment
        )
        
        self.assertIsNotNone(progress)
        self.assertEqual(progress.user, self.user)
        self.assertEqual(progress.course, self.course)
        self.assertEqual(progress.progress_percentage, 0.0)
        self.assertEqual(progress.completed_lessons, 0)
        self.assertEqual(progress.total_lessons, 3)
    
    def test_mark_lesson_complete(self):
        """Testa marcação de aula como completa"""
        ProgressManager.initialize_course_progress(
            self.user, self.enrollment
        )
        
        # Marcar primeira aula
        progress = ProgressManager.mark_lesson_complete(
            self.user, self.lesson1
        )
        
        self.assertTrue(progress.completed)
        self.assertIsNotNone(progress.completed_at)
        
        # Verificar progresso do curso
        course_progress = ProgressManager.get_course_progress(
            self.user, self.course
        )
        self.assertAlmostEqual(course_progress.progress_percentage, 33.33, places=1)
    
    def test_mark_lesson_incomplete(self):
        """Testa desmarcação de aula"""
        ProgressManager.initialize_course_progress(
            self.user, self.enrollment
        )
        
        # Marcar completa
        ProgressManager.mark_lesson_complete(self.user, self.lesson1)
        
        # Desmarcar
        progress = ProgressManager.mark_lesson_incomplete(
            self.user, self.lesson1
        )
        
        self.assertFalse(progress.completed)
        self.assertIsNone(progress.completed_at)
    
    def test_complete_all_lessons(self):
        """Testa conclusão de todas as aulas"""
        ProgressManager.initialize_course_progress(
            self.user, self.enrollment
        )
        
        # Completar todas as aulas
        for lesson in self.course.lessons.all():
            ProgressManager.mark_lesson_complete(self.user, lesson)
        
        # Verificar progresso
        course_progress = ProgressManager.get_course_progress(
            self.user, self.course
        )
        course_progress.calculate_progress()
        
        self.assertEqual(course_progress.progress_percentage, 100.0)
        self.assertEqual(course_progress.completed_lessons, 3)
        self.assertEqual(course_progress.total_lessons, 3)
    
    def test_get_lesson_progress(self):
        """Testa obtenção de progresso de uma aula"""
        ProgressManager.initialize_course_progress(
            self.user, self.enrollment
        )
        ProgressManager.mark_lesson_complete(self.user, self.lesson1)
        
        progress = ProgressManager.get_lesson_progress(
            self.user, self.lesson1
        )
        
        self.assertIsNotNone(progress)
        self.assertTrue(progress.completed)
    
    def test_get_course_progress(self):
        """Testa obtenção de progresso do curso"""
        ProgressManager.initialize_course_progress(
            self.user, self.enrollment
        )
        
        progress = ProgressManager.get_course_progress(
            self.user, self.course
        )
        
        self.assertIsNotNone(progress)
        self.assertEqual(progress.user, self.user)
        self.assertEqual(progress.course, self.course)
    
    def test_get_all_lessons_completed(self):
        """Testa obtenção de todas as aulas completadas"""
        ProgressManager.initialize_course_progress(
            self.user, self.enrollment
        )
        
        ProgressManager.mark_lesson_complete(self.user, self.lesson1)
        ProgressManager.mark_lesson_complete(self.user, self.lesson2)
        
        completed = ProgressManager.get_all_lessons_completed(
            self.user, self.course
        )
        
        self.assertEqual(completed.count(), 2)


class CertificateManagerTests(TestCase):
    """Testes para o CertificateManager"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.course = Course.objects.create(
            name='Python Iniciante',
            slug='python-iniciante',
            description='Curso de Python'
        )
        
        self.lesson = Lesson.objects.create(
            name='Aula 1',
            course=self.course,
            number=1
        )
        
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status=1
        )
    
    def test_create_certificate(self):
        """Testa criação de certificado"""
        # Inicializar progresso
        course_progress = ProgressManager.initialize_course_progress(
            self.user, self.enrollment
        )
        
        # Completar curso
        ProgressManager.mark_lesson_complete(self.user, self.lesson)
        course_progress.calculate_progress()
        course_progress.save()
        
        # Criar certificado
        certificate = CertificateManager.create_certificate(
            self.user, self.course, course_progress
        )
        
        self.assertIsNotNone(certificate)
        self.assertEqual(certificate.user, self.user)
        self.assertEqual(certificate.course, self.course)
        self.assertIsNotNone(certificate.certificate_number)
    
    def test_generate_certificate_number(self):
        """Testa geração de número de certificado"""
        certificate = Certificate(
            user=self.user,
            course=self.course,
            course_progress=None
        )
        
        number = certificate.generate_certificate_number()
        
        self.assertIsNotNone(number)
        self.assertEqual(len(number), 16)
        self.assertTrue(number.isupper())
    
    def test_get_certificate(self):
        """Testa obtenção de certificado existente"""
        # Criar certificado
        course_progress = ProgressManager.initialize_course_progress(
            self.user, self.enrollment
        )
        ProgressManager.mark_lesson_complete(self.user, self.lesson)
        course_progress.calculate_progress()
        course_progress.save()
        
        CertificateManager.create_certificate(
            self.user, self.course, course_progress
        )
        
        # Obter certificado
        certificate = CertificateManager.get_certificate(
            self.user, self.course
        )
        
        self.assertIsNotNone(certificate)
        self.assertEqual(certificate.user, self.user)
    
    def test_certificate_requires_100_percent(self):
        """Testa que certificado requer 100% de progresso"""
        course_progress = ProgressManager.initialize_course_progress(
            self.user, self.enrollment
        )
        
        # Tentar criar certificado sem completar
        with self.assertRaises(ValueError):
            CertificateManager.create_certificate(
                self.user, self.course, course_progress
            )


class LessonProgressModelTests(TestCase):
    """Testes para o modelo LessonProgress"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.course = Course.objects.create(
            name='Teste',
            slug='teste'
        )
        
        self.lesson = Lesson.objects.create(
            name='Aula',
            course=self.course
        )
    
    def test_create_lesson_progress(self):
        """Testa criação de progresso de aula"""
        progress = LessonProgress.objects.create(
            user=self.user,
            lesson=self.lesson
        )
        
        self.assertFalse(progress.completed)
        self.assertIsNone(progress.completed_at)
    
    def test_lesson_progress_unique_constraint(self):
        """Testa restrição única de progresso"""
        LessonProgress.objects.create(
            user=self.user,
            lesson=self.lesson
        )
        
        # Tentar criar duplicado
        with self.assertRaises(Exception):
            LessonProgress.objects.create(
                user=self.user,
                lesson=self.lesson
            )


class CourseProgressModelTests(TestCase):
    """Testes para o modelo CourseProgress"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.course = Course.objects.create(
            name='Teste',
            slug='teste'
        )
        
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            course=self.course,
            status=1
        )
    
    def test_calculate_progress(self):
        """Testa cálculo de progresso"""
        # Criar aulas
        lesson1 = Lesson.objects.create(
            name='Aula 1',
            course=self.course
        )
        lesson2 = Lesson.objects.create(
            name='Aula 2',
            course=self.course
        )
        
        # Criar progresso
        progress = CourseProgress.objects.create(
            user=self.user,
            course=self.course,
            enrollment=self.enrollment
        )
        
        # Sem aulas concluídas
        progress.calculate_progress()
        self.assertEqual(progress.progress_percentage, 0.0)
        
        # Com uma aula concluída
        LessonProgress.objects.create(
            user=self.user,
            lesson=lesson1,
            completed=True
        )
        progress.calculate_progress()
        self.assertAlmostEqual(progress.progress_percentage, 50.0, places=1)
        
        # Duas aulas concluídas
        LessonProgress.objects.create(
            user=self.user,
            lesson=lesson2,
            completed=True
        )
        progress.calculate_progress()
        self.assertEqual(progress.progress_percentage, 100.0)
