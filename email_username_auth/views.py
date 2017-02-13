from django.contrib.auth import authenticate
from django.shortcuts import render
from django.views.generic.edit import FormView

from nopassword.utils import get_user_model, get_username_field

from .forms import RegistrationForm


class RegistrationView(FormView):
    template_name = 'email_username_auth/registration_form.html'
    form_class = RegistrationForm

    def form_valid(self, form):
        new_user = self.register(form)
        self._send_login_code(getattr(new_user, get_username_field()))
        return render(self.request, 'registration/sent_mail.html')

    def form_invalid(self, form):
        if self._user_is_already_registered(form.errors.as_data()):
            self._send_login_code(form.data[get_username_field()])
            return render(self.request, 'registration/sent_mail.html')

        else:
            return super(RegistrationView, self).form_invalid(form)

    def _user_is_already_registered(self, errors):
        errors = errors.get(get_username_field())

        if errors is None:
            return False

        if len(errors) == 1 and errors[0].code == 'unique':
            return True

        return False

    def _send_login_code(self, username):
        code = authenticate(**{get_username_field(): username})
        code.next = self.request.GET.get('next')
        code.save()
        code.send_login_code(
            secure=self.request.is_secure(),
            host=self.request.get_host(),
        )

    def register(self, form):
        username = form.cleaned_data[get_username_field()]
        user_model = get_user_model()
        return user_model.objects.create_user(username)
