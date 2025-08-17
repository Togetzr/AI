# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from random import random

from odoo import _, api, fields, models

from odoo.addons.resource_booking.models.resource_booking import _availability_is_fitting
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)
class ResourceBookingInherit(models.Model):
    _inherit = "resource.booking"
    
    resource_id = fields.Many2one('resource.resource',string="Recourses")
    resource_booking_combination_type_id = fields.Many2one("resource.booking.combination.type",string="Combination Type")
    
    def _get_best_combination(self):
        """Pick best combination based on current booking state."""
        # No dates? Then return whatever is already selected (can be empty)
        if not self.start:
            return self.combination_id
        # If there's a combination already, put it 1st (highest priority)
        sorted_combinations = self.combination_id + (
            self.type_id._get_combinations_priorized() - self.combination_id
        )
        if self.resource_booking_combination_type_id:
            sorted_combinations = sorted_combinations.filtered(lambda x:x.id in self.resource_booking_combination_type_id.combination_ids.ids)
#        _logger.info("--sorted_combinations---%s"%sorted_combinations)
        start_dt = fields.Datetime.context_timestamp(self, self.start)
        end_dt = fields.Datetime.context_timestamp(self, self.stop)
        # Get 1st combination available in the desired interval
        for combination in sorted_combinations:
            available_intervals = self._get_intervals(start_dt, end_dt, combination)
            if _availability_is_fitting(available_intervals, start_dt, end_dt):
                return combination
        # Tell portal user there's no combination available
        if self.env.context.get("using_portal"):
            hours = (self.stop - self.start).total_seconds() / 3600
            raise ValidationError(
                _("No resource combinations available on %s")
                % self.env["calendar.event"]._get_display_time(
                    self.start, self.stop, hours, False
                )
            )
