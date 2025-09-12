from django.db import models
from cloudinary.models import CloudinaryField

class Artwork(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = CloudinaryField ('image', folder='artworks/')
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    art_id = models.CharField(max_length=100, unique=True)  # Unique identifier for the artwork

    def __str__(self):
        return self.title
