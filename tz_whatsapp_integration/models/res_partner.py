
from odoo import fields, models
import requests
import json
import logging
_logger = logging.getLogger(__name__)

class PARTNER(models.Model):
    _inherit = 'res.partner'
    
    formetted_number = fields.Char()
    first_flow_id = fields.Many2one('whatsapp.flow')
    first_flow_message = fields.Char()
