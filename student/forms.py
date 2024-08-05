from django import forms
from .models import Post, Comment

class Register(forms.Form):
    username= forms.CharField(label="Username",max_length=100)
    email= forms.EmailField(label="Email",max_length=100)
    password = forms.CharField(label="Password", max_length=100, widget=forms.PasswordInput)

class Login(forms.Form):
    username= forms.CharField(label="username",max_length=100)
    password = forms.CharField(label="Password", max_length=100, widget=forms.PasswordInput)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text','photo']

    

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']