# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class WhatsAppTemplateButton(models.Model):
    _inherit = 'whatsapp.template.button'
    
    send_default_company_flow = fields.Boolean(string="Send Default Flow")
