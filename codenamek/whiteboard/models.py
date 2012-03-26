from django.db import models
from codenamek.common import common_models

class WhiteboardSession(common_models.KnetworkBaseModel):
    whiteboard_title = models.CharField(max_length=50)
    whiteboard_hash = models.CharField(max_length=255)
