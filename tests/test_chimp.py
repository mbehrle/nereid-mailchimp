# -*- coding: utf-8 -*-
"""
    nereid_mailchimp.test

    Test the mailchimp plugin for nereid

    :copyright: (c) 2010-2011 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details.
"""
import json
from ast import literal_eval
from decimal import Decimal
import unittest2 as unittest

from trytond.config import CONFIG
CONFIG.options['db_type'] = 'sqlite'
CONFIG.options['data_path'] = '/home/shalabh'
CONFIG['smtp_server'] = 'smtp.gmail.com'
CONFIG['smtp_user'] = 'test@xyz.com'
CONFIG['smtp_password'] = 'testpassword'
CONFIG['smtp_port'] = 587
CONFIG['smtp_tls'] = True
from trytond.modules import register_classes
register_classes()

from nereid.testing import testing_proxy
from trytond.transaction import Transaction

GUEST_EMAIL = 'guest@example.com'
NEW_USER = 'new@example.com'
NEW_PASS = 'password'
NEW_USER2 = 'test@openlabs.co.in'
NEW_PASS2 = 'testpassword'

class TestNereidMailChimp(unittest.TestCase):
    'Test case for nereid mailchimp'

    @classmethod
    def setUpClass(cls):
        # Install module
        testing_proxy.install_module('nereid_chimp')

        country_obj = testing_proxy.pool.get('country.country')
        address_obj = testing_proxy.pool.get('party.address')

        with Transaction().start(testing_proxy.db_name, 1, None) as txn:
            # Create company
            company = testing_proxy.create_company('Test Company')
            testing_proxy.set_company_for_user(1, company)

            cls.guest_user = testing_proxy.create_guest_user(email=GUEST_EMAIL)
            
            cls.regd_user_id = testing_proxy.create_user_party('Registered User', 
                'email@example.com', 'password')

            cls.available_countries = country_obj.search([], limit=5)
            cls.site = testing_proxy.create_site('testsite.com', 
                countries = [('set', cls.available_countries)])

            testing_proxy.create_template('home.jinja', ' Home ', cls.site)
            testing_proxy.create_template(
                'login.jinja', 
                '{{ login_form.errors }} {{get_flashed_messages()}}', cls.site)
            testing_proxy.create_template(
                'registration.jinja', 
                '{{ form.errors }} {{get_flashed_messages()}}', cls.site)
            
            testing_proxy.create_template(
                'reset-password.jinja', '', cls.site)
            testing_proxy.create_template(
                'change-password.jinja',
                '{{ change_password_form.errors }}', cls.site)
            testing_proxy.create_template(
                'address-edit.jinja',
                '{{ form.errors }}', cls.site)
            testing_proxy.create_template(
                'address.jinja', '', cls.site)
            testing_proxy.create_template(
                'account.jinja', '', cls.site)

            txn.cursor.commit()

    def get_app(self, **options):
        options.update({
            'SITE': 'testsite.com',
            'GUEST_USER': self.guest_user,
            })
        return testing_proxy.make_app(**options)
        
    def setUp(self):
        self.address_obj = testing_proxy.pool.get('party.address')
        self.country_obj = testing_proxy.pool.get('country.country')
        self.subdivision_obj = testing_proxy.pool.get('country.subdivision')
        self.website_obj = testing_proxy.pool.get('nereid.website')
        self.contact_mech_obj = testing_proxy.pool.get('party.contact_mechanism')
        
    def test_0010_registration_form(self):
        "Successful rendering of an empty registration page"
        app = self.get_app()
        with app.test_client() as c:
            response = c.get('/registration')
            self.assertEqual(response.status_code, 200)

    def test_0020_registration_no_chimp_api(self):
        """No API for mailchimp configured. Should throw an error."""
        with Transaction().start(testing_proxy.db_name, testing_proxy.user, None):
            website_id = self.website_obj.search([])[0]
            website = self.website_obj.browse(website_id)
            country = website.countries[0]
            subdivision = country.subdivisions[0]
            
        app = self.get_app()
        with app.test_client() as c:
            registration_data = {
                'name': 'New Test user',
                'company': 'Test Company',
                'street': 'New Street',
                'email': NEW_USER,
                'password': NEW_PASS,
                'zip': 'ABC123',
                'city': 'Test City',
                'country': country.id,
                'subdivision': subdivision.id,
                'confirm': NEW_PASS,
            }

            response = c.post('/registration', data=registration_data)
            self.assertEqual(response.status_code, 302)

    def test_0030_registration_w_chimp_api(self):
        """API for mailchimp configured."""
        with Transaction().start(testing_proxy.db_name, testing_proxy.user, None) as txn:
            website_id, = self.website_obj.search([])
            website = self.website_obj.browse(website_id)
            country = website.countries[0]
            subdivision = country.subdivisions[0]
            self.website_obj.write(website_id, {
                'mailchimp_api_key': '4419cf2a4f09df800adf03ee9c4bd6d0-us2',
                'mailchimp_default_list': 'openlabs List',
                })

            txn.cursor.commit()
            
        app = self.get_app()
        with app.test_client() as c:
            registration_data = {
                'name': 'New Test user',
                'company': 'Test Company',
                'street': 'New Street',
                'email': NEW_USER2,
                'password': NEW_PASS2,
                'zip': 'ABC123',
                'city': 'Test City',
                'country': country.id,
                'subdivision': subdivision.id,
                'confirm': NEW_PASS2,
            }

            response = c.post('/registration', data=registration_data)
            self.assertEqual(response.status_code, 302)

def suite():
    "Nereid Mailchimp test suite"
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestNereidMailChimp)
        )
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
