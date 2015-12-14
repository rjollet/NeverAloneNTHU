from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    MALE = 'M'
    FEMALE = 'F'

    HOMOSEXUAL =  1
    HETEROSEXUAL = 2
    
    GENDER = (
        (MALE, 'Man'),
        (FEMALE, 'Woman'),
    )
    
    SEXUALITY = (
        (HETEROSEXUAL, 'Heterosexual'),
        (HOMOSEXUAL, 'Homosexual'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER)
    sexuality =  models.IntegerField(choices=SEXUALITY)
