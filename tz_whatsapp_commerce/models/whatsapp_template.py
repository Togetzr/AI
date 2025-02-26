from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class Whatsapptemplate(models.Model):
    _inherit = 'whatsapp.template'
    
    order_confirmation_template = fields.Boolean(string="Order Confirmation Template")
    product_category_send = fields.Boolean(string="Send Product Category")
    testing_category_number = fields.Many2one('res.partner',string='Testing Number for test the product category')
    
    def send_category_to_number(self):
        response = self.env['whatsapp'].send_product_category_message(self.body,self.wa_account_id,self.testing_category_number)
        _logger.info("-=response=-%s"%response)
    
    def unlink(self):
        _logger.info('--rempakte-%s'%self.env.ref('tz_whatsapp_commerce.sale_order_send_confirmation_wa_message'))
        _logger.info('--self-%s'%self.ids)
        if self.env.ref('tz_whatsapp_commerce.sale_order_send_confirmation_wa_message').sudo().id in self.ids:
            raise UserError("You can not delete whatsapp sale order template")
        return super(Whatsapptemplate,self).unlink()
