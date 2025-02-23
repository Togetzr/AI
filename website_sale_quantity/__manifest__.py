{
    'name': 'Website Sale Quantity',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Add increment and decrement buttons to specify the quantity in the product list view on the website.',
    'description': """
        This module adds + and - buttons next to the quantity input in the product list view on the website, allowing users to specify the quantity before adding items to the cart.
    """,
    'author': 'Togetzr',
    'website': 'http://www.yourcompany.com',
    'depends': ['website_sale'],
    'data': [
        'views/templates.xml',
    ],
    'assets': {
        'website.assets_frontend': [
            'website_sale_quantity/static/src/js/quantity_buttons.js',
            'website_sale_quantity/static/src/css/quantity_buttons.css',
        ],
    },
    'installable': True,
    'auto_install': False,
}