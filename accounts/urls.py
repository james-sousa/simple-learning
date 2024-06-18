from django.urls import path
from django.contrib.auth import views as auth_views
from accounts import views as accounts_views

app_name = 'accounts'


urlpatterns = [
    path('', accounts_views.dashboard, name='dashboard'),
    path('entrar/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('sair/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('cadastre-se/', accounts_views.register, name='register'),
    path('editar/', accounts_views.edit, name='edit'),
    path('editar-senha/', accounts_views.edit_password, name='edit_password'),
    
]