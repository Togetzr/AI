from odoo import http, _
from odoo.http import request, Response
import logging
_logger = logging.getLogger(__name__)

class WhatsappControllers(http.Controller):
    
    @http.route(['/web/whatsapp/image/<string:model>/<int:id>/<string:field>'], type='http', auth="public")
    def content_image(self, xmlid=None, model='ir.attachment', id=None, field='raw',
                      filename_field='name', filename=None, mimetype=None, unique=False,
                      download=False, width=0, height=0, crop=False, access_token=None,
                      nocache=False):

        record = request.env['ir.binary'].sudo()._find_record(xmlid, model, id and int(id), access_token)
        stream = request.env['ir.binary'].sudo()._get_image_stream_from(
            record, field, filename=filename, filename_field=filename_field,
            mimetype=mimetype, width=int(width), height=int(height), crop=crop,
        )

        send_file_kwargs = {'as_attachment': download}
        if unique:
            send_file_kwargs['immutable'] = True
            send_file_kwargs['max_age'] = http.STATIC_CACHE_LONG
        if nocache:
            send_file_kwargs['max_age'] = None

        res = stream.get_response(**send_file_kwargs)
        res.headers['Content-Security-Policy'] = "default-src 'none'"
        return res
