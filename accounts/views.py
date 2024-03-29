from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.http import HttpResponse
from django import template
from django.views import View
from accounts.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .decorators import *
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from django.urls import reverse
from todo.models import *
from .forms import *


@unauthenticated_user
def registerPage(request):
    form = UserAdminCreationForm()
    if request.method == 'POST':
        form = UserAdminCreationForm(request.POST)
        email = request.POST['email']
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            email_body = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            }

            link = reverse('activate', kwargs={
                            'uidb64': email_body['uid'], 'token': email_body['token']})

            email_subject = 'Activate your account'

            activate_url = 'http://'+current_site.domain+link

            email = EmailMessage(
                email_subject,
                'Hi '+user.first_name + ', Please the link below to activate your account \n'+activate_url,
                'noreply@signstel.com',
                [email],
            )
            email.send(fail_silently=False)
            username = form.cleaned_data.get('first_name')

            messages.success(request, f'Your Account has been created! Please Confirm your email to complete registration.'+" " + username)
            return redirect('login')
        else:
            form = UserAdminCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=id)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None


        if user is not None and  account_activation_token.check_token(user, token):
            user.is_active = True
            user.profile.email_confirmed = True
            email=user.email
            print(email)
            email_subject = 'Welcome To Signstel'

            email = EmailMessage(
                email_subject,
                'Hi '+user.first_name + ', Welcome to Signstel Here You Can Enjoy Your Work \n',
                'noreply@signstel.com',
                [email],
            )
            email.send(fail_silently=False)
            user.save()
            login(request, user)
            messages.success(request, ('Your account have been confirmed.'))
            return redirect('home')
        else:
            messages.warning(request, ('The confirmation link was invalid, possibly because it has already been used.'))
            return redirect('home')

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.info(request, 'Username Or Password is incorrect')

    context = {}
    return render(request, 'accounts/login.html', context)


@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@admin_only
def profile(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance =request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance =request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request,f'Your Account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance =request.user)
        p_form = ProfileUpdateForm(instance =request.user.profile)
    
    new_form = ManagerAdminCreationForm()
    if request.method == 'POST':
        new_form = ManagerAdminCreationForm(request.POST)
        email = request.POST['email']
        if new_form.is_valid():
            user = new_form.save(commit=False)
            user.is_active = False
            value =new_form.cleaned_data['group']
            user.save()
            print(value)
            group = Group.objects.get(name= value)
            user.groups.add(group)
            
            current_site = get_current_site(request)
            email_body = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            }

            link = reverse('activate', kwargs={
                            'uidb64': email_body['uid'], 'token': email_body['token']})

            email_subject = 'Activate your account'

            activate_url = 'http://'+current_site.domain+link

            email = EmailMessage(
                email_subject,
                'Hi '+user.first_name + ', Please the link below to activate your account \n'+activate_url,
                'noreply@signstel.com',
                [email],
            )
            email.send(fail_silently=False)
            username = new_form.cleaned_data.get('first_name')

            messages.success(request, f'Account has been created for '+" " + username)
            
        else:
            new_form = ManagerAdminCreationForm()
            messages.warning(request, 'Form in valid ')
    
    context = {
        'tasks':tasks,
        'u_form': u_form,
        'p_form': p_form,
        'new_form':new_form
    }

    return render(request, 'accounts/profile.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Customer'])
def userPage(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance =request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance =request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request,f'Your Account has been updated!')
            return redirect('user-page')
    else:
        u_form = UserUpdateForm(instance =request.user)
        p_form = ProfileUpdateForm(instance =request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render (request, 'accounts/user.html', context)

@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template
        
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))