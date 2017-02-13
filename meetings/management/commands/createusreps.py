import argparse

from apiclient.discovery import build

from django.conf import settings
from django.core.management.base import BaseCommand

from meetings.models import (Division, Office, Official, Address,
    SocialMediaChannel, Email, Website, Phone)


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('ocd_id', nargs='*', type=str)
        parser.add_argument('--infile', type=argparse.FileType('r'))

    def _create_division(self, ocd_id, division):
        return Division.objects.get_or_create(ocd_id=ocd_id, defaults={
            'name': division['name']
        })

    def _create_office(self, office, division_model):
        return Office.objects.get_or_create(division=division_model,
            name=office['name'])

    def _create_official(self, official, office_model):
        official_model, created = Official.objects.get_or_create(
            name=official['name'],
            office=office_model,
            defaults={
              'party': official['party']
            })

        if created:
            for address in official['address']:
                Address.objects.create(
                    official=official_model,
                    line1=address['line1'],
                    line2=address.get('line2', ''),
                    line3=address.get('line3', ''),
                    city=address['city'],
                    state=address['state'],
                    postal_code=address['zip']
                )

            for channel in official['channels']:
                SocialMediaChannel.objects.create(
                    channel_id=channel['id'],
                    channel_type=channel['type'],
                    official=official_model
                )

            for number in official['phones']:
                Phone.objects.create(
                    phone=number,
                    official=official_model
                )

            for url in official['urls']:
                Website.objects.create(
                    url=url,
                    official=official_model
                )

            for email in official.get('emails', []):
                Email.objects.create(
                    address=email,
                    official=official_model
                )

        return official, created

    def handle(self, *args, **options):
        ocd_ids = []

        if options['infile']:
            for ocd_id in options['infile']:
                ocd_ids.append(ocd_id.strip())

        else:
            ocd_ids = options['ocd_id']

        service = build('civicinfo', 'v2', developerKey=settings.GOOGLE_API_KEY)
        resource = service.representatives()

        for ocd_id in ocd_ids:
            request = resource.representativeInfoByDivision(
                ocdId=ocd_id,
                roles='legislatorLowerBody')
            response = request.execute()

            division = response['divisions'][ocd_id]
            office_index = response['divisions'][ocd_id]['officeIndices'][0]
            office = response['offices'][office_index]
            official_index = office['officialIndices'][0]
            official = response['officials'][official_index]

            division_model, created = self._create_division(ocd_id, division)
            office_model, created = self._create_office(office, division_model)
            official_model, created = self._create_official(official,
                office_model)
