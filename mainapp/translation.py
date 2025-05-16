from modeltranslation.translator import register, TranslationOptions
from .models import Survey, Answers, Category, LibText

@register(Survey)
class SurveyTranslationOptions(TranslationOptions):
    fields = ('question',)

@register(Answers)
class AnswersTranslationOptions(TranslationOptions):
    fields = ('choice_text',)


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(LibText)
class LibTextTranslationOptions(TranslationOptions):
    fields = ('title', 'content',)