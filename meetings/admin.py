from django.contrib import admin

from .models import (Division, Office, Official, Email, Phone, Address,
        SocialMediaChannel, Website, ContactAttempt, Meeting)


admin.site.register(Division)
admin.site.register(Office)


class EmailInline(admin.TabularInline):
    model = Email
    extra = 0


class PhoneInline(admin.TabularInline):
    model = Phone
    extra = 0


class AddressInline(admin.StackedInline):
    model = Address
    extra = 0


class SocialMediaChannelInline(admin.TabularInline):
    model = SocialMediaChannel
    extra = 0


class WebsiteInline(admin.TabularInline):
    model = Website
    extra = 0


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    search_fields = ['official__name']


@admin.register(Official)
class OfficialAdmin(admin.ModelAdmin):
    inlines = [
        PhoneInline,
        EmailInline,
        AddressInline,
        SocialMediaChannelInline,
        WebsiteInline,
    ]


@admin.register(ContactAttempt)
class ContactAttemptAdmin(admin.ModelAdmin):
    readonly_fields = ('datetime',)
