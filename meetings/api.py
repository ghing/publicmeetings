from datetime import datetime

from meetings.models import Official

from restless.constants import OK
from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer

class OfficialResource(DjangoResource):
    preparer = FieldsPreparer(fields={
        'id': 'id',
        'name': 'name',
        'party': 'party',
        'in_office': 'in_office',
        'meeting_info_source': 'meeting_info_source',
    })

    def build_response(self, data, status=OK):
        resp = super(OfficialResource, self).build_response(data, status)
        resp['Access-Control-Allow-Origin'] = '*'
        return resp

    def list(self):
        qs = Official.objects.all()

        without_meeting_since = self.request.GET.get('without_meeting_since')
        if without_meeting_since is not None:
            since_date = datetime.strptime(without_meeting_since,
                '%Y-%m-%d').date()
            qs = qs.without_meetings_since(since_date)

        through_twitter = self.request.GET.get('through_twitter')
        if through_twitter is not None:
            qs = qs.promotes_meetings_through_twitter()

        return qs

    def prepare(self, data):
        prepped = super(OfficialResource, self).prepare(data)
        prepped['meetings'] = self._prepare_meetings(data)
        prepped['social_media'] = self._prepare_social_media(data)
        prepped['office'] = self._prepare_office(data)

        extra_fields = set(['phones', 'emails'])
        include_fields = self.request.GET.getlist('include_field')
        for fieldname in include_fields:
            if fieldname in extra_fields:
                preparer = getattr(self, '_prepare_{0}'.format(fieldname))
                prepped[fieldname] = preparer(data)

        return prepped

    def _prepare_meetings(self, data):
        return [self._prepare_meeting(m) for m in data.meetings.order_by('date')]

    def _prepare_meeting(self, meeting):
        prepared = {
            'id': meeting.id,
            'date': meeting.date,
            'time': meeting.time,
            'meeting_type': meeting.meeting_type,
            'location': meeting.location,
            'event_website': meeting.event_website,
            'sources': [s.url for s in meeting.sources.all()],
        }

        return prepared

    def _prepare_social_media(self, data):
        return [self._prepare_social_media_channel(c)
                for c in data.channels.all()]

    def _prepare_social_media_channel(self, channel):
        return {
            'channel_id': channel.channel_id,
            'channel_type': channel.channel_type,
        }

    def _prepare_office(self, data):
        return {
            'name': data.office.name,
            'division': self._prepare_division(data.office.division),
        }

    def _prepare_division(self, division):
        return {
            'ocd_id': division.ocd_id,
            'name': division.name,
        }

    def _prepare_phones(self, data):
        return [self._prepare_phone(p) for p in data.phones.all()]

    def _prepare_phone(self, data):
        return data.phone

    def _prepare_emails(self, data):
        return [self._prepare_email(e) for e in data.emails.all()]

    def _prepare_email(self, data):
        return data.address
