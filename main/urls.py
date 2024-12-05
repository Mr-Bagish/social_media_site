from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("like-post/<uuid:post_id>", views.like_post, name="like-post"),
    path("comment/<uuid:post_id>",views.coment,name='comment'),
    path("commentlist/<uuid:post_id>",views.commentlist,name='commentlist'),
    path('follow',views.follower,name='follow'),
    path('search',views.search,name='search'),
    path("profile/<str:pk>",views.profile, name='profile'),
    path("signup/", views.signup, name="signup"),
    path("signin/", views.signin, name="signin"),
    path('upload',views.upload,name='upload'),
    path("signout/", views.signout, name="signout"),
    path("setting/", views.setting, name="setting")
]