import odoo

from odoo import http, models, fields, _
from odoo.http import request

class OnboardController(http.Controller):
    
    
    @http.route('/wa_onboarding', type='http', auth="public",website = True )
    def index(self, **kw):
        print("---kw",kw)
        return request.render("tz_wa_onboard_website.waonboard")
