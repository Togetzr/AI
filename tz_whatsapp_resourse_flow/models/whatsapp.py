from odoo import fields,api, models, _

class Whatsapp(models.Model):
    _inherit = 'whatsapp'
    
    def send_interactive_template_message(self,wa_template_id,partner_id,company_id,type,record):
        if not company_id.hair_dresser_company:
            return super(Whatsapp,self).send_interactive_template_message(wa_template_id=wa_template_id,partner_id=partner_id,company_id=company_id,type=type,record=record)
        final_message = self.get_final_message_for_template(wa_template_id,record)
        data = {'body':{"text":final_message}}
        buttons = wa_template_id._get_interactive_button()
        if wa_template_id.button_ids.filtered(lambda x:x.send_default_company_flow):
            if request.env['resource.booking.type'].sudo().search([('gender','!=',False)],limit=1):
                if request.env['resource.booking'].sudo().search([('partner_ids','=',partner_id.id)],limit=1):
                    flow_id = self.env.ref('tz_whatsapp_resourse_flow.advance_flow_with_gender')
                else:
                    flow_id = self.env.ref('tz_whatsapp_resourse_flow.normal_flow_with_gender')
            else:
                if request.env['resource.booking'].sudo().search([('partner_ids','=',partner_id.id)],limit=1):
                    flow_id = self.env.ref('tz_whatsapp_resourse_flow.advance_flow')
                else:
                    flow_id = self.env.ref('tz_whatsapp_resourse_flow.normal_flow')
            flow_data,random_string = flow_id.get_flow_message_data()
            data['action'] = flow_data.get('action')
            self._send_interactive(wa_template_id,False,partner_id,data,company_id,'flow')
        else:
            super(Whatsapp,self).send_interactive_template_message(wa_template_id=wa_template_id,partner_id=partner_id,company_id=company_id,type=type,record=record)
        
