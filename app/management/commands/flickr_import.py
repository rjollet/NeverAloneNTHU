from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from app.models import Picture, Interest

from argparse import ArgumentTypeError
import flickrapi
from neomodel.exception import UniqueProperty


class Command(BaseCommand):
    help = ('Imports couple photos from Flickr, '
            'saves them in the graph with their related interests')

    MAX_IMPORTED_PHOTOS = 100
    SEARCH_TAG = 'couple,love'

    def check_max_import_arg(self, value):
        """raises ArgumentTypeError if the argument is not a positive number"""

        try:
            ivalue = int(value)
        except ValueError:
            raise ArgumentTypeError("invalid int value: '{}'".format(value))

        if ivalue < 1:
            raise ArgumentTypeError("should be more than 0: {}".format(ivalue))

        return ivalue

    def add_arguments(self, parser):

        parser.add_argument('flickr-api-key', type=str)
        parser.add_argument('flickr-secret', type=str)

        parser.add_argument('--max-import',
                            dest='max-import',
                            help='Change the maximum number of photos to import',
                            type=self.check_max_import_arg)

    def handle(self, *args, **options):
        flickr_api_key = options.get('flickr-api-key')
        flickr_secret = options.get('flickr-secret')

        max_imported = options.get('max-import')
        if type(max_imported) is not int:  # None if not present => use default value
            max_imported = self.MAX_IMPORTED_PHOTOS

        try:
            self.stdout.write("Ready to import".format(max_imported))

            photos = self.retrieve_photos_from_flickr(
                api_key=flickr_api_key,
                secret=flickr_secret,
                limit=max_imported)

            self.save_to_graph(photos)

            call_command('trim_graph', verbosity=3, interactive=False)
        except KeyboardInterrupt:
            self.stderr.write("\rCommand interrupted!")

    def retrieve_photos_from_flickr(self, api_key, secret,
                                    limit, preferred_size='Large Square'):
        """
        parameters
        ----------
        api_key: str - Flickr's api key
        secret: str - Flickr's secret
        limit: int - maximum number of photos to retrieve
        preferred_size: str - the photo size we want to get the URL to

        For a list of available photo sizes, see https://www.flickr.com/services/api/flickr.photos.getSizes.html (see 'label' attribute, e.g. 'Small 320').
        Default photo size: 'Square' (75x75).

        returns
        -------
        array of photos' tags (related interests) and URL

        Example:
        [
            {
                'tags': ['biking', 'sunset'],
                'url': 'http://farm2.staticflickr.com/1103/567229075_2cf8456f01_s.jpg',
            },

            ...
        ]
        """

        photos = []

        flickr = flickrapi.FlickrAPI(api_key=api_key, secret=secret)

        self.stdout.write("* Searching Flickr for photos (maximum {})".format(limit),
                          ending='\r')

        # Flickr API returns XML-structured results,
        # we will use Python's ElementTree library to access the real data

        index = 1
        for photo in flickr.walk(
                tags=self.SEARCH_TAG,
                tag_mode='all',
                license="2,3,4,6"):

            if index > limit:
                break

            photo_id = photo.get('id')

            photo_info = flickr.photos.getInfo(photo_id=photo_id)[0]  # [0]: getInfo always returns an array of 1 item

            photo_tags = [tag.attrib['raw'] for tag in photo_info.find('tags').findall('tag')]

            photo_sizes = flickr.photos.getSizes(photo_id=photo_id) \
                .find('sizes').findall('size')

            # search for the URL of the photo with the preferred size
            photo_urls = [size.attrib['source'] for size in photo_sizes
                          if size.attrib['label'] == preferred_size]

            # at this step, we only have 1 URL (1 size = 1 URL) or an empty array (the size was not found)
            if len(photo_urls) == 0:
                # the preferred size is not available, skip this photo
                continue

            photo_url = photo_urls[0]

            # white spaces are necessary to clear the previous line ('Searching Flickr for...')
            self.stdout.write('* Photos found: {}                         '.format(index), ending='\r')

            index += 1

            photos.append({
                'tags': photo_tags,
                'url': photo_url,
            })

        self.stdout.write('')  # prints newline

        return photos

    def save_to_graph(self, photos):
        """
        parameters
        ----------
        photos: array - see the return of retrieve_photos_from_flickr() for the structure
        """

        self.stdout.write("* Saving photos information in the graph", ending='\r')

        # list of tags from all photos without duplicates (several photos may have the same tag)
        # used to cache the Interest objects and create the nodes if they don't exist
        # while reducing the number of queries on the database
        interests = {}

        index = 1
        for photo in photos:
            url = photo['url']

            try:
                picture = Picture(pictureURL=url)
                picture.save()
            except UniqueProperty:
                # a picture node with this url already exists in the graph
                # we will only update the interests it is RELATED_TO
                picture = Picture.nodes.get(pictureURL=url)

            for tag in photo['tags']:
                if tag == self.SEARCH_TAG:
                    # we don't add the 'couple' tag to the database because of course our app is about couples
                    continue

                # if the tag hasn't been added yet to the list of interests
                if tag not in interests:
                    try:
                        interest = Interest(label=tag)
                        interest.save()
                    except UniqueProperty:
                        # an interest node with this label already exists in the graph
                        interest = Interest.nodes.get(label=tag)

                    interests[tag] = interest
                else:
                    # the interest is already in the list, get it and avoid a useless query to the db
                    interest = interests[tag]

                picture.tags.connect(interest)

            self.stdout.write('* Photos saved: {}                         '.format(index),
                              ending='\r')

            index += 1

        self.stdout.write('')
