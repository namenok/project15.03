
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=30, verbose_name = "Назва")
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

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


# class LibUserPost(models.Model):
#     title = models.CharField(max_length=30, verbose_name = "Заголовок посту")
#     content = models.TextField(verbose_name = "Опис посту")
#     published_date = models.DateTimeField(auto_now_add=True, verbose_name = "Дата та час посту")
#     user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = "Автор")
#     date = models.DateField()
#     to_category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Мій текст належить до Категорії", related_name='posts')
#     def __str__(self):
#         return f"{self.user.username} - {self.date}"
#
#     class Meta:
#         verbose_name = "постЮзерВБібліотеку"
#         verbose_name_plural = "постиЮзерВБібліотеку Пости"

class Post(models.Model):
    title = models.CharField(max_length=30, verbose_name = "Заголовок посту")
    content = models.TextField(verbose_name = "Опис посту")
    published_date = models.DateTimeField(auto_created=True, verbose_name = "Дата та час посту")
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.CASCADE, verbose_name="Категорія")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = "Автор")
    poster = models.ImageField(upload_to='uploads')
    teg = models.ManyToManyField(Teg, blank=True, related_name='posts', verbose_name="Хештеги")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "ПостБложний"
        verbose_name_plural = "ПостиБложні"


class PersonalPost(models.Model):
    title = models.CharField(max_length=30, verbose_name = "Заголовок посту")
    content = models.TextField(verbose_name = "Опис посту")
    published_date = models.DateTimeField(auto_now_add=True, verbose_name = "Дата та час посту")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = "Автор")
    poster = models.ImageField(upload_to='uploads' ,verbose_name = "ПостерДоПерсональногоПосту")
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    class Meta:
        verbose_name = "ОсобистийПост"
        verbose_name_plural = "Особисті Пости"
        unique_together = ('user', 'poster', 'date', 'content')




class LibText(models.Model):
    title = models.CharField(max_length=30, verbose_name="Заголовок мого поля з текстом")
    content = models.TextField(verbose_name="Зміст")
    to_category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Мій текст належить до Категорії")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "пост адміна для Бібліотеки"
        verbose_name_plural = "постИ адміна для бібліотеки"



class Survey(models.Model):
    question = models.CharField(max_length=100)

    def __str__(self):
        return self.question





class Answers(models.Model):
    survey = models.ForeignKey(Survey, related_name='answers', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=50)
    def __str__(self):
        return self.choice_text



class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    answer_choice = models.ForeignKey(Answers, on_delete=models.CASCADE)
    answered_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField()

    class Meta:
        unique_together = ('user', 'survey', 'date')  # Унікальна комбінація користувача, опитування і дати

    def __str__(self):
        return f"Відповідь {self.user.username} на {self.survey.question} {self.date}"