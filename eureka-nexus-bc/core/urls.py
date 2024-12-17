from django.urls import path
from. import views

urlpatterns = [
    # base views
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('delete-account/', views.delete_account, name='delete_account'),

    # profile views (user profile)
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.public_profile_view, name='public_profile'),

    # post views (posts)
    path('posts/', views.post_list, name='post_list'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:pk>/status/', views.update_post_status, name='update_post_status'),
    path('wikidata-search/', views.wikidata_search, name='wikidata_search'),

    # comment views (comments)
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/edit-tag/', views.edit_comment_tag, name='edit_comment_tag'),

    # voting views (voting)
    path('post/<int:post_id>/vote/', views.vote_post, name='post_vote'),
    path('comment/<int:comment_id>/vote/', views.vote_comment, name='comment_vote'),

    # search views (search)
    path('search/', views.search_posts, name='search_posts'),
    path('advanced-search/', views.advanced_search, name='advanced_search'),

    # following views (following)
    path('post/<int:post_id>/follow/', views.toggle_follow_post, name='toggle_follow_post'),
    path('toggle-follow/<str:username>/', views.toggle_follow_user, name='toggle_follow_user'),
]