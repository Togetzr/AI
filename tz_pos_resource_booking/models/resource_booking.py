# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from random import random

from odoo import _, api, fields, models
import pytz
import logging
_logger = logging.getLogger("wp_final_msg")


class ResourceBooking(models.Model):
    _inherit = "resource.booking"
    
    sale_id = fields.Many2one('sale.order',string="Sale Order")
    
    def get_summery_info_old(self):
        super(ResourceBooking,self).get_summery_info()
        summery = "N° de réservation : %s\n"%self.sale_id.name
        summery += "Nom : %s\n"%self.partner_id.name
        summery += "Zone : %s\n"%self.combination_id.name
        summery += "N° de convives : %s\n"%self.type_id.name
        summery += "Date de réservation : %s\n"%self.start
        _logger.info(f"Appintment time -> {self.start}")
#        self.start.astimezone(pytz.timezone(self._context.get('tz')))
        return summery

    def get_summery_info(self):
        super(ResourceBooking,self).get_summery_info()
        company_time_zone = self.env.company.resource_tz or 'Europe/Paris'
        utc_timezone = pytz.utc
        utc_time = utc_timezone.localize(self.start)
        paris_timezone = pytz.timezone(company_time_zone)
        paris_time = utc_time.astimezone(paris_timezone)
        paris_time = paris_time.replace(tzinfo=None)
        summery = "N° de réservation %s\n"%self.sale_id.name
        summery += "Nom : %s\n"%self.partner_id.name
        summery += "Zone : %s\n"%self.combination_id.name
        summery += "N° de convives : %s\n"%self.type_id.name
        summery += "Date de réservation : %s\n"%paris_time
        return summery

    def action_open_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Linked Sale Orders'),
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.sale_id.ids)],
        }
    
    def action_confirm(self):
        super(ResourceBooking,self).action_confirm()
        for rec in self.filtered(lambda x:x.type_id and x.type_id.product_id):
            product_id = rec.type_id.product_id
            vals = {
                'client_order_ref':rec.name,
                'partner_id':rec.partner_ids[0].id if rec.partner_ids else False,
                'booking_id':rec.id,
                'order_line':[(0,0,{
                    'product_id':product_id.id,
                    'name':product_id.name,
                    'product_uom_qty':1,
                    'tax_id':[(6, 0, product_id.taxes_id.ids)],
                })]
            }
            sale_order_obj = self.env['sale.order'].create(vals)
            rec.sale_id = sale_order_obj.id
    
    
    
