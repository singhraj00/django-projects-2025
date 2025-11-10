# Create your models here.
from django.db import models

class Tour(models.Model):
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50, help_text="e.g. 5 Days / 4 Nights")
    image = models.ImageField(upload_to='tours/', blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
