from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    whatsapp_commerce_id = fields.Char(string="Whatsapp Commerce Id")
