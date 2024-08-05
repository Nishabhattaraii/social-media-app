from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CommentForm, Register, Login, PostForm
from .models import Like, Post
from django.contrib.auth import authenticate, login as auth_login , logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

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
            return HttpResponse("Login failed. Please correct the errors below.")
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