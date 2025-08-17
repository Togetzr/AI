from odoo import api, fields, models, _
import base64
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    whatsapp_product_catalogue_id = fields.Char(string="Whatsapp Product Catalogue")
    whatsapp_catalogue_id = fields.Char(string="Whatsapp Commerce ID")
    whatsapp_commerce_catalogue_enable = fields.Boolean(string="Whatsapp Catalogue")
    whatsapp_commerce_cart_enable = fields.Boolean(string="Whatsapp Cart")
    
#    def get_anothertype_default_messages(self,auther_id,contact_exist=False):
#        if self.env.ref('tz_whatsapp_commerce.mpm_wa_message'):
#            self.env['whatsapp'].send_mpm_message(self.env.ref('tz_whatsapp_commerce.mpm_wa_message'),auther_id,self)
#            return True
#        return False
    
    def sync_catalogue_details(self):
        response = self.env['whatsapp'].whatsapp_api_requests("GET",f"/{self.wa_phonenumber_id}/whatsapp_commerce_settings?is_catalog_visible=false",company_id=self)
        _logger.info("--response--%s"%response)
        if response.get('data',[]):
            self.write({
                'whatsapp_catalogue_id':response.get('data')[0].get('id'),
                'whatsapp_commerce_catalogue_enable':response.get('data')[0].get('is_catalog_visible'),
                'whatsapp_commerce_cart_enable':response.get('data')[0].get('is_cart_enabled'),
            })
        else:
            raise UserError('No catalogue found')
        if not self.whatsapp_product_catalogue_id:
            data = {
                    "name": self.name + "Catalog",  # Name of the catalog
                }
            response = self.env['whatsapp'].whatsapp_api_requests("GET",f"/{self.waba_id}/product_catalogs",company_id=self)
            _logger.info("-catalogue-response--%s"%response)
            if response and response.get('data',[]):
                self.whatsapp_product_catalogue_id = response.get('data',[])[0].get('id')
    
    def switch_whatsapp_commerce_catalogue(self):
        if self.whatsapp_commerce_catalogue_enable:
            response = self.env['whatsapp'].whatsapp_api_requests("POST",f"/{self.wa_phonenumber_id}/whatsapp_commerce_settings?is_catalog_visible=false",company_id=self)
            self.whatsapp_commerce_catalogue_enable = False
        else:
            response = self.env['whatsapp'].whatsapp_api_requests("POST",f"/{self.wa_phonenumber_id}/whatsapp_commerce_settings?is_catalog_visible=true",company_id=self)
            self.whatsapp_commerce_catalogue_enable = True
        
    def switch_commerce_cart_enable(self):
        if self.whatsapp_commerce_cart_enable:
            response = self.env['whatsapp'].whatsapp_api_requests("POST",f"/{self.wa_phonenumber_id}/whatsapp_commerce_settings?is_cart_enabled=false",company_id=self)
            self.whatsapp_commerce_cart_enable = True
        else:
            response = self.env['whatsapp'].whatsapp_api_requests("POST",f"/{self.wa_phonenumber_id}/whatsapp_commerce_settings?is_cart_enabled=true",company_id=self)
            self.whatsapp_commerce_cart_enable = True
    
    def unsupported_type(self,message,auther_id,company_id):
        if message.get('type') == 'order':
            line_vals = [(0,0,{
                'product_id':int(line.get('product_retailer_id')),
                'product_uom_qty':line.get('quantity'),
                'price_unit':line.get('item_price'),
                'name':self.env['product.template'].browse(int(line.get('product_retailer_id'))).name
            }) for line in message.get('order').get('product_items')]
            vals = {
                'partner_id':auther_id.id,
                'order_line':line_vals,
                "whatsapp_commerce_id":message.get('id')
            }
            sale_order = self.env['sale.order'].with_company(company_id.id).create(vals)
#            whatsapp_template_id = self.env['whatsapp.template'].search([('wa_account_id','=',company_id.id),('order_confirmation_template','=',True)],limit=1)
#            if whatsapp_template_id:
#                composer_id = self.env['whatsapp.composer'].with_context(active_model='sale.order',wa_template_id=whatsapp_template_id.id,active_id=sale_order.id).create({})
#                composer_id.wa_template_id = whatsapp_template_id.id
#                response = composer_id._send_whatsapp_template()
            body = _("Hello %s,\n\n\
                We received your order. Your order no is %s amount of %s EUR.\n\n\
                For confirm the order please click https://test.itieit.com/hyperlink .\n\n\
                Thank You\n\n\
                ITieIt\n\n\
                itieit.com\
                ")%(sale_order.partner_id.name,sale_order.name,sale_order.amount_total)
#            self.env['whatsapp']._send(sale_order.partner_id,{'body':body},company_id)
            default_template = self.env.ref('tz_whatsapp_commerce.sale_order_send_paynow_confirmation_wa_message').sudo()
            self.env['whatsapp'].with_context(model='sale.order',res_id=sale_order.id).send_interactive_template_message(default_template,auther_id,company_id,"button",sale_order)
            
#            {"messaging_product":"whatsapp","contacts":[{"input":"917069282934","wa_id":"917069282934"}],"messages":[{"id":"wamid.HBgMOTE3MDY5MjgyOTM0FQIAERgSMjAyNUY4RDVDNjk1MDhDMDFGAA==","message_status":"accepted"}]}
#{'context': {'from': '33749181848', 'id': 'wamid.HBgMOTE3MDY5MjgyOTM0FQIAERgSMjAyNUY4RDVDNjk1MDhDMDFGAA=='}, 'from': '917069282934', 'id': 'wamid.HBgMOTE3MDY5MjgyOTM0FQIAEhggMUUyMjI4OUY0QUI1RTFFODMzOTNGNDg3RjM1RDdDQjcA', 'timestamp': '1713596191', 'type': 'button', 'button': {'payload': 'Confirm', 'text': 'Confirm'}}

            return False
            
        return super(ResCompany,self).unsupported_type(message,auther_id,company_id)
