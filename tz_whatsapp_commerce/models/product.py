from odoo import api, fields, models, _
from odoo.exceptions import UserError
import array as arr
import json
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    whatsapp_product_id = fields.Char(string="Whatsapp Product ID",company_dependent=True)
    batch_handle = fields.Char(string="Batch handle")
    def check_batch_api(self):
        response = self.env['whatsapp'].whatsapp_api_requests("GET",f"/{self.env.company.whatsapp_product_catalogue_id}/check_batch_request_status",company_id=self.env.company,params={'handle':self.whatsapp_product_id})
        
        raise UserError(str(response))
    
    def update_whatsapp_data(self):
        if not self.env.company.whatsapp_product_catalogue_id:  
            raise UserError(_("Your company do not have catalogue. Please configure it from company page."))

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        requests_obj = []
        requests_obj.append({
            "method": "UPDATE",
            "data":{
                "product_type":self.categ_id.name if self.categ_id else 'All',
                "image_link":f'{base_url}/web/whatsapp/image/product.template/{self.id}/image_1920',
                "title":self.name,
                "id":str(self.id),
                "price":"%s %s"%(str(self.list_price),self.env.company.currency_id.name),
                "description":self.name,
                "link":f"{base_url}/web#id={self.id}&model=product.template&view_type=form",
                "condition":"new",
                "availability":"in stock" if self.qty_available else "out of stock",
                "inventory":int(self.qty_available),
                "brand":self.default_code or '',
            }
        })
        
        params =json.dumps({
            "item_type": "PRODUCT_ITEM",
            'requests':requests_obj
        })

        response = self.env['whatsapp'].whatsapp_api_requests("POST",f"/{self.env.company.whatsapp_product_catalogue_id}/items_batch",company_id=self.env.company,data=params)
        _logger.info("---repsonse  %s"%response)
        self.batch_handle = response.get('handles')[0]
        
    def sync_whatsapp_data(self):
        if not self.env.company.whatsapp_product_catalogue_id:  
            raise UserError(_("Your company do not have catalogue. Please configure it from company page."))
        if self.whatsapp_product_id:
            raise UserError(_("Product is already exist"))
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        
        params = json.dumps({
                "product_type":self.categ_id.name if self.categ_id else 'All',
                "image_url":f'{base_url}/web/whatsapp/image/product.template/{self.id}/image_1920',
                "name":self.name,
                "price":str(int(self.list_price*100)),
                "retailer_id":str(self.id),
                "description":self.name,
                "url":f"{base_url}/web#id={self.id}&model=product.template&view_type=form",
                "condition":"new",
                "availability":"in stock" if self.qty_available else "out of stock",
                "inventory":str(int(self.qty_available)),
                "brand":self.default_code or '',
                "category":self.categ_id.name,
                'currency':self.env.company.currency_id.name
            })
        _logger.info("-=-params --%s"%params)
        response = self.env['whatsapp'].whatsapp_api_requests("POST",f"/{self.env.company.whatsapp_product_catalogue_id}/products",company_id=self.env.company,data=params)
        _logger.info("-=-repsonse --%s"%response)
        self.whatsapp_product_id = response.get('id')
