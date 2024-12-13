from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from . import views_voting

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('logout/', views.logout_view, name='logout'),
    #path('create_post/', views.create_post, name='create_post'),
    #path('search/', views.search, name='search'),
    path('posts/', views.post_list, name='post_list'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:pk>/status/', views.update_post_status, name='update_post_status'),
    path('wikidata-search/', views.wikidata_search, name='wikidata_search'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/edit-tag/', views.edit_comment_tag, name='edit_comment_tag'),
    path('post/<int:post_id>/vote/', views_voting.vote, name='post_vote'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)