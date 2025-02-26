# -*- coding: utf-8 -*-
#############################################################################
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
    'name': 'Odoo Whatsapp Commerce',
    'version': '17.0.1.0.1',
    'category': 'Extra Tools',
    'summary': """Odoo Whatsapp Integration""",
    'description': """Added options for sending Whatsapp messages sale order, invoices, 
    website portal view and share the attachment of documents using share option available in each records through 
    Whatsapp""",
    'author': 'Mayur Nagar <mayurnagar7069@gmail.com>',
    'website': "https://itieit.com",
    'company': 'ITIEIT',
    'maintainer': 'Mayur Nagar',
    'depends': ['tz_whatsapp_integration','sale'],
    'data': [
        "data/whatsapp_data.xml",
        "views/product.xml",
        "views/whatsapp_template.xml",
        "views/product_category.xml",
        "views/res_company.xml",
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
