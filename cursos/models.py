from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from core.mail import send_mail_template

class CourseManager(models.Manager):

    def search(self, query):
        return self.get_queryset().filter(
            models.Q(name__icontains=query) | \
            models.Q(description__icontains=query)
        )

class Course(models.Model):

    name = models.CharField('Nome', max_length=100)
    slug = models.SlugField('Atalho')
    description = models.TextField('Descrição Simples', blank=True)
    about = models.TextField('Sobre o Curso', blank=True)
    start_date = models.DateField(
        'Data de Início', null=True, blank=True
    )
    image = models.ImageField(
        upload_to='courses/images', verbose_name='Imagem',
        null=True, blank=True
    )

    created_at = models.DateTimeField(
        'Criado em', auto_now_add=True
    )
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    objects = CourseManager()

    def __str__(self):
        return self.name

    
    def get_absolute_url(self):
        return reverse('cursos:details',kwargs={'slug':self.slug})

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['name']


class Lesson(models.Model):
    name = models.CharField('Nome', max_length=100)
    description = models.TextField('Descrição', blank=True)
    number = models.IntegerField('Número (ordem)', blank=True, default=0)
    release_date = models.DateField('Data de Liberação', blank=True, null=True)
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Curso', related_name='lessons')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now_add=True)

    def __str__(self):
        return self.name
    
    def is_available(self):
        if self.release_date:
            today = timezone.now().date()
            return self.release_date > today
        return False

    class Meta:
        verbose_name = 'Aula'
        verbose_name_plural = 'Aulas'
        ordering = ['number']
    
class Material(models.Model):
    name = models.CharField('Nome', max_length=100)
    embedded = models.TextField('Vídeo embedded', blank=True)
    file = models.FileField(upload_to='lessons/materials', blank=True, null=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='Aula', related_name='materials')

    def is_embedded(self):
        return bool(self.embedded)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiais'


class Enrollment(models.Model):
    
    STATUS_CHOICES = (
        (0, 'Pendente'),
        (1, 'Aprovado'),
        (2, 'Cancelado'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Usuário',
        related_name='enrollments',
        on_delete=models.CASCADE

    )
    course = models.ForeignKey(
        Course, verbose_name='Curso', related_name='enrollments',
        on_delete=models.CASCADE
    )
    status = models.IntegerField(
        'Situação', choices=STATUS_CHOICES, default=1, blank=True
    )

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    update = models.DateTimeField('Atualizado em', auto_now=True)

    def active(self):
        self.status = 1
        self.save()
    
    def is_approved(self):
        return self.status == 1
    
    
    class Meta:
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'
        unique_together = (('user', 'course'),)

class Announcement(models.Model):

    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Curso', related_name='announcements')
    title = models.CharField('Titulo', max_length=100)
    content = models.TextField('Conteúdo')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Anúncio'
        verbose_name_plural = 'Anúncios'
        ordering = ['-created_at']


class Comment(models.Model):

    announcement = models.ForeignKey(
        Announcement, verbose_name='Anúncio', on_delete=models.CASCADE, related_name='comments'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='usuário')
    comment = models.TextField('Comentário')

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
        ordering = ['created_at']

class LessonProgress(models.Model):
    """
    Modelo para rastrear o progresso de um usuário em cada aula.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Usuário',
        related_name='lesson_progress',
        on_delete=models.CASCADE
    )
    lesson = models.ForeignKey(
        Lesson, verbose_name='Aula', related_name='progress',
        on_delete=models.CASCADE
    )
    completed = models.BooleanField('Concluída', default=False)
    completed_at = models.DateTimeField('Concluída em', null=True, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.lesson.name}'

    class Meta:
        verbose_name = 'Progresso da Aula'
        verbose_name_plural = 'Progressos das Aulas'
        unique_together = (('user', 'lesson'),)


class CourseProgress(models.Model):
    """
    Modelo para rastrear o progresso geral de um usuário em um curso.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Usuário',
        related_name='course_progress',
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course, verbose_name='Curso', related_name='progress',
        on_delete=models.CASCADE
    )
    enrollment = models.OneToOneField(
        Enrollment, verbose_name='Inscrição',
        on_delete=models.CASCADE, related_name='progress'
    )
    completed_lessons = models.IntegerField('Aulas Concluídas', default=0)
    total_lessons = models.IntegerField('Total de Aulas', default=0)
    progress_percentage = models.FloatField('Percentual de Progresso', default=0.0)
    completed_at = models.DateTimeField('Curso Concluído em', null=True, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.course.name} ({self.progress_percentage}%)'

    def calculate_progress(self):
        """Calcula o percentual de progresso do usuário no curso."""
        lessons = self.course.lessons.all().count()
        if lessons == 0:
            self.progress_percentage = 0.0
        else:
            completed = LessonProgress.objects.filter(
                user=self.user,
                lesson__course=self.course,
                completed=True
            ).count()
            self.progress_percentage = (completed / lessons) * 100
            self.completed_lessons = completed
            self.total_lessons = lessons
        return self.progress_percentage

    class Meta:
        verbose_name = 'Progresso do Curso'
        verbose_name_plural = 'Progressos dos Cursos'
        unique_together = (('user', 'course'),)


class Certificate(models.Model):
    """
    Modelo para armazenar informações sobre o certificado do usuário.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Usuário',
        related_name='certificates',
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course, verbose_name='Curso', related_name='certificates',
        on_delete=models.CASCADE
    )
    course_progress = models.OneToOneField(
        CourseProgress, verbose_name='Progresso do Curso',
        on_delete=models.CASCADE, related_name='certificate'
    )
    certificate_number = models.CharField('Número do Certificado', max_length=50, unique=True)
    issued_at = models.DateTimeField('Emitido em', auto_now_add=True)
    certificate_file = models.FileField(
        upload_to='certificates', verbose_name='Arquivo do Certificado',
        null=True, blank=True
    )

    def __str__(self):
        return f'Certificado {self.certificate_number} - {self.user.username}'

    def generate_certificate_number(self):
        """Gera um número único para o certificado."""
        import hashlib
        from django.utils import timezone
        data = f'{self.user.id}{self.course.id}{timezone.now().isoformat()}'
        return hashlib.md5(data.encode()).hexdigest()[:16].upper()

    class Meta:
        verbose_name = 'Certificado'
        verbose_name_plural = 'Certificados'
        unique_together = (('user', 'course'),)


def post_save_announcement(instance, created, **kwargs):
    if created:
        subject = instance.title
        context = {
            'announcement': instance
        }
        template_name = 'courses/announcement_mail.html'
        enrollments = Enrollment.objects.filter(
            course=instance.course, status=1
        )
        for enrollment in enrollments:
            recipient_list = [enrollment.user.email]
            send_mail_template(subject, template_name, context, recipient_list)

models.signals.post_save.connect(
    post_save_announcement, sender=Announcement,
    dispatch_uid='post_save_announcement'
)