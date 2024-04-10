from django.urls import path

from home import views as hv
from login import views as lv
from signup import views as sv

urlpatterns = [
    path('', hv.displayHomePage, name="home"),
    path('login', lv.displayLoginPage, name="login"),
    path('signup', sv.signup, name="signup"),
    path('signup/<int:step>/', sv.signup_step, name='signup_step'),
]
