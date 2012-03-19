from django.db import models

# Create your models here.
class LearningSession(models.Model):
    learningSessionId = models.CharField(max_length=250)
    learningSessionTitle = models.CharField(max_length=250)
    active = models.BooleanField()
    description = models.TextField()
    createdOn = models.TimeField()
    slug = models.SlugField(unique=True)
    
    def __unicode__(self):
        return self.learningSessionTitle
    
    
