from django.db import models
from django.contrib.auth.models import User


class Entry(models.Model):

    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "ДумкаФорма"
        verbose_name_plural = "ДумкиФорма"

    def __str__(self):
        return f'{self.text[:50]}...'


class Foto(models.Model):

    image = models.ImageField(upload_to='media')
    class Meta:
        verbose_name = "Зображення"
        verbose_name_plural = "УсіЗображення"




class Category(models.Model):
    name = models.CharField(max_length=30, verbose_name = "Назва")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"


class Teg(models.Model):
    name = models.TextField(max_length=10)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Хештег"
        verbose_name_plural = "Хештеги"



class Post(models.Model):
    title = models.CharField(max_length=30, verbose_name = "Заголовок посту")
    content = models.TextField(verbose_name = "Опис посту")
    published_date = models.DateTimeField(auto_created=True, verbose_name = "Дата та час посту")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name = "Категорія")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = "Автор")
    # (юзер не потрібен бо акаунт
    # буде ен доступний для багатьох юзерів приберу це потім
    poster = models.URLField(
        default="https://images.pexels.com/photos/147465/pexels-photo-147465.jpeg?auto=compress&cs=tinysrgb&w=600",
        verbose_name = "Постер")
    teg = models.ManyToManyField(Teg, blank=True, related_name='posts', verbose_name="Хештеги")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "ПостБложний"
        verbose_name_plural = "ПостиБложні"





class LibText(models.Model):
    title = models.CharField(max_length=30, verbose_name="Заголовок мого поля з текстом")
    content = models.TextField(verbose_name="Зміст")
    to_category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Мій текст належить до Категорії")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Мій постик"
        verbose_name_plural = "Мої постики"


class CheckForm(models.Model):
    date = models.DateTimeField(verbose_name="дата опитування")
    answer1 = models.BooleanField(verbose_name="мені сумно", default=False)
    answer2 = models.BooleanField(verbose_name="мені весело", default=False)
    answer3 = models.BooleanField(verbose_name="мені норм", default=False)

    class Meta:
        verbose_name = "Опитуваннячко"
        verbose_name_plural = "Опитування"



