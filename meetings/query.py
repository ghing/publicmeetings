from django.db import models


class OfficialQuerySet(models.QuerySet):
    def us_reps(self):
        """Get officials that are members of the United States House of Representatives"""
        return self.filter(
            office__division__ocd_id__regex=r'ocd-division/country:us/state:[a-z]{2}/cd:\d+')

    def without_meetings(self):
        return self.annotate(num_meetings=models.Count('meetings'))\
                   .filter(num_meetings=0)

    def without_meetings_since(self, date):
        """Get officials without a meeting since a given date"""

        return self.annotate(num_meetings=models.Count(
            models.Case(models.When(meetings__date__gte=date, then=1))))\
        .filter(num_meetings=0)

    def promotes_meetings_through_twitter(self):
        q = (models.Q(meeting_info_source__icontains="social media") |
             models.Q(meeting_info_source__icontains="twitter"))
        return self.filter(q)

    def without_contact_attempts(self):
        return self.annotate(num_contact_attempts=models.Count('contact_attempts'))\
            .filter(num_contact_attempts=0)

    def order_by_contact_attempts(self, desc=False):
        order_by = 'num_contact_attempts'
        if desc:
            order_by = '-' + order_by

        return self.annotate(num_contact_attempts=models.Count('contact_attempts'))\
           .order_by(order_by)
