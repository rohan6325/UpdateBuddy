from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, URLValidator
from django.core.exceptions import ValidationError




# Create your models here.
class update(models.Model):
    title = models.CharField(max_length=50)
    content =models.CharField(max_length=700)
    author = models.ForeignKey(User , on_delete=models.CASCADE)
    date = models.DateTimeField(default= timezone.now)
  
    def __str__(self) :
        return self.title
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk':self.pk})


from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, URLValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse

class Learnings(models.Model):
    SUBJECT_CHOICES = [
        ('DSA', 'DSA'),
        ('Web development', 'Web development'),
        ('App development', 'App development'),
        ('DBMS', 'DBMS'),
        ('android development', 'android development'),
        ('Data Science', 'Data Science'),
        ('OS', 'OS'),
        ('Networking', 'Networking'),
        ('Apptitude', 'Apptitude'),
    ]

    subject = models.CharField(default='select subject', max_length=50, choices=SUBJECT_CHOICES, null=False, blank=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    hours_learned = models.FloatField(validators=[MinValueValidator(0.5)])
    learning_detail = models.TextField(default="Enter learning details", null=False, blank=False)
    links = models.TextField(default="", null=False, blank=False)

    def clean(self):
        if self.date > timezone.now().date():
            raise ValidationError("The date cannot be in the future for completed learnings.")

    def save(self, *args, **kwargs):
        # Call the clean method to validate the date
        self.clean()
        
        # Validate the links
        url_validator = URLValidator()
        links_list = self.links.split(',')
        for link in links_list:
            link = link.strip()
            try:
                url_validator(link)
            except ValidationError:
                raise ValidationError(f"Invalid URL: {link}")
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('learning-detail', kwargs={'pk': self.pk})

class MyLearningList(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    learning = models.ForeignKey(Learnings, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user.username} - {self.learning.subject} - {self.status}"