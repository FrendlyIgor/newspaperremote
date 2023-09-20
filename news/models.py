from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum



class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"Имя автора - {self.authorUser.username}"
       
        
    ratingAuthor = models.SmallIntegerField(default = 0)
    
    def update_rating(self):
        postRat = self.post_set.all().aggregate(postRating=Sum('rating'))
        pRat = 0
        pRat += postRat.get('postRating')

        commentRating = self.authorUser.comment_set.all().aggregate(commentRating=Sum('rating'))
        cRat = 0
        cRat += commentRating.get('commentRating')

        self.ratingAuthor = pRat * 3 + cRat
        self.save()

class Category(models.Model):
    NameCategory = models.CharField(max_length=64, unique = True)
    subscribers = models.ManyToManyField(User, blank = True)# blank - список может быть пустым (пока еще никто не подписался)
    def __str__(self):
        return self.NameCategory
  
    
 #модель, объединяющая подписчика и категорию   


   
class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    
    news = 'nw'
    article = 'ar'
    
    how_choise = [
        (news, 'новость'),
        (article, 'статья'),
    ]
    categoryType = models.CharField(max_length = 2, choices = how_choise, default = news)
    dataCategory = models.DateTimeField(auto_now_add = True)
    postCategory = models.ManyToManyField(Category, through = "PostCategory")
    title = models.CharField(max_length=128)
    text = models.TextField()
    rating = models.SmallIntegerField(default=0)
    
    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:124] + '...'
    
    def __str__(self):
       return f'Пост #{self.pk} - Название: {self.title}'
    
    def get_absolute_url(self): # добавим абсолютный путь, чтобы после создания нас перебрасывало на страницу с товаром
       return f'/post/{self.id}'

class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete = models.CASCADE)
    category = models.ForeignKey(Category, on_delete = models.CASCADE)

class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    dateCreation = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.commentPost.author.authorUser.username
       
        
    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()