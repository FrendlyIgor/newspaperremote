from django.urls import path
from .views import PostList, PostDetail, postSearch, Posts, PostCreateView, PostDetailView, PostUpdateView, PostDeleteView,\
PostCategoryView, subscribe_to_category, unsubscribe_from_category
app_name = 'news'
urlpatterns = [
    # path -- означает путь. 
    #path('', index, name='index'),здесь должна быть главная страница
    #path('', AuthorList.as_view()),
    #path('<int:pk>', AuthorDetail.as_view()),
    path('search/', postSearch.as_view()),
    path('', PostList.as_view(), name='posts'),
    path('posts/', Posts.as_view()),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),#         Ссылка на детали поста
    path('post/post_edit/<int:pk>/', PostUpdateView.as_view(), name='post_edit'),#       Ссылка на редактирование поста
    path('post/post_add/', PostCreateView.as_view(), name='post_add'),#                    Ссылка на создание поста
    path('post/post_delete/<int:pk>/', PostDeleteView.as_view(), name='post_delete'),#  Ссылка на удаеление поста
    path('category/<int:pk>/', PostCategoryView.as_view(), name='category'),
    path('subscribe/<int:pk>/', subscribe_to_category, name='subscribe'),
    path('unsubscribe/', unsubscribe_from_category, name='unsubscribe'),
]