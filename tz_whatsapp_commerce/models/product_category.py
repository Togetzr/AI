from odoo import api, fields, models, _
from odoo.exceptions import UserError
import array as arr
import json
import logging
_logger = logging.getLogger(__name__)

class Productcategory(models.Model):
    _inherit = 'product.category'
    
    wa_category_id = fields.Char(string="Whatsapp Category")
    
    def sync_whatsapp_data(self):
        if not self.env.company.whatsapp_catalogue_id:  
            raise UserError(_("Your company do not have catalogue. Please configure it from company page."))
        
        params = json.dumps({
            "categorization_criteria":["CATEGORY","BRAND","PRODUCT_TYPE"],
        })
        
        response = self.env['whatsapp'].whatsapp_api_requests("GET",f"/{self.env.company.whatsapp_catalogue_id}/categories",company_id=self.env.company,data=params)
        _logger.info("-=-responseresponseresponse %s"%response)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        requests_obj = [{"categorization_criteria":"CATEGORY",
                    "criteria_value":self.id,
                    "name":self.name}]
#        requests_obj.append({
#            "data":
#                [{"categorization_criteria":"CATEGORY",
#                    "criteria_value":self.id,
#                    "name":self.name}]
#            
#        })
        
        params =json.dumps({"data":requests_obj})

        response = self.env['whatsapp'].whatsapp_api_requests("POST",f"/{self.env.company.whatsapp_catalogue_id}/categories",company_id=self.env.company,data=params)
        _logger.info('=-=responseresponseresponse %s'%response)
