from django.shortcuts import render,redirect

# Create your views here.
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .models import Feature
import os


# Create your views here.
def index(request):
   feature=Feature.objects.all()

   return render(request, 'index.html',{'features': feature})

def register(request):
 if request.method == 'POST':
   username = request.POST['username']
   email = request.POST['email']
   password = request.POST['password']
   password2 = request.POST['password2']
   
   if password == password2 :
      if User.objects.filter(email=email).exists():
         messages.info(request, 'Email already exists')
         return redirect('register')
      elif User.objects.filter(username=username).exists():
         messages.info(request,'Username already exists')
         return redirect('register')
      else:
         user= User.objects.create_user(username = username, email=email, password=password)
         user.save();
         return redirect('login')
   else:
      messages.info(request, 'Password doesnt match')
      return redirect('register')     
 else:  
   return render(request, 'register.html' )  

def login(request):
   if request.method == 'POST':
      username = request.POST['username']
      password = request.POST['password']

      user = auth.authenticate(username=username, password=password)

      if user is not None:
         auth.login(request, user)
         return redirect('/')
      else:
         messages.info(request, 'Credential invalid')   
         return redirect('login')
   
   else:
       return render(request, 'login.html')

    
    
def logout(request):
   auth.logout(request)
   return redirect('/') 

def post(request, pk): 
    return render(request,'post.html', {'pk' : pk})  
 
def upload(request):
   return redirect('upload_file')

def upload_file(request):
   def upload_file(request):
      if request.method == "POST":
        my_uploaded_file = request.FILES['my_uploaded_file'].read() # get the uploaded file
        f=open(my_uploaded_file)
        print(f.readlines())
        return render(request,"<h1> Successful</h1>")
                     
      else:
         return render(request, '<h1> unsuccessful</h1>')

def indexx(request):
   
   context={}

   if request.method == 'POST':
      uploaded_file = request.FILES['document']

      print(uploaded_file)
      
      if uploaded_file.name.endswith('.csv'):
         #save the file in media folder  
         savefile= FileSystemStorage() 

         name = savefile.save(uploaded_file.name, uploaded_file)# this is the name of file

         #know where to save the file
         d = os.getcwd() #current directory of the project
         file_directory = d+'\media\\'+name
         return redirect(index)
      
   return render(request, 'indexx.html')