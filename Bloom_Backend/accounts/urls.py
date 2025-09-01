from django.urls import path
from .views import RegisterView, login

urlpatterns = [
    # Register endpoint
    path('register/', RegisterView.as_view(), name='register'),

    # Login endpoint
    path('login/', login, name='login'),
]
