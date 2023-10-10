from django.contrib import admin
from .models import Post, Author
from .models import Post, Author, Category

# Register your models here.
# создаём новый класс для представления posts в админке
def nullfy_quantity(modeladmin, request, queryset): # все аргументы уже должны быть вам знакомы, самые нужные из них это request — объект хранящий информацию о запросе и queryset — грубо говоря набор объектов, которых мы выделили галочками.
    queryset.update(quantity=0)
nullfy_quantity.short_description = 'Обнулить товары' # описание для более понятного представления в админ панеле задаётся, как будто это объект
class PostAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    list_display = ('title', 'categoryType', 'dataCategory') # генерируем список имён всех полей для более красивого отображения
    list_filter = ['title', 'category']
    search_fields = ['title']
    actions = [nullfy_quantity]
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['authorUser', 'ratingAuthor']
    list_filter = ['authorUser']
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['NameCategory']
    list_filter = ['subscribers']
    search_fields = ['NameCategory']


    
admin.site.register(Post, PostAdmin)    
admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)