from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import uuid
# Create your models here.
class Profile(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    id_user=models.IntegerField()
    bio=models.CharField(max_length=5000, blank=True)
    location=models.CharField(max_length=30, blank=True)
    profileimg=models.ImageField( default='book-icon.png', upload_to='profile_pics')

    def __str__(self):
        return self.user.username
    
class Post(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    image=models.ImageField(upload_to='post_pics')
    text=models.TextField()
    created_at=models.DateTimeField(default=datetime.now)
    no_of_likes=models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class Likepost(models.Model):
    post_id=models.CharField(max_length=50)
    username=models.CharField(max_length=100)

    def __str__(self):
        return self.username
    
class Followers(models.Model):
    username=models.CharField(max_length=50)
    follower=models.CharField(max_length=50)

    def __str__(self):
        return self.username

class Comment(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    post_id=models.CharField(max_length=50)
    text=models.TextField()

    def __str__(self):
        return self.user.username
    