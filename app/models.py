from django.contrib.auth.models import AbstractUser
from django.db import models
from annoying.fields import AutoOneToOneField
from multiselectfield import MultiSelectField


SUBJECT_CHOICES = (
    ('Technology','Technology'),
    ('Humanities','Humanities'),
    ('Mathematics','Mathematics'),
    ('Arts','Arts'),
    ('Sports','Sports'),
    ('Curiosity','Curiosity'),
    ('Science','Science'),
    ('Self-improvement', 'Self-improvement'),
)


class User(AbstractUser):
    saved_posts = models.ManyToManyField('Post', blank=True)
    avatar = models.CharField(max_length=300)
    like_subjects = MultiSelectField(choices=SUBJECT_CHOICES, max_choices=7, max_length=23)
    bio = models.TextField()

#https://stackoverflow.com/questions/10602071/following-users-like-twitter-in-django-how-would-you-do-it
class UserProfile(models.Model):
    user = AutoOneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    follows = models.ManyToManyField('UserProfile', related_name='followed_by')

class Comment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500)

class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.PROTECT, related_name="post_poster")
    image = models.ImageField()
    title = models.CharField(max_length=200)
    subject = models.CharField(choices=SUBJECT_CHOICES, max_length=25)
    sub_subject = models.CharField(max_length=200, blank=True) 
    description = models.TextField()
    content = models.TextField()
    likes = models.PositiveIntegerField()
    comments = models.ManyToManyField(Comment, blank=True, related_name='comments')
    timestamp = models.DateField(auto_now_add=True)

    # def get_likes_len(self):
    #     return len(self.likes)

    # def get_comments_len(self):
    #     return len(self.comments)



