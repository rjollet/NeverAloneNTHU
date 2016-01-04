from django.db import models
from django.contrib.auth.models import User
from neomodel import StructuredNode, StringProperty, RelationshipTo, RelationshipFrom


class UserProfile(models.Model):
    MALE = 'M'
    FEMALE = 'F'

    INTERESTED_IN_MEN = 1
    INTERESTED_IN_WOMEN = 2
    INTERESTED_IN_BOTH = 3

    GENDER = (
        (MALE, 'Man'),
        (FEMALE, 'Woman'),
    )

    INTERESTED_IN = (
        (INTERESTED_IN_MEN, 'Men'),
        (INTERESTED_IN_WOMEN, 'Women'),
        (INTERESTED_IN_BOTH, 'Both'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER)
    interested_in = models.IntegerField(choices=INTERESTED_IN)


class Interest(StructuredNode):
    label = StringProperty(unique_index=True, required=True)

    # RelationshipFrom/To enforces the direction of edges:
    # a picture is RELATED_TO a interest, not the other way around
    pictures = RelationshipFrom('Picture', 'RELATED_TO')


class Picture(StructuredNode):
    pictureURL = StringProperty(unique_index=True, required=True)

    tags = RelationshipTo('Interest', 'RELATED_TO')
