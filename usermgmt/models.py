from django.db import models
from django.contrib.auth.models import User
from tagging.fields import TagField

class Profile(models.Model):
    user = models.ForeignKey(User)
    location = models.CharField(max_length = 250, blank = True)
    about = models.TextField(blank = True)
    interests = TagField()

    def __unicode__(self):
        return "%s's profile" % self.user.username
