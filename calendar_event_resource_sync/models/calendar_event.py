from odoo import models, api

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    def unlink(self):
        # updated the new code for timeoff
        leave_model = self.env['resource.calendar.leaves']
        for event in self:
            leave = leave_model.search([
                ('date_from', '=', event.start),
                ('date_to', '=', event.stop),
                ('name', '=', event.name),
            ])
            if leave:
                leave.unlink()

        return super().unlink()

    def write(self, vals):
        for event in self:
            resource = self.env['resource.resource'].search(
                [('user_id', '=', event.user_id.id)], limit=1
            )
            if resource and event.start and event.stop:
                # Use existing (old) start/stop values to find current leave
                leave = self.env['resource.calendar.leaves'].search([
                    ('resource_id', '=', resource.id),
                    ('date_from', '=', event.start),
                    ('date_to', '=', event.stop),
                    ('name', '=', event.name),
                ], limit=1)

                if leave:
                    # Update leave with new values if provided
                    leave.write({
                        'date_from': vals.get('start', event.start),
                        'date_to': vals.get('stop', event.stop),
                        'name': vals.get('name', event.name),
                    })
                else:
                    # Only create if no existing leave found for original event
                    self.env['resource.calendar.leaves'].create({
                        'name': vals.get('name', event.name) or 'Calendar Event',
                        'resource_id': resource.id,
                        'calendar_id': resource.calendar_id.id,
                        'date_from': vals.get('start', event.start),
                        'date_to': vals.get('stop', event.stop),
                        'time_type': 'leave',
                    })

        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        # updated the new code for timeoff
        # Create calendar leaves
        for event in records:
            resource = self.env['resource.resource'].search(
                [('user_id', '=', event.user_id.id)], limit=1
            )
            if resource and event.start and event.stop:
                self.env['resource.calendar.leaves'].create({
                    'name': event.name or 'Calendar Event',
                    'resource_id': resource.id,
                    'calendar_id': resource.calendar_id.id,
                    'date_from': event.start,
                    'date_to': event.stop,
                    'time_type': 'leave',
                })

        return records
