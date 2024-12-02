from django.urls import path
from .views import UserProfileView, EditProfileView, SignupView, LoginView, LogoutView

urlpatterns = [
    path('api/signup/', SignupView.as_view(), name='signup'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/profile/', UserProfileView.as_view(), name='profile'),
    path('api/profile/edit/', EditProfileView.as_view(), name='edit-profile'),
]
