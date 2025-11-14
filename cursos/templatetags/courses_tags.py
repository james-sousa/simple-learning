from django import template
from cursos.models import Course

register = template.Library()


@register.simple_tag
def my_courses(user):
    """Retorna os cursos do usuário"""
    return user.enrollments.all().values_list('course', flat=True)
