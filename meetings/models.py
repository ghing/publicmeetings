from datetime import datetime

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.text import slugify

import archieml

from .query import OfficialQuerySet


class Division(models.Model):
    """Political division"""
    # We could use this as the primary key, but OCD IDs have slashes in them
    # which would make using them in URLs weird
    ocd_id = models.CharField(
        max_length=254,
        help_text=("Open Civic Data division ID"),
        unique=True)
    name = models.CharField(
        max_length=254,
        help_text="Name of political division")

    class Meta:
        ordering = ['ocd_id']

    def __str__(self):
        return self.name


class Office(models.Model):
    """Political office"""
    division = models.ForeignKey(
        'Division',
        on_delete=models.CASCADE,
        related_name="offices")
    name = models.CharField(
            max_length=254,
        help_text="Name of office")
    # TODO: Add role, level based on
    # https://developers.google.com/civic-information/docs/v2/representatives#resource

    def __str__(self):
        return self.name


class Official(models.Model):
    """A person holding political office"""

    name = models.CharField(max_length=254)
    party = models.CharField(max_length=254)
    # We could model this, perhaps in a better way, with a range of dates,
    # but the Google Civic Information API, where we'll likely get a lot
    # of the data that will populate these models doesn't have the range
    # that a person is in an office.
    in_office = models.BooleanField(
        default=True,
        help_text="Is this person currently holding office")
    meeting_info_source = models.TextField(blank=True)
    office = models.ForeignKey(
        'Office',
        on_delete=models.CASCADE,
        related_name='officials'
    )

    objects = OfficialQuerySet.as_manager()

    def __str__(self):
        return self.name

    def next_meeting(self):
        return self.meetings.filter(date__gte=datetime.now().date()).order_by('date').first()

    def last_meeting(self):
        return self.meetings.filter(date__lt=datetime.now().date()).order_by('-date').first()

    @property
    def slug(self):
        return slugify(self.name)


class Address(models.Model):
    """Mailing address for an official"""

    line1 = models.CharField(max_length=254)
    line2 = models.CharField(max_length=254, blank=True)
    line3 = models.CharField(max_length=254, blank=True)
    location_name = models.CharField(max_length=254, blank=True)
    city = models.CharField(max_length=254)
    state = models.CharField(max_length=254)
    postal_code = models.CharField(max_length=254)
    official = models.ForeignKey('Official', related_name='addresses')

    def __str__(self):
        bits = [self.line1]
        if self.line2:
            bits.append(self.line2)

        if self.line3:
            bits.append(self.line3)

        bits.append("{}, {} {}".format(self.city, self.state, self.postal_code))
        return "\n".join(bits)


class SocialMediaChannel(models.Model):
    """Social media channel for an official"""

    CHANNEL_TYPE_CHOICES = (
        ('GooglePlus', 'Google+'),
        ('YouTube', 'YouTube'),
        ('Facebook', 'Facebook'),
        ('Twitter', 'Twitter'),
    )

    CHANNEL_TYPE_LOOKUP = {k: v for k, v in CHANNEL_TYPE_CHOICES}

    channel_id = models.CharField(max_length=254)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPE_CHOICES)
    official = models.ForeignKey('Official', related_name='channels')

    def __str__(self):
        return self.channel_id

    def get_url(self):
        url_templates = {
            'Facebook': "https://www.facebook.com/{channel_id}",
            'Twitter': "https://twitter.com/{channel_id}",
            'YouTube': "https://www.youtube.com/user/{channel_id}",
            'GooglePlus': "https://plus.google.com/u/0/+{channel_id}",
        }
        return url_templates[self.channel_type].format(**vars(self))

    def get_service_name(self):
        return self.CHANNEL_TYPE_LOOKUP[self.channel_type]


class Email(models.Model):
    """Email address for an official"""

    address = models.EmailField()
    official = models.ForeignKey('Official', related_name='emails')

    def __str__(self):
        return self.address


class Website(models.Model):
    """Website for an official"""
    url = models.URLField()
    official = models.ForeignKey('Official', related_name='urls')

    def __str__(self):
        return self.url


class Phone(models.Model):
    """Phone number for an official"""
    phone = models.CharField(max_length=20)
    official = models.ForeignKey('Official', related_name='phones')

    def __str__(self):
        return self.phone


class Meeting(models.Model):
    """Public meeting held by an official"""
    MEETING_TYPE_CHOICES = (
      ('in-person', "In-person"),
      ('telephone', "Telephone"),
      ('facebook', "Facebook"),
      ('radio', "Radio"),
    )

    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    location = models.TextField(blank=True)
    meeting_type = models.CharField(max_length=10,
        choices=MEETING_TYPE_CHOICES, blank=True, null=True)
    event_website = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    official = models.ForeignKey('Official', related_name='meetings')
    sources = GenericRelation('Source', related_query_name='meetings')

    def __str__(self):
        return "{} on {}".format(self.official, self.date)

    def fields_from_notes(self):
        normalized = {}
        parsed = archieml.loads(self.notes)
        for k, v in parsed.items():
            normalized[slugify(k).replace('-', '_')] = v

        return normalized


class ContactAttempt(models.Model):
    """Contact made with an elected official"""
    METHOD_CHOICES = (
        ('phone', "Phone"),
        ('email', "Email"),
    )

    datetime = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    contacted = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    official = models.ForeignKey('Official', related_name='contact_attempts')

    def __str__(self):
        return "{} on {} by {}".format(self.official, self.datetime, self.user)


class Source(models.Model):
    """Source for a piece of information in this system"""

    url = models.URLField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.url
