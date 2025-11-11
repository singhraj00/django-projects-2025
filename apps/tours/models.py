# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tour(models.Model):
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50, help_text="e.g. 5 Days / 4 Nights")
    image = models.ImageField(upload_to='tours/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="External image URL (used if no file uploaded)")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def display_image(self):
        """Return local image if available, otherwise fallback to image_url."""
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return "https://wallpapercave.com/wp/wp10611294.jpg"
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum([r.rating for r in reviews]) / reviews.count(), 1)
        return 0

class Review(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.tour}"
    
class ContactMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.email}"
