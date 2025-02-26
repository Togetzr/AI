# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import pytz
from odoo import http,fields, _
from odoo.http import request
from odoo.addons.tz_whatsapp_integration.controllers.main import PortalReports
from odoo.addons.resource_booking.models.resource_booking import _availability_is_fitting
from odoo.addons.resource.models.utils import  float_to_time
import json
from datetime import datetime, timedelta
import locale
import logging
_logger = logging.getLogger("wp_data_flow")

class WhatsappResourseFlow(PortalReports):

    def get_resource_calendar_attendance_slot(self, data=None):
        resource_booking = request.env['resource.booking'].sudo()
        combination_id = request.env['resource.booking.combination'].sudo().search([('id','=',int(data.get("data").get("resourse",False)))]) if data.get('data').get('resourse',False) and data.get('data').get('resourse',False) != 'AutoAssign' else False
        type_id = request.env['resource.booking.type'].sudo().browse(int(data.get('data').get('services')))
        sorted_combinations = combination_id if combination_id else type_id._get_combinations_priorized()
        slots = []
        _logger.info(f"slot data -> {data}")
        if data.get("data").get("appointment",False):
            resource_booking_type = request.env['resource.booking.type'].sudo().search([('id','=',int(data.get("data").get("services",False)))])
            day = datetime.strptime(data.get("data").get("appointment",False), '%Y-%m-%d')
            booking_times = resource_booking_type.resource_calendar_id.attendance_ids.filtered(lambda x:x.dayofweek == str(day.weekday()) and x.day_period != 'lunch')
            # company_time_zone = self.env.company.resource_tz or 'Europe/Paris'
            for booking_time in booking_times:
                start_time = datetime.combine(day, float_to_time(booking_time.hour_from))
                end_time = datetime.combine(day, float_to_time(booking_time.hour_to))
                # _logger.info(f"start_time-start_time-start_time {start_time}")
                current_time = start_time
                day_records = request.env['resource.booking'].sudo().search([('start', '>=', day), ('stop', '<', day + timedelta(days=1)), ('combination_id', 'in', sorted_combinations.ids)])
                company_time_zone = request.env.company.resource_tz or 'Europe/Paris'

                while current_time < end_time:
                    next_time = current_time + timedelta(minutes=30)
                    slot_available = True
                    for record in day_records:
                        utc_timezone = pytz.utc
                        utc_time = utc_timezone.localize(record.start)
                        paris_timezone = pytz.timezone(company_time_zone)
                        paris_time = utc_time.astimezone(paris_timezone)
                        paris_time = paris_time.replace(tzinfo=None)
                        slot_available = current_time != paris_time
                        # _logger.info(f"slot -> {slot_available} paris {paris_time}, current {current_time}")
                        if not slot_available:
                            break

                    slots.append({
                        "id":f"{current_time.strftime('%H:%M')}",
                        "title":f"{current_time.strftime('%H:%M')} - {next_time.strftime('%H:%M')}",
                        "enabled":slot_available})
                    current_time = next_time


                #while current_time < end_time:
                    #next_time = current_time + timedelta(minutes=30)
                    #slot_available = True
                    # resource_booking_ids = request.env['resource.booking'].sudo().search([('start','<=',current_time),('stop','>',current_time),('combination_id','in',sorted_combinations.ids)])
                    # existing_record = request.env['resource.booking'].sudo().search([('combination_id', 'in', sorted_combinations.ids)])
                    #resource_booking_ids = request.env['resource.booking'].sudo().search([('start','<=',current_time),('stop','>',current_time),('combination_id','in',sorted_combinations.ids)])
                    #_logger.info(f"in while loop {current_time}")
                    # _logger.info(f"in while loop without condistion -- {existing_record.start} - {existing_record.stop}")
                    # _logger.info(f"found record resource_booking_ids -- {resource_booking_ids} {resource_booking_ids.start} - {resource_booking_ids.stop}")
                    #if resource_booking_ids and len(sorted_combinations) == len(resource_booking_ids.mapped('combination_id')):
                    #    slot_available = False
                    #slots.append({
                    #    "id":f"{current_time.strftime('%H:%M')}",
                    #    "title":f"{current_time.strftime('%H:%M')} - {next_time.strftime('%H:%M')}",
                    #    "enabled":slot_available})
                    #current_time = next_time
        
        return slots


    def get_resource_calendar_attendance1(self ,cal_type=None):
        locale.setlocale(locale.LC_TIME, "%s.UTF-8"%(request.env.user.lang))
        #locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
        #locale.setlocale(locale.LC_TIME, "ar_SA.UTF-8")
        if cal_type:
            cal_type = int(cal_type)

            booking_type = request.env['resource.booking.type'].sudo().search([('id', '=', cal_type)])
            if booking_type:
                attendances = booking_type.resource_calendar_id.attendance_ids
                # Filter attendances to include only records where day_period is not 'lunch'
                filtered_attendances = attendances.filtered(lambda att: att.day_period != 'lunch')

                x = filtered_attendances.mapped('dayofweek')
            print('x >>>>>>> ' , x)
        today = datetime.now().date()

        # Get the start date (today) and end date (today + 7 days)
        end_date = today + timedelta(days=7)

        # Initialize response list
        response = []

        # Iterate through the days from today to the end date
        current_date = today+ timedelta(days=1)
        while current_date <= end_date:
            print('current_date.weekday()' , current_date.weekday())
            # Check if the current day is a working day (you can customize this based on your logic)
            if current_date.weekday() < 7  :  # Assuming Monday to Friday are working days
                response.append({
                    'id': current_date.strftime('%Y-%m-%d'),
                    'title': "%s %s"%(current_date.strftime("%A").capitalize(),current_date.strftime('%d-%m-%Y')) ,
         #           'title': current_date.strftime('%d-%m-%Y') ,
                    'valid' : True if  str(current_date.weekday()) in x else False
                })

            # Move to the next day
            current_date += timedelta(days=1)

        return response
    
    @http.route(['/wa-django/flow'], methods=['POST'],type='json', auth="public", website=True)
    def whatsapp_django_data_flow(self,**kw):
        data = json.loads(request.httprequest.data)
        _logger.info(f"all data {data}")
        # _logger.info("---data---%s"%data)
        message = request.env['mail.message'].sudo().search([('message_unique_id', '=', data.get('flow_token'))])
        # _logger.info("---->message<-----%s---%s"%(message,message.wa_flow_id))
        
        if message.wa_flow_id and message.wa_flow_id.is_resourse_flow:
            result = {}
            if message.wa_flow_id.flow_type == 'modifier':
                bookings = request.env[message.model].sudo().browse(message.res_id)
                if data.get("screen") == "QUESTION_ONE":
                    if data.get("data").get("component_action",False) and data.get("data").get("component_action",False) == 'update_resource':
                        if data.get("data").get("resourse",False):
                            booking_combination = request.env['resource.booking.combination'].sudo().search([('id','=',int(data.get("data").get("resourse",False)))])
                            combination_rel = request.env['resource.booking.type.combination.rel'].sudo().search([('combination_id','in',booking_combination.ids)])
                            booking_types = request.env['resource.booking.type'].sudo().search([('combination_rel_ids','in',combination_rel.ids),('gender','in',[False,data.get('data').get('gender',False)])])
                        else:
                            booking_types = request.env['resource.booking.type'].sudo().search([('gender','in',[False,data.get('data').get('gender',False)])])
                        services_source = [{
                                        "id":str(x.id),
                                        "title":x.name
                                    } for x in booking_types]
                        result = {
                            "version": '3.1',
                            "screen": "QUESTION_ONE",
                            "data": {
                                "name":data.get('data').get('name'),
                                "family_name":data.get('data').get('family_name'),
                                "gender":data.get('data').get('gender',''),
    #                            "resourse_source":resourse_source,
                                "services_source":services_source,
                                "date_source":[{"id":"selection","title":"Please Select Service"}],
                                "time_source":[{"id":"selection","title":"Please Select Service"}]
                                },
                            }
                    elif data.get("data").get("component_action",False) and data.get("data").get("component_action",False) == 'update_services':
                        today = datetime.now()
                        data_resource = self.get_resource_calendar_attendance1(data.get('data').get('services'))
                        date_res =[]
                        for i in data_resource:
                            if i['valid']:
                                date_res.append({
                                    "id" : i['id'],
                            "title":i['title']
                                })
                        result = {
                            "version": '3.1',
                            "screen": "QUESTION_ONE",
                            "data": {
                                    "name":data.get('data').get('name'),
                                    "family_name":data.get('data').get('family_name'),
                                    "gender":data.get('data').get('gender',''),
                                    "resourse":data.get('data').get('resourse',"AutoAssign"),
                                    "services":data.get('data').get('services'),
                                    "date_source":date_res,
                                    "time_source":[{"id":"selection","title":"Please Select Date"}]
                                },
                            }
                    elif data.get("data").get("component_action",False) and data.get("data").get("component_action",False) == 'update_date':
                        resource_booking = request.env['resource.booking'].sudo()
                        combination_id = request.env['resource.booking.combination'].sudo().search([('id','=',int(data.get("data").get("resourse",False)))]) if data.get('data').get('resourse',False) and data.get('data').get('resourse',False) != 'AutoAssign' else False
                        result = {
                            "version": '3.1',
                            "screen": "QUESTION_ONE",
                            "data": {
                                },
                            }
                        if data.get("data").get("appointment",False):
                            result["data"]["time_source"] = self.get_resource_calendar_attendance_slot(data)
                    else:
                        today = datetime.now()
                        data_resource = self.get_resource_calendar_attendance1(data.get('data').get('services'))
                        date_res =[]
                        for i in data_resource:
                            if i['valid']:
                                date_res.append({
                                    "id" : i['id'],
                            "title":i['title']
                                })
                        result = {
                            "version": '3.1',
                            "screen": "QUESTION_ONE",
                            "data": {
                                    "name":data.get('data').get('name'),
                                    "family_name":data.get('data').get('family_name'),
                                    "gender":data.get('data').get('gender',''),
                                    "resourse":data.get('data').get('resourse',"AutoAssign"),
                                    "services":data.get('data').get('services'),
                                    "date_source":date_res,
                                    "time_source":[{"id":"selection","title":"Please Select Date"}]
                                },
                            }
                if data.get("data").get("component_action",False) and data.get("data").get("component_action",False) == 'update_date':
                    resource_booking = request.env['resource.booking'].sudo()
                    combination_id = request.env['resource.booking.combination'].sudo().search([('id','=',int(data.get("data").get("resourse",False)))]) if data.get('data').get('resourse',False) and data.get('data').get('resourse',False) != 'AutoAssign' else False
                    result = {
                        "version": '3.1',
                        "screen": "QUESTION_ONE",
                        "data": {
                            },
                        }
                    if data.get("data").get("appointment",False):
                        result["data"]["time_source"] = self.get_resource_calendar_attendance_slot(data)
                else:
                    today = datetime.now()
                    date_source = [{
                        "id" : (today + timedelta(days=i)).strftime('%Y-%m-%d'),
                        "title":"%s %s"((today + timedelta(days=i)).strftime("%A"),(today + timedelta(days=i)).strftime('%d-%m-%Y'))
                     } for i in range(7)]
                    result = {
                        "version": '3.1',
                        "screen": "QUESTION_ONE",
                        "data": {
                                "date_source":date_res,
                                "time_source":[{"id":"selection","title":"Please Select Date"}]
                            },
                        }
            elif message.wa_flow_id.flow_type in ['normal_booking','adv_booking']:
                partner = request.env['res.partner'].sudo().search([('formetted_number','=',message.formetted_number)])
                bookings = request.env['resource.booking'].sudo().search([('partner_ids','in',partner.ids)],order="id desc",limit=1)
                _logger.info("---result---%s"%result)
                if data.get("data").get("component_action",False) == 'update_booking_type':
                    result = {
                        "version": '3.1',
                        "screen": "CUSTOMER_INFO",
                        "data": {
                                "last_booking_error_visible":True,
                                "last_booking_error":"",
                                'init_values':{
                                    "name":"",
                                    "family_name":"",
                                    "gender":"",
                                    "phone":""
                                }
                            }
                        }
                    if data.get("data").get("booking_type",False) == 'self':
                        result['data']['init_values'].update({
                                "name":partner.name or "",
                                "family_name":partner.sur_name or "",
                                "gender":partner.gender or "male",
                                "phone":partner.phone or partner.mobile
                        })
                        name_required = True
                        name_visible = True
                        last_booking_required = False
                        last_booking_visible = False
                    elif data.get("data").get("booking_type",False) == 'other':
                        name_required = True
                        name_visible = True
                        last_booking_required = False
                        last_booking_visible = False
                    elif data.get("data").get("booking_type",False) == 'reschedule':
                        bookings = request.env['resource.booking'].sudo().search([('partner_ids','in',partner.ids),('start','>',datetime.now())],order="id desc",limit=1)
                        result['data'].update({
                            "last_bookings":[{
                                                            "id":booking.id,
                                                            "title":"%s [%s]"%(booking.name,str(booking.start))
                                                        } for booking in bookings] if bookings else [{"id": "0","title": "No Bookings Here"}],
                            "last_booking_error_visible":True if bookings else False
                        })
                        name_required = False
                        name_visible = False
                        last_booking_required = True
                        last_booking_visible = True
                    else:
                        name_required = False
                        name_visible = False
                        last_booking_required = False
                        last_booking_visible = False
                    result['data'].update({
                            "name_required":name_required,
                            "name_visible":name_visible,
                            "last_booking_required":last_booking_required,
                            "last_booking_visible":last_booking_visible
                            })
                elif data.get("screen") == "CUSTOMER_INFO":
                    resourse_source = [
                        {"id":str(x.id),
                        "title":x.name} for x in request.env['resource.booking.combination'].sudo().search([])
                    ]
                    services_source = [{
                                        "id":str(x.id),
                                        "title":x.name
                                    } for x in request.env['resource.booking.type'].sudo().search([('gender','in',[False,data.get('data').get('gender',False)])])]
                    # _logger.info("---services_source--%s"%services_source)
                    result = {
                        "version": '3.1',
                        "screen": "QUESTION_ONE",
                        "data": {
                            "name":data.get('data').get('name',partner.name),
                            "family_name":data.get('data').get('family_name',''),
                            "gender":data.get('data').get('gender',''),
                            "email": data.get('data').get('email',''),
                            "resourse_source":resourse_source,
                            "services_source":services_source,
                            "date_source":[{"id":"selection","title":"Please Select Service"}],
                            "time_source":[{"id":"selection","title":"Please Select Service"}]
                            },
                        }
                elif data.get("screen") == "QUESTION_ONE":
                    if data.get("data").get("component_action",False) and data.get("data").get("component_action",False) == 'update_resource':
                        if data.get("data").get("resourse",False):
                            booking_combination = request.env['resource.booking.combination'].sudo().search([('id','=',int(data.get("data").get("resourse",False)))])
                            combination_rel = request.env['resource.booking.type.combination.rel'].sudo().search([('combination_id','in',booking_combination.ids)])
                            booking_types = request.env['resource.booking.type'].sudo().search([('combination_rel_ids','in',combination_rel.ids),('gender','in',[False,data.get('data').get('gender',False)])])
                        else:
                            booking_types = request.env['resource.booking.type'].sudo().search([('gender','in',[False,data.get('data').get('gender',False)])])
                        services_source = [{
                                        "id":str(x.id),
                                        "title":x.name
                                    } for x in booking_types]
                        result = {
                            "version": '3.1',
                            "screen": "QUESTION_ONE",
                            "data": {
                                "name":data.get('data').get('name'),
                                "family_name":data.get('data').get('family_name'),
                                "gender":data.get('data').get('gender',''),
    #                            "resourse_source":resourse_source,
                                "services_source":services_source,
                                "date_source":[{"id":"selection","title":"Please Select Service"}],
                                "time_source":[{"id":"selection","title":"Please Select Service"}]
                                },
                            }
                    elif data.get("data").get("component_action",False) and data.get("data").get("component_action",False) == 'update_services':
                        today = datetime.now()
                        data_resource = self.get_resource_calendar_attendance1(data.get('data').get('services'))
                        date_res =[]
                        for i in data_resource:
                            if i['valid']:
                                date_res.append({
                                    "id" : i['id'],
                            "title":i['title']
                                })
                        result = {
                            "version": '3.1',
                            "screen": "QUESTION_ONE",
                            "data": {
                                    "name":data.get('data').get('name'),
                                    "family_name":data.get('data').get('family_name'),
                                    "gender":data.get('data').get('gender',''),
                                    "resourse":data.get('data').get('resourse',"AutoAssign"),
                                    "services":data.get('data').get('services'),
                                    "date_source":date_res,
                                    "time_source":[{"id":"selection","title":"Please Select Date"}]
                                },
                            }
                    elif data.get("data").get("component_action",False) and data.get("data").get("component_action",False) == 'update_date':
                        resource_booking = request.env['resource.booking'].sudo()
                        today = datetime.now()
                        data_resource = self.get_resource_calendar_attendance1(data.get('data').get('services'))
                        date_res =[]
                        for i in data_resource:
                            if i['valid']:
                                date_res.append({
                                    "id" : i['id'],
                                    "title":i['title']
                                })
                        combination_id = request.env['resource.booking.combination'].sudo().search([('id','=',int(data.get("data").get("resourse",False)))]) if data.get('data').get('resourse',False) and data.get('data').get('resourse',False) != 'AutoAssign' else False
                        type_id = request.env['resource.booking.type'].sudo().browse(int(data.get('data').get('services')))
                        sorted_combinations = combination_id if combination_id else type_id._get_combinations_priorized()
                        result = {
                            "version": '3.1',
                            "screen": "QUESTION_ONE",
                            "data": {
                                    "name":data.get('data').get('name'),
                                    "family_name":data.get('data').get('family_name'),
                                    "gender":data.get('data').get('gender',''),
                                    "resourse":data.get('data').get('resourse',"AutoAssign"),
                                    "services":data.get('data').get('services'),
                                    "date_source":date_res,
                                },
                            }
                        if data.get("data").get("appointment",False):
                            result["data"]["time_source"] = self.get_resource_calendar_attendance_slot(data)
                    else:
                        today = datetime.now()
                        data_resource = self.get_resource_calendar_attendance1(data.get('data').get('services'))
                        date_res =[]
                        for i in data_resource:
                            if i['valid']:
                                date_res.append({
                                    "id" : i['id'],
                            "title":i['title']
                                })
                        result = {
                            "version": '3.1',
                            "screen": "QUESTION_ONE",
                            "data": {
                                    "name":data.get('data').get('name'),
                                    "family_name":data.get('data').get('family_name'),
                                    "gender":data.get('data').get('gender',''),
                                    "resourse":data.get('data').get('resourse',"AutoAssign"),
                                    "services":data.get('data').get('services'),
                                    "date_source":date_res,
                                    "time_source":[{"id":"selection","title":"Please Select Date"}]
                                },
                            }
#                elif data.get("screen") == "BOOKING_INFO":
#                    if data.get("data").get("component_action",False) and data.get("data").get("component_action",False) == 'update_date':
#                        resource_booking = request.env['resource.booking'].sudo()
#                        
#                        combination_id = request.env['resource.booking.combination'].sudo().search([('id','=',int(data.get("data").get("resourse",False)))]) if data.get('data').get('resourse',False) and data.get('data').get('resourse',False) != 'AutoAssign' else False
#                        type_id = request.env['resource.booking.type'].sudo().browse(int(data.get('data').get('services')))
#                        sorted_combinations = combination_id if combination_id else type_id._get_combinations_priorized()
#                        result = {
#                            "version": '3.1',
#                            "screen": "BOOKING_INFO",
#                            "data": {
#                                    "name":data.get('data').get('name'),
#                                    "family_name":data.get('data').get('family_name'),
#                                    "gender":data.get('data').get('gender',''),
#                                    "resourse":data.get('data').get('resourse',"AutoAssign"),
#                                    "services":data.get('data').get('services'),
#                                },
#                            }
#                        if data.get("data").get("appointment",False):
#                            result["data"]["time_source"] = self.get_resource_calendar_attendance_slot(data)
            # _logger.info("=-=-result  %s"%result)
            # _logger.info("Final Result  %s"%result)
            return result
        else:
            return super(WhatsappResourseFlow,self).whatsapp_django_data_flow(kw=kw)


