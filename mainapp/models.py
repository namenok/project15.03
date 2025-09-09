from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class PersonalPost(models.Model):
    title = models.CharField(max_length=30, verbose_name=_("заголовок"))
    content = models.TextField(verbose_name=_("опис"))
    published_date = models.DateTimeField(
        auto_now_add=True, verbose_name=_("дата та час")
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("автор"))

    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    class Meta:
        verbose_name = _("ОсобистийПост")
        verbose_name_plural = _("Особисті Пости")
        unique_together = ("user", "date", "content")


class Survey(models.Model):
    question = models.CharField(max_length=150)

    def __str__(self):
        return self.question


class Answers(models.Model):
    CHOICES = (("good", _("Добре")), ("neutral", _("Середнє")), ("bad", _("Погано")))
    marker = models.CharField(max_length=10, choices=CHOICES)
    survey = models.ForeignKey(Survey, related_name="answers", on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=150)

    def __str__(self):
        return self.choice_text


class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    answer_choice = models.ForeignKey(Answers, on_delete=models.CASCADE)
    answered_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField()

    class Meta:
        unique_together = (
            "user",
            "survey",
            "date",
        )

    def __str__(self):
        return _("відповідь %(username)s на %(question)s %(date)s") % {
            "username": self.user.username,
            "question": self.survey.question,
            "date": self.date,
        }


class Track(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    spotify_track_id = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user} - {self.date} - {self.spotify_track_id}"


class SpotifyToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="spotify_token")
    access_token = models.CharField()
    refresh_token = models.CharField()
    expires_in = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        """Check if token is expired based on created_at + expires_in"""
        from datetime import timedelta, datetime
        expiry = self.created_at + timedelta(seconds=self.expires_in)
        return datetime.utcnow().replace(tzinfo=expiry.tzinfo) >= expiry
