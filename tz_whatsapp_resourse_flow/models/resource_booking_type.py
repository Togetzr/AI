# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from random import random

from odoo import _, api, fields, models


class ResourceBookingType(models.Model):
    _inherit = "resource.booking.type"
    
    gender = fields.Selection([('male','Male'),('female','Female')],string="Gender")
    resource_ids = fields.Many2many('resource.resource','resource_booking_type_rel','resource_id','booking_type_id',string="Recourses")
    resource_domain = fields.Char(compute="compute_resource_domain")
    
    @api.depends()
    def compute_resource_domain(self):
        for rec in self:
            rec.resource_domain = f"[('id','in',{rec.combination_rel_ids.mapped('combination_id').mapped('resource_ids').ids})]" if rec.combination_rel_ids and rec.combination_rel_ids.mapped('combination_id') and rec.combination_rel_ids.mapped('combination_id').mapped('resource_ids') else "[('id','in',[])]"
