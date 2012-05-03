from django import template
from django.utils.safestring import SafeUnicode
from django.contrib.auth.models import *

register = template.Library()

@register.filter
def in_group(user, group):
    got_group = Group.objects.get(id=group)
    print got_group
    for ugroup in user.groups.all():
        if ugroup.id == got_group.id:
            return True
    
    return False;
    
in_group.is_safe = True
