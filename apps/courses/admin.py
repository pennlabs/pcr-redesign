from django.contrib import admin

from .models import Department, CourseHistory, Course, Instructor, Alias, Section, Review, ReviewBit


admin.site.register(Department)
admin.site.register(CourseHistory)
admin.site.register(Course)
admin.site.register(Instructor)
admin.site.register(Alias)
admin.site.register(Section)
admin.site.register(Review)
admin.site.register(ReviewBit)
