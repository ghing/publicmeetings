from django.test import TestCase

from meetings.models import Division, Office, Official, SocialMediaChannel

class SocialMediaChannelTestCase(TestCase):
    def setUp(self):
        division = Division.objects.create(
            ocd_id="ocd-division/country:us/state:ky/cd:5",
            name="Kentucky's 5th congressional district",
        )
        office = Office.objects.create(
            name="United States House of Representatives KY-05",
            division=division,
        )
        self.official = Official.objects.create(
            name="Harold Rogers",
            office=office)

    def test_get_url_facebook(self):
        channel = SocialMediaChannel(
            official=self.official,
            channel_type="Facebook",
            channel_id="CongressmanHalRogers",
        )
        self.assertEqual(channel.get_url(),
            "https://www.facebook.com/CongressmanHalRogers")

    def test_get_url_twitter(self):
        channel = SocialMediaChannel(
            official=self.official,
            channel_type="Twitter",
            channel_id="RepHalRogers",
        )
        self.assertEqual(channel.get_url(),
            "https://twitter.com/RepHalRogers")

    def test_get_url_youtube(self):
        channel = SocialMediaChannel(
            official=self.official,
            channel_type="YouTube",
            channel_id="RepHalRogers",
        )
        self.assertEqual(channel.get_url(),
            "https://www.youtube.com/user/RepHalRogers")


    def test_get_url_google_plus(self):
        channel = SocialMediaChannel(
            official=self.official,
            channel_type="GooglePlus",
            channel_id="RepHalRogers",
        )
        self.assertEqual(channel.get_url(),
            "https://plus.google.com/u/0/+RepHalRogers")

    def test_get_service_name_facebook(self):
        channel = SocialMediaChannel(
            official=self.official,
            channel_type="Facebook",
            channel_id="CongressmanHalRogers",
        )
        self.assertEqual(channel.get_service_name(),
            "Facebook")

    def test_get_service_name_twitter(self):
        channel = SocialMediaChannel(
            official=self.official,
            channel_type="Twitter",
            channel_id="RepHalRogers",
        )
        self.assertEqual(channel.get_service_name(),
            "Twitter")

    def test_get_service_name_youtube(self):
        channel = SocialMediaChannel(
            official=self.official,
            channel_type="YouTube",
            channel_id="RepHalRogers",
        )
        self.assertEqual(channel.get_service_name(),
            "YouTube")

    def test_get_service_name_google_plus(self):
        channel = SocialMediaChannel(
            official=self.official,
            channel_type="GooglePlus",
            channel_id="RepHalRogers",
        )
        self.assertEqual(channel.get_service_name(),
            "Google+")
