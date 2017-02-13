from django.conf import settings
from django.db import models

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
        ('GooglePlus', 'Google +'),
        ('YouTube', 'YouTube'),
        ('Facebook', 'Facebook'),
        ('Twitter', 'Twitter'),
    )

    channel_id = models.CharField(max_length=254)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPE_CHOICES)
    official = models.ForeignKey('Official', related_name='channels')

    def __str__(self):
        return self.channel_id


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
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    location = models.TextField(blank=True)
    event_website = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    official = models.ForeignKey('Official', related_name='meetings')

    def __str__(self):
        return "{} on {}".format(self.official, self.date)


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
