{
    "name": "Calendar Event Timeoff Sync",
    "version": "1.0",
    "depends": ["resource_booking", "website", "calendar", 'portal','tz_whatsapp_resourse_flow'],
    "author": "Amit Yadav",
    "category": "Human Resources",
    "summary": "Sync calendar events with resource leaves",
    "description": "Keeps resource.calendar.leaves in sync with calendar.event records",
    'data': [
        'views/calendar_form_action.xml',
        'views/calender_template.xml',
             ],
    'assets': {
        'website.assets_wysiwyg': [
            'calendar_event_resource_sync/static/src/js/website_form_reservation_editor.js',

        ],
    },

    "installable": True,
    "application": False
}
