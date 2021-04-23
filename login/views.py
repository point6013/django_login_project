import hashlib
import datetime

from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from . import models
from .models import User
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from .forms import UserForms, RegisterForm

app_name = 'login'


# Create your views here.x

def hash_code(s, salt='website'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(code=code, user=user, )
    return code


def send_mail(email, code):
    from django.core.mail import EmailMultiAlternatives
    subject = '来自xxxxxx.com的确认邮件'
    text_content = '''感谢注册xxx.com，这里是刘江的博客和教程站点，专注于Python、Django和机器学习技术的分享！\
                    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''

    html_content = '''
                    <p>感谢注册<a href="http://{}/user/confirm/?code={}" target=blank>www.liujiangblog.com</a>，\
                    这里是xx的博客和教程站点，专注于Python、Django和机器学习技术的分享！</p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def index(request):
    if not request.session.get('is_login', None):
        # logout 之后，is_login为None，跳转到登录界面
        return redirect('/user/login/')
    # 如果已经检测到已经登录，则跳转index页面
    return render(request, 'login/index.html')


def login(request):
    if request.session.get('is_login', None):
        # 不允许重复登录,如果登录状态没有消失，返回index页面
        return redirect('/user/index/')

    if request.method == 'POST':
        # hashkey = CaptchaStore.generate_key()
        # image_url = captcha_image_url(hashkey)
        login_form = UserForms(request.POST)
        message = '请检查填写的内容'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            try:
                user = User.objects.get(name=username)
            except:
                message = '用户不存在！'
                return render(request, 'login/login.html', locals())

            if not user.has_confirmed:
                message = '该用户还未经过邮件确认'
                return render(request, 'login/login.html', locals())
            if user.password == hash_code(password):
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('/user/index')  # 跳转另外一个应用
            else:
                message = '密码不正确！'
                return render(request, 'login/login.html', locals())
        else:
            return render(request, 'login/login.html', locals())
    login_form = UserForms()
    # 使用locals 函数就不用费劲去构造一个形如{'message':message, 'login_form':login_form}的字典了
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        # 不允许重复登录
        return redirect('/user/index/')

    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        message = '请检查填写内容'
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')
            sex = register_form.cleaned_data.get('sex')
            if password1 != password2:
                message = '两次输入的密码不一致！'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = User.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已存在'
                    return render(request, 'login/register.html', locals())

                same_email_user = User.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱已注册'
                    return render(request, 'login/register.html', locals())

                new_user = User()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                code = make_confirm_string(new_user)
                send_mail(email, code)
                message = '请前往邮箱进行确认！'
                return render(request, 'login/confirm.html', locals())

        else:
            render(request, 'login/register.html', locals())
    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        # 如果没有登录，则跳转登录界面
        return redirect('/user/login/')
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect('/user/login/')


def user_confirm(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求！'
        return render(request, 'login/confirm.html', locals())
    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已经过期，请重新注册！'
        return render(request, 'login/register.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return redirect('/user/login/', locals())
