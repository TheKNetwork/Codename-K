# -*- coding: utf-8 -*-
import uuid

from django.contrib.sites.models import RequestSite, Site
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.utils.translation import ugettext as _

from registration.backends.default import DefaultBackend
from registration.models import RegistrationProfile
from registration import signals

from forms import RegistrationForm
from models import UserProfile


def send_registration_email(user_email):
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import get_template
    from django.template import Context

    user = User.objects.get(email=user_email)
    reg_profile  = RegistrationProfile.objects.get(user=user)

    plaintext = get_template('registration/activation_email.txt')
    html = get_template('registration/activation_email.txt')
    domain = Site.objects.get_current().domain

    d = Context({"domain": domain, "activation_key": reg_profile.activation_key})

    subject = _('Registration successfully completed')
    from_email = settings.DEFAULT_FROM_EMAIL
    to = user_email
    text_content = plaintext.render(d)
    html_content = html.render(d)
    msg = EmailMultiAlternatives(subject, text_content, from_email, (to, ))
    msg.attach_alternative(html_content, "text/html")
    msg.send()


class RegistrationBackend(DefaultBackend):
    def get_form_class(self, request):
        return RegistrationForm

    def register(self, request, **kwargs):
        username = kwargs['username']
        password = str(uuid.uuid4())
        email = kwargs['email']
        _user = RegistrationProfile.objects.create_inactive_user(username, email, password, site=None)
        _user.save()
        try:
            profile = _user.get_profile()
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=_user)
        profile.save()
        send_registration_email(_user.email)
        return _user

    def activate(self, request, activation_key):
        activated = RegistrationProfile.objects.activate_user(activation_key)
        if activated:
            signals.user_activated.send(sender=self.__class__,
                                        user=activated,
                                        request=request)
        return activated