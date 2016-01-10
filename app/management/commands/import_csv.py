from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_date
from django.contrib.auth.models import User
import csv

from app.models import UserProfile, Person


class Command(BaseCommand):
    help = ('Imports user data from CSV into the database and the graph')

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        filename = options['filename']

        self.stdout.write("Ready to import {}".format(filename))

        with open(filename, newline='') as csvfile:
            data = csv.reader(csvfile, delimiter=',')

            for row_index, row in enumerate(data, start=1):
                # format of a user data row:
                # username,password,dob,gender,interested_in,description,picture,email
                # * dob is in year-month-day format (e.g. 1991-01-21)
                # * gender is either M or F (see model for UserProfile)
                # * interested_in is either M, F or B
                # * description is a string (no comma allowed)
                # * picture is the URL of the user's profile picture
                # * email is an email address
                username, password, dob_raw, gender, interested_in, description, picture, email = row

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password)

                try:
                    dob = parse_date(dob_raw)
                except ValueError:
                    self.stderr.write("Invalid date value: {}".format(dob_raw))
                    self.stderr.write("Skipping row number {}".format(row_index))
                    continue

                if dob is None:
                    self.stderr.write("Invalid date format: {}".format(dob_raw))
                    self.stderr.write("Skipping row number {}".format(row_index))
                    continue

                user_profile = UserProfile.objects.create(
                    user=user,
                    dob=dob,
                    gender=gender,
                    interested_in=interested_in,
                    description=description,
                    profilePicture=picture)

                # the graph node is automatically created with the UserProfile
