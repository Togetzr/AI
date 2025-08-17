# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.addons.resource.models.utils import Intervals


class ResourceBookingCombinationInherit(models.Model):
    _inherit = "resource.booking.combination"
    
    custom_name = fields.Char(string='Display Name',required=True)
    combination_type_id = fields.Many2one("resource.booking.combination.type",string="Combination Type")
