from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse

from .models import Question, Choice
# from django.template import loader
from django.shortcuts import render, HttpResponseRedirect,get_object_or_404


# Create your views here.


def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # template = loader.get_template('polls/index.html')
    # output = ','.join([q.question_text for q in latest_question_list])
    context = {'latest_question_list': latest_question_list}

    return render(request, 'polls/index.html', context)

    # return HttpResponse("欢迎来的投票站点")


def detail(request, question_id):
    """
    get_object_or_404()
    方法将一个Django模型作为第一个位置参数，
    后面可以跟上任意数量的关键字参数，如果对象不存在则弹出Http404错误。
    :param request:
    :param question_id:
    :return:  HttpResponse
    """
    question = get_object_or_404(Question, pk=question_id)
    # return HttpResponse('you are looking at quetion %s' % question)
    return render(request, 'polls/detail.html', {'question': question})


def result(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})
    # return HttpResponse('you are looking at the result of the question %d ' % question_id)


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST.get('choice',None))
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
