# -*- coding: UTF-8 -*-
'''
    nereid_mailchimp.party

    :copyright: (c) 2010-2012 by Openlabs Technologies & Consulting (P) LTD
    :license: GPLv3, see LICENSE for more details
'''
import json

from wtforms import Form, TextField, validators, PasswordField, BooleanField,\
    HiddenField
from wtfrecaptcha.fields import RecaptchaField
from werkzeug.wrappers import BaseResponse
from nereid.globals import current_app
from nereid import request, redirect, url_for, flash
from trytond.model import ModelView, ModelSQL
from trytond.config import CONFIG

from .chimp import list_subscribe
from .i18n import _, get_translations


class RegistrationForm(Form):
    "Simple Registration form"

    def _get_translations(self):
        """
        Provide alternate translations factory.
        """
        return get_translations()

    name = TextField(_('Name'), [validators.Required(),])
    email = TextField(_('e-mail'), [validators.Required(), validators.Email()])
    password = PasswordField(_('New Password'), [
        validators.Required(),
        validators.EqualTo('confirm', message=_('Passwords must match'))])
    confirm = PasswordField(_('Confirm Password'))

    if 're_captcha_public' in CONFIG.options:
        captcha = RecaptchaField(
            public_key=CONFIG.options['re_captcha_public'],
            private_key=CONFIG.options['re_captcha_private'],
            secure=True
        )
    newsletter = BooleanField(_('Subscribe to Newsletter'), default=False)


class NewsletterForm(Form):
    "New Newsletter Subscription form"
    name = TextField(_('Name'), [validators.Required(),])
    email = TextField(_('Email ID'), [validators.Required(),])
    next = HiddenField('Next')


class NereidUser(ModelSQL, ModelView):
    """Extending user to include newsletter subscription info
    """
    _name = 'nereid.user'

    registration_form = RegistrationForm

    def registration(self):
        """This method will super the registration method in nereid
        and will call list_subscribe methom from chimp.py if successful 
        submission of registration form takes place.
        """
        response = super(NereidUser, self).registration()
        if request.method == 'POST' and \
            request.values.get('newsletter', False) == 'True':
            if isinstance(response, BaseResponse) and \
                    response.status_code == 302:
                result = list_subscribe()
                if result:
                    current_app.logger.debug(json.loads(result.data))
        return response

    def list_subscribe(self):
        """A helper method which just proxies list_subscribe so that
        this could be accessed by a pool lookup.
        """
        return list_subscribe()

    def subscribe_newsletter(self):
        """This method will allow the user to subscribe to a newsletter
        just by filling up email and name(mandatory for guest user)
        """
        form = NewsletterForm(request.form)
        if form.validate():
            result = json.loads(list_subscribe().data)
            if not result['success']:
                current_app.logger.error(result)
                flash(_('We could not subscribe you into the newsletter.'
                    ' Try again later'))
            else:
                flash(
                    _('You have been successfully subscribed to newsletters.')
                )
        return redirect(
            request.values.get('next', url_for('nereid.website.home'))
        )

NereidUser()
