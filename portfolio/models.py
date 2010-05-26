from django.db import models
from tagging.fields import TagField

STATUS = (
        ('0', 'Incomplete'),
        ('1', 'Rough Draft'),
        ('2', 'Edited'),
        ('3', 'Completed'),
        ('4', 'Abandoned')
        )

MEDIA = (
        ('0', 'Score'),
        ('1', 'Recording'),
        ('2', 'Writing'),
        ('3', 'Image'),
        ('4', 'Webdesign'),
        ('5', 'Software'),
        ('6', 'Mixed')
        )

class License(models.Model):
    slug = models.SlugField(unique = True)
    title = models.CharField(max_length = 120)
    description = models.CharField(max_length = 500)
    url = models.URLField(blank = True)
    display = models.CharField(max_length = 120)

    def __unicode__(self):
        return self.title

class MultiPart(models.Model):
    slug = models.SlugField(unique = True)
    title = models.CharField(max_length = 250)
    description = models.TextField()
    date = models.DateField()
    external_link = models.URLField(blank = True)
    status = models.CharField(max_length = 1, choices = STATUS)
    part_of_work = models.ForeignKey('MultiPart', blank = True, null = True)
    media = models.CharField(max_length = 1, choices = MEDIA)
    license = models.ForeignKey('License', blank = True, null = True)
    tags = TagField()

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.get_media_display())

    class Meta:
        ordering = ['media', 'title']

class Score(models.Model):
    slug = models.SlugField(unique = True)
    title = models.CharField(max_length = 250)
    description = models.TextField()
    instrumentation = models.CharField(max_length = 120)
    date = models.DateField()
    duration = models.DecimalField(max_digits = 5, decimal_places = 2)
    sib_file = models.FileField(blank = True, null = True, upload_to = 'sibData')
    pdf_file = models.FileField(blank = True, null = True, upload_to = 'pdfData')
    part_of_work = models.ForeignKey('MultiPart', blank = True, null = True)
    external_link = models.URLField(blank = True)
    status = models.CharField(max_length = 1, choices = STATUS)
    license = models.ForeignKey('License', blank = True, null = True)
    tags = TagField()

    def __unicode__(self):
        return "%s (Score)" % self.title

    class Meta:
        ordering = ['title']

class Recording(models.Model):
    slug = models.SlugField(unique = True)
    title = models.CharField(max_length = 250)
    source = models.CharField(max_length = 250, blank = True)
    performer = models.CharField(max_length = 250, blank = True)
    description = models.TextField()
    date = models.DateField()
    music_file = models.FileField(upload_to = 'mp3Data')
    duration = models.DecimalField(max_digits = 5, decimal_places = 2)
    score = models.ForeignKey('Score', blank = True, null = True)
    part_of_work = models.ForeignKey('MultiPart', blank = True, null = True)
    external_link = models.URLField(blank = True)
    status = models.CharField(max_length = 1, choices = STATUS)
    license = models.ForeignKey('License', blank = True, null = True)
    tags = TagField()

    def __unicode__(self):
        return "%s (Recording)" % self.title

    class Meta:
        ordering = ['title']

class Writing(models.Model):
    TYPE = (
            ('s', 'story'),
            ('c', 'chapter'),
            ('a', 'article'),
            ('l', 'letter')
            )
    slug = models.SlugField(unique = True)
    title = models.CharField(max_length = 250)
    type = models.CharField(max_length = 1, choices = TYPE)
    description = models.TextField()
    date = models.DateField()
    full_text = models.TextField()
    part_of_work = models.ForeignKey('MultiPart', blank = True, null = True)
    external_link = models.URLField(blank = True)
    status = models.CharField(max_length = 1, choices = STATUS)
    license = models.ForeignKey('License', blank = True, null = True)
    tags = TagField()

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']

class Image(models.Model):
    TYPE = (
            ('p', 'Photograph'),
            ('d', 'Graphic design')
            )
    slug = models.SlugField(unique = True)
    title = models.CharField(max_length = 250)
    description = models.TextField()
    date = models.DateField()
    image = models.ImageField(upload_to = 'imageData')
    thumb = models.ImageField(upload_to = 'imageData/thumbs', blank = True, null = True)
    type = models.CharField(max_length = 1, choices = TYPE)
    part_of_work = models.ForeignKey('MultiPart', blank = True, null = True)
    external_link = models.URLField(blank = True)
    status = models.CharField(max_length = 1, choices = STATUS)
    license = models.ForeignKey('License', blank = True, null = True)
    tags = TagField()

    def __unicode__(self):
        return '%s (Image)' % self.title

    class Meta:
        ordering = ['title']

class Website(models.Model):
    slug = models.SlugField(unique = True)
    title = models.CharField(max_length = 250)
    description = models.TextField()
    date = models.DateField()
    image = models.ImageField(upload_to = 'websiteData')
    part_of_work = models.ForeignKey('MultiPart', blank = True, null = True)
    external_link = models.URLField()
    status = models.CharField(max_length = 1, choices = STATUS)
    license = models.ForeignKey('License', blank = True, null = True)
    tags = TagField()

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']

class Program(models.Model):
    slug = models.SlugField(unique = True)
    title = models.CharField(max_length = 250)
    description = models.TextField()
    date = models.DateField()
    image = models.ImageField(upload_to = 'programData', blank = True, null = True)
    file = models.FileField(upload_to = 'programData', blank = True, null = True)
    part_of_work = models.ForeignKey('MultiPart', blank = True, null = True)
    external_link = models.URLField(blank = True)
    status = models.CharField(max_length = 1, choices = STATUS)
    license = models.ForeignKey('License', blank = True, null = True)
    tags = TagField()

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']
