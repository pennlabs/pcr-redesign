import re

from django.http import JsonResponse, Http404
from django.shortcuts import render, reverse, redirect, get_object_or_404

from django.db.models import Q
from .models import Course, Instructor, Review, Department, CourseHistory


def course(request, code):
    try:
        dept, num = re.match(r"(\w+)-(\d+)", code).groups()
    except AttributeError:
        raise Http404
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
    query = request.GET.get("q", "")

    return JsonResponse({
        "departments": [{
            "category": "Departments",
            "keywords": dept.code,
            "title": dept.code,
            "desc": dept.name,
            "url": reverse("department", kwargs={"code": dept.code}),
        } for dept in Department.objects.filter(code__icontains=query)],
        "courses": [{
            "category": "Courses",
            "title": course.code.replace("-", " "),
            "desc": course.name,
            "url": reverse("course", kwargs={"code": course.code})
        } for course in Course.objects.filter(primary_alias__coursenum__icontains=query)],
        "instructors": [{
            "category": "Instructors",
            "title": instructor.name,
            "desc": ", ".join([x.code for x in instructor.departments]),
            "url": reverse("instructor", kwargs={"name": instructor.code})
        } for instructor in Instructor.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query))]
    })


def about(request):
    return render(request, 'about.html')


def faq(request):
    return render(request, 'faq.html')


def cart(request):
    return render(request, 'cart.html')


def logout(request):
    return redirect('https://idp.pennkey.upenn.edu/logout')
