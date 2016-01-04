from django.core.management.base import BaseCommand, CommandError
from app.models import Picture, Interest

from neomodel import db


class Command(BaseCommand):
    help = ('Trims the graph in two times: '
            '\n* Delete all interests that have less than 2 pictures RELATED_TO them'
            '\n* Delete all pictures without any interest')

    def handle(self, *args, **options):
        try:
            self.stdout.write("Ready to trim")

            self.remove_weak_interests()
            self.remove_weak_pictures()

            self.stdout.write("Finished trimming")
        except KeyboardInterrupt:
            self.stderr.write("\rCommand interrupted!")

    def remove_weak_interests(self):
        """Removes all interests that have less than 2 pictures RELATED_TO them."""

        self.stdout.write("Removing all interests that have less than 2 pictures RELATED_TO them")

        query = "MATCH (i:Interest) OPTIONAL MATCH i<-[r:RELATED_TO]-(p:Picture) WITH i, COUNT(p) AS rel WHERE rel < 2 OR rel IS NULL DETACH DELETE i"

        results, meta = db.cypher_query(query)

    def remove_weak_pictures(self):
        """Removes all pictures that are not RELATED_TO any interest."""

        self.stdout.write("Removing all pictures that are not RELATED_TO any interest")

        query = "MATCH (p:Picture) OPTIONAL MATCH p--(i:Interest) WITH p, i WHERE i IS NULL DETACH DELETE p"

        results, meta = db.cypher_query(query)
