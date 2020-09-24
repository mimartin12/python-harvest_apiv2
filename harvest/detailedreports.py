
# Copyright 2020 Bradbase

import itertools

from datetime import datetime, timedelta, date
from calendar import monthrange
from harvest import Harvest
from .harvestdataclasses import *

class DetailedReports(Harvest):

    def __init__(self, uri, auth):
        self.client_cache = {}
        self.project_cache = {}
        self.task_cache = {}
        self.user_cache = {}
        super().__init__(uri, auth)

    def timeframe(self, timeframe, from_date=None, to_date=None):
        quarters = [None,
                    [1, 3], [1, 3], [1, 3],
                    [4, 6], [4, 6], [4, 6],
                    [7, 9], [7, 9], [7, 9],
                    [10, 12], [10, 12], [10, 12]]
        today = datetime.now().date()

        timeframe_upper = timeframe.upper()

        if timeframe_upper == 'THIS WEEK':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)

        elif timeframe_upper == 'LAST WEEK':
            today = today - timedelta(days=7)
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)

        elif timeframe_upper == 'THIS SEMIMONTH':
            if today.day <= 15:
                start_date = today.replace(day=1)
                end_date = today.replace(day=15)
            else:
                start_date = today.replace(day=16)
                end_date = today.replace(
                    day=monthrange(today.year, today.month)[1])

        elif timeframe_upper == 'LAST SEMIMONTH':
            if today.day <= 15:
                if today.month == 1:
                    start_date = today.replace(
                        year=today.year-1, month=12, day=16)
                    end_date = today.replace(
                        year=today.year-1,
                        month=12,
                        day=monthrange(today.year-1, 12)[1])
                else:
                    start_date = today.replace(month=today.month-1, day=16)
                    end_date = today.replace(
                        month=today.month-1,
                        day=monthrange(today.year, today.month-1)[1])
            else:
                start_date = today.replace(day=1)
                end_date = today.replace(day=15)

        elif timeframe_upper == 'THIS MONTH':
            start_date = today.replace(day=1)
            end_date = today.replace(
                day=monthrange(today.year, today.month)[1])

        elif timeframe_upper == 'LAST MONTH':
            if today.month == 1:
                start_date = today.replace(year=today.year-1, month=12, day=1)
                end_date = today.replace(
                    year=today.year-1,
                    month=12,
                    day=monthrange(today.year-1, 12)[1])
            else:
                start_date = today.replace(month=today.month-1, day=1)
                end_date = today.replace(
                    month=today.month-1,
                    day=monthrange(today.year, today.month-1)[1])

        elif timeframe_upper == 'THIS QUARTER':
            quarter = quarters[today.month]
            start_date = date(today.year, quarter[0], 1)
            end_date = date(
                today.year,
                quarter[1],
                monthrange(today.year, quarter[1])[1])

        elif timeframe_upper == 'LAST QUARTER':
            if today.month <= 3:
                quarter = [10, 12]
                today = today.replace(year=today.year-1)
            else:
                quarter = quarters[today.month-3]
            start_date = date(today.year, quarter[0], 1)
            end_date = date(
                today.year,
                quarter[1],
                monthrange(today.year, quarter[1])[1])

        elif timeframe_upper == 'THIS YEAR':
            start_date = date(today.year, 1, 1)
            end_date = date(today.year, 12, 31)

        elif timeframe_upper == 'LAST YEAR':
            start_date = date(today.year-1, 1, 1)
            end_date = date(today.year-1, 12, 31)

        elif timeframe_upper == 'ALL TIME':
            return {}

        # Not currently supported
        elif timeframe_upper == 'CUSTOM':
            raise ValueError("Custom timeframe not currently supported.")

        else:
            raise ValueError(
                "unknown argument \'timeframe\': \'%s\'" % timeframe_upper)

        return {'from_date': start_date, 'to_date': end_date}


    # team is user
    def detailed_time(self, time_frame='All Time', clients=[None], projects=[None], tasks=[None], team=[None], include_archived_items=False, group_by='Date', activeProject_only=False):
        arg_configs = []
        time_entry_results = DetailedTimeReport([])

        for element in itertools.product(clients, projects, team):
            kwargs = {}

            if element[0] !=None:
                kwargs['client_id'] = element[0]

            if element[1] !=None:
                kwargs['project_id'] = element[1]

            if element[2] !=None:
                kwargs['user_id'] = element[2]

            kwargs = dict(self.timeframe(time_frame), **kwargs)

            arg_configs.append(kwargs)

        tmp_time_entry_results = []
        if arg_configs == []:
            time_entries = self.time_entries()
            tmp_time_entry_results.extend(time_entries.time_entries)
            if time_entries.total_pages > 1:
                for page in range(2, time_entries.total_pages + 1):
                    time_entries = self.time_entries(page=page)
                    tmp_time_entry_results.extend(time_entries.time_entries)
        else:
            for config in arg_configs:
                time_entries = self.time_entries(**kwargs)
                tmp_time_entry_results.extend(time_entries.time_entries)
                if time_entries.total_pages > 1:
                    for page in range(2, time_entries.total_pages + 1):
                        time_entries = self.time_entries(page=page, **kwargs)
                        tmp_time_entry_results.extend(time_entries.time_entries)

        for time_entry in tmp_time_entry_results:
            user = None
            if time_entry.user.id not in self.user_cache.keys():
                user = self.get_user(time_entry.user.id)
                self.user_cache[time_entry.user.id] = user
            else:
                user = self.user_cache[time_entry.user.id]

            hours = time_entry.hours
            billable_amount = 0.0
            cost_amount = 0.0
            billable_rate = time_entry.billable_rate
            cost_rate = time_entry.cost_rate

            if hours is not None:
                if billable_rate is not None:
                    billable_amount = billable_rate * hours
                if cost_rate is not None:
                    cost_amount = cost_rate * hours

            time_entry_results.detailed_time_entries.append( DetailedTimeEntry(date=time_entry.spent_date, client=time_entry.client.name, project=time_entry.project.name, project_code=time_entry.project.code, task=time_entry.task.name, notes=time_entry.notes, hours=hours, billable=str(time_entry.billable), invoiced='', approved='', first_name=user.first_name, last_name=user.last_name, roles=user.roles, employee='Yes', billable_rate=billable_rate, billable_amount=billable_amount, cost_rate=cost_rate, cost_amount=cost_amount, currency=time_entry.client.currency, external_reference_url=time_entry.external_reference) )

        return time_entry_results
