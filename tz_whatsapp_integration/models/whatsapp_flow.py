
from odoo import fields,api, models, _
import requests
import json
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval, test_python_expr
import tempfile, shutil
import binascii
import os
import uuid
from base64 import b64decode, b64encode
#from pywa import WhatsApp
#from pywa.types.flows import Screen,FlowJSON,FlowCategory, FlowStatus, FlowActionType,Layout, TextHeading,EmbeddedLink, Action,ActionNext,ActionNextType,ScreenData,TextInput,InputType,Form,Footer,TextSubheading,OptIn
#from pywa.errors import FlowUpdatingError
#from pywa.types import FlowButton
#from pywa import utils
import logging
_logger = logging.getLogger(__name__)
from urllib.parse import urlparse

class WHATSAPPFLOW(models.Model):
    _name = 'whatsapp.flow'
    _inherit = ['mail.thread']
    
    name = fields.Char(string="Name")
    categories = fields.Selection([("SIGN_UP","SIGN_UP"),
                                    ("SIGN_IN","SIGN_IN"),
                                    ("APPOINTMENT_BOOKING","APPOINTMENT_BOOKING"),
                                    ("LEAD_GENERATION","LEAD_GENERATION"),
                                    ("CONTACT_US","CONTACT_US"),
                                    ("CUSTOMER_SUPPORT","CUSTOMER_SUPPORT"),
                                    ("SURVEY","SURVEY"),
                                    ("OTHER","OTHER")],default="OTHER",string="Categories")
    whatsapp_flow_id = fields.Char(string="WhatsApp Flow Id")
    flow_file = fields.Binary(string="Flow File")
    flow_attachment = fields.Many2one('ir.attachment',string="Flow File")
    flow_action = fields.Selection([('navigate','Navigate'),('data_exchange','Data Exchange')],default='navigate',string="Flow Action")
    company_id = fields.Many2one('res.company',string="Company",required=True,default=lambda self:self.env.user.company_id)
    testing_category_number = fields.Many2one('res.partner',string='Testing Number for test the product category')
    model_id = fields.Many2one(comodel_name='ir.model', string='Applies to', ondelete='cascade', default=lambda self: self.env.ref('base.model_res_partner'),
                               help="Model on which the Server action for sending WhatsApp will be created.", required=True, tracking=True)
    model = fields.Char(
        string='Related Document Model', related='model_id.model',
        index=True, precompute=True, store=True, readonly=True)
    phone_field = fields.Char(
        string='Phone Field', 
        precompute=True, readonly=False, required=True, store=True)
    body = fields.Text(string="Template body", tracking=True)
    button_name = fields.Char(string="Button Name", tracking=True)
    screen_name = fields.Char(string="Screen Name", tracking=True)
    is_published = fields.Boolean()
    call_method_after_response = fields.Char(string='Call method after receive the response')
    reply_with_template = fields.Many2one('whatsapp.template',string="Reply with Template")
    reply_with_multiple_templates = fields.Many2many('whatsapp.template',string="Reply with Extra Templates")
    code = fields.Text(string="Python Code")
    endpoint_uri = fields.Char(string="Endpoint URI")
    send_summery = fields.Boolean(string="Send summary after finish flow",default=True)

    
    @api.constrains('code')
    def _check_python_code(self):
        for action in self.sudo().filtered('code'):
            msg = test_python_expr(expr=action.code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)
    
    def get_flow_message_data(self):
        random_uuid = uuid.uuid4()
        random_string = str(random_uuid)
        parameters = {
                        "flow_message_version": "3",
                        "flow_token": random_string,
                        "flow_id": self.whatsapp_flow_id,
                        "flow_cta": self.button_name,
                        "flow_action": self.flow_action,
                        "mode":"draft"
                  }
        if self.flow_action == 'navigate':
            parameters['flow_action_payload'] = {
                          "screen": self.screen_name,
                      }
        parameters['mode'] = 'published' if self.is_published else 'draft'
        data = {"body": {"text": self.body},
                "action":{
                    "name": "flow",
                      "parameters": parameters
                    }
                }
        return data,random_string
    
    def send_test_message(self):
        data,random_string = self.get_flow_message_data()
        self.env['whatsapp']._send_interactive(False,self,self.testing_category_number,data,self.company_id,"flow",message_unique_id=random_string)
    
    def send_flow_message(self,auther_id):
        data,random_string = self.get_flow_message_data()
        self.env['whatsapp'].with_context(model=self.model_id.model,)._send_interactive(False,self,auther_id,data,self.company_id,"flow",message_unique_id=random_string)
    
    def send_publish(self):
        if not self.whatsapp_flow_id:
            raise UserError("Please sync a flow with whatsapp first")
        self.is_published = True
        self._cr.commit()
        response = self.env['whatsapp'].whatsapp_api_requests("POST", f"/{self.whatsapp_flow_id}/publish",company_id=self.company_id)
    
    def send_flow_to_whatsapp(self):
        if not self.whatsapp_flow_id:
            files = {
                'name': self.name,
                'categories':str([self.categories]),
                "data_api_version": "3.0"
            }
            if self.endpoint_uri:
                files['endpoint_uri'] = self.endpoint_uri
#            elif self.company_id.webhook_verify_token :
            else:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                base_url = urlparse(base_url).netloc
                self.endpoint_uri = "https://%s/api/whatsapp-flow/data-exchange"%(base_url)
                files['endpoint_uri'] = self.endpoint_uri
#            else:
#                raise UserError(_("Endpoint URi is required. Please contact your administrator for it."))
#            files['endpoint_uri'] = self.endpoint_uri
            response = self.env['whatsapp'].whatsapp_api_requests("POST", f"/{self.env.company.waba_id}/flows",company_id=self.company_id, data=files)
            if response.get('id',False):
                self.whatsapp_flow_id = response.get('id')
                self._cr.commit()
            else:
                raise UserError(response)
        
        payload = {
                    'name': 'flow.json',
                    'asset_type': 'FLOW_JSON'
                }

        files = [
          ('file',('flow.json',self.flow_attachment.raw,'application/json'))
        ]

        response = self.env['whatsapp'].upload_flow_whatsapp(company_id=self.company_id, data=payload, files=files,whatsapp_flow_id=self.whatsapp_flow_id)
        raise UserError(str(response))
