from modeltranslation.translator import register, TranslationOptions
from .models import Survey, Answers


@register(Survey)
class SurveyTranslationOptions(TranslationOptions):
    fields = ("question",)


@register(Answers)
class AnswersTranslationOptions(TranslationOptions):
    fields = ("choice_text",)



