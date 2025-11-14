from django.urls import path
from cursos import views

app_name = 'cursos'

urlpatterns = [
    path('', views.index, name='index'),
    path('<slug:slug>/', views.details, name='details'),
    path('<slug:slug>/inscricao/', views.enrollment, name='enrollment'),
    path('<slug:slug>/cancelar-inscricao/', views.undo_enrollment, name='undo_enrollment'),
    path('<slug:slug>/anuncios/', views.announcements, name='announcements'),
    path('<slug:slug>/anuncios/<int:pk>/', views.show_announcement, name='show_announcement'),
    path('<slug:slug>/aulas/', views.lessons, name='lessons'),
    path('<slug:slug>/aulas/<int:pk>/', views.lesson, name='lesson'),
    path('<slug:slug>/materiais/<int:pk>/', views.material, name='material'),
    
    # Rotas de Progresso e Certificado
    path('<slug:slug>/aulas/<int:lesson_id>/completar/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('<slug:slug>/aulas/<int:lesson_id>/descompletar/', views.mark_lesson_incomplete, name='mark_lesson_incomplete'),
    path('<slug:slug>/progresso/', views.get_course_progress, name='course_progress'),
    path('<slug:slug>/certificado/download/', views.download_certificate, name='download_certificate'),
    path('meus-certificados/', views.my_certificates, name='my_certificates'),
]
