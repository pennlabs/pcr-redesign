from django.urls import path, include
from django.views.generic.base import TemplateView


urlpatterns = [
    path(r'/', TemplateView.as_view(template_name="index.html"), name="index"),

    #pcr_detail urls
    path('instructor/<ID-NAME>', views.instructor, name="instructor"),
    path('course/<DEPT-CODE>', views.course, name="course"),
    path('department/<DEPT>', views.department, name="department"),

    #searchbar URLs
    path('autocomplete_data.json/<data>', views.autocomplete_data),

    #static URLs
    path('/logout', views.logout, name="logout"),
    path('/about', views.about, name="about"),
    path('/cart', views.cart, name="cart"),
    path('/faq', views.faq, name="faq"),
]
