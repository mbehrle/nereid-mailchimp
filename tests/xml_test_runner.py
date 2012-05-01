# -*- coding: utf-8 -*-
'''
    
    XML Test Runner for Nereid Integration with MailChimp
    
    :copyright: (c) 2011-2012 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details
    
'''
from nereid.contrib.testing import xmlrunner
from test_chimp import suite

if __name__ == '__main__':
    with open('result.xml', 'wb') as stream:
        xmlrunner.XMLTestRunner(stream).run(suite())
