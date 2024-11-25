from django.urls import path
from .views import SignupView, LoginView, LogoutView, EditProfileView, ActivateAccountView, UserProfileView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('edit-profile/', EditProfileView.as_view(), name='edit-profile'),
    path('activate/<str:token>/', ActivateAccountView.as_view(), name='activate-account'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]
