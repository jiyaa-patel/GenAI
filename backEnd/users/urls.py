from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView, ProtectedView
from .views import ProtectedView , GoogleLoginView , ManualLoginView , list_users

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('signup/', RegisterView.as_view(), name='signup'), 
    path('login/', ManualLoginView.as_view(), name="login"),  
    path("google-login/", GoogleLoginView.as_view(), name="google-login"),
    path('list-users/', list_users, name='list_users'),  # New endpoint to list users
]