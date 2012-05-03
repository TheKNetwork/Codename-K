from django.db import models
from datetime import datetime

class WhiteboardSession(models.Model):
    whiteboard_title = models.CharField(max_length=50)
    whiteboard_hash = models.CharField(max_length=4000)
    whiteboard_url = models.CharField(max_length=4000)
    
    date_created = models.DateTimeField()
    date_modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.date_created == None:
            self.date_created = datetime.now()
            self.date_modified = datetime.now()
            super(WhiteboardSession, self).save()

    def get_absolute_url(self):
    	return "/classroom/%s" % self.url

    def __unicode__(self):
    	return self.title

