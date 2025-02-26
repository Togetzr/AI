# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.mail.controllers.thread import ThreadController
from odoo import http
from odoo.http import request
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
import logging
_logger = logging.getLogger(__name__)

class DISCUSSCONTROLLER(ThreadController):
    
    @http.route('/mail/message/post', methods=['POST'], type='json', auth='public')
    @add_guest_to_context
    def mail_message_post(self, thread_model, thread_id, post_data, context=None):
        message_data = super(DISCUSSCONTROLLER,self).mail_message_post(thread_model=thread_model, thread_id=thread_id, post_data=post_data, context=context)
        _logger.info("--post_data %s"%post_data)
        _logger.info("--thread_model %s"%thread_model)
        _logger.info("--thread_id %s"%message_data)
        thread = request.env[thread_model].sudo().browse(int(thread_id))
        partners = thread.channel_member_ids.mapped('partner_id') - request.env['res.partner'].sudo().browse(message_data.get('author').get('id'))
        channel_partner_sudo = request.env['res.users'].sudo().search([('partner_id','=',message_data.get('author').get('id'))],limit=1)
        whatsapp = request.env['whatsapp']
        whatsapp.send_message(partners,post_data,channel_partner_sudo,thread.company_id)
        return message_data
        
#         {'id': 878, 'body': Markup('<p>Hello</p>'), 'date': datetime.datetime(2024, 8, 21, 13, 47, 50), 'email_from': '"Administrator" <admin@togetzr.com>', 'message_type': 'comment', 'subtype_id': (1, 'Discussions'), 'subject': False, 'model': 'discuss.channel', 'res_id': 3, 'record_name': 'Administrator, Mayur NAGAR', 'starred_partner_ids': [], 'author': {'id': 3, 'name': 'Administrator', 'is_company': False, 'user': {'id': 2, 'isInternalUser': True}, 'type': 'partner'}, 'default_subject': 'Administrator, Mayur NAGAR', 'notifications': [], 'attachments': [], 'trackingValues': [], 'linkPreviews': [], 'reactions': [], 'pinned_at': False, 'create_date': datetime.datetime(2024, 8, 21, 13, 47, 50, 597988), 'write_date': datetime.datetime(2024, 8, 21, 13, 47, 50, 597988), 'needaction_partner_ids': [], 'history_partner_ids': [], 'is_note': False, 'is_discussion': True, 'subtype_description': False, 'recipients': [], 'scheduledDatetime': False, 'module_icon': '/mail/static/description/icon.png', 'sms_ids': [], 'temporary_id': 876.01}

