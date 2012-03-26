from django.db import models
from datetime import datetime

"""
"""

class KnetworkBaseModel(models.Model):
    date_created = models.DateTimeField()
    date_modified = models.DateTimeField()

    def save(self):
        if self.date_created == None:
            self.date_created = datetime.now()
            self.date_modified = datetime.now()
            super(KnetworkBaseModel, self).save()
