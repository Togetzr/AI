# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from random import random
from odoo.exceptions import UserError
from odoo import _, api, fields, models
from odoo.addons.base.models.res_partner import _tz_get


class ResCompany(models.Model):
    _inherit = "res.company"

    hair_dresser_company = fields.Boolean(string="Is Hair Dresser",default=True)
    resource_tz = fields.Selection(
        _tz_get, string='Timezone', required=True, default=lambda self: self.env.user.tz,
        help="Timezone For Resource")

    def sync_flows_to_facebook(self):
        if not self.data_uri_domain or not self.webhook_verify_token:
            raise UserError(_("Endpoint URi Is required. Please contact your administrator for it."))
        flow_ids = ['normal_flow','normal_flow_with_gender','advance_flow','advance_flow_with_gender']
        for flow in flow_ids:
            flow_id = self.env.ref('tz_whatsapp_resourse_flow.%s'%flow)
            flow_id.sync_to_whatsapp_default()
