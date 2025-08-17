# from odoo import http, fields
# from odoo.http import request
# from datetime import timedelta
# from dateutil.parser import isoparse
# from datetime import datetime
# from odoo.exceptions import ValidationError
# from odoo.tests.common import Form
#
#
# class BookingWebsiteController(http.Controller):
#
#     @http.route('/booking', type='http', auth='public', website=True)
#     def booking_page(self, **kwargs):
#         booking_type_id = int(kwargs.get('booking_type_id')) if kwargs.get('booking_type_id') else False
#         combination_id = int(kwargs.get('combination_id')) if kwargs.get('combination_id') else False
#         booking_env = request.env['resource.booking']
#
#         # Get all booking types
#         booking_types = request.env['resource.booking.type'].sudo().search([])
#         booking_type = request.env['resource.booking.type'].sudo().browse([booking_type_id])
#
#         # Get combinations for selected type
#         combinations_domain = []
#         if booking_type_id:
#             combinations_domain = [('type_rel_ids.type_id', '=', booking_type_id)]
#
#         combinations = request.env['resource.booking.combination'].sudo().search(combinations_domain)
#
#         # Use session ID to manage booking
#
#         session_key = f'booking_id_{request.session.sid}'
#         session_booking_id = request.session.get(session_key)
#         booking = booking_env.sudo().browse(session_booking_id) if session_booking_id else None
#
#         if not booking_type_id or not combination_id:
#             if booking and booking.exists():
#                 request.session.pop(session_key, None)
#             booking = None
#         else:
#             if booking and booking.exists():
#                 if booking.type_id.id != booking_type_id or booking.combination_id.id != combination_id:
#                     booking.write({
#                         'type_id': booking_type_id,
#                         'combination_id': combination_id,
#                     })
#             else:
#                 booking = booking_env.sudo().create({
#                     'type_id': booking_type_id,
#                     'combination_id': combination_id,
#                 })
#                 request.session[session_key] = booking.id
#
#         if not booking:
#             # fallback: any booking (as in old code)
#             booking = booking_env.sudo().search([], limit=1)
#
#         # Get datetime (naive)
#         now = fields.Datetime.now()
#         year = int(kwargs.get('year', now.year))
#         month = int(kwargs.get('month', now.month))
#
#         # Use model method to get calendar context and slots
#         calendar_context = booking._get_calendar_context(year=year, month=month, now=now)
#
#         # Filter out slots already booked (confirmed bookings)
#         if combination_id:
#             booked_slots = request.env['resource.booking'].sudo().search([
#                 ('combination_id', '=', combination_id),
#                 ('state', '=', 'confirmed'),
#             ])
#
#             # Collect booked datetimes (start times)
#             booked_datetimes = set()
#             for b in booked_slots:
#                 start_dt = fields.Datetime.from_string(b.start)
#                 booked_datetimes.add(start_dt)
#
#             # Filter slots
#             filtered_slots = {}
#             for date_key, slot_list in (calendar_context.get('slots') or {}).items():
#                 available_slots = [slot for slot in slot_list if slot not in booked_datetimes]
#                 if available_slots:
#                     filtered_slots[date_key] = available_slots
#
#             # Update context
#             calendar_context['slots'] = filtered_slots
#
#         values = {
#             'booking_types': booking_types,
#             'combinations': combinations,
#             'res_lang': calendar_context.get('res_lang'),
#             'booking': booking,
#             'calendar': calendar_context.get('calendar'),
#             'now': calendar_context.get('now'),
#             'slots': calendar_context.get('slots'),
#             'start': calendar_context.get('start'),
#             'weekday_names': calendar_context.get('weekday_names'),
#             'selected_type': booking_type_id,
#             'selected_combo': combination_id,
#             'access_token': booking.access_token,
#             'selected_type_tz': booking_type.resource_calendar_id.tz if booking_type and booking_type.resource_calendar_id else '',
#         }
#         return request.render('calendar_event_resource_sync.booking_template', values)
from odoo import http, fields
from odoo.http import request
from datetime import timedelta
from dateutil.parser import isoparse
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.tests.common import Form
import pytz



class BookingWebsiteController(http.Controller):

    @http.route('/booking', type='http', auth='public', website=True)
    def booking_page(self, **kwargs):
        booking_env = request.env['resource.booking']

        booking_type_id = int(kwargs.get('booking_type_id')) if kwargs.get('booking_type_id') else False
        combination_raw = kwargs.get('combination_id')
        if combination_raw == 'auto_assign':
            combination_id = 'auto_assign'
        elif combination_raw:
            combination_id = int(combination_raw)
        else:
            combination_id = False

        # Get all booking types
        booking_types = request.env['resource.booking.type'].sudo().search([])
        booking_type = request.env['resource.booking.type'].sudo().browse([booking_type_id])

        # Get combinations for selected type
        combinations_domain = []
        if booking_type_id:
            combinations_domain = [('type_rel_ids.type_id', '=', booking_type_id)]

        combinations = request.env['resource.booking.combination'].sudo().search(combinations_domain)

        # Use session ID to manage booking
        session_key = f'booking_id_{request.session.sid}'
        session_booking_id = request.session.get(session_key)
        booking = booking_env.sudo().browse(session_booking_id) if session_booking_id else None

        if not booking_type_id or not combination_id:
            if booking and booking.exists():
                request.session.pop(session_key, None)
            booking = None
        else:
            if booking and booking.exists():
                vals = {'type_id': booking_type_id}
                if combination_id == 'auto_assign':
                    vals.update({
                        'combination_auto_assign': True,
                        'combination_id': False,
                    })
                else:
                    vals.update({
                        'combination_auto_assign': False,
                        'combination_id': combination_id,
                    })
                booking.write(vals)
            else:
                vals = {'type_id': booking_type_id}
                if combination_id == 'auto_assign':
                    vals.update({
                        'combination_auto_assign': True,
                        'combination_id': False,
                    })
                else:
                    vals.update({
                        'combination_auto_assign': False,
                        'combination_id': combination_id,
                    })
                booking = booking_env.sudo().create(vals)
                request.session[session_key] = booking.id

        if not booking:
            # fallback: any booking
            booking = booking_env.sudo().search([], limit=1)

        # Get datetime (naive)
        now = fields.Datetime.now()
        year = int(kwargs.get('year', now.year))
        month = int(kwargs.get('month', now.month))

        # Use model method to get calendar context and slots
        calendar_context = booking._get_calendar_context(year=year, month=month, now=now)

        # Filter out slots already booked (confirmed bookings)
        if combination_id and combination_id != 'auto_assign':
            booked_slots = request.env['resource.booking'].sudo().search([
                ('combination_id', '=', combination_id),
                ('state', '=', 'confirmed'),
            ])

            booked_datetimes = set()
            for b in booked_slots:
                start_dt = fields.Datetime.from_string(b.start)
                booked_datetimes.add(start_dt)

            filtered_slots = {}
            for date_key, slot_list in (calendar_context.get('slots') or {}).items():
                available_slots = [slot for slot in slot_list if slot not in booked_datetimes]
                if available_slots:
                    filtered_slots[date_key] = available_slots

            calendar_context['slots'] = filtered_slots

        # Decide which value to mark as selected in UI
        selected_combo_value = (
            'auto_assign' if combination_id == 'auto_assign' else combination_id
        )

        values = {
            'booking_types': booking_types,
            'combinations': combinations,
            'res_lang': calendar_context.get('res_lang'),
            'booking': booking,
            'calendar': calendar_context.get('calendar'),
            'now': calendar_context.get('now'),
            'slots': calendar_context.get('slots'),
            'start': calendar_context.get('start'),
            'weekday_names': calendar_context.get('weekday_names'),
            'selected_type': booking_type_id,
            'selected_combo': selected_combo_value,
            'access_token': booking.access_token,
            'selected_type_tz': booking_type.resource_calendar_id.tz if booking_type and booking_type.resource_calendar_id else '',
        }
        return request.render('calendar_event_resource_sync.booking_template', values)


# class BookingController(http.Controller):
#
    # @http.route('/scheduled', type='http', auth="public", website=True, csrf=True, methods=['GET', 'POST'])
    # def portal_booking_scheduled(self, **post):
    #     # Check login
    #     if not request.env.user or request.env.user._is_public():
    #         request.session['booking_post_data'] = post
    #         return request.redirect('/web/login?redirect=/scheduled')
    #
    #     # Retrieve stored data after login if needed
    #     if not post and request.session.get('booking_post_data'):
    #         post = request.session.pop('booking_post_data')
    #
    #     when = post.get('when')
    #     booking_type_id = post.get('booking_type_id')
    #     combination_id = post.get('combination_id')
    #     access_token = post.get('access_token')
    #     booking_id = int(post.get('booking')) if post.get('booking') else False
    #
    #     if not (booking_type_id and combination_id and when):
    #         return request.redirect('/booking')
    #
    #     booking_env = request.env['resource.booking'].sudo()
    #
    #     when_tz_aware = isoparse(when)
    #     when_naive = datetime.utcfromtimestamp(when_tz_aware.timestamp())
    #
    #     booking_type = request.env['resource.booking.type'].sudo().browse(int(booking_type_id))
    #     combination = request.env['resource.booking.combination'].sudo().browse(int(combination_id))
    #     duration_hours = booking_type.duration if booking_type and booking_type.duration else 1.0
    #
    #     end_time = when_naive + timedelta(hours=duration_hours)
    #
    #     existing_booking = None
    #     if access_token:
    #         existing_booking = booking_env.search([('access_token', '=', access_token)], limit=1)
    #     elif booking_id:
    #         existing_booking = booking_env.search([('id', '=', booking_id)])
    #
    #     error_message = False
    #     booking = None
    #
    #     try:
    #         if existing_booking:
    #             booking = existing_booking
    #             booking.write({
    #                 'type_id': int(booking_type_id),
    #                 'combination_id': int(combination_id),
    #                 'start': when_naive,
    #                 'stop': end_time,
    #             })
    #         else:
    #             booking_vals = {
    #                 'type_id': int(booking_type_id),
    #                 'combination_id': int(combination_id),
    #                 'access_token': access_token,
    #                 'start': when_naive,
    #                 'stop': end_time,
    #                 'partner_id': request.env.user.partner_id.id,  # Store user who booked
    #             }
    #             booking = booking_env.create(booking_vals)
    #
    #         booking.action_confirm()
    #
    #         # ✅ Clear session booking ID after successful confirmation
    #         session_id = request.session.sid
    #         session_booking_key = f'booking_id_{session_id}'
    #         if session_booking_key in request.session:
    #             request.session.pop(session_booking_key)
    #
    #     except Exception as error:
    #         error_message = str(error)
    #
    #     values = {
    #         'when': when,
    #         'booking_type_id': booking_type.name if booking_type else '',
    #         'combination_id': combination.name if combination else '',
    #         'booking_id': booking.id if booking else '',
    #         'start': when_naive,
    #         'stop': end_time,
    #         'error_message': error_message,
    #     }
    #
    #     return request.render('calendar_event_resource_sync.booking_confirmation_template', values)

class BookingController(http.Controller):

    # @http.route('/scheduled', type='http', auth="public", website=True, csrf=True, methods=['GET', 'POST'])
    # def portal_booking_scheduled(self, **post):
    #     # Check login
    #     if not request.env.user or request.env.user._is_public():
    #         request.session['booking_post_data'] = post
    #         return request.redirect('/web/login?redirect=/scheduled')
    #
    #     if not post and request.session.get('booking_post_data'):
    #         post = request.session.pop('booking_post_data')
    #
    #     when = post.get('when')
    #     booking_type_id = post.get('booking_type_id')
    #     combination_raw = post.get('combination_id') or False
    #     access_token = post.get('access_token')
    #     booking_id = int(post.get('booking')) if post.get('booking') else False
    #
    #     if not (booking_type_id and combination_raw and when):
    #         return request.redirect('/booking')
    #
    #     booking_env = request.env['resource.booking'].sudo()
    #
    #     when_tz_aware = isoparse(when)
    #     when_naive = datetime.utcfromtimestamp(when_tz_aware.timestamp())
    #
    #     booking_type = request.env['resource.booking.type'].sudo().browse(int(booking_type_id))
    #     duration_hours = booking_type.duration if booking_type and booking_type.duration else 1.0
    #     end_time = when_naive + timedelta(hours=duration_hours)
    #
    #     existing_booking = None
    #     if access_token:
    #         existing_booking = booking_env.search([('access_token', '=', access_token)], limit=1)
    #     elif booking_id:
    #         existing_booking = booking_env.search([('id', '=', booking_id)], limit=1)
    #
    #     booking = None
    #
    #     # Build base vals first
    #     base_vals = {
    #         'type_id': int(booking_type_id),
    #         'start': when_naive,
    #         'stop': end_time,
    #         'partner_id': request.env.user.partner_id.id,
    #     }
    #     booking = existing_booking
    #
    #     if existing_booking and combination_raw != 'auto_assign':
    #         booking.write({
    #             'type_id': int(booking_type_id),
    #             'combination_id': int(combination_raw),
    #             'start': when_naive,
    #             'stop': end_time,
    #             'partner_id': request.env.user.partner_id.id,
    #
    #         })
    #     elif existing_booking and combination_raw == 'auto_assign':
    #         booking.write(base_vals)
    #     else:
    #         booking = booking_env.create(base_vals)
    #         booking.write({
    #             'combination_id': int(combination_raw),
    #         })
    #
    #     # Final validation
    #     if not booking.combination_id:
    #         raise ValidationError("Cannot schedule this booking because no resources are available or assigned.")
    #
    #     # Confirm
    #     booking.action_confirm()
    #
    #     # Clear session key
    #     session_id = request.session.sid
    #     session_booking_key = f'booking_id_{session_id}'
    #     if session_booking_key in request.session:
    #         request.session.pop(session_booking_key)
    #
    #     values = {
    #         'when': when,
    #         'booking_type_id': booking_type.name if booking_type else '',
    #         'combination_id': booking.combination_id.name if booking.combination_id else '',
    #         'booking_id': booking.id if booking else '',
    #         'start': when_naive,
    #         'stop': end_time,
    #         'error_message': False,
    #     }
    #
    #     return request.render('calendar_event_resource_sync.booking_confirmation_template', values)
    @http.route('/scheduled', type='http', auth="public", website=True, csrf=True, methods=['GET', 'POST'])
    def portal_booking_scheduled(self, **post):
        # Check login
        if not request.env.user or request.env.user._is_public():
            request.session['booking_post_data'] = post
            return request.redirect('/web/login?redirect=/scheduled')

        if not post and request.session.get('booking_post_data'):
            post = request.session.pop('booking_post_data')

        when = post.get('when')
        booking_type_id = post.get('booking_type_id')
        combination_raw = post.get('combination_id') or False
        access_token = post.get('access_token')
        booking_id = int(post.get('booking')) if post.get('booking') else False

        if not (booking_type_id and combination_raw and when):
            return request.redirect('/booking')

        booking_env = request.env['resource.booking'].sudo()

        try:
            when_tz_aware = isoparse(when)
        except Exception:
            raise ValidationError("Invalid datetime format for 'when'.")

        when_naive = datetime.utcfromtimestamp(when_tz_aware.timestamp())

        booking_type = request.env['resource.booking.type'].sudo().browse(int(booking_type_id))
        if not booking_type.exists():
            raise ValidationError("Invalid booking type.")

        duration_hours = booking_type.duration if booking_type.duration else 1.0
        end_time = when_naive + timedelta(hours=duration_hours)

        existing_booking = None
        if access_token:
            existing_booking = booking_env.search([('access_token', '=', access_token)], limit=1)
        elif booking_id:
            existing_booking = booking_env.search([('id', '=', booking_id)], limit=1)

        base_vals = {
            'type_id': int(booking_type_id),
            'start': when_naive,
            'stop': end_time,
            'partner_id': request.env.user.partner_id.id,
        }

        booking = existing_booking

        if existing_booking and combination_raw != 'auto_assign':
            booking.write({
                'type_id': int(booking_type_id),
                'combination_id': int(combination_raw),
                'start': when_naive,
                'stop': end_time,
                'partner_id': request.env.user.partner_id.id,
            })
        elif existing_booking and combination_raw == 'auto_assign':
            booking.write(base_vals)
        else:
            booking = booking_env.create(base_vals)
            booking.write({
                'combination_id': int(combination_raw),
            })

        if not booking.combination_id:
            raise ValidationError("Cannot schedule this booking because no resources are available or assigned.")

        booking.action_confirm()

        # Clear session key
        session_id = request.session.sid
        session_booking_key = f'booking_id_{session_id}'
        if session_booking_key in request.session:
            request.session.pop(session_booking_key)


        # Define Paris timezone
        paris_tz = pytz.timezone('Europe/Paris')

        # Convert start (when_tz_aware) to Paris timezone
        start_in_paris = when_tz_aware.astimezone(paris_tz)

        # Compute end_time from when_naive (UTC naive), then localize to UTC and convert
        end_time_naive = when_naive + timedelta(hours=duration_hours)
        end_time_utc = pytz.utc.localize(end_time_naive)
        stop_in_paris = end_time_utc.astimezone(paris_tz)

        # Prepare values
        values = {
            'when': when,
            'booking_type_id': booking_type.name if booking_type else '',
            'combination_id': booking.combination_id.name if booking.combination_id else '',
            'booking_id': booking.id,
            'start': start_in_paris.strftime('%Y-%m-%d %H:%M'),
            'stop': stop_in_paris.strftime('%Y-%m-%d %H:%M'),
            'error_message': False,
        }

        return request.render('calendar_event_resource_sync.booking_confirmation_template', values)
