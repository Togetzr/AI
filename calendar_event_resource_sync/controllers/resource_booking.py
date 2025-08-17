from odoo import models, fields
from datetime import timedelta
from odoo.addons.resource.models.utils import Intervals


class ResourceBooking(models.Model):
    _inherit = 'resource.booking'
    _description = 'Resource Booking'

    def _get_slots_from_combination(self, booking_type, combination, start_dt, end_dt):
        """
        Compute available slots using booking type and combination only,
        without requiring an existing booking record.
        """
        result = {}
        now = fields.Datetime.context_timestamp(self, fields.Datetime.now())

        # Use slot_duration and duration from booking_type
        slot_duration = timedelta(hours=booking_type.slot_duration or 1.0)
        booking_duration = timedelta(hours=booking_type.duration or 1.0)

        # Use modifications_deadline if present
        min_start_dt = now
        if hasattr(booking_type, 'modifications_deadline'):
            min_start_dt += timedelta(hours=booking_type.modifications_deadline)

        start_dt = max(start_dt, min_start_dt)

        # Get intervals from combination
        intervals = combination._get_intervals(start_dt, end_dt)
        intervals = self._merge_intervals(intervals)

        for available_start, available_stop in intervals._items:
            test_start = available_start
            while test_start + booking_duration <= available_stop:
                if test_start >= start_dt:
                    day = test_start.date()
                    if day not in result:
                        result[day] = []
                    result[day].append(test_start)
                test_start += slot_duration

        # Sort slots per day
        for day in result:
            result[day] = sorted(result[day])

        return result

    def _merge_intervals(self, intervals):
        """
        Merge intervals where start of current interval == stop of previous.
        """
        intervals_list = [list(tup) for tup in intervals._items]

        for i in range(len(intervals_list)):
            stop = intervals_list[i][1]
            if (
                stop.hour == 23 and stop.minute == 59 and stop.second == 59 and stop.microsecond == 999999
            ):
                intervals_list[i][1] += timedelta(microseconds=1)

        for i in range(len(intervals_list) - 1, 0, -1):
            if intervals_list[i][0] == intervals_list[i - 1][1]:
                intervals_list[i - 1][1] = intervals_list[i][1]
                del intervals_list[i]

        return Intervals([tuple(interval) for interval in intervals_list])
