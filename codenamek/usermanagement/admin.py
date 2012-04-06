from django.contrib import admin

from models import UserProfile, Class, School


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'is_teacher', 'is_student')
    list_filter=('is_teacher', 'is_student')


class ClassAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'school_url', 'gender_flag')


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(School, SchoolAdmin)
