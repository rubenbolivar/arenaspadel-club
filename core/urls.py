from django.urls import path
from . import views

urlpatterns = [
    path('courts/', views.get_courts),
    path('courts/<int:court_id>/availability/', views.check_court_availability),
    path('reservations/', views.create_reservation),
    path('payments/', views.process_payment),
]