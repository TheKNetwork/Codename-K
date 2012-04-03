from django.db import models
from datetime import datetime

class WhiteboardSession(models.Model):
    prepopulated_fields = { 'slug': ['whiteboard_hash'] }

    whiteboard_title = models.CharField(max_length=50)
    whiteboard_hash = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    
    date_created = models.DateTimeField()
    date_modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.date_created == None:
            self.date_created = datetime.now()
            self.date_modified = datetime.now()
            super(WhiteboardSession, self).save()

    def get_absolute_url(self):
    	return "/classroom/%s/" % self.slug

    def __unicode__(self):
    	return self.title

