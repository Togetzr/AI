
from odoo import fields, models, _
import requests
import json
import pytz
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
import logging
_logger = logging.getLogger("wp_message-API")

DEFAULT_ENDPOINT = "https://graph.facebook.com/"

class WHATSAPP(models.Model):
    _name = 'whatsapp'
    
    def get_whatsapp_data(self,company_id=None):
        access_token = self.env['ir.config_parameter'].sudo().get_param('saas.default_access_token')
        return {
            'access_token':access_token,
            'wa_phonenumber_id':company_id.wa_phonenumber_id if company_id else self.env.user.company_id.wa_phonenumber_id,
            'app_uid':company_id.app_uid if company_id else self.env.user.company_id.app_uid,
            'waba_id':company_id.waba_id if company_id else self.env.user.company_id.waba_id,
        }
    
    def whatsapp_api_requests(self, request_type, url, auth_type="", params=False, headers=None, data=False, files=False, endpoint_include=False,company_id=None):
        
        whatsapp_data = self.get_whatsapp_data(company_id)
        
        headers = headers or {}
        params = params or {}
        
        if auth_type == 'oauth':
            headers.update({'Authorization': 'OAuth %s'%(whatsapp_data.get('access_token')),'Content-Type': 'application/json'})
        else:
            headers.update({'Authorization': 'Bearer %s'%(whatsapp_data.get('access_token')),'Content-Type': 'application/json'})
        call_url = (DEFAULT_ENDPOINT + self.env['ir.config_parameter'].sudo().get_param('saas.default_wa_app_version') + url) if not endpoint_include else url
        _logger.info("---call_url  %s"%call_url)
        res = requests.request(request_type, call_url, params=params, headers=headers, data=data, files=files, timeout=10)
        if 'error' in res.json():
            raise UserError("%s\n\nStatus Code:%s"%(res.text,res.status_code))

        return res.json()
    
    def upload_flow_whatsapp(self,data=False, files=False,company_id=None,whatsapp_flow_id=None):
        access_token = self.env['ir.config_parameter'].sudo().get_param('saas.default_access_token')
        headers = {
            'Authorization': 'Bearer %s'%(access_token),
        }

        response = requests.post(DEFAULT_ENDPOINT+f"/{whatsapp_flow_id}/assets", headers=headers,files=files,data=data)
        return response.json()
    
    def upload_demo_document(self,attachment,company_id):
        whatsapp_data = self.get_whatsapp_data(company_id)
        params = {
            'file_length': attachment.file_size,
            'file_type': attachment.mimetype,
            'access_token': whatsapp_data.get('access_token'),
        }
        uploads_session_response_json = self.whatsapp_api_requests("POST", f"/{whatsapp_data.get('app_uid')}/uploads", params=params,company_id=company_id)
        upload_session_id = uploads_session_response_json.get('id')
        if not upload_session_id:
            raise UserError(_("Document upload session open failed, please retry after sometime."))
        # Upload file
        upload_file_response_json = self.whatsapp_api_requests("POST", f"/{upload_session_id}", params=params, auth_type="oauth", headers={'file_offset': '0'}, data=attachment.datas,company_id=company_id)
        file_handle = upload_file_response_json.get('h')
        if not file_handle:
            raise UserError(_("Document upload failed, please retry after sometime."))
        return file_handle
    
    def upload_document(self,attachment,company_id):
        access_token = self.env['ir.config_parameter'].sudo().get_param('saas.default_access_token')
        headers = {
            'Authorization': 'Bearer %s'%(access_token),
        }

        response = requests.post(DEFAULT_ENDPOINT+'/%s/media'%(company_id.wa_phonenumber_id), headers=headers,files=[('file', (attachment.name, attachment.raw, attachment.mimetype))],data={'messaging_product':'whatsapp'})
        return response.json().get('id')
    
    def get_whatsapp_documents(self,url):
        whatsapp_data = self.get_whatsapp_data(company_id)
        headers = {
                    'Authorization': 'Bearer %s'%(whatsapp_data.get('access_token')),
                    'Content-Type': 'application/json',
                }
        call_url = DEFAULT_ENDPOINT + url
        response = requests.request("GET", call_url, params={}, headers=headers, data=False, files=False, timeout=10)
        response_json = response.json()
        file_url = response_json.get('url')
        file_response = requests.request("GET", file_url, params={}, headers=headers, data=False, files=False, timeout=10)
        datas = file_response.content
        _logger.info(f"---API----")
        _logger.info(f"whatsapp_data {whatsapp_data}")
        _logger.info(f"call_url {call_url}")
        _logger.info(f"response {response}")
        _logger.info(f"response_json {response_json}")
        _logger.info(f"file_url {file_url}")
        _logger.info(f"file_response {file_response}")
        _logger.info(f"datas {datas}")
        _logger.info(f"---API----")
        return datas
    
    def get_final_message_for_template(self,wa_template_id,record):
        final_message = wa_template_id.body
        variables = wa_template_id.variable_ids._get_variables_value(record)
        for variable in wa_template_id.variable_ids.filtered(lambda x:x.line_type == 'body'):
#            _logger.info("-variable.name=-%s---%s"%(variables.get(f'body-{variable.name}'),type(variables.get(f'body-{variable.name}'))))
            try:
                timezone = pytz.timezone(self.env.user.tz or 'Europe/Paris')
                data_time = datetime.strptime(variables.get(f'body-{variable.name}'), "%Y-%m-%d %H:%M:%S")
                variables[f'body-{variable.name}'] = pytz.utc.localize(data_time).astimezone(timezone).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                print("Invalid datetime format")
            final_message = final_message.replace(variable.name,variables.get(f'body-{variable.name}'))
        #_logger.info("---------------------")
        #_logger.info(f"---final_message-----{final_message}")
        #_logger.info("---------------------")
        return final_message
    
    def send_interactive_template_message(self,wa_template_id,partner_id,company_id,type,record):
        final_message = self._context.get('final_message',False) if self._context.get('final_message',False) else self.get_final_message_for_template(wa_template_id,record)
        if wa_template_id.mess_type == 'template':
            free_text_json = self._get_text_free_json(wa_template_id)
            self.send_template_message(final_message,record,wa_template_id,free_text_json,partner=partner_id)
        else:
            data = {'body':{"text":final_message}}
            buttons = wa_template_id._get_interactive_button()
#            template_variables_value = wa_template_id.variable_ids._get_variables_value(record)
#            buttons = wa_template_id._get_button_components(free_text_json={}, template_variables_value=template_variables_value)
            _logger.info(f"context -> {self._context}")
            _logger.info(f"final message -> {final_message}")
            if wa_template_id.button_ids.filtered(lambda x:x.button_type == 'flow'):
                flow_id = wa_template_id.button_ids.mapped('replied_with_flow')[0]
                flow_data,random_string = flow_id.get_flow_message_data()
                data['action'] = flow_data.get('action')
                self._send_interactive(wa_template_id,flow_id,partner_id,data,company_id,'flow',message_unique_id=random_string)
            elif buttons:
                data["action"] = {
                    "buttons":buttons
                }
                self._send_interactive(wa_template_id,False,partner_id,data,company_id,type)
            elif wa_template_id.send_location:
                data["action"] = {
                    "name":"send_location"
                }
            
                self._send_interactive(wa_template_id,False,partner_id,data,company_id,"location_request_message")
            else:
                self.env['whatsapp']._send(partner_id,{'body':final_message},company_id)
        
    def _get_text_free_json(self,wa_template_id):
        """This method is used to prepare free text json using values set in free text field of composer."""
        json_vals = {}
        if wa_template_id.header_text:
            json_vals['header_text'] = wa_template_id.header_text
#        if self.number_of_free_text:
#            free_text_field = [f"free_text_{i + 1}" for i in range(self.number_of_free_text)]
#            for value in free_text_field:
#                if self[value]:
#                    json_vals[value] = self[value]
#        if self.button_dynamic_url_1:
#            json_vals['button_dynamic_url_1'] = self.button_dynamic_url_1
#        if self.button_dynamic_url_2:
#            json_vals['button_dynamic_url_2'] = self.button_dynamic_url_2
        return json_vals
        
    def send_template_message(self,body,record,wa_template_id,free_text_json={},partner=False):
        attachment_id = self.env['ir.attachment']
        if wa_template_id.report_id:
            report_content, report_format = wa_template_id.report_id._render_qweb_pdf(wa_template_id.report_id, record.id)
            if wa_template_id.report_id.print_report_name:
                report_name = safe_eval(wa_template_id.report_id.print_report_name, {'object': record}) + '.' + report_format
            else:
                report_name = record.name + '.' + report_format
            attachment_id = self.env['ir.attachment'].create({
                'name': report_name,
                'raw': report_content,
                'mimetype': 'application/pdf',
            })
        company = wa_template_id.wa_account_id
        channel = self.find_active_channel(record.partner_id,company)
        post_values = {
            'attachment_ids': attachment_id.ids,
            'body': body,
            'message_type': 'comment'
        }
        channel.message_post(**post_values)
        post_values.update({'whatsapp_template_id':wa_template_id.id})
        message = self.env['mail.message'].create(
            dict(post_values, res_id=record.id, model=record._name,
                 subtype_id=self.env['ir.model.data']._xmlid_to_res_id("mail.mt_note"))
        )
        send_vals, attachment = wa_template_id._get_send_template_vals(
                    record=record, free_text_json=free_text_json,
                    attachment=attachment_id or False,company_id=company)
        whatsapp_data = self.get_whatsapp_data(company)
        partner_id = partner if partner else record.partner_id
        data = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': partner_id.mobile or partner_id.phone,
            'type': 'template',
            'template': send_vals
            }
        
        headers = {
                'Authorization': 'Bearer %s'%(whatsapp_data.get('access_token')),
                'Content-Type': 'application/json',
            }
        _logger.info("---data---%s"%data)
        response = requests.post(DEFAULT_ENDPOINT+'/%s/messages'%(whatsapp_data.get('wa_phonenumber_id')), headers=headers, data=json.dumps(data))
        if 'error' not in response.json():
            record.partner_id.formetted_number = response.json().get('contacts')[0].get('wa_id')
            message.msg_uid = response.json().get('messages')[0].get('id')
            
            return response
        else:
            raise UserError(response.json().get('error'))
    
    def _send_location(self,partner,data,company_id):
        message_data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": partner.mobile or partner.phone,
            "type": "location",
            "location":data
        }
        post_values = {
            'body': "Location Send",
            'message_type': 'comment'
        }
        
        channel = self.find_active_channel(partner,company_id)
        channel.message_post()
        response = self.whatsapp_api_requests("POST", '/%s/messages'%(company_id.wa_phonenumber_id), data=json.dumps(message_data),company_id=company_id)
        _logger.info("=22-=-response %s"%response)
        if 'error' not in response:
            partner.formetted_number = response.get('contacts')[0].get('wa_id')
            
            return response
        else:
            raise UserError(response.json().get('error'))
    
    def _send_interactive(self,wa_template_id,wa_flow_id,partner,data,company_id,type,message_unique_id=False):
        _logger.info("=-=data  %s"%data)
        message_data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": partner.mobile or partner.phone,
            "type": "interactive",
            "interactive":{
                "type":type
            }
        }
        message_data['interactive'].update(data)
        
        post_values = {
            'body': data.get('body'),
            'message_type': 'comment'
        }
        
        channel = self.find_active_channel(partner,company_id)
        channel.message_post()
        
        post_values.update({
            'whatsapp_template_id':wa_template_id.id  if wa_template_id else False,
            'wa_flow_id':wa_flow_id.id  if wa_flow_id else False,
            'formetted_number':partner.formetted_number
        })
        
        if message_unique_id:post_values["message_unique_id"] = message_unique_id
        
        res_id = wa_template_id.id if wa_template_id else wa_flow_id.id if wa_flow_id else False
        model = wa_template_id._name if wa_template_id else wa_flow_id._name if wa_flow_id else False
        if 'model' in self._context:
            model = self._context.get('model')
        if 'res_id' in self._context:
            res_id = self._context.get('res_id')
        message = self.env['mail.message'].create(
            dict(post_values, res_id=res_id, model=model,
                 subtype_id=self.env['ir.model.data']._xmlid_to_res_id("mail.mt_note"))
        )
        _logger.info("=-=-message_data %s"%message_data)
        response = self.whatsapp_api_requests("POST", '/%s/messages'%(company_id.wa_phonenumber_id), data=json.dumps(message_data),company_id=company_id)
        _logger.info("=22-=-response %s"%response)
        if 'error' not in response:
            partner.formetted_number = response.get('contacts')[0].get('wa_id')
            message.msg_uid = response.get('messages')[0].get('id')
            
            return response
        else:
            raise UserError(response.json().get('error'))
    
    def send_message(self,partners,post_data,channel_partner_sudo,company_id):
        if company_id.whatsapp_user == channel_partner_sudo.partner_id:
            self._send(partners,post_data,company_id)
            
    def _send(self,partners,post_data,company_id):
        whatsapp_data = self.get_whatsapp_data(company_id)
        headers = {
                    'Authorization': 'Bearer %s'%(whatsapp_data.get('access_token')),
                    'Content-Type': 'application/json',
                }
        for partner in partners:
            if post_data.get('body',False):
                data = {
                      "messaging_product": "whatsapp",
                      "to": partner.mobile or partner.phone,
                      "type": "text",
                      "recipient_type": "individual",
                      "text": {
                        "body": post_data.get('body',False)
                      }
                }
                response = requests.post(DEFAULT_ENDPOINT+'/%s/messages'%(whatsapp_data.get('wa_phonenumber_id')), headers=headers, data=json.dumps(data))
                response = response.json()
                if 'error' not in response:
                    partner.formetted_number = response.get('contacts')[0].get('wa_id')
                    return response
            if post_data.get('attachment_ids',False):
                attachments = self.env['ir.attachment'].browse(post_data.get('attachment_ids',False))
                for attachment in attachments:
                    response = requests.post('https://graph.facebook.com/v18.0/%s/media'%(company_id.wa_phonenumber_id), headers={'Authorization': 'Bearer %s'%(whatsapp_data.get('access_token'))},files={'file':(attachment.name, attachment.datas, attachment.mimetype)},data={'type': attachment.mimetype,'messaging_product':'whatsapp'})
                    media_id = response.json().get('id')
                    data = {
                        "messaging_product": "whatsapp",
                        "to": partner.mobile or partner.phone,
                        "recipient_type": "individual",
                    }
                    if 'image' in attachment.mimetype:
                        data.update({
                            "type":"image",
                            "image": {
	                            "caption": attachment.name,
	                            "id": media_id
                            }
                        })
                    elif 'video' in attachment.mimetype:
                        data.update({
                            "type":"video",
                            "image": {
	                            "caption": attachment.name,
	                            "id": media_id
                            }
                        })
                    elif 'audio' in attachment.mimetype:
                        data.update({
                            "type":"audio",
                            "audio": {
	                            "id": media_id
                            }
                        })
                    else:
                        data.update({
                            "type":"document",
                            "document": {
	                            "id": media_id,
                        		"filename": attachment.name
                            }
                        })
                    response = requests.post('https://graph.facebook.com/v18.0/%s/messages'%(whatsapp_data.get('wa_phonenumber_id')), headers=headers, data=json.dumps(data))
                    if 'error' not in response.json():
                        partner.formetted_number = response.json().get('contacts')[0].get('wa_id')
                        return response
                        
    def find_active_channel(self,partner_id, company_id):
        channel_partners = self.env['discuss.channel.member'].sudo().search([('partner_id','=',partner_id.id)])
        whatsapp_user = self.env['discuss.channel.member'].sudo().search([('partner_id','=',company_id.whatsapp_user.id)])
        domain = [('channel_type','=','group'),('id','in',channel_partners.mapped('channel_id').ids),('channel_member_ids','in',channel_partners.ids),('channel_member_ids','in',whatsapp_user.ids)]
        channel = self.env['discuss.channel'].search(domain,limit=1)
        if not channel:
            vals = {
                'channel_member_ids':[(0,0,{'partner_id': partner_id.id}),(0,0,{'partner_id':company_id.whatsapp_user.id})],
                'channel_type':'group',
                'company_id':company_id.id,
                'name':"%s, %s"%(company_id.whatsapp_user.name,partner_id.name)
            }
            channel = self.env['discuss.channel'].sudo().create(vals)
        return channel
