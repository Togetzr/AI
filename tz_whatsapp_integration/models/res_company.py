# -*- coding: utf-8 -*-
#############################################################################
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from functools import reduce
from odoo import models, api, _,fields
from werkzeug import urls
import json
from datetime import datetime, time,timezone,timedelta
import pytz
import requests
from odoo.tools import plaintext2html
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval,wrap_module
import base64
import re
#from odoo.tools.safe_eval import datetime,pytz
import logging
# _logger = logging.getLogger(__name__)
_logger = logging.getLogger("wp_message")


DEFAULT_ENDPOINT = "https://graph.facebook.com/v18.0"

class COMPANY(models.Model):
    _inherit='res.company'
    
    app_uid = fields.Char(string="App ID", tracking=2)
    fb_api_version = fields.Char(string="API Version")
    fb_configuration_id = fields.Char(string="Configuration ID")
    wa_access_token = fields.Char(string="Access Token")
    waba_id = fields.Char(string="Whatsapp Business ID")
    wa_phonenumber_id = fields.Char(string="Whatsapp Phonenumber ID")
    config_id = fields.Char(string="Whatsapp Config ID")
    webhook_verify_token = fields.Char(string="Whatsapp verification Token",default="watogetzr")
    platform_domain = fields.Char(string="Domain Name only for whatsapp purpose",help="Use only domain name 'togetzr.com'")
    data_uri_domain = fields.Char(string="Domain Name for endpoint uri",default="olr1.net")
    whatsapp_user = fields.Many2one('res.partner',string="Whatsapp User")
    public_key_attachment = fields.Binary(string="Public Key File")
    private_key_attachment = fields.Binary(string="Private Key File")
    saas_domain = fields.Char()
    
    def whatsapp_onboard(self):
        # We simply call the setup bar function.
        action = self.env.ref('tz_whatsapp_integration.action_setting_whatsapp_onboard').sudo().read()[0]
        action['params'] = {'company_id':self.id}
        return action
    
    def set_webhook_subdomain(self):
        whatsapp_data = self.env['whatsapp'].get_whatsapp_data(self)
        client_domain = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        headers = {
            'Authorization': f'Bearer {whatsapp_data.get("access_token")}',
            'Content-Type': 'application/json',
        }

        data = {
             "override_callback_uri":urls.url_join(client_domain, '/wa-callback'),
             "verify_token":self.webhook_verify_token
        }
        _logger.info("--register webhook data-%s"%data)
        response = requests.post(
            DEFAULT_ENDPOINT+f'/{self.waba_id}/subscribed_apps',
            headers=headers,
            data=data,
        )
        _logger.info("---response %s"%response.text)
    
    @api.model
    def set_whatsapp_configurations(self,company_id,phone_number_id,waba_id):
    
        _logger.info("--working-%s--%s---%s"%(company_id,phone_number_id,waba_id))
        company_id = self.env['res.company'].browse(company_id)
        
        company_id.write({
            'wa_phonenumber_id':phone_number_id,
            'waba_id':waba_id,
            'app_uid':self.env['ir.config_parameter'].sudo().get_param('saas.default_wa_app_id'),
            'fb_api_version':self.env['ir.config_parameter'].sudo().get_param('saas.default_wa_app_version'),
            'fb_configuration_id':self.env['ir.config_parameter'].sudo().get_param('saas.default_contribution_id'),
            'wa_access_token':self.env['ir.config_parameter'].sudo().get_param('saas.default_access_token')
        })
        self._cr.commit()
        whatsapp_data = self.env['whatsapp'].get_whatsapp_data(company_id)
        
        client_domain = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        headers = {
            'Authorization': f'Bearer {whatsapp_data.get("access_token")}',
            'Content-Type': 'application/json',
        }

        data = {
             "override_callback_uri":urls.url_join(client_domain, '/wa-callback'),
             "verify_token":company_id.webhook_verify_token
        }
        _logger.info("--register webhook data-%s"%data)
        response = requests.post(
            DEFAULT_ENDPOINT+f'/{waba_id}/subscribed_apps',
            headers=headers,
            data=data,
        )
        _logger.info("--register webhook callback-response %s"%response.text)
    
    @api.model
    def get_whatsapp_configurations(self,company_id):
        company_id = self.env['res.company'].browse(company_id)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        client_domain = self.env['ir.config_parameter'].sudo().get_param('saas.default_main_server')
        parameters = '/wa_onboarding?'
        parameters += "app_id=%s&api_version=%s&FBconfiguration_id=%s&base_url=%s"%(self.env['ir.config_parameter'].sudo().get_param('saas.default_wa_app_id'),self.env['ir.config_parameter'].sudo().get_param('saas.default_wa_app_version'),self.env['ir.config_parameter'].sudo().get_param('saas.default_contribution_id'),base_url)
        return urls.url_join(client_domain, parameters)
    
    def set_public_key(self):
        if not self.public_key_attachment:
            raise UserError('Public Key File required')
        whatsapp_data = self.env['whatsapp'].get_whatsapp_data(self)
        headers = {
            'Authorization': f'Bearer {whatsapp_data.get("access_token")}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        decoded_data = base64.b64decode(self.public_key_attachment)
        text_data = decoded_data.decode('utf-8')
        data = {
            'business_public_key': text_data,
        }
        
        response = requests.post(
            DEFAULT_ENDPOINT+f'/{whatsapp_data.get("wa_phonenumber_id")}/whatsapp_business_encryption',
            headers=headers,
            data=data,
        )
        raise UserError(response.text)
    
    def get_public_key(self):
        whatsapp_data = self.env['whatsapp'].get_whatsapp_data(self)
        
        headers = {
            'Authorization': f'Bearer {whatsapp_data.get("access_token")}',
        }
        
        response = requests.get(DEFAULT_ENDPOINT+f'/{whatsapp_data.get("wa_phonenumber_id")}/whatsapp_business_encryption', headers=headers)

        raise UserError(response.text)
    
    def get_anothertype_default_messages(self,auther_id,message,contact_exist=False):
        default_template = self.env['whatsapp.template'].search([('default_template','=',True),('wa_account_id','=',self.id),('id','!=',self.env.ref('tz_whatsapp_integration.first_template').id),('trigger_word','!=',False)])
        if message.isdigit() and (int(message)) <= len(default_template):
            trigger_template = default_template[int(message) - 1]
            _logger.info("--trigger_template--%s"%trigger_template.is_mpm_template)
            if trigger_template.is_mpm_template:
                self.env['whatsapp'].send_mpm_message(trigger_template,auther_id,self)
            else:
                self.env['whatsapp'].with_context(model='res.company',res_id=self.id).send_interactive_template_message(trigger_template,auther_id,self,"button",self)
            return True
        elif default_template:
            message = self.env.ref('tz_whatsapp_integration.first_template').body + "\n"
            count = 1
            for temp in default_template:
                message += "%s. %s \n"%(str(count),temp.trigger_word)
                count += 1
                trigger = self.env['whatsapp.trigger.message'].search([('company_id','=',self.id),('name','=ilike',temp.trigger_word.lower()),'|',('template_id','=',temp.id),('mpm_template','=',temp.id)],limit=1)
                if not trigger:
                    vals = {
                        'company_id':self.id,
                        'name':temp.trigger_word,
                    }
                    if temp.is_mpm_template:
                        vals['mpm_template'] = temp.id
                    else:
                        vals['template_id'] = temp.id
                    self.env['whatsapp.trigger.message'].create(vals)
            self.env['whatsapp']._send(auther_id,{'body':message},self)
            return True
        return False
    
    def send_default_template_message(self,message,auther_id,company_id,contact_exist):
        trigger_message = self.env['whatsapp.trigger.message'].search([('company_id','=',company_id.id),('name','=ilike',message['text']['body'].lower()),'|','|','|',('flow_id','!=',False),('mpm_template','!=',False),('template_id','!=',False),('message','!=',False)],limit=1)
        if message['text']['body'].lower() == 'gps':
            data = {
                    "longitude": company_id.partner_id.partner_latitude,
                    "latitude": company_id.partner_id.partner_longitude,
                    "name": company_id.name,
                    "address": company_id.partner_id.contact_address.replace('\n',' ')
                }
            self.env['whatsapp']._send_location(auther_id,data,company_id)
        elif message['text']['body'].lower() == 'contact':
            self.env['whatsapp']._send(auther_id,{'body':"Merci de nous avoir contactés. Nous reviendrons vers vous dès que possible."},company_id)
        elif trigger_message:
            if trigger_message.message:
                self.env['whatsapp']._send(auther_id,{'body':trigger_message.message},company_id)
            if trigger_message.template_id:
                self.env['whatsapp'].with_context(model='res.company',res_id=company_id.id).send_interactive_template_message(trigger_message.template_id,auther_id,company_id,"button",company_id)
            if trigger_message.flow_id:
                trigger_message.flow_id.send_flow_message(auther_id)
            if trigger_message.mpm_template:
                self.env['whatsapp'].send_mpm_message(trigger_message.mpm_template,auther_id,company_id)
        else:
            other_default_message = company_id.get_anothertype_default_messages(auther_id,message['text']['body'].lower()) if not self._context.get('no_other_type_default',False) else False
            if not other_default_message:
                default_template = self.env['whatsapp.template'].search([('default_template','=',True),('wa_account_id','=',company_id.id),('contact_exist','=',contact_exist)],limit=1)
                if not default_template:
                    default_template = self.env['whatsapp.template'].search([('default_template','=',True),('wa_account_id','=',company_id.id)],limit=1)
                if default_template and not 'context' in message:
                    self.env['whatsapp'].with_context(model='res.company',res_id=company_id.id).send_interactive_template_message(default_template,auther_id,company_id,"button",company_id)
        
#        else:
#            auther_id.first_flow_id.send_flow_message(auther_id)
    
    def fake_resoursebutton(self):
        vals = {'name': 'Yyd Yeys', 'partner_ids': [(4, 12)], 'email': '', 'type_id': 2, 'start': datetime(2025, 3, 11, 15, 0), 'combination_auto_assign': True, 'combination_id': 13, 'resource_booking_combination_type_id': 1}
        record = self.env['resource.booking'].sudo().create(vals)
        _logger.info("--recrord=-%s---%s"%(record,record.combination_id))
        record.action_confirm()
    
    def fake_button_click(self):
        message =   {'context': {'from': '33749181848', 'id': 'wamid.HBgMOTE3MDY5MjgyOTM0FQIAERgSNTEyODIwMkY0MzAzRjcwN0I4AA=='}, 'from': '917069282934', 'id': 'wamid.HBgMOTE3MDY5MjgyOTM0FQIAEhggMDZBNjYxQkIzNjJDRTMyMzY3RDEyQjc1ODAyQTBFQjkA', 'timestamp': '1723060473', 'type': 'interactive', 'interactive': {'type': 'nfm_reply', 'nfm_reply': {'response_json': '{"name":"Mayur","family_name":"NAGAR","email":"Mayurnagar007.mayur@gmail.com","resourse":"1","services":"1","appointment":"2024-08-09","appointment_time":"09:00","flow_token":"870a826a-cc74-4115-8bfe-2d8cad478249"}', 'body': 'Sent', 'name': 'flow'}}}

        
#        self.whatsapp_button_click(message,False,self)

        self.unsupported_type(message,False,self)
    
    def whatsapp_button_click(self,message,auther_id,company_id):
        _logger.info("--message--%s"%message)
        if 'context' in message:
            button_name = message.get('button').get('text') if message.get('button') else message.get('interactive').get('button_reply').get('title')
            _logger.info("--button_name--%s"%button_name)
            replied_id = self.env['mail.message'].sudo().search([('msg_uid', '=', message['context'].get('id'))],limit=1)
            if replied_id:
                whatsapp_template_id = replied_id.whatsapp_template_id
                _logger.info("--whatsapp_template_id--%s"%whatsapp_template_id)
                button = self.env['whatsapp.template.button'].sudo().search([('wa_template_id','=',whatsapp_template_id.id),('name','=',button_name),('button_type','=','quick_reply')],limit=1)
                _logger.info("--button.replied_with_message--%s"%button.replied_with_message)
                if button:
                    partner_id = self.env['res.partner'].search([('formetted_number','=',message.get('from',False))],limit=1)
                    if button.call_method_after_click:
                        obj = self.env[replied_id.model].sudo().browse(replied_id.res_id)
                        try:
                            getattr(obj, button.call_method_after_click)()
                        except Exception as e:
                            self.env['whatsapp']._send(partner_id,{'body':str(e)},whatsapp_template_id.wa_account_id)
                            return button_name
                    if button.replied_with_template:
                        if whatsapp_template_id:
                            record = self.env[replied_id.model].browse(replied_id.res_id)
                            
                            self.env['whatsapp'].with_context(model=replied_id.model,res_id=replied_id.res_id).send_interactive_template_message(button.replied_with_template,partner_id,company_id,"button",record)
#                            final_message = button.replied_with_template.body
#                            variables = button.replied_with_template.variable_ids._get_variables_value(record)
#                            for variable in button.replied_with_template.variable_ids.filtered(lambda x:x.line_type == 'body'):
#                                _logger.info("-variable.name=-%s---%s"%(variables.get(f'body-{variable.name}'),type(variables.get(f'body-{variable.name}'))))
#                                final_message = final_message.replace(variable.name,variables.get(f'body-{variable.name}'))
#                        
#                            
#                            buttons = button.replied_with_template._get_interactive_button()
#                            if buttons:
#                                data = {
#                                    'body':{"text":final_message},
#                                    'action':{
#                                            "buttons":buttons
#                                        }
#                                }
#                                self.env['whatsapp'].with_context(model=replied_id.model,res_id=replied_id.res_id)._send_interactive(button.replied_with_template,False,partner_id,data,company_id,"button")
                            
#                            composer_id = self.env['whatsapp.composer'].with_context(active_model=replied_id.model,default_wa_template_id=whatsapp_template_id.id,active_id=replied_id.res_id).create({})
#                            composer_id.wa_template_id = button.replied_with_template.id
#                            response = composer_id._send_whatsapp_template()
                    if button.replied_with_message:
                        self.env['whatsapp']._send(partner_id,{'body':button.replied_with_message},whatsapp_template_id.wa_account_id)
                    if button.replied_with_flow:
                        if not partner_id.first_flow_id:
                            partner_id.first_flow_id = button.replied_with_flow.id
                        button.replied_with_flow.send_flow_message(partner_id)
                    if button.code:
                        data = {'partner_id':partner_id,
                            'env':self.env,
                            "message":message,
                            "datetime":datetime,
                            "pytz":pytz
                            }
                        safe_eval(button.code, data, mode='exec', nocopy=True)
#                    else:
#                        partner_id.first_flow_id.send_flow_message(partner_id)
        return button_name
    
    def whatsapp_location_button(self,message,auther_id,company_id):
#        {'context': {'from': '33749181848', 'id': 'wamid.HBgMOTE3MDY5MjgyOTM0FQIAERgSMjUyNDM3M0M1MzExRjlBOEU0AA=='}, 'from': '917069282934', 'id': 'wamid.HBgMOTE3MDY5MjgyOTM0FQIAEhggQjlCM0ZDNjVBODE1MEU1Q0VEQTlDNTAzREFGMjI4NzMA', 'timestamp': '1716899539', 'location': {'latitude': 23.0014732, 'longitude': 72.6223196}, 'type': 'location'}
        if 'context' in message:
            replied_id = self.env['mail.message'].sudo().search([('msg_uid', '=', message['context'].get('id'))],limit=1)
            if replied_id:
                record = self.env[replied_id.model].sudo().browse(replied_id.res_id)
                if 'partner_id' in replied_id.whatsapp_template_id.lat_field:
                    record.partner_id.partner_latitude = message.get('location').get('latitude')
                else:
                    record.write({replied_id.whatsapp_template_id.lat_field:message.get('location').get('latitude')})
                if 'partner_id' in replied_id.whatsapp_template_id.lng_field:
                    record.partner_id.partner_longitude = message.get('location').get('longitude')
                else:
                    record.write({replied_id.whatsapp_template_id.lng_field:message.get('location').get('longitude')})
                message_data = f'''
Nom de l’entreprise :- {record.name}
E-mail professionnel :- {record.email_from}
Nom du gestionnaire :- {record.contact_name}
Telephone du gestionnaire :- {record.mobile}
                '''
                description = record.description.replace("<p>","").replace("</p>","")
                lines = description.split('\n')
                cleaned_lines = [re.sub(r'\s+', '', line) for line in lines if line.strip()]
                message_data += '\n'.join(cleaned_lines)
                self.env['whatsapp']._send(auther_id,{'body':message_data},company_id)
                
        body_message = "Latitude : %s\nLongitude : %s"%(message.get('location').get('latitude'),message.get('location').get('longitude'))
        return body_message
    
    def unsupported_type(self,message,auther_id,company_id):
        if message.get('type',False) == 'interactive' and message.get('interactive',False).get('type',False) == 'nfm_reply' and message.get('interactive',False).get('nfm_reply',False).get('name',False) == 'flow':
            response = json.loads(message.get('interactive',False).get('nfm_reply',False).get('response_json',False))
            replied_id = self.env['mail.message'].sudo().search([('msg_uid', '=', message['context'].get('id'))])
            if replied_id:
                # timezone = pytz.timezone(self.env.user.tz or 'Europe/Paris')
                timezone = pytz.timezone(self.env.company.resource_tz or 'Europe/Paris')
                partner_id = self.env['res.partner'].search([('formetted_number','=',message.get('from',False))],limit=1)
                whatsapp_flow_id = replied_id.wa_flow_id
                message_data = ""
                del response['flow_token']
                for rec in response:
                    message_data += "%s : %s\n"%(rec.replace("_"," ").title(),response.get(rec))
                record = False
                if whatsapp_flow_id.is_resourse_flow and whatsapp_flow_id.flow_type == 'modifier':
                    bookings = self.env[replied_id.model].sudo().browse(replied_id.res_id)
                    start = datetime.strptime("%s %s"%(response.get("appointment",False),response.get("appointment_time")), '%Y-%m-%d %H:%M')
                    start = timezone.localize(start)
                    bookings.start = start.astimezone(pytz.utc)
                    message_data = bookings.get_summery_info()
                elif whatsapp_flow_id.is_resourse_flow:
                    partner_vals = {}
                    full_name = f"{response.get('name', str())} {response.get('family_name', str())}"
                    if partner_id.name != full_name:
                        partner_vals["name"] = full_name
                    if partner_id.first_name != response.get("name",""):
                        partner_vals["first_name"] = response.get("name","")
                    if partner_id.sur_name != response.get("family_name",""):
                        partner_vals["sur_name"] = response.get("family_name","")
                    if partner_id.email != response.get("email", ''):
                        partner_vals["email"] = response.get("email", '')
                    if partner_id.gender != response.get("gender",""):
                        partner_vals["gender"] = response.get("gender","")
                    if partner_vals:partner_id.write(partner_vals)
                    start = datetime.strptime("%s %s"%(response.get("appointment",False),response.get("appointment_time")), '%Y-%m-%d %H:%M')
                    start = timezone.localize(start)
                    
                    combination_id = self.env['resource.booking.combination.type'].sudo().search([('id','=',int(response.get('resourse',False)))]) if response.get('resourse',False) and response.get('resourse',False) != 'AutoAssign' else False
                    type_id = self.env['resource.booking.type'].sudo().browse(int(response.get('services')))
                    
                    sorted_combinations = type_id._get_combinations_priorized().filtered(lambda x:x.id in combination_id.combination_ids.ids) if combination_id else type_id._get_combinations_priorized()
                    
                    vals = {
                        "name":"%s %s"%(response.get("name",partner_id.name), response.get("family_name",partner_id.sur_name)),
                        "partner_ids":[(4,partner_id.id)],
                        "email": response.get("email", ''),
                        "type_id":int(response.get("services",False)),
                        "start":start.astimezone(pytz.utc).replace(tzinfo=None),
                        "combination_auto_assign":True,
                        "combination_id":sorted_combinations.ids[0]
                    }
                    
                    if response.get('resourse',False) and response.get('resourse',False) != 'AutoAssign':
                        vals.update({
                            "resource_booking_combination_type_id":int(response.get('resourse',False)),
#                            "combination_auto_assign":False
                        })
                    _logger.info("--vals=-%s---"%(vals))
                    record = self.env['resource.booking'].sudo().create(vals)
                    _logger.info("--recrord=-%s---%s"%(record,record.combination_id))
                    try:
                        record.action_confirm()
                    except Exception as e:
                        self.env['whatsapp']._send(partner_id,{'body':str(e)},company_id)
                        return {"body":str(e)}
                    
                    message_data = record.get_summery_info()
                if whatsapp_flow_id.code:
                    for key, value in response.items():
                        if type(value) != type([]):
                            if value.isdigit():
                                response[key] = int(value)
                            else:
                                try:
                                    response[key] = float(value)
                                except ValueError:
                                    pass  # If conversion fails, leave the value unchanged
#                        {"name":"Mayur",
#                        "family_name":"Nagar",
#                        "email":"Mayurnagar7069@gmail.com",
#                        "resourse":"1",
#                        "services":"2",
#                        "appointment":"2024-08-09",
#                        "appointment_time":"09:30"}
                        
                        
                    if whatsapp_flow_id.id == 1:
                        timezone = pytz.timezone(self.env.user.tz or 'Europe/Paris')  # Replace 'Your/Desired/Timezone' with your desired timezone
                        # Convert timestamp to datetime object
                        timestamp = int(response.get("appointment")) / 1000  # Assuming milliseconds timestamp
                        appointment_datetime = datetime.fromtimestamp(timestamp) + timedelta(days=1)

                        localized_datetime = timezone.localize(appointment_datetime)
                        
                        # Parse appointment time
                        hour, minute = map(int, response.get("appointment_time").split(':'))
                        appointment_time_obj = time(hour, minute)

                        # Combine date and time to create final datetime object
                        final_datetime = datetime.combine(appointment_datetime.date(), appointment_time_obj)

                        # Specify desired timezone for localization
                        

                        # Localize the datetime object
                        localized_datetime = timezone.localize(final_datetime)

                        localized_datetime = localized_datetime.astimezone(pytz.utc).replace(tzinfo=None)
                        vals = {
                            "name":response.get("name",partner_id.name) + response.get("family_name",""),
                            "phone":message.get('from',False),
                            "service_ids":[(6,0,[int(service) for service in response.get("services",[])])],
                            "time":localized_datetime,
                            "chair_id":response.get("chair_id",False),
                            "partner_id":partner_id.id,
                            "email":response.get("email",False)
                        }
                        if partner_id.email != response.get("email",False):
                            partner_id.email = response.get("email",False)
                        
                        record = self.env[whatsapp_flow_id.model_id.model].sudo().create(vals)
                        description = f'''Name :- {response.get("name",False)} + {response.get("family_name",False)} \n
                                        Phone :- {message.get('from',False)}\n
                                        Email :- {response.get("email",False)}\n
                                        Time :- {record.time}\n
                                        Services :- {','.join([x.name for x in record.service_ids])}\n
                                        Hair Dresser :- {record.chair_id.name}
                            '''
                        event_vals = {
                            "name":"Appointment Booking : %s (%s)"%(response.get("name",False),message.get("from",False)),
    #                        "partner_ids":[(4,partner_id.id)],
                            "start":localized_datetime,
                            "stop":localized_datetime + timedelta(hours=1),
                            "description":description
                        }
                        event = self.env['calendar.event'].with_user(2).sudo().create(event_vals)
                        record.sudo().event_id = event.id
                    else:
                        data = {
                                'model':self.env[whatsapp_flow_id.model_id.model],
                                'env':self.env,
                                'response':response,
                                "message":message,
                                "partner_id":partner_id
                                }
                        data_return = safe_eval(whatsapp_flow_id.code, data, mode='exec', nocopy=True)
                        # _logger.info("-=-=-data_return",data_return)
                if whatsapp_flow_id.reply_with_template:
                    if not record:record = self.env[whatsapp_flow_id.model_id.model].search([],limit=1,order="id desc")
                    self.env['whatsapp'].with_context(model=record._name,res_id=record.id,final_message=message_data).send_interactive_template_message(whatsapp_flow_id.reply_with_template,partner_id,company_id,"button",record)
                    if whatsapp_flow_id.reply_with_multiple_templates:
                        for temp in whatsapp_flow_id.reply_with_multiple_templates:
                            self.env['whatsapp'].with_context(model=record._name,res_id=record.id).send_interactive_template_message(temp,partner_id,company_id,"button",record)
                elif whatsapp_flow_id.send_summery:
                    self.env['whatsapp']._send(partner_id,{'body':message_data},company_id)
                # _logger.info("--->message_data<---%s"%message_data)
                _logger.info("\n\n--->message_data<---%s"%message_data)
                return {"body":message_data}

        return False
    
    
    def find_active_channel(self,from_number, sender_name=False, create_if_not_found=True):
        responsible_partners = self.env['res.partner'].sudo().search([('formetted_number','=',from_number)],limit=1)
        contact_exist = True if responsible_partners else False
        if not responsible_partners:
            responsible_partners = self.env['res.partner'].sudo().create({
                'company_id':self.id,
                'name':sender_name,
                'phone':from_number,
                'formetted_number':from_number
            })
#            return False,False
        channel_partners = self.env['discuss.channel.member'].sudo().search([('partner_id','=',responsible_partners.id)])
        whatsapp_user = self.env['discuss.channel.member'].sudo().search([('partner_id','=',self.whatsapp_user.id)])
        domain = [('channel_type','=','group'),('id','in',channel_partners.mapped('channel_id').ids),('channel_member_ids','in',channel_partners.ids),('channel_member_ids','in',whatsapp_user.ids)]
        channel = self.env['discuss.channel'].search(domain,limit=1)
        if not channel:
            vals = {
                'channel_member_ids':[(0,0,{'partner_id': responsible_partners.id}),(0,0,{'partner_id':self.whatsapp_user.id})],
                'channel_type':'group',
                'company_id':self.id,
                'name':"%s, %s"%(self.whatsapp_user.name,responsible_partners.name)
            }
            channel = self.env['discuss.channel'].sudo().create(vals)
        return channel,responsible_partners,contact_exist
