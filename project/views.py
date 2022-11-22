from django.shortcuts import render,redirect

# Create your views here.
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .models import Feature
from .models import Filename
import os
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
import numpy as np
from sklearn import preprocessing
import tensorflow as tf
import xlsxwriter


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
         document = request.FILES.get('document') # get the uploaded file
         # is_private = request.POST.get('is_private', False);
         

         # print(f.readlines())
         indexx(request)
         return redirect('index')
                     
      else:
         return redirect('index')

def indexx(request):
   
   context={}

   if request.method == 'POST':
      uploaded_file = request.FILES['document']

      print(uploaded_file.name)
      
    
      print(request.user.email)
      
      if uploaded_file.name.endswith('.csv'):
         #save the file in media folder  
         savefile= FileSystemStorage() 

         name = savefile.save(uploaded_file.name, uploaded_file)# this is the name of file

         #know where to save the file
         d = os.getcwd() #current directory of the project
         file_directory = d+'\media\\'+name
         ML(request.user.email,uploaded_file.name)
         return redirect(index)
      
   return render(request, 'indexx.html')

def ML(email,file):
   df=pd.read_csv(f"C:\\Users\\DELL\\Desktop\\software project\\SemiFinal\\Sales_Prediction\\media\\{file}")

   df.columns=["Date","Holiday","Avg. % ad spend of gross revenue","Avg. % discount","Sales"]

   train_length=len(df["Sales"])-df["Sales"].isnull().sum()

   test_lenth=df["Sales"].isnull().sum()

   le=preprocessing.LabelEncoder()
   encoded=le.fit_transform(df["Holiday"])

   from sklearn.preprocessing import MinMaxScaler
   scaler=MinMaxScaler()

   scaled_ad_spend=scaler.fit_transform(df["Avg. % ad spend of gross revenue"][:,np.newaxis])

   scaled_discount=scaler.fit_transform(df["Avg. % discount"][:,np.newaxis])
   scaled_sales= scaler.fit_transform(df["Sales"][:,np.newaxis])

   scaled_discount2=np.array(scaled_discount)
   scaled_sales2=np.array(scaled_sales)
   encoded=np.array(encoded)

   encoded=encoded.reshape((len(df["Sales"]),1))

   final3=np.array((encoded[:train_length],scaled_ad_spend[:train_length],scaled_discount[:train_length]))

   test=np.array((encoded[train_length:],scaled_ad_spend[train_length:],scaled_discount[train_length:]))
   # print(test.shape)

   test=test.reshape((test_lenth,3))

   final3=final3.reshape((train_length,3))

   from keras.preprocessing.sequence import TimeseriesGenerator
   n_input=3
   n_features=3
   generator=TimeseriesGenerator(final3,scaled_sales[:train_length],length=n_input,batch_size=1)

   model = Sequential()
   model.add(LSTM(100, activation='relu', input_shape=(n_input,n_features)))
   model.add(Dense(1))
   model.summary()

   model.compile(loss=tf.keras.losses.mse,optimizer=tf.keras.optimizers.Adam(lr=0.001))
   model.fit(generator,epochs=150,batch_size=30)

   first_eval_batch=final3[-n_input:,:,np.newaxis]
   current_batch = first_eval_batch.reshape((1, n_input, n_features))
   # print(first_eval_batch)
   # print(current_batch)

   final3=final3.astype(np.uint8)

   test=test.astype(np.uint8)

   predictions=[]
   for i in range(0,test_lenth):
      if i==0:
         predictions.append(model.predict(current_batch)[0])
         # print("hi")
      elif i==1:
         # print("pass")
         # first_eval_batch=final3[-n_input+1:,:,np.newaxis]
         first_eval_batch=final3[-n_input+1:,:,np.newaxis]
         first_eval_batch=list(first_eval_batch)
         # print(first_eval_batch)
         first_eval_batch.append(test[0,:,np.newaxis])
         # print(first_eval_batch)
         first_eval_batch=np.array(first_eval_batch)
         current_batch = first_eval_batch.reshape((1, n_input, n_features))
         # print(current_batch)
         predictions.append(model.predict(current_batch)[0])
      elif i==2:
         first_eval_batch=final3[-n_input+2:,:,np.newaxis]
         first_eval_batch=list(first_eval_batch)
         first_eval_batch.append(test[0,:,np.newaxis])
         first_eval_batch.append(test[1,:,np.newaxis])
         # print(first_eval_batch)
         first_eval_batch=np.array(first_eval_batch)

         current_batch = first_eval_batch.reshape((1, n_input, n_features))
         # print(current_batch)
         predictions.append(model.predict(current_batch)[0])
      else:
         first_eval_batch=test[i-n_input:i,:,np.newaxis]
         current_batch = first_eval_batch.reshape((1, n_input, n_features))
         # print(current_batch)
         predictions.append(model.predict(current_batch)[0])

   scaled_predictions = scaler.inverse_transform(predictions)
   print(scaled_predictions)
   true_predictions=[]
   
   for y in range(0,len(scaled_predictions)):
      
      for i in scaled_predictions[y]:
         # print(i)
         if i<=0:
            i=-i
            true_predictions.append(i)
            # print(i)
         else:
            true_predictions.append(i)
   # print(true_predictions)
   Workbookname=np.random.randint(0,1000)
   workbook = xlsxwriter.Workbook(f'{Workbookname}.xlsx')
   worksheet = workbook.add_worksheet()
   worksheet.write('A1', 'Date')
   worksheet.write('B1', 'Sales')

   row = 1
   column = 0
   for i in df["Date"][train_length:]:
   
      worksheet.write(row, column, i)
      row += 1

   row = 1
   column +=1
   for i in true_predictions :

      worksheet.write(row, column, i)
      row += 1
      
   workbook.close()

   print("Done!")
   import smtplib
   from email.mime.multipart import MIMEMultipart
   from email.mime.text import MIMEText
   from email.mime.base import MIMEBase
   from email import encoders
   fromaddr = "predict.io.2k22@gmail.com"
   toaddr = f"{email}"   

   msg = MIMEMultipart() 
   msg['From'] = fromaddr
   
   # storing the receivers email address 
   msg['To'] = toaddr
   
   # storing the subject 
   msg['Subject'] = "Prediction results"
   
   # string to store the body of the mail
   body = "Thank you for using our website, here are the results."
   
   # attach the body with the msg instance
   msg.attach(MIMEText(body, 'plain'))
   
   # open the file to be sent 
   filename = f"{Workbookname}.xlsx"
   attachment = open(f'{Workbookname}.xlsx', "rb")

   # instance of MIMEBase and named as p
   p = MIMEBase('application', 'octet-stream')
   
   # To change the payload into encoded form
   p.set_payload((attachment).read())
   
   # encode into base64
   encoders.encode_base64(p)
      
   p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
   
   # attach the instance 'p' to instance 'msg'
   msg.attach(p)
   
   # creates SMTP session
   s = smtplib.SMTP('smtp.gmail.com', 587)
   
   # start TLS for security
   s.starttls()
   
   # Authentication
   s.login(fromaddr, "merwuzzcsxlpzjve")
   
   # Converts the Multipart msg into a string
   text = msg.as_string()
   
   # sending the mail
   s.sendmail(fromaddr, toaddr, text)
   
   # terminating the session
   s.quit()
         
