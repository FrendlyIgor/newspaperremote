from django.forms import ModelForm
from .models import Post
from django import forms

# Создаём модельную форму
class PostForm(ModelForm):
# В класс мета, как обычно, надо написать модель, по которой будет строиться форма, и нужные нам поля. Мы уже делали что-то похожее с фильтрами
   class Meta:
       model = Post
       fields = ['author', 'title', 'categoryType', 'text',]
       widgets = {
           """ 'author' : forms.TextInput(attrs={
               'placeholder' : 'Напиши Имя',
               'class': 'form-control'
           }), """
           'title' : forms.TextInput(attrs={
           'placeholder' : 'Напиши название',
           'class': 'form-control'
         }),
         'text' : forms.Textarea(attrs={
           'class': 'form-control',
           'placeholder' : 'Напиши текст'
         })
       }
    