from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CommentForm, Register, Login, PostForm
from .models import Like, Post
from django.contrib.auth import authenticate, login as auth_login , logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

def register(request):
    if request.method == 'POST':
        form = Register(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Create a new user
            User.objects.create_user(username=username, email=email, password=password)
            return HttpResponse("Registration successful")
        else:
            return HttpResponse("Registration failed. Please correct the errors below.")
    else:
        form = Register()
    return render(request, 'register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = Login(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Authenticate the user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)  # Use the aliased function
                return redirect('post_list')
            else:
                return HttpResponse("Invalid credentials")
        else:
            return HttpResponse("Login failed.")
    else:
        form = Login()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('login')


def post_list(request):
    posts=Post.objects.all().order_by('-created_at')
    return render(request,'post_list.html',{'posts':
       posts} )

@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST,request.FILES)
        if form.is_valid():
            post=form.save(commit=False)
            post.user=request.user
            post.save()
            return redirect('post_list')
       
    else:
         form = PostForm()
         return render(request,'post_form.html',{'form':form})
    

@login_required
def post_edit(request,post_id):
    post=get_object_or_404(Post,pk=post_id, user=request.user)
    if request.method == "POST":
        form = PostForm(request.POST,request.FILES,instance=post) 
        if form.is_valid():
            post=form.save(commit=False)
            post.user=request.user
            post.save()
            return redirect('post_list')

    else:
       form = PostForm(instance=post)
       return render(request,'post_form.html',{'form':form})
    
@login_required
def post_delete(request, post_id):
    post=get_object_or_404(Post, pk=post_id, user=request.user)
    if request.method =='POST':
        post.delete()
        return redirect('post_list')
    return render(request,'post_confirm_delete.html',{'post':post})


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    Like.objects.get_or_create(user=request.user, post=post)
    return redirect('post_list')

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('post_list')
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form, 'post': post})



import json
import random
import numpy as np
import nltk
import pickle
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
from django.shortcuts import render

# Initialize lemmatizer and load model and data
lemmatizer = WordNetLemmatizer()
intents = json.loads(open("intents.json").read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbotmodel.h5')

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            return random.choice(i['responses'])
    return "I don't understand!"

def chatbot_response(message):
    ints = predict_class(message)
    res = get_response(ints, intents)
    return res


def chatbot_view(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:
            bot_response = chatbot_response(user_message)
            return JsonResponse({
                'user_message': user_message,
                'bot_response': bot_response
            })
    return render(request, 'post_list.html')
