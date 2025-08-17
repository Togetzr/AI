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
    'name': 'Resource Extend',
    'version': '17.0.1.0.1',
    'category': 'Extra Tools',
    'summary': """Resource Extend""",
    'description': """""",
    'author': 'Mayur Nagar <mayurnagar7069@gmail.com>',
    'website': "https://itieit.com",
    'company': 'ITIEIT',
    'maintainer': 'Mayur Nagar',
    'depends': ['resource_booking'],
    'data': [
        "security/ir.model.access.csv",
        "views/resource_booking_combination.xml",
        "views/resource_booking_combination_type.xml"
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
