from datetime import datetime

from meetings.models import Official

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

        return prepped

    def _prepare_meetings(self, data):
        return [self._prepare_meeting(m) for m in data.meetings.order_by('date')]

    def _prepare_meeting(self, meeting):
        return {
            'id': meeting.id,
            'date': meeting.date,
            'time': meeting.time,
            'meeting_type': meeting.meeting_type,
            'location': meeting.location,
            'event_website': meeting.event_website,
        }

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
