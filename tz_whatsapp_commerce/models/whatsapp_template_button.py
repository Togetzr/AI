from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class WhatsapptemplateButtons(models.Model):
    _inherit = 'whatsapp.template.button'
    
    button_type = fields.Selection(selection_add=[
        ('MPM', 'MPM')],ondelete={'MPM': 'set quick_reply'})
