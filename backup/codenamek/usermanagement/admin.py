from django.contrib import admin

from models import *


class UserProfileAdmin(admin.ModelAdmin):
    pass

class ClassAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'school_url', 'gender_flag')

class ClassroomTeamAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Classroom, ClassAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(ClassroomTeam, ClassroomTeamAdmin)