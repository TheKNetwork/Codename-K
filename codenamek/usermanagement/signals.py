def create_profile(sender, instance, signal, created, **kwargs):
    """When user is created also create a matching profile."""
 
    from codenamek.usermanagement.models import UserProfile
 
    if created:
        UserProfile(user = instance).save()
        
def create_class(sender, instance, signal, created, **kwargs):
    """When a group is created, immediately make that group a class"""
    
    from codenamek.usermanagement.models import Class
    
    if created:
        Class(group = instance).save()        