from odoo import fields,api, models, _
import base64
import logging
from odoo.tools import file_open
from urllib.parse import urlparse
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class Flows(models.Model):
    _inherit = 'whatsapp.flow'
    
    is_resourse_flow = fields.Boolean(string="Is Resourse Flow")
    flow_type = fields.Selection([('normal_booking','Normal Booking'),('normal_booking_gender','Normal Booking With Gender'),('adv_booking','Advance Booking'),('adv_booking_gender','Advance Booking With Gender'),('modifier','Modify Appointment')],string="Flow Type")
    
    def create_attachements_for_flow(self):
        flow_ids = {'normal_flow':'hair_dresser',
                    'normal_flow_with_gender':'hair_dresser_gender',
                    'advance_flow':'hair_dresser_advance',
                    'advance_flow_with_gender':'hair_dresser_advance_gender',
                    'modifier_flow':'appointment_modifier'
                    }
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url = urlparse(base_url).netloc
        for flow in flow_ids:
            
            flow_id = self.env.ref('tz_whatsapp_resourse_flow.%s'%flow)
            vals = {
                'name':flow,
                'type':'binary',
                'mimetype':'application/json'
            }
            with file_open('tz_whatsapp_resourse_flow/models/%s.json'%(flow_ids.get(flow)), 'rb') as file:
                vals['datas'] = base64.b64encode(file.read())
            attachement_obj = self.env['ir.attachment'].create(vals)
            flow_id.flow_attachment = attachement_obj.id
#            if flow_id.company_id.data_uri_domain and flow_id.company_id.webhook_verify_token and base_url:
#                flow_id.endpoint_uri = "https://%s/api/data?wa_token=%s&default_url=%s"%(flow_id.company_id.data_uri_domain,flow_id.company_id.webhook_verify_token,base_url)

    def sync_to_whatsapp_default(self):
        if not self.whatsapp_flow_id:
            files = {
                'name': self.name,
                'categories':str([self.categories]),
                "data_api_version": "3.0"
            }
            if self.endpoint_uri:
                files['endpoint_uri'] = self.endpoint_uri
            else:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                base_url = urlparse(base_url).netloc
                self.endpoint_uri = "https://%s/api/whatsapp-flow/data-exchange"%(base_url)
                files['endpoint_uri'] = self.endpoint_uri
#            else:
#                raise UserError(_("Endpoint URi Is required. Please contact your administrator for it."))
            response = self.env['whatsapp'].whatsapp_api_requests("POST", f"/{self.env.company.waba_id}/flows",company_id=self.company_id, data=files)
            if response.get('id',False):
                self.whatsapp_flow_id = response.get('id')
                self._cr.commit()
            else:
                raise UserError(response)
        
        payload = {'name': 'flow.json',
                    'asset_type': 'FLOW_JSON'
                }

        files=[
          ('file',('flow.json',self.flow_attachment.raw,'application/json'))
        ]

        response = self.env['whatsapp'].upload_flow_whatsapp(company_id=self.company_id, data=payload,  files=files,whatsapp_flow_id=self.whatsapp_flow_id)
