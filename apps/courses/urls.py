from django.urls import path, include
from django.views.generic.base import TemplateView

from . import views


urlpatterns = [
    path('', TemplateView.as_view(template_name="index.html"), name="index"),

    #pcr_detail urls
    path('instructor/<name>', views.instructor, name="instructor"),
    path('course/<code>', views.course, name="course"),
    path('department/<code>', views.department, name="department"),

    #searchbar URLs
    path('autocomplete_data', views.autocomplete_data, name="autocomplete"),

    #static URLs
    path('logout', views.logout, name="logout"),
    path('about', views.about, name="about"),
    path('cart', views.cart, name="cart"),
    path('faq', views.faq, name="faq"),
]
