from django.shortcuts import render,redirect,HttpResponse
from django.http import JsonResponse
from .get_det import imdb
from .models import Watchlist,User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .forms import CreateUserForm

# Create your views here.
def home(request):
    if request.method == "POST":
        q = request.POST.get("query")
        return redirect("search",q,None)

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