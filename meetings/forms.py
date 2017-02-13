from django import forms

from .models import ContactAttempt, Meeting, Official

# Use Bootstrap's class
DEFAULT_FORM_WIDGET_CLASS = 'form-control'

class MeetingForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': DEFAULT_FORM_WIDGET_CLASS,
        }),
        required=False
    )

    class Meta:
        model = Meeting
        # Use HTML5 input types to get widgets and do some client-side
        # validation
        fields = ['official', 'date', 'time', 'location', 'event_website', 'notes']
        widgets = {
            'official': forms.HiddenInput(),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': DEFAULT_FORM_WIDGET_CLASS,
            }),
            'location': forms.Textarea(attrs={
                'class': DEFAULT_FORM_WIDGET_CLASS,
            }),
            'event_website': forms.URLInput(attrs={
                'class': DEFAULT_FORM_WIDGET_CLASS,
            }),
            'notes': forms.Textarea(attrs={
                'class': DEFAULT_FORM_WIDGET_CLASS,
            })
        }


class ContactAttemptForm(forms.ModelForm):
    class Meta:
        model = ContactAttempt
        fields = ['user', 'official', 'contacted', 'notes', 'method']
        widgets = {
            'user': forms.HiddenInput(),
            'official': forms.HiddenInput(),
            'contacted': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'notes': forms.Textarea(attrs={
                'class': DEFAULT_FORM_WIDGET_CLASS,
                'placeholder': "Put any notes from your call or e-mail with the representative here",
            }),
            'method': forms.HiddenInput()
        }


class OfficialMeetingInfoForm(forms.ModelForm):
    class Meta:
        model = Official
        fields = ['id', 'meeting_info_source']
        widgets = {
            'id': forms.HiddenInput(),
            'meeting_info_source': forms.Textarea(attrs={
                'class': DEFAULT_FORM_WIDGET_CLASS,
            }),
        }
