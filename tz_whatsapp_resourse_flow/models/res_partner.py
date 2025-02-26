# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from random import random

from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    gender = fields.Selection([('male','Male'),('female','Female')],string="Gender")
    first_name = fields.Char(string="First Name")
    sur_name = fields.Char(string="Last Name")
