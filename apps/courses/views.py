import re

from django.shortcuts import render, redirect, get_object_or_404

from .models import Course, Instructor, Review, Department, CourseHistory


def course(request, code):
    dept, num = re.match("(\w+)-(\d+)", code).groups()
    course = get_object_or_404(Course, primary_alias__department__code__iexact=dept, primary_alias__coursenum=num)
    reviews = Review.objects.filter(section__course__history=course.history)
    context = {
        'item': course,
        'reviews': reviews,
        'title': "{} {}".format(dept, num)
    }
    return render(request, 'detail/course.html', context)


def instructor(request, name):
    instructor = get_object_or_404(Instructor, id=name.split("-", 1)[0])
    context = {
        'item': instructor,
        'reviews': instructor.reviews,
        'title': instructor.name
    }
    return render(request, 'detail/instructor.html', context)


def department(request, code):
    department = get_object_or_404(Department, code=code)
    context = {
        'item': department,
        'title': department.code,
        'reviews': Review.objects.filter(section__course__primary_alias__department=department)
    }
    return render(request, 'detail/department.html', context)


def autocomplete(request):
    pass


def about(request):
    return render(request, 'about.html')


def faq(request):
    return render(request, 'faq.html')


def cart(request):
    return render(request, 'cart.html')


def logout(request):
    return redirect('https://idp.pennkey.upenn.edu/logout')
