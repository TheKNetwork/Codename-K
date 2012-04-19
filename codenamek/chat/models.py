
from django.db import models
from django.template.defaultfilters import slugify


class ChatRoom(models.Model):

    name = models.CharField(max_length=150)
    slug = models.SlugField(blank=True)

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ("room", ("/chat/%s" % self.slug,))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(ChatRoom, self).save(*args, **kwargs)

class ChatUser(models.Model):

    name = models.CharField(max_length=150)
    session = models.CharField(max_length=150)
    room = models.ForeignKey("chat.ChatRoom", related_name="users")

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        return self.name
