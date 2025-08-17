from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    whatsapp_commerce_id = fields.Char(string="Whatsapp Commerce Id")
    has_unavailable_product = fields.Boolean(
        string="Has Unavailable Product",
        compute="_compute_has_unavailable_product",
        store=True
    )

    @api.depends('order_line.product_unavailable')
    def _compute_has_unavailable_product(self):
        """
            Computes whether the sale order contains any unavailable products.
            Sets 'has_unavailable_product' to True if any order line has 'product_unavailable' set to True.
        """
        for order in self:
            order.has_unavailable_product = any(line.product_unavailable for line in order.order_line)
    
    def get_whatsapp_dynamic_link(self):
        payment_link_create = self.env['payment.link.wizard'].sudo().with_context({
            'active_model': self._name,
            'active_id': self.id,
        }).with_company(self.company_id.id).create({})
        return payment_link_create.link


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    forecast_quantity = fields.Float(
        string="Forecasted Quantity",
        compute="_compute_forecast_quantity",
        store=True
    )

    product_unavailable = fields.Boolean(
        string="Product Unavailable",
        compute="_compute_product_unavailable",
        store=True
    )

    @api.depends('product_id.qty_available', 'product_id.outgoing_qty')
    def _compute_forecast_quantity(self):
        """Computes the forecasted quantity as available stock minus outgoing stock."""
        for line in self:
            line.forecast_quantity = (
                    line.product_id.qty_available - line.product_id.outgoing_qty) if line.product_id else 0.0

    @api.depends('forecast_quantity')
    def _compute_product_unavailable(self):
        """Marks a product as unavailable if its forecasted quantity is zero or negative."""
        for line in self:
            line.product_unavailable = line.forecast_quantity <= 0
