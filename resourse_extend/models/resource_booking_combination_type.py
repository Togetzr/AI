# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from random import random

from odoo import _, api, fields, models


class ResourceBookingCombinationType(models.Model):
    _name = "resource.booking.combination.type"
    
    combination_ids = fields.One2many("resource.booking.combination","combination_type_id")
    name = fields.Char(string="Name",required=True)
