# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
import json
import os
import logging
from base64 import b64decode, b64encode
import requests
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from odoo.addons.tz_whatsapp_integration.controllers.main import PortalReports

_logger = logging.getLogger(__name__)

def decrypt_request(encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64,wa_private_key):
    flow_data = b64decode(encrypted_flow_data_b64)
    iv = b64decode(initial_vector_b64)

    # Decrypt the AES encryption key
    encrypted_aes_key = b64decode(encrypted_aes_key_b64)
#    private_key = load_pem_private_key(
#        PRIVATE_KEY.encode('utf-8'), password=None)
    private_key = load_pem_private_key(
        wa_private_key.encode('utf-8'), password=None)
        
    aes_key = private_key.decrypt(encrypted_aes_key, OAEP(
        mgf=MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

    # Decrypt the Flow data
    encrypted_flow_data_body = flow_data[:-16]
    encrypted_flow_data_tag = flow_data[-16:]
    decryptor = Cipher(algorithms.AES(aes_key),
                        modes.GCM(iv, encrypted_flow_data_tag)).decryptor()
    decrypted_data_bytes = decryptor.update(
        encrypted_flow_data_body) + decryptor.finalize()
    decrypted_data = json.loads(decrypted_data_bytes.decode("utf-8"))
    return decrypted_data, aes_key, iv

def encrypt_response(response, aes_key, iv):
    # Flip the initialization vector
    flipped_iv = bytearray()
    for byte in iv:
        flipped_iv.append(byte ^ 0xFF)

    # Encrypt the response data
    encryptor = Cipher(algorithms.AES(aes_key),
                        modes.GCM(flipped_iv)).encryptor()
    return b64encode(
        encryptor.update(json.dumps(response).encode("utf-8")) +
        encryptor.finalize() +
        encryptor.tag
    ).decode("utf-8")


class WAIntegrationController(http.Controller):

    @http.route('/api/whatsapp-flow/data-exchange', type='http', auth='public', methods=['POST'], csrf=False)
    def data(self, **kwargs):
        data = json.loads(request.httprequest.get_data().decode('utf-8'))
        kwargs.update(data)
#        client_domain = kwargs.get('default_url', 'demo.itieit.com')
#        if client_domain not in request.env['ir.config_parameter'].sudo().get_param('web.base.url'):
#            headers = {
#                'Content-Type': 'application/x-www-form-urlencoded'
#            }
#            return requests.post(f"https://{client_domain}/api/whatsapp-flow/data-exchange", headers=headers, data=data)
        #try:
        # Fetch the parameters
#        client_domain = kwargs.get('default_url', 'demo.itieit.com')
        client_domain = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        wa_token = "watogetzr"

        # Get private key from external service
#        url = f"{client_domain}/get-private-key"
#        payload = json.dumps({"params": {"security_token": wa_token}})
#        headers = {
#            'Content-Type': 'application/json',
#            'user-token': 'mmmmmmm'
#        }

#        response = requests.get(url, headers=headers, data=payload)
#        response.raise_for_status()  # Raise an error if the request failed
#        wa_private_key = response.json().get('result', {}).get('key')
        
        PRIVATE_KEY = request.env['res.company'].sudo().search([('private_key_attachment','!=',False)],limit=1)
        
        wa_private_key = b64decode(PRIVATE_KEY.private_key_attachment).decode('utf-8')
        if not wa_private_key:
            return {"error": "Failed to get private key"}

        # Parse the encrypted data
        encrypted_flow_data_b64 = kwargs.get('encrypted_flow_data')
        encrypted_aes_key_b64 = kwargs.get('encrypted_aes_key')
        initial_vector_b64 = kwargs.get('initial_vector')

        # Decrypt the request data
        decrypted_data, aes_key, iv = decrypt_request(
            encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64, wa_private_key
        )
        _logger.info("--decrypted_data-%s"%decrypted_data)
        # Send decrypted data to external flow endpoint
        flow_url = f"http://localhost:8069/wa-django/flow"
        payload = json.dumps(decrypted_data)
        headers = {'Content-Type': 'application/json'}

        flow_response = requests.post(flow_url, headers=headers, data=payload)
#        flow_response.raise_for_status()
#        # Encrypt the response data
        encrypted_response = encrypt_response(flow_response.json().get('result'), aes_key, iv)

        # Return the encrypted response
        return request.make_response(encrypted_response, [('Content-Type', 'text/plain')])
