from django.contrib import admin
from .models import Question, Choice


# admin.site.register(Question)


# Register your models here.

# class ChoiceInline(admin.StackedInline):
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    # fields = ['pub_date', 'question_text']
    list_filter = ['pub_date']
    search_fields = ['question_text']
    list_display = ['question_text', 'pub_date', 'was_published_recently']
    fieldsets = [(None, {'fields': ['question_text']}),
                 ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
                 ]
    inlines = [ChoiceInline]


admin.site.register(Choice)

admin.site.register(Question, QuestionAdmin)
