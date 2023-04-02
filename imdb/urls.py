from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    path("search/<str:q>/<str:year>",views.search,name="search"),
    path("login",views.login_page,name="login"),
    path("register",views.register_page,name="register"),
    path("watchlist",views.watchlist,name="watchlist"),
    path("result_sugg",views.result_suggestion,name="result_suggestion"),
]