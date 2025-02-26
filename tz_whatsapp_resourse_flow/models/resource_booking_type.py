# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from random import random

from odoo import _, api, fields, models


class ResourceBookingType(models.Model):
    _inherit = "resource.booking.type"
    
    gender = fields.Selection([('male','Male'),('female','Female')],string="Gender")
    
