from django.shortcuts import render, redirect
from django.http import JsonResponse

# Create your views here.
def instructor(request, name):
    pass

def course(request, code):
    pass

def department(request, code):
    pass

def autocomplete_data(request):
    pass

def about(request):
    return render(request, "about.html")

def faq(request):
    return render(request, "faq.html")

def cart(request):
    return render(request, "cart.html")

def logout(request):
    return redirect("https://idp.pennkey.upenn.edu/logout")
