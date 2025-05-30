
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=30, verbose_name=_("Назва"))
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
        verbose_name = _("Категорія")
        verbose_name_plural = _("Категорії")




class Teg(models.Model):
    name = models.TextField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Хештег")
        verbose_name_plural = _("Хештеги")



# від юзера в бібліотеку
class Post(models.Model):
    title = models.CharField(max_length=30, verbose_name=_("Заголовок посту"))
    content = models.TextField(verbose_name=_("Опис посту"))
    published_date = models.DateTimeField(auto_created=True, verbose_name=_("Дата та час посту"))
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.CASCADE, verbose_name=_("Категорія"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Автор"))
    teg = models.ManyToManyField(Teg, blank=True, related_name='posts', verbose_name=_("Хештеги"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("запис користувача в бібліотеку")
        verbose_name_plural = _("записи користувача в бібліотеку")


#персональний юзера в його щоденник
class PersonalPost(models.Model):
    title = models.CharField(max_length=30, verbose_name = _("Заголовок посту"))
    content = models.TextField(verbose_name = _("Опис посту"))
    published_date = models.DateTimeField(auto_now_add=True, verbose_name = _("Дата та час посту"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = _("Автор"))

    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    class Meta:
        verbose_name = _("ОсобистийПост")
        verbose_name_plural = _("Особисті Пости")
        unique_together = ('user', 'date', 'content')


#з адмінки в бібліотеку
class LibText(models.Model):
    title = models.CharField(max_length=30, verbose_name=_("Заголовок мого поля з текстом"))
    content = models.TextField(verbose_name=_("Зміст"))
    to_category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name = "libtexts", verbose_name=_("Мій текст належить до Категорії"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("пост з aдмінки для бібліотеки")
        verbose_name_plural = _("постИ з адмінки для бібліотеки")



class Survey(models.Model):
    question = models.CharField(max_length=100)

    def __str__(self):
        return self.question



class Answers(models.Model):
    CHOICES = (
        ('good', _('Добре')),
        ('neutral', _('Середнє')),
        ('bad', _('Погано'))
    )
    marker = models.CharField(max_length=10, choices=CHOICES)
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
        return _("Відповідь %(username)s на %(question)s %(date)s") % {
            'username': self.user.username,
            'question': self.survey.question,
            'date': self.date,
        }