from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, ListView, CreateView
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import ProcessFormView

from .forms import (ContactAttemptForm, MeetingForm, OfficialMeetingInfoForm,
    SourceFormSet)
from .models import Meeting, Official


class MeetingCreateView(LoginRequiredMixin, CreateView):
    model = Meeting
    form_class = MeetingForm

    def get_initial(self):
        initial = super(MeetingCreateView, self).get_initial()
        initial.update(official=self._official)
        return initial

    def get(self, request, *args, **kwargs):
        self._official = Official.objects.get(pk=kwargs['pk'])
        self._user = request.user

        return super(MeetingCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._official = Official.objects.get(pk=kwargs['pk'])
        self._user = request.user

        form = self.get_form()
        source_form = SourceFormSet(self.request.POST)

        if form.is_valid() and source_form.is_valid():
            return self.form_valid(form, source_form)
        else:
            return self.form_invalid(form, source_form)

    def form_valid(self, form, source_form):
        self.object = form.save()
        source_form.instance = self.object
        source_form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, source_form):
        pass

    def get_context_data(self, **kwargs):
        context = super(MeetingCreateView, self).get_context_data(**kwargs)
        context['official'] = self._official
        context['source_form'] = SourceFormSet()

        return context

    def get_success_url(self):
        return reverse('official-detail', kwargs={
            'pk': self._official.pk,
            'slug': self._official.slug,
        })


class OfficialDetailView(LoginRequiredMixin, DetailView):
    model = Official
    context_object_name = 'official'


class OfficialListView(ListView):
    model = Official
    context_object_name = 'officials'

    def get_queryset(self):
        qs = Official.objects.all()

        without_meetings_since = self.request.GET.get('without_meetings_since')
        if without_meetings_since is not None:
            since_date = datetime.strptime(without_meetings_since, '%Y-%m-%d')
            qs = qs.without_meetings_since(since_date)

        return qs.order_by('office__division__name')


class MultipleFormsMixin(ContextMixin):
    """
    A mixin class that provides facilities for creating and displaying multiple
    forms in a single page.

    """

    initial = {}
    success_url = None
    # A mapping of prefix to form classes
    form_classes = {}

    def get_initial(self, prefix=None):
        """
        Returns the initial data to use for forms on this view.
        """
        return self.initial.copy()

    def get_form(self, form_class, prefix=None):
        """
        Returns an instance of the form to be used in this view.
        """
        return form_class(prefix=prefix, **self.get_form_kwargs(prefix))

    def get_form_kwargs(self, prefix=None):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {
            'initial': self.get_initial(prefix),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_success_url(self):
        """
        Returns the supplied success URL.
        """
        if self.success_url:
            # Forcing possible reverse_lazy evaluation
            url = force_text(self.success_url)
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")
        return url

    def get_context_data(self, **kwargs):
        """
        Insert the form into the context dict.
        """
        if 'forms' not in kwargs:
            kwargs['forms'] = self.get_forms()
        return super(MultipleFormsMixin, self).get_context_data(**kwargs)

    def get_form_classes(self):
        return self.form_classes

    def get_forms(self, form_classes):
        return {prefix: self.get_form(klass, prefix)
                for prefix, klass in form_classes.items()}

    def forms_valid(self, forms):
        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, forms):
        return self.render_to_response(self.get_context_data(forms=forms))


class ProcessMultipleFormsView(ProcessFormView):
    """
    A mixin that processes multiple forms on POST. Every form must be
    valid.
    """
    def get(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        return self.render_to_response(self.get_context_data(forms=forms))

    def post(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        if all([form.is_valid() for form in forms.values()]):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)


class BaseMultipleFormsView(MultipleFormsMixin, ProcessMultipleFormsView):
    """
    A base view for displaying several forms.
    """


class MultipleFormsView(TemplateResponseMixin, BaseMultipleFormsView):
    """
    A view for displaing several forms, and rendering a template response.
    """


class CallUsRepView(LoginRequiredMixin, MultipleFormsView):
    template_name = "meetings/call_us_rep.html"

    form_classes = {
        'next_meeting': MeetingForm,
        'last_meeting': MeetingForm,
        'contact_attempt': ContactAttemptForm,
        'meeting_info_source': OfficialMeetingInfoForm,
    }

    def get_success_url(self):
        return reverse('call-us-rep')

    def get_representative(self):
        return Official.objects.us_reps()\
            .without_meetings()\
            .without_contact_attempts()\
            .order_by('?')\
            .first()

    def get_initial(self, prefix=None):
        if prefix == 'contact_attempt':
            return {
                'official': self._representative,
                'user': self._user,
                'method': 'phone',
            }
        elif prefix in ('next_meeting', 'last_meeting'):
            return {
                'official': self._representative,
            }

    def get_context_data(self, **kwargs):
        context = super(CallUsRepView, self).get_context_data(**kwargs)
        context['representative'] = self._representative

        if self._representative is not None:
            context['contact_attempts'] = self._representative.contact_attempts.order_by('-datetime')

        else:
            context['contact_attempts'] = []

        return context

    def get(self, request, *args, **kwargs):
        self._representative = self.get_representative()
        self._user = request.user
        return super(CallUsRepView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._representative = self.get_representative()
        self._user = request.user

        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        if all([form.is_valid() for form in forms.values()]):
            forms['contact_attempt'].save()
            msg = _("You contacted {representative_name}.  Thanks! "
                    "You can contact another representative using "
                    "the form below.").format(
                representative_name=self._representative.name)
            messages.add_message(request, messages.SUCCESS, msg)

            if forms['next_meeting'].cleaned_data['date']:
                forms['next_meeting'].save()

            if forms['last_meeting'].cleaned_data['date']:
                forms['last_meeting'].save()

            forms['meeting_info_source'].save()

            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)

    def get_form_kwargs(self, prefix=None):
        kwargs = super(CallUsRepView, self).get_form_kwargs(prefix)

        if prefix == 'meeting_info_source':
            kwargs['instance'] = self._representative

        return kwargs
