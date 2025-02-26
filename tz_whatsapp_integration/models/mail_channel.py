
from odoo import fields, models
import requests
import json
import logging
_logger = logging.getLogger(__name__)

class Channel(models.Model):
    _inherit = 'discuss.channel'
    
    company_id = fields.Many2one('res.company')
