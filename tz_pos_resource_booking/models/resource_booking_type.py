# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from random import random

from odoo import _, api, fields, models


class ResourceBookingType(models.Model):
    _inherit = "resource.booking.type"
    
    product_id = fields.Many2one('product.product',string="Product")
    price = fields.Monetary(string="Price")
    currency_id = fields.Many2one('res.currency',related="company_id.currency_id")
    
    @api.model
    def create(self,vals):
        rec = super(ResourceBookingType,self).create(vals)
        for r in rec.filtered(lambda x:x.price):
            v = {'name':r.name,
                'list_price':r.price,
                'detailed_type':'service',
                'available_in_pos':True}
            r.product_id = self.env['product.product'].sudo().create(v).id
        return rec
    
    def write(self,vals):
        rec = super(ResourceBookingType,self).write(vals)
        for r in self:
            v = {'name':r.name,
                'list_price':r.price,
                'detailed_type':'service',
                'available_in_pos':True}
            if r.product_id:
                r.product_id.write(v)
            else:
                r.product_id = self.env['product.product'].sudo().create(v).id
        return rec
