# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from markupsafe import Markup
from werkzeug import urls
from werkzeug.exceptions import Forbidden
import werkzeug.datastructures
import json
import os
from base64 import b64decode, b64encode
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1, hashes
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

from datetime import datetime, timedelta, date
from http import HTTPStatus
from odoo.tools import plaintext2html
import mimetypes

import logging
_logger = logging.getLogger("all_messages")

PRIVATE_KEY = os.environ.get('PRIVATE_KEY')

class PortalReports(http.Controller):
    
    @http.route(['/c'], type='http', auth="none",methods=['POST', 'GET'], csrf=False)
    def whatsapp_trigger(self, **kwargs):
        return  request.redirect('https://wa.me/c/33763266762')
    
    @http.route(['/get-private-key'], methods=['GET'],type='json', auth="public", website=True,cors="*")
    def get_wa_private_key(self,**kw):
        data = json.loads(request.httprequest.data)
        PRIVATE_KEY = request.env['res.company'].sudo().search([('webhook_verify_token', '=', data.get("params").get("security_token",False))])
        return {'key':b64decode(PRIVATE_KEY.private_key_attachment).decode('utf-8').encode('utf-8') if PRIVATE_KEY else False}
    
    @http.route(['/wa-django/flow'], methods=['POST'],type='json', auth="public", website=True)
    def whatsapp_django_data_flow(self,**kw):
        data = json.loads(request.httprequest.data)
        _logger.info("-=-data--%s"%data)
        if data.get('action',False) == 'ping':
            return {
                    "data": {
                        "status": "active"
                    }
                }
        result = {}
#        
        message = request.env['mail.message'].sudo().search([('message_unique_id', '=', data.get('flow_token'))])
        _logger.info("---message----------%s"%message)
        if message.wa_flow_id:
            if data.get("screen") == "QUESTION_ONE":
                result = {
                    "version": '3.1',
                    "screen": "BOOKING_INFO",
                    "data": {
                        "chair_id":data.get('data').get('chair_id'),
                        "services":data.get('data').get('services'),
                        "min_date":str(int( datetime.now().timestamp() * 1000)),
                        "max_date":str(int( (datetime.now() + timedelta(days=7)).timestamp() * 1000)),
                        "data_source":[
                              {
                                "id": "09:00",
                                "title": "09:00"
                              },
                              {
                                "id": "09:30",
                                "title": "09:30"
                              },
                              {
                                "id": "10:00",
                                "title": "10:00"
                              },
                              {
                                "id": "10:30",
                                "title": "10:30"
                              },
                              {
                                "id": "11:00",
                                "title": "11:00"
                              },
                              {
                                "id": "11:30",
                                "title": "11:30"
                              },
                              {
                                "id": "12:00",
                                "title": "12:00"
                              },
                              {
                                "id": "12:30",
                                "title": "12:30"
                              },
                              {
                                "id": "13:00",
                                "title": "13:00"
                              },
                              {
                                "id": "13:30",
                                "title": "13:30"
                              },
                              {
                                "id": "14:00",
                                "title": "14:00"
                              },
                              {
                                "id": "14:30",
                                "title": "14:30"
                              },
                              {
                                "id": "15:00",
                                "title": "15:00"
                              },
                              {
                                "id": "15:30",
                                "title": "15:30"
                              },
                              {
                                "id": "16:00",
                                "title": "16:00"
                              },
                              {
                                "id": "16:30",
                                "title": "16:30"
                              },
                              {
                                "id": "17:00",
                                "title": "17:00"
                              },
                              {
                                "id": "17:30",
                                "title": "17:30"
                              },
                              {
                                "id": "18:00",
                                "title": "18:00"
                              }
                            ]
                        },
                    }
            elif data.get("screen") == "BOOKING_INFO":
                if data.get("data").get("component_action",False) and data.get("data").get("component_action",False) == 'update_date':
                    result = {
                        "version": '3.0',
                        "screen": "BOOKING_INFO",
                        "data": {
                            "data_source":[
                                  {
                                    "id": "09:30",
                                    "title": "09:30"
                                  },
                                  {
                                    "id": "10:00",
                                    "title": "10:00"
                                  },
                                  {
                                    "id": "10:30",
                                    "title": "10:30"
                                  },
                                  {
                                    "id": "11:00",
                                    "title": "11:00"
                                  },
                                  {
                                    "id": "11:30",
                                    "title": "11:30"
                                  },
                                  {
                                    "id": "12:00",
                                    "title": "12:00"
                                  },
                                  {
                                    "id": "12:30",
                                    "title": "12:30"
                                  },
                                  {
                                    "id": "13:00",
                                    "title": "13:00"
                                  },
                                  {
                                    "id": "13:30",
                                    "title": "13:30"
                                  },
                                  {
                                    "id": "14:00",
                                    "title": "14:00"
                                  },
                                  {
                                    "id": "14:30",
                                    "title": "14:30"
                                  },
                                  {
                                    "id": "15:00",
                                    "title": "15:00"
                                  },
                                  {
                                    "id": "15:30",
                                    "title": "15:30"
                                  },
                                  {
                                    "id": "16:00",
                                    "title": "16:00"
                                  },
                                  {
                                    "id": "16:30",
                                    "title": "16:30"
                                  },
                                  {
                                    "id": "17:00",
                                    "title": "17:00"
                                  },
                                  {
                                    "id": "17:30",
                                    "title": "17:30"
                                  },
                                  {
                                    "id": "18:00",
                                    "title": "18:00"
                                  }
                                ]
                            },
                        }
        
        _logger.info("---result---%s"%result)
        return result
    
    @http.route(['/sign-up-flow'], methods=['POST'],type='json', auth="public", website=True)
#    @wa.on_flow_request("/sign-up-flow")
    def on_sign_up_request(self,**kw):
        data = json.loads(request.httprequest.data)
        _logger.info('--->data   %s'%data)
        encrypted_flow_data_b64 = data['encrypted_flow_data']
        encrypted_aes_key_b64 = data['encrypted_aes_key']
        initial_vector_b64 = data['initial_vector']

        decrypted_data, aes_key, iv = self.decrypt_request(
            encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64)
        _logger.info('--->decrypted_data   %s'%decrypted_data)
        response = dict(
            version=data.get('version'),
            screen="SIGN_UP",
            error_message="You are not registered. Please sign up",
            data={
                "first_name_initial_value": "",
                "last_name_initial_value": "",
                "email_initial_value": "mayurnagar7069@gmail.com",
                "password_initial_value": "",
                "confirm_password_initial_value": "",
            },
        )

        encrypted_response = self.encrypt_response(response, aes_key, iv)
        _logger.info("=--encrypted_response---%s"%encrypted_response)
        headers = werkzeug.datastructures.Headers(None)
        headers['Content-Type'] = 'text/plain;charset=utf-8'
        response = request.make_response(encrypted_response,headers=headers.to_wsgi_list())
        return response
#        if flow.action == FlowRequestActionType.DATA_EXCHANGE:
#            if flow.screen == "SIGN_UP":
#                if user_repository.exists(flow.data["email"]):
#                    ...
#                elif flow.data["password"] != flow.data["confirm_password"]:
#                    ...
#                elif not any(char.isdigit() for char in flow.data["password"]):
#                    ...
#                else:
#                    ...
#            elif flow.screen == "LOGIN":
#                ...
#            elif flow.screen == "LOGIN_SUCCESS":
#            ...
    
    
    def decrypt_request(self,encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64):
        flow_data = b64decode(encrypted_flow_data_b64)
        iv = b64decode(initial_vector_b64)

        encrypted_aes_key = b64decode(encrypted_aes_key_b64)
        PRIVATE_KEY = request.env['res.company'].search([],limit=1)
        encoded_data = b64decode(PRIVATE_KEY.private_key_attachment).decode('utf-8').encode('utf-8')
        
        private_key = load_pem_private_key(
            encoded_data, password=None)
        aes_key = private_key.decrypt(encrypted_aes_key, OAEP(
            mgf=MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

        encrypted_flow_data_body = flow_data[:-16]
        encrypted_flow_data_tag = flow_data[-16:]
        decryptor = Cipher(algorithms.AES(aes_key),
                           modes.GCM(iv, encrypted_flow_data_tag)).decryptor()
                           
        decrypted_data_bytes = (decryptor.update(
            encrypted_flow_data_body) + decryptor.finalize())
        decrypted_data = json.loads(decrypted_data_bytes.decode("utf-8"))
        return decrypted_data, aes_key, iv


    def encrypt_response(self,response, aes_key, iv):
        flipped_iv = bytearray()
        for byte in iv:
            flipped_iv.append(byte ^ 0xFF)

        encryptor = Cipher(algorithms.AES(aes_key),
                           modes.GCM(flipped_iv)).encryptor()

        return b64encode(
            encryptor.update(json.dumps(response).encode("utf-8")) +
            encryptor.finalize() +
            encryptor.tag
        ).decode("utf-8")
    
    @http.route(['/wa-fastapi/flow'], methods=['POST'],type='json', auth="public", website=True)
    def whatsapp_fastapi_data_flow(self,**kw):
        data = json.loads(request.httprequest.data)
        _logger.info("-=-data--%s"%data)
        result = {}
        
        message = request.env['mail.message'].sudo().search([('message_unique_id', '=', data.get('flow_token'))])
        _logger.info("---message----------%s"%message)
        if message.wa_flow_id:
            result = {"screen": "BOOKING_INFO",
                        "data": {
                            "chair_id":"1",
                            "services":["1"]
                        }
                    }
        
        if data.get("screen") == "LOGIN":
            if  data.get("data",{}).get("email",False) == 'admin@itieit.com':
                result = dict(screen="LOGIN_SUCCESS",
                    data={})
            else:
                result = dict(screen="SIGN_UP",
                    error_message="You are not registered. Please sign up",
                    data={
                        "first_name_initial_value": "",
                        "last_name_initial_value": "",
                        "email_initial_value": data.get("data",{}).get("email",False),
                        "password_initial_value": "",
                        "confirm_password_initial_value": "",
                    })
        _logger.info("-=-result--%s"%result)
        return result
    
    @http.route(['/wa-data-exchange'], methods=['POST'],type='json', auth="public", website=True)
    def whatsapp_data_exchange_flow(self,**kw):
        data = json.loads(request.httprequest.data)

        encrypted_flow_data_b64 = data['encrypted_flow_data']
        encrypted_aes_key_b64 = data['encrypted_aes_key']
        initial_vector_b64 = data['initial_vector']

        decrypted_data, aes_key, iv = self.decrypt_request(
            encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64)
        _logger.info("----decrypted_data---%s"%decrypted_data)
        print(decrypted_data)

        response = {
            "version": "3.1",
            "screen": "BOOKING_INFO",
            "data": {
                "chair_id":"1",
                "services":["1"]
            },
        }
        _logger.info("=-=-response   %s"%response)
        encrypted_response = self.encrypt_response(response, aes_key, iv)
        _logger.info("=-=-encrypted_response   %s"%encrypted_response)
        headers = werkzeug.datastructures.Headers(None)
        headers['Content-Type'] = 'text/plain;charset=utf-8'
        response = request.make_response(encrypted_response,headers=headers.to_wsgi_list())
        return response
#        return encrypted_response,200
    
    @http.route(['/wa-callback'], methods=['GET'],type='http', auth="public", website=True)
    def whatsapp_callback_detail(self, **kw):
        token = kw.get('hub.verify_token')
        mode = kw.get('hub.mode')
        challenge = kw.get('hub.challenge')
        _logger.info("---token %s"%token)
        if not (token and mode and challenge):
            return Forbidden()
        wa_account = request.env['res.company'].sudo().search([('webhook_verify_token', '=', token)])
        if mode == 'subscribe' and wa_account:
            response = request.make_response(challenge)
            response.status_code = HTTPStatus.OK
            return response
        response = request.make_response({})
        response.status_code = HTTPStatus.FORBIDDEN
        return response
        
    
    @http.route(['/wa-callback'], methods=['POST'],type='json', auth="public", website=True)
    def whatsapp_callback_detail_POST(self, **kw):
        data = json.loads(request.httprequest.data)
        _logger.info("webhook wa :- %s"%data)
        
        for entry in data['entry']:
            account_id = entry['id']
            for changes in entry.get('changes', []):
                value = changes['value']
                phone_number_id = value.get('metadata', {}).get('phone_number_id', {})
                if not phone_number_id:
                    phone_number_id = value.get('whatsapp_business_api_data', {}).get('phone_number_id', {})
                if phone_number_id:
                    wa_account_id = request.env['res.company'].sudo().search([
                        ('wa_phonenumber_id', '=', phone_number_id), ('waba_id', '=', account_id)])
                    if wa_account_id and changes['field'] == 'messages':
                        for message in value.get('messages',[]):
                            _logger.info('message  %s'%message)
                            sender_name = value.get('contacts', [{}])[0].get('profile', {}).get('name')
                            from_number = message.get('from')
                            message_type = message.get('type')

                            channel,auther_id,contact_exist = wa_account_id.find_active_channel(from_number, sender_name=sender_name, create_if_not_found=True)
                            _logger.info("=-=-auther %s--%s"%(channel,auther_id))
                            if channel:
                                
                                kwargs = {
                                    'author_id': auther_id.id,
                                    'subtype_xmlid': 'mail.mt_comment',
                                }
#                                if 'context' in message:
#                                    kwargs['msg_uid'] = message['context'].get('id')
                                if message_type == 'text':
                                    kwargs['body'] = plaintext2html(message['text']['body'])
                                    wa_account_id.send_default_template_message(message,auther_id,wa_account_id,contact_exist)
                                elif message_type in ('document', 'image', 'audio', 'video', 'sticker'):
                                    filename = message[message_type].get('filename')
                                    mime_type = message[message_type].get('mime_type')
                                    caption = message[message_type].get('caption')
                                    document_id = message[message_type]['id']
                                    whatsapp = request.env['whatsapp']
                                    datas = whatsapp.get_whatsapp_documents(f"/{document_id}")
                                    if not filename:
                                        extension = mimetypes.guess_extension(mime_type) or ''
                                        filename = message_type + extension
                                    kwargs['attachments'] = [(filename, datas)]
                                    if caption:
                                        kwargs['body'] = plaintext2html(caption)
                                elif message_type == 'button' or (message_type == 'interactive' and message.get('interactive').get('type') == 'button_reply'):
                                    button_name = wa_account_id.whatsapp_button_click(message,auther_id,wa_account_id)
                                    kwargs['body'] = button_name
                                elif message_type == 'location':
                                    kwargs['body'] = wa_account_id.whatsapp_location_button(message,auther_id,wa_account_id)
                                else:
                                    result = wa_account_id.unsupported_type(message,auther_id,wa_account_id)
                                    if result:
                                        kwargs.update(result)
                                    else:
                                        _logger.warning("Unsupported whatsapp message type: %s", message)
                                        continue
                                    _logger.info("----kwargs %s"%kwargs)
                                channel.message_post(message_type='comment',**kwargs)
