# -*- coding: UTF-8 -*-
'''
    nereid_mailchimp.party

    :copyright: (c) 2010-2011 by Openlabs Technologies & Consulting (P) LTD
    :license: GPLv3, see LICENSE for more details
'''
import json
from wtforms import Form, TextField, IntegerField, SelectField, validators, \
    PasswordField, BooleanField
from werkzeug.wrappers import BaseResponse
from nereid.globals import current_app
from nereid import request
from trytond.model import ModelView, ModelSQL, fields
from trytond.config import CONFIG

from .chimp import list_subscribe

class RegistrationForm(Form):
    "Simple Registration form"
    name = TextField('Name', [validators.Required(),])
    company = TextField('Company', [validators.Required(),])
    street = TextField('Street', [validators.Required(),])
    streetbis = TextField('Street (Bis)')
    zip = TextField('Post Code', [validators.Required(),])
    city = TextField('City', [validators.Required(),])
    country = SelectField('Country', [validators.Required(),], coerce=int)
    subdivision = IntegerField('State/Country', [validators.Required()])
    email = TextField('e-mail', [validators.Required(), validators.Email()])
    if 're_captcha_public' in CONFIG.options:
        captcha = RecaptchaField(
            public_key=CONFIG.options['re_captcha_public'], 
            private_key=CONFIG.options['re_captcha_private'], secure=True)
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    newsletter = BooleanField('Subscribe to Newsletter', default=True)
    
    
class Address(ModelSQL, ModelView):
    """Extending address to include newsletter subscription info
    """
    _name = 'party.address'
    
    registration_form = RegistrationForm
    
    def registration(self):
        """This method will super the registration method in nereid
        and will call list_subscribe methom from chimp.py if successful 
        submission of registration form takes place.
        """
        response = super(Address, self).registration()
        if isinstance(response, BaseResponse) and response.status_code == 302:
            result = list_subscribe()
            current_app.logger.debug(json.loads(result.data))
        return response
            
Address()            
