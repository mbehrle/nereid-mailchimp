# -*- coding: UTF-8 -*-
'''
    nereid_mailchimp.site

    MailChimp configuration fields in site

    :copyright: (c) 2010-2011 by Openlabs Technologies & Consulting (P) LTD
    :license: GPLv3, see LICENSE for more details
'''
from trytond.model import ModelView, ModelSQL, fields

class WebSite(ModelSQL, ModelView):
    """MailChimp config fields in website
    """
    _name = "nereid.website"
    
    mailchimp_api_key = fields.Char('MailChimp API Key')
    mailchimp_default_list = fields.Char('Default List Name')
    
WebSite()
