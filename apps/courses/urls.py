from django.urls import path, include
from django.views.generic.base import TemplateView

from . import views


urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),

    # pcr_detail urls
    path('course/<code>', views.course, name='course'),
    path('instructor/<code>', views.instructor, name='instructor'),
    path('department/<code>', views.department, name='department'),

    # searchbar URLs
    path('autocomplete', views.autocomplete, name='autocomplete'),

    # static URLs
    path('logout', views.logout, name='logout'),
    path('about', views.about, name='about'),
    path('cart', views.cart, name='cart'),
    path('faq', views.faq, name='faq'),
]
