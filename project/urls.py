from django.urls import path
from . import views 

urlpatterns= [
   path('',views.index,name='index'),
   path('register',views.register,name='register'),
   path('login',views.login,name='login'),
   path('logout',views.logout,name='logout'),
   path('upload',views.upload,name="upload"),
   path('upload_file',views.upload_file,name="upload_file"),
   path('post/<str:pk>', views.post, name='post'),
   path('indexx',views.indexx,name='indexx'),
]  