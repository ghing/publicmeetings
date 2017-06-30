from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import (Division, Office, Official, Email, Phone, Address,
        SocialMediaChannel, Website, ContactAttempt, Meeting, Source)


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


class SourceInline(GenericTabularInline):
    model = Source
    extra = 1


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    inlines = [SourceInline,]
    search_fields = ['official__name']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
            if db_field.name == "official":
                kwargs["queryset"] = Official.objects.order_by('name')

            return super(MeetingAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


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
