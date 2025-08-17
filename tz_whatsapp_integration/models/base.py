
from odoo import fields, models
import logging
_logger = logging.getLogger(__name__)

class BASE(models.AbstractModel):
    _inherit = 'base'
    
    def get_whatsapp_dynamic_link(self):
        return False
