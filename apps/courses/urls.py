from django.urls import path, include
from django.views.generic.base import TemplateView
<<<<<<< HEAD
=======

>>>>>>> 0d2af0dd2c0766e607e9259d31ca0389bf75fe5d

urlpatterns = [
    path(r'/', TemplateView.as_view(template_name="index.html"), name="index"),

    #pcr_detail urls
    path('instructor/<ID_NAME>', views.instructor, name="instructor"),
    path('course/<DEPT_CODE>', views.course, name="course"),
    path('department/<DEPT>', views.department, name="department"),

    #searchbar URLs
    path('autocomplete_data.json/<data>', views.autocomplete_data),

    #static URLs
    path('/logout', views.logout, name="logout"),
    path('/about', views.about, name="about"),
    path('/cart', views.cart, name="cart"),
    path('/faq', views.faq, name="faq"),

    #/api TO BE MOVED TO ITS OWN Directory
    # path('/api', views.api, name="api"),

]
