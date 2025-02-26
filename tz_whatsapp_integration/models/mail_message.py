
from odoo import fields, models
import requests
import json
import logging
_logger = logging.getLogger(__name__)

class messagesmail(models.Model):
    _inherit = 'mail.message'
    
    msg_uid = fields.Char(string="Message ID")
    formetted_number = fields.Char(string="Formetted Number")
    whatsapp_template_id = fields.Many2one('whatsapp.template')
    wa_flow_id = fields.Many2one('whatsapp.flow')
    message_unique_id = fields.Char(string="Whatsapp Message Unique ID from odoo")
