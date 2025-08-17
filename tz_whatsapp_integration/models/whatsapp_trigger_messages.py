
from odoo import fields,api, models, _
import logging
_logger = logging.getLogger(__name__)

class WHATSAPPTRIGGERMESSAGE(models.Model):
    _name = 'whatsapp.trigger.message'
    
    name = fields.Char(string="Name")
    company_id = fields.Many2one('res.company',string="Company",required=True)
    flow_id = fields.Many2one('whatsapp.flow',string="Flow")
    template_id = fields.Many2one('whatsapp.template',string="Template")
    message = fields.Text(string="Custom Message")
    mpm_template = fields.Many2one('whatsapp.template',string="MPM Template")
