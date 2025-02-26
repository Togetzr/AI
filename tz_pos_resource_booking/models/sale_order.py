# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from random import random

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    booking_id = fields.Many2one('resource.booking',string="Booking")
    
