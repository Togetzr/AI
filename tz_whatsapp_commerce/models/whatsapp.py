
from odoo import models, _
import requests
import json
from odoo.exceptions import UserError
from odoo.addons.tz_whatsapp_integration.models.whatsapp import DEFAULT_ENDPOINT
import logging
_logger = logging.getLogger(__name__)

class WHATSAPP(models.Model):
    _inherit = 'whatsapp'
    
    def send_mpm_message(self,template,partner,company_id):
        products = self.env['product.template'].search([('whatsapp_product_id','!=',False)])
        sections = []
        for category in products.mapped('categ_id'):
            sections.append({
                'title':category.name,
                'product_items':[{'product_retailer_id':str(x.id)} for x in products.filtered(lambda x:x.categ_id == category)]
            })
        product_details = {
                'thumbnail_product_retailer_id':str(products[0].id),
                'sections':sections
            }
        
    
        message_data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": partner.mobile or partner.phone,
            "type": "template",
            "template":{
                "name": template.template_name,
                "language": {
                  "code": template.lang_code
                },
                "components": [

#                  /* Header component required if template uses a header variable, otherwise omit */
#                  {
#                    "type": "header",
#                    "parameters": [
#                      {
#                        "type": "text",
#                        "text": template.header_text
#                      }
#                    ]
#                  },

#                  /* Body component required if template uses a body variable, otherwise omit */
#                  {
#                    "type": "body",
#                    "parameters": [
#                      {
#                        "type": "text",
#                        "text": template.body
#                      }
#                    ]
#                  },

#                  /* MPM button component always required */
                  {
                    "type": "button",
                    "sub_type": "mpm",
                    "index": 0,
                    "parameters": [
                      {
                        "type": "action",
                        "action": product_details
                      }
                    ]
                  }
                ]
              }
        }
        
        post_values = {
            'body': template.body,
            'message_type': 'comment'
        }
        
        channel = self.find_active_channel(partner,company_id)
        channel.message_post()
        
        post_values.update({
            'whatsapp_template_id':template.id  if template else False,
            'wa_flow_id':False,
            'formetted_number':partner.formetted_number
        })
        
#        if message_unique_id:post_values["message_unique_id"] = message_unique_id
        
        res_id = template.id if template else False
        model = template._name if template else False
        if 'model' in self._context:
            model = self._context.get('model')
        if 'res_id' in self._context:
            res_id = self._context.get('res_id')
        message = self.env['mail.message'].create(
            dict(post_values, res_id=res_id, model=model,
                 subtype_id=self.env['ir.model.data']._xmlid_to_res_id("mail.mt_note"))
        )
        _logger.info("=-=-message_data %s"%message_data)
        response = self.whatsapp_api_requests("POST", '/%s/messages'%(company_id.wa_phonenumber_id), data=json.dumps(message_data),company_id=company_id)
        _logger.info("=22-=-response %s"%response)
        if 'error' not in response:
            partner.formetted_number = response.get('contacts')[0].get('wa_id')
            message.msg_uid = response.get('messages')[0].get('id')
            
            return response
        else:
            raise UserError(response.json().get('error'))
        
        
        
#        return self._send_interactive(template,False,partner,data,company_id,"template")
#        {
#          "messaging_product": "whatsapp",
#          "recipient_type": "individual",
#          "to": "<TO>",
#          "type": "template",
#          "template": 
#        }
    
    def send_product_category_message(self,body,company,test_number):
        channel_partners = self.env['mail.channel.member'].sudo().search([('partner_id','=',test_number.id)])
        whatsapp_user = self.env['mail.channel.member'].sudo().search([('partner_id','=',company.whatsapp_user.id)])
        domain = [('channel_type','=','group'),('id','in',channel_partners.mapped('channel_id').ids),('channel_member_ids','in',channel_partners.ids),('channel_member_ids','in',whatsapp_user.ids)]
        channel = self.env['mail.channel'].search(domain,limit=1)
        if not channel:
            vals = {
                'channel_member_ids':[(0,0,{'partner_id': test_number.id}),(0,0,{'partner_id':company.whatsapp_user.id})],
                'channel_type':'group',
                'company_id':company.id,
                'name':"%s, %s"%(company.whatsapp_user.name,test_number.name)
            }
            channel = self.env['mail.channel'].sudo().create(vals)
        post_values = {
            'body': body,
            'message_type': 'comment'
        }
        channel.message_post(**post_values)
        whatsapp_data = self.get_whatsapp_data(company)
        categories = []
        for category in self.env['product.category'].search([]):
            categories.append({
                    "id":category.id,
                    "title": category.name,
                  } )
        data = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': test_number.mobile or test_number.phone,
            'type': 'interactive',
            'interactive': {
                      "type": "list",
                      "body": {
                        "text": body
                      },
                      "action": {
                        "button": "Menu",
                        "sections":[
                          {
                            "title":"Categories",
                            "rows": categories
                          }
                        ]
                      }
                    }
            }
        
        headers = {
                'Authorization': 'Bearer %s'%(whatsapp_data.get('access_token')),
                'Content-Type': 'application/json',
            }
        response = requests.post(DEFAULT_ENDPOINT+'/%s/messages'%(whatsapp_data.get('wa_phonenumber_id')), headers=headers, data=json.dumps(data))
        if 'error' not in response.json():
            test_number.formetted_number = response.json().get('contacts')[0].get('wa_id')
            
            return response
        else:
            raise UserError(str(response.json().get('error')))
