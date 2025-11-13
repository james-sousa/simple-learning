"""
Módulo de progresso e certificado para gerenciar o acompanhamento do usuário nos cursos
"""
from django.utils import timezone
from django.core.files.base import ContentFile
from datetime import datetime
from .models import LessonProgress, CourseProgress, Certificate, Lesson, Course


class ProgressManager:
    """
    Gerenciador de progresso do usuário em um curso.
    """
    
    @staticmethod
    def mark_lesson_complete(user, lesson):
        """
        Marca uma aula como concluída para um usuário.
        """
        progress, created = LessonProgress.objects.get_or_create(
            user=user,
            lesson=lesson
        )
        if not progress.completed:
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.save()
        
        # Atualizar progresso do curso
        ProgressManager.update_course_progress(user, lesson.course)
        
        return progress

    @staticmethod
    def mark_lesson_incomplete(user, lesson):
        """
        Marca uma aula como não concluída para um usuário.
        """
        try:
            progress = LessonProgress.objects.get(user=user, lesson=lesson)
            progress.completed = False
            progress.completed_at = None
            progress.save()
            
            # Atualizar progresso do curso
            ProgressManager.update_course_progress(user, lesson.course)
        except LessonProgress.DoesNotExist:
            pass
        
        return progress

    @staticmethod
    def get_lesson_progress(user, lesson):
        """
        Obtém o progresso de um usuário em uma aula específica.
        """
        try:
            return LessonProgress.objects.get(user=user, lesson=lesson)
        except LessonProgress.DoesNotExist:
            return None

    @staticmethod
    def get_course_progress(user, course):
        """
        Obtém o progresso de um usuário em um curso.
        """
        try:
            progress = CourseProgress.objects.get(user=user, course=course)
            progress.calculate_progress()
            progress.save()
            return progress
        except CourseProgress.DoesNotExist:
            return None

    @staticmethod
    def initialize_course_progress(user, enrollment):
        """
        Inicializa o progresso de um usuário em um curso após matrícula.
        """
        course = enrollment.course
        try:
            progress = CourseProgress.objects.get(user=user, course=course)
        except CourseProgress.DoesNotExist:
            progress = CourseProgress.objects.create(
                user=user,
                course=course,
                enrollment=enrollment
            )
        
        progress.calculate_progress()
        progress.save()
        return progress

    @staticmethod
    def update_course_progress(user, course):
        """
        Atualiza o progresso geral do usuário em um curso.
        """
        try:
            progress = CourseProgress.objects.get(user=user, course=course)
            progress.calculate_progress()
            progress.save()
            
            # Verificar se o curso foi concluído
            if progress.progress_percentage >= 100 and progress.completed_at is None:
                progress.completed_at = timezone.now()
                progress.save()
            
            return progress
        except CourseProgress.DoesNotExist:
            return None

    @staticmethod
    def get_all_lessons_completed(user, course):
        """
        Retorna todas as aulas concluídas de um usuário em um curso.
        """
        return LessonProgress.objects.filter(
            user=user,
            lesson__course=course,
            completed=True
        )

    @staticmethod
    def get_user_courses_progress(user):
        """
        Retorna o progresso do usuário em todos os cursos em que está inscrito.
        """
        progresses = CourseProgress.objects.filter(user=user)
        for progress in progresses:
            progress.calculate_progress()
        return progresses


class CertificateManager:
    """
    Gerenciador de geração de certificados.
    """
    
    @staticmethod
    def create_certificate(user, course, course_progress):
        """
        Cria um certificado para um usuário após completar um curso.
        """
        if course_progress.progress_percentage < 100:
            raise ValueError("Usuário deve completar 100% do curso para receber certificado")
        
        certificate_number = Certificate(
            user=user,
            course=course,
            course_progress=course_progress
        ).generate_certificate_number()
        
        certificate, created = Certificate.objects.get_or_create(
            user=user,
            course=course,
            course_progress=course_progress,
            defaults={'certificate_number': certificate_number}
        )
        
        return certificate

    @staticmethod
    def generate_certificate_pdf(certificate):
        """
        Gera um arquivo PDF do certificado.
        """
        try:
            from reportlab.lib.pagesizes import landscape, A4
            from reportlab.lib.colors import HexColor
            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import ImageReader
            from io import BytesIO
            import os
            
            # Criar buffer para o PDF
            buffer = BytesIO()
            
            # Configurar página em paisagem
            width, height = landscape(A4)
            
            # Criar canvas
            c = canvas.Canvas(buffer, pagesize=landscape(A4))
            
            # Adicionar fundo (cor ou imagem)
            c.setFillColor(HexColor("#f5f5f5"))
            c.rect(0, 0, width, height, fill=1, stroke=0)
            
            # Adicionar borda decorativa
            c.setLineWidth(3)
            c.setStrokeColor(HexColor("#2c3e50"))
            c.rect(20, 20, width-40, height-40)
            
            # Título
            c.setFont("Helvetica-Bold", 48)
            c.setFillColor(HexColor("#2c3e50"))
            c.drawCentredString(width/2, height - 80, "CERTIFICADO DE CONCLUSÃO")
            
            # Subtítulo
            c.setFont("Helvetica-Bold", 24)
            c.setFillColor(HexColor("#34495e"))
            c.drawCentredString(width/2, height - 130, "de")
            
            # Nome do curso
            c.setFont("Helvetica-Bold", 28)
            c.setFillColor(HexColor("#2980b9"))
            course_name = certificate.course.name
            # Quebrar texto se necessário
            if len(course_name) > 50:
                lines = CertificateManager._wrap_text(course_name, 50)
                y_pos = height - 170
                for line in lines:
                    c.drawCentredString(width/2, y_pos, line)
                    y_pos -= 30
            else:
                c.drawCentredString(width/2, height - 170, course_name)
            
            # Texto de premiação
            c.setFont("Helvetica", 16)
            c.setFillColor(HexColor("#2c3e50"))
            c.drawCentredString(width/2, height - 250, "Certificamos que")
            
            # Nome do usuário
            c.setFont("Helvetica-Bold", 22)
            c.setFillColor(HexColor("#2980b9"))
            c.drawCentredString(width/2, height - 290, certificate.user.get_full_name() or certificate.user.username)
            
            # Texto final
            c.setFont("Helvetica", 14)
            c.setFillColor(HexColor("#2c3e50"))
            c.drawCentredString(width/2, height - 330, "Completou com êxito todas as atividades propostas no curso acima mencionado,")
            c.drawCentredString(width/2, height - 355, "demonstrando aptidão e compromisso com a educação continuada.")
            
            # Data de emissão
            c.setFont("Helvetica", 12)
            c.drawString(50, 80, f"Emitido em: {certificate.issued_at.strftime('%d de %B de %Y')}")
            
            # Número do certificado
            c.drawString(50, 60, f"Número: {certificate.certificate_number}")
            
            # Assinatura
            c.setFont("Helvetica-Oblique", 10)
            c.drawCentredString(width - 100, 100, "_________________")
            c.drawCentredString(width - 100, 80, "Administração")
            
            # Finalizar PDF
            c.showPage()
            c.save()
            
            return buffer.getvalue()
        
        except ImportError:
            raise ImportError("reportlab é necessário para gerar PDF. Instale com: pip install reportlab")

    @staticmethod
    def _wrap_text(text, max_length):
        """
        Quebra texto em múltiplas linhas.
        """
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) <= max_length:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines

    @staticmethod
    def save_certificate_file(certificate):
        """
        Gera e salva o arquivo PDF do certificado.
        """
        try:
            pdf_content = CertificateManager.generate_certificate_pdf(certificate)
            
            filename = f"certificado_{certificate.user.id}_{certificate.course.id}_{certificate.certificate_number}.pdf"
            certificate.certificate_file.save(
                filename,
                ContentFile(pdf_content),
                save=True
            )
            
            return certificate
        
        except ImportError as e:
            print(f"Aviso: {e}. O certificado não será salvo em PDF, mas o objeto Certificate foi criado.")
            return certificate

    @staticmethod
    def get_certificate(user, course):
        """
        Obtém o certificado de um usuário para um curso.
        """
        try:
            return Certificate.objects.get(user=user, course=course)
        except Certificate.DoesNotExist:
            return None

    @staticmethod
    def check_and_generate_certificate(user, course):
        """
        Verifica se o usuário completou o curso e gera certificado se necessário.
        """
        try:
            course_progress = CourseProgress.objects.get(user=user, course=course)
            course_progress.calculate_progress()
            
            if course_progress.progress_percentage >= 100:
                # Verificar se certificado já existe
                existing_certificate = CertificateManager.get_certificate(user, course)
                if existing_certificate:
                    return existing_certificate
                
                # Criar novo certificado
                certificate = CertificateManager.create_certificate(user, course, course_progress)
                certificate = CertificateManager.save_certificate_file(certificate)
                return certificate
        
        except CourseProgress.DoesNotExist:
            pass
        
        return None
