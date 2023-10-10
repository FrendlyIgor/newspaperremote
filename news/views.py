from typing import Any, Dict
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, User, Author, Category
from datetime import datetime
from django.shortcuts import render, redirect,HttpResponseRedirect
from django.template.loader import render_to_string
from .filters import PostFilter
from django.core.paginator import Paginator
from django.core.mail import EmailMultiAlternatives
from django.views import View
from .forms import PostForm
from django.urls import reverse_lazy, resolve
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
import logging

logger = logging.getLogger('django')

DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL

    # Create your views here.

class PostCategoryView(ListView):
    model = Post
    template_name = 'news/category.html'
    context_object_name = 'posts'
    ordering = ['-dateCreation']  # сортировка по дате в порядке убывания
    paginate_by = 2
#запрос на получение id
    def get_queryset(self):
        self.id = resolve(self.request.path_info).kwargs['pk']
        c = Category.objects.get(id=self.id)
        queryset = Post.objects.filter(category=c)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        category = Category.objects.get(id=self.id)
        subscribed = category.subscribers.filter(email=user.email)#подписчики на категорию, отфильтрованные по email
        if not subscribed:#если пользователя нет, то передаем в через контекст категорию
            context['category'] = category
        return context
    
class PostList(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'news/posts.html'  # указываем имя шаблона, в котором будет лежать HTML, в нём будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'posts'
    ordering = ['-id']
    paginate_by = 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['choices'] = Post.how_choise
        context['form'] = PostForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST) # создаём новую форму, забиваем в неё данные из POST-запроса
        if form.is_valid(): # если пользователь ввёл всё правильно и нигде не накосячил, то сохраняем новый товар
           form.save()
        return super().get(request, *args, **kwargs)
    
        # дженерик для получения деталей о посте    
class PostDetailView(DetailView):
   model = Post
   template_name = 'news/post_detail.html'
   context_object_name = 'post'
   queryset = Post.objects.all()

   def get_object(self, *args, **kwargs): # переопределяем метод получения объекта, как ни странно
        obj = cache.get(f'Пост - {self.kwargs["pk"]}', None)# кэш очень похож на словарь, и метод get  действует также
        #он забирает объект по ключу, если его нет, то забирает None
#Если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(queryset=self.queryset) 
            cache.set(f'Пост - {self.kwargs["pk"]}', obj)
        
        return obj

    # дженерик для создания объекта. Надо указать только имя шаблона и класс формы
class PostCreateView(CreateView, PermissionRequiredMixin):
    """ permission_required = ('news:post_add') """
    template_name = 'news/post_add.html'
    model = Post
    form_class = PostForm
    success_url = '/posts/'

    """ def post(self, request, *args, **kwargs):
        form = self.get_form()
        user = request.user
        if form.is_valid():
            post = form.save(commit=False)
            post.author = Author.objects.get_or_create(user=user)[0]
            post.save()
            return self.form_valid(form)
        return redirect('news:posts') """
    
    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)

        self.object = form.save()

        self.category_list = self.object.category.all()

        for category in self.category_list:

            for sub in category.subscribers.all():

                html_content = render_to_string(
                    'new_post.html',
                    {
                        'user': sub,
                        'post': self.object,
                    }
                )

                msg = EmailMultiAlternatives(
                    subject=f'{self.object.title}',
                    body=self.object.text,
                    from_email='divIgordiv@yandex.ru',
                    to=[f'{sub.email}'],
                )
                msg.attach_alternative(html_content, "text/html")  # добавляем html
                msg.send()  # отсылаем
                #print(html_content)

        return HttpResponseRedirect(self.get_success_url())
    
    # дженерик для редактирования объекта
class PostUpdateView( UpdateView, PermissionRequiredMixin):
    template_name = 'news/post_edit.html'
    form_class = PostForm
    success_url = '/posts/post/{id}'
       
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)
      
    # дженерик для удаления товара
class PostDeleteView(DeleteView):
    template_name = 'news/post_delete.html'
    queryset = Post.objects.all()
    success_url = reverse_lazy('news:posts') # не забываем импортировать функцию reverse_lazy из пакета django.urls
       
class PostDetail(DetailView):
    model = Post
    template_name = 'news/post.html'
    context_object_name = 'post'

class Posts(View):

   def get(self, request):
        posts = Post.objects.order_by('-id')
        p = Paginator(posts, 1) # Создаём объект класса пагинатор, передаём ему список наших постов и их количество для одной страницы
        posts = p.get_page(request.GET.get('page', 1)) # Берём номер страницы из get-запроса. Если ничего не передали, будем показывать первую страницу
        # Теперь вместо всех объектов в списке товаров хранится только нужная нам страница с товарами

        data = {
        'posts': posts,
        }

        return render(request, 'news/posts.html', data)

class postSearch(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'news/search.html'  # указываем имя шаблона, в котором будет лежать HTML, в нём будут все инструкции о том, 
                                        #как именно пользователю должны вывестись наши объекты
    context_object_name = 'posts'  # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через HTML-шаблон
    ordering = ['-id'] # сортировка по цене в порядке убывания
    paginate_by = 1 # поставим постраничный вывод в один элемент
  
        # метод get_context_data нужен нам для того, чтобы мы могли передать переменные в шаблон. В возвращаемом словаре context будут храниться все переменные. 
        # Ключи этого словари и есть переменные, к которым мы сможем потом обратиться через шаблон
    def get_context_data(self, **kwargs): # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset()) # вписываем наш фильтр в контекст
        return context
    
class UserSubscribtion(ListView):
    pass
@login_required
def subscribe_to_category(request, pk):
    user = request.user
    category = Category.objects.get(id = pk)

    if not category.subscribers.filter(id=user.id).exists():
        category.subscribers.add(user)
        email=user.email
        html = render_to_string(
            'mail/subscribed.html',
            {
                'category': category,
                'user': user,
            },
        )

        msg = EmailMultiAlternatives(
            subject=f'{category} subcription',
            body='',
            from_email=DEFAULT_FROM_EMAIL,
            to=[email,],
        )
        msg.attach_alternative(html, 'text/html')#какого типа данные (text/html)
        try:
            msg.send()
        except Exception as e:
            print(e)
        return redirect('news:posts')#redirect - перенаравление
    return redirect(request.META.get('HTTP_REFERER'))#возврат к исходной странице, с которой этот запрос поступил
#функция отписки 
@login_required
def unsubscribe_from_category(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    if category.subscribers.filter(id=user.id).exists():
        category.subscribers.remove(user)
    return redirect('protect:index')