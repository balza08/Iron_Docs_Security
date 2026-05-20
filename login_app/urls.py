from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('', views.home, name='home'),
    path('nuova/', views.nuova_doc, name='nuova_doc'),
    path('doc/<int:doc_id>/', views.visualizza_doc, name='visualizza_doc'),
    path('doc/<int:doc_id>/elimina/', views.elimina_doc, name='elimina_doc'),
    path('doc/<int:doc_id>/txt/', views.scarica_txt, name='scarica_txt'),
    path('doc/<int:doc_id>/pdf/', views.scarica_pdf, name='scarica_pdf'),
]
