from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from .get_det import imdb
from .models import Watchlist,User
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from .forms import CreateUserForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage

# Create your views here.
def mail(message,recipient_list):
    email = EmailMessage(
    'From PITBULL',
    message,
    settings.EMAIL_HOST_USER,
    recipient_list,
    )
    
    email.send(fail_silently=False)


def home(request):
    trending_this_week_url = "https://api.themoviedb.org/3/trending/all/day?api_key=b8da327ca3bd7ccdc7dfdba3de3184ec"
    popular_movies_url = "https://api.themoviedb.org/3/movie/popular?api_key=b8da327ca3bd7ccdc7dfdba3de3184ec&language=en-US&page=1"
    popular_in_theatre_url = "https://api.themoviedb.org/3/movie/now_playing?api_key=b8da327ca3bd7ccdc7dfdba3de3184ec&language=en-US&page=1"
    popular_shows_url = "https://api.themoviedb.org/3/trending/tv/week?api_key=b8da327ca3bd7ccdc7dfdba3de3184ec"
    
    return render(request, 'imdb/home.html',context={
        "trending_this_week":imdb().get_from_api(trending_this_week_url),
        "popular_movies":imdb().get_from_api(popular_movies_url),
        "popular_shows":imdb().get_from_api(popular_shows_url),
        "popular_in_theatre" : imdb().get_from_api(popular_in_theatre_url),
    })

def search(request,q,year):
    if request.method == "POST" and 'query' in request.POST:
        q = request.POST.get("query")
        return redirect("search",q,year)
    try:
        if request.POST.get("type") == 'save':
            Watchlist.objects.get_or_create(profile_id=request.user.id,movie_show=request.POST.get("name"),year=request.POST.get("year"))
            return HttpResponse("success")
        elif request.POST.get("type") == 'unsave':
            Watchlist.objects.get(profile_id=request.user.id,movie_show=request.POST.get("name"),year=request.POST.get("year")).delete()
            return HttpResponse("success")
    except:
        messages.warning(request,f"Something went wrong")


    movie_shows_details = imdb().get_movie_show(q,year)
    return render(request,"imdb/search.html",context={
        "movie_show":movie_shows_details,
        "in_watchlist":Watchlist.objects.filter(profile_id=request.user.id,movie_show=q,year=int(year)).exists()
    })

def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request,f'Hey {username}, welcome to IMDb')
            return redirect('home')
            
        else:
            messages.warning(request,f'Invalid username or password')
        
    return render(request,"imdb/login.html")

def register_page(request):
    form = CreateUserForm()
    email_exists_in_db = True


    if request.method == 'POST':
        first_name = request.POST.get('username')
        user_email = request.POST.get('email')
        form = CreateUserForm(request.POST)
        password_1 = request.POST.get('password1')
        password_2 = request.POST.get('password2')

        #Checking if the email is already in use.
        if User.objects.filter(email=user_email).exists():
            messages.error(request,'The email you entered is already in use')
            email_exists_in_db = False

               


        if form.is_valid() and email_exists_in_db: 
            
            user = form.save()
            login(request,user)
            user_ins = User.objects.get(id=user.id)
            messages.success(request,f'Hey {first_name} welcome to IMDb')
            return redirect('home')
           

        else:
            try:
                int(password_1)
                messages.error(request,'Password cannot contain only numbers')
            except:
                pass
            #Checking if the password and conformation password matches.

            """The reason why I put this here instead of putiing this with other error checker is because django will 
            automatically look for password mismatch errors so if the form is not valid then this might 
            be the reason so you don't have to put this statement at the top.It will also increase the speed.
            It is the same for whitespace in username error so we will put that here too. Thats why we put the other 
            error checkers above form.is_valid() statement django will not be looking for email already exists or password
            length is less than 8 errors."""

            
            if password_1 != password_2:
                messages.error(request,"The password does'nt match. Make sure you enter the same password on both fields")
            
            elif ' ' in request.POST.get('username'):
                messages.error(request,"You can't have whitespaces in user name replace it with a symbol.")

            elif len(password_1) < 8:
                messages.error(request,'Password should atleast contain 8 characters')
            
            else:
                messages.error(request,"Password can't be similar to username or other personal information")
        
    return render(request,'imdb/register.html')


def watchlist(request):
    if request.method == 'POST':
        if 'id' in request.POST:
            Watchlist.objects.get(id=request.POST['id']).delete()
            return HttpResponse("Done")

    wlist = Watchlist.objects.filter(profile_id=request.user.id).order_by("added_date")
    return render(request,"imdb/watchlist.html",context={
        "list": wlist.reverse(),
    })

def result_suggestion(request):
    results = imdb().search_sugg(request.POST.get('query'))
    return JsonResponse(results)

def logout_user(request):
    logout(request)
    return HttpResponse("success")

def password_reset(request):
    if request.method == 'POST':
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            entered_email = request.POST.get('email')
            associated_users = User.objects.filter(email=entered_email)
            if associated_users.exists():
                for user in associated_users:
                    contexts = {
                        "email":user.email,
                        'domain':request.META['HTTP_HOST'],
                        'site_name': 'PITBULL',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    content = render_to_string('change-password/mail-content.txt',contexts)
                    mail(content,[user.email])
                    return redirect('password_reset_done')
            else:
                messages.error(request,"The email you entered does'nt exists")
    password_reset_form = PasswordResetForm()
    return render(request,'change-password/change-password.html',{"form":password_reset_form})


def delete_user(request):
    if request.method == 'POST':
        entered_password = request.POST.get('entered_password')
        user = User.objects.get(id=request.user.id)
        if user.check_password(entered_password):
            user.delete()
            messages.success(request,"Successfully deleted your account")
            
        else:
            messages.warning(request,"The password you entered is invalid")
        
        return HttpResponse("success")
    