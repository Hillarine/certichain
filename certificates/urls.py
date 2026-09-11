from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_certificate, name='create_certificate'),
    path('certificate/<uuid:pk>/', views.certificate_detail, name='certificate_detail'),
    path('verify/', views.verify_certificate, name='verify_certificate'),
    path('verify/result/<str:certificate_id>/', views.verification_result, name='verification_result'),
    path('certificate/<uuid:pk>/revoke/', views.revoke_certificate, name='revoke_certificate'),
    path('api/blockchain-status/', views.api_blockchain_status, name='blockchain_status'),
]