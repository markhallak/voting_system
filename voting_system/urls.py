from django.urls import path

from home import views as hv
from login import views as lv
from signup import views as sv
from elections import views as ev
from notifications import views as nv
from bookmarks import views as bv

urlpatterns = [
    path('', hv.displayHomePage, name="home"),
    path('login', lv.displayLoginPage, name="login"),
    path('signup', sv.signup, name="signup"),
    path('signup/<int:step>/', sv.signup_step, name="signup_step"),
    path('generate-qr-code', sv.generate_qr_code, name="generate-qr-code"),
    path('my_elections', ev.displayMyElectionsPage, name="my_elections"),
    path('notifications', nv.displayNotificationsPage, name="notifications"),
    path('bookmarks', bv.displayBookmarksPage, name="bookmarks")
]
