from django.db import models

class NewsItem(models.Model):
    ctime = models.DateTimeField(auto_now_add = True)
    mtime = models.DateTimeField(auto_now = True)
    title = models.CharField(max_length = 250)
    text = models.TextField()
    
    class Meta:
        ordering = ['-ctime']
