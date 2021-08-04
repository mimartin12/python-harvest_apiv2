
# Copyright 2020 Bradbase

import json
from dataclasses import asdict
from collections import deque
from datetime import timedelta, datetime
import time
import copy

import requests
from requests_oauthlib import OAuth2Session
from dacite import from_dict

from .harvestdataclasses import *

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

def assemble_query_string(**kwargs):
    query_string = list()

    if not 'page' in kwargs:
        kwargs['page'] = 1

    if not 'per_page' in kwargs:
        kwargs['per_page'] = 100

    for k, v in kwargs.items():
        if v is None:
            continue
        elif type(v) is bool:
            v = str(v).lower()
        query_string.append(f'{k}={v}')
    output_query_string = '&'.join(query_string)
    return output_query_string


class HarvestError(Exception):
    pass

class Harvest(object):

    # 15 seconds is from the Harvest API doco https://help.getharvest.com/api-v2/introduction/overview/general/
    RATE_LIMIT_REQUESTS_DURATION_SECONDS = 15
    # 15 mins is from the Harvest API doco https://help.getharvest.com/api-v2/introduction/overview/general/
    RATE_LIMIT_REPORTS_DURATION_SECONDS = 900

    RATE_LIMIT_REQUEST_COUNT = 100

    def __init__(self, uri, auth):
        self.__uri = uri.rstrip('/')
        parsed = urlparse(uri)

        self.__headers = {'User-Agent': 'bradbase/python-harvest-apiv2',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        if not (parsed.scheme and parsed.netloc):
            raise HarvestError('Invalid harvest uri "{0}".'.format(uri))

        if isinstance(auth, PersonalAccessToken):
            self.__headers['Authorization'] = auth.access_token
            self.__headers['Harvest-Account-ID'] = auth.account_id

        elif isinstance(auth, OAuth2_ClientSide_Token):
            self.__headers['Authorization'] = auth.access_token

        elif isinstance(auth, OAuth2_ServerSide):
            self.__headers['Authorization'] = auth.token.access_token

        else:
            raise HarvestError('Invalid authorization type "{0}".'.format(type(auth)))

        self.__auth = auth
        self.request_throttle = deque()
        self.reports_throttle = deque()
        self.request_time_limit = timedelta(seconds=self.RATE_LIMIT_REQUESTS_DURATION_SECONDS)
        self.reports_time_limit = timedelta(seconds=self.RATE_LIMIT_REPORTS_DURATION_SECONDS)

    @property
    def uri(self):
        return self.__uri

    @property
    def headers(self):
        return self.__headers

    @property
    def auth(self):
        return self.__auth

    ## Client Contacts

    def client_contacts(self, page=1, per_page=100, client_id=None, updated_since=None):
        url = '/contacts?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)
        if client_id is not None:
            url = '{0}&client_id={1}'.format(url, client_id)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=ClientContacts, data=self._get(url))

    def get_client_contact(self, contact_id):
        return from_dict(data_class=ClientContact, data=self._get('/contacts/{0}'.format(contact_id)))

    def create_client_contact(self, client_id, first_name, **kwargs):
        url  = '/contacts'
        kwargs.update({'client_id': client_id, 'first_name': first_name})
        return from_dict(data_class=ClientContact, data=self._post(url, data=kwargs))

    def update_client_contact(self, contact_id, **kwargs):
        url = '/contacts/{0}'.format(contact_id)
        return from_dict(data_class=ClientContact, data=self._patch(url, data=kwargs))

    def delete_client_contact(self, contact_id):
        self._delete('/contacts/{0}'.format(contact_id))

    ## Clients
    def clients(self, **kwargs):
        """
        :param page: Page number to return, defaults to `1`
        :type page: int
        :param per_page: Number of clients to return per page, defaults to `100`
        :type per_page: int
        :param is_active: Include archived clients in return, defaults to `None`
        :type is_active: bool or None
        :param updated_since: Include clients updated since, defaults to `None`
        :type updated_since: datetime or None
        :return: Return a list of client objects.
        :rtype: list
        """
        baseurl = '/clients?'
        query_string = assemble_query_string(**kwargs)
        url = f"{baseurl}{query_string}"

        return from_dict(data_class=Clients, data=self._get(url))

    def get_client(self, client_id):
        return from_dict(data_class=Client, data=self._get('/clients/{0}'.format(client_id)))

    def create_client(self, name, **kwargs):
        url  = '/clients'
        kwargs.update({'name': name})
        response = self._post(url, data=kwargs)

        if 'message' in response.keys():
            return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=Client, data=response)

    def update_client(self, client_id, **kwargs):
        url = '/clients/{0}'.format(client_id)
        return from_dict(data_class=Client, data=self._patch(url, data=kwargs))

    def delete_client(self, client_id):
        self._delete('/clients/{0}'.format(client_id))

    ## Company

    def company(self, **kwargs):
        """
        :param page: Page number to return, defaults to `1`
        :type page: int
        :param per_page: Number of clients to return per page, defaults to `100`
        :type per_page: int
        :param is_active: Include archived clients in return, defaults to `None`
        :type is_active: bool or None
        :param updated_since: Include clients updated since, defaults to `None`
        :type updated_since: datetime or None
        :return: Return a list of client objects.
        :rtype: list
        """
        baseurl = '/company?'
        query_string = assemble_query_string(**kwargs)
        url = f"{baseurl}{query_string}"

        return from_dict(data_class=Company, data=self._get(url))

    ## Invoices

    def invoice_messages(self, invoice_id, page=1, per_page=100, updated_since=None):
        url = '/invoices/{0}/messages'.format(invoice_id)
        url = '{0}?page={1}'.format(url, page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=InvoiceMessages, data=self._get(url))

    def create_invoice_message(self, invoice_id, recipients, **kwargs):
        url  = '/invoices/{0}/messages'.format(invoice_id)
        kwargs.update({'recipients': recipients})
        response = self._post(url, data=kwargs)

        if 'message' in response.keys():
            return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=InvoiceMessage, data=response)

    def mark_draft_invoice(self, invoice_id, event_type):
        url = '/invoices/{0}/messages'.format(invoice_id)
        return from_dict(data_class=InvoiceMessage, data=self._post(url, data={'event_type': event_type}))

    def mark_draft_invoice_as_sent(self, invoice_id):
        return self.mark_draft_invoice(invoice_id, 'send')

    def mark_open_invoice_as_closed(self, invoice_id):
        return self.mark_draft_invoice(invoice_id, 'close')

    def reopen_closed_invoice(self, invoice_id):
        return self.mark_draft_invoice(invoice_id, 're-open')

    def mark_open_invoice_as_draft(self, invoice_id):
        return self.mark_draft_invoice(invoice_id, 'draft')

    def delete_invoice_message(self, invoice_id, message_id):
        self._delete('/invoices/{0}/messages/{1}'.format(invoice_id, message_id))


    def invoice_payments(self, invoice_id, page=1, per_page=100, updated_since=None):
        url = '/invoices/{0}/payments'.format(invoice_id)
        url = '{0}?page={1}'.format(url, page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=InvoicePayments, data=self._get(url))

    def create_invoice_payment(self, invoice_id, amount, **kwargs):
        url  = '/invoices/{0}/payments'.format(invoice_id)
        kwargs.update({'amount': amount})
        response = self._post(url, data=kwargs)

        if 'message' in response.keys():
            return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=InvoicePayment, data=response)

    def delete_invoice_payment(self, invoice_id, payment_id):
        self._delete('/invoices/{0}/payments/{1}'.format(invoice_id, payment_id))


    def invoices(self, page=1, per_page=100, client_id=None, project_id=None, updated_since=None, from_date=None, to_date=None, state=None):
        url = '/invoices?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if client_id is not None:
            url = '{0}&client_id={1}'.format(url, client_id)
        if project_id is not None:
            url = '{0}&project_id={1}'.format(url, project_id)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)
        if from_date is not None:
            url = '{0}&from={1}'.format(url, from_date)
        if to_date is not None:
            url = '{0}&to={1}'.format(url, to_date)
        if state is not None:
            url = '{0}&state={1}'.format(url, state)

        return from_dict(data_class=Invoices, data=self._get(url))

    def get_invoice(self, invoice_id):
        return from_dict(data_class=Invoice, data=self._get('/invoices/{0}'.format(invoice_id)))

    def create_invoice(self, client_id, **kwargs):
        url = '/invoices'
        kwargs.update({'client_id': client_id})
        return from_dict(data_class=Invoice, data=self._post(url, data=kwargs))

    def create_free_form_invoice(self, invoice : FreeFormInvoice):
        invoice_dict = asdict(invoice)
        client_id = invoice_dict['client_id']
        invoice_dict.pop('client_id', None)
        return self.create_invoice(client_id, **invoice_dict)

    def create_invoice_based_on_tracked_time_and_expenses(self, invoice : InvoiceImport):
        # translates from_date to from
        invoice_dict = json.loads(invoice.to_json())
        client_id = invoice_dict['client_id']
        invoice_dict.pop('client_id', None)
        return self.create_invoice(client_id, **invoice_dict)

    # line_items is a list of LineItem
    def update_invoice(self, invoice_id, **kwargs):
        url = '/invoices/{0}'.format(invoice_id)
        response = self._patch(url, data=kwargs)

        if 'message' in response.keys():
            return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=Invoice, data=response)

    def create_invoice_line_item(self, invoice_id, line_items):
        if not isinstance(line_items, list):
            return ErrorMessage(message="line_items is not a list")
        return self.update_invoice(invoice_id, line_items=line_items)


    def update_invoice_line_item(self, invoice_id, line_item):
        if not isinstance(line_item, dict):
            return ErrorMessage(message="line_items is not a dictionary")
        return self.update_invoice(invoice_id, line_items = [line_item])

    # line_items is a list of LineItems
    def delete_invoice_line_items(self, invoice_id, line_items):
        url = '/invoices/{0}'.format(invoice_id)

        delete_line_item = []
        for item in line_items:
            delete_line_item.append({'id':item['id'], '_destroy':True})

        return from_dict(data_class=Invoice, data=self._patch(url, data={'line_items': delete_line_item}))

    def delete_invoice(self, invoice_id):
        self._delete('/invoices/{0}'.format(invoice_id))

    def invoice_item_categories(self, page=1, per_page=100, updated_since=None):
        url = '/invoice_item_categories?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=InvoiceItemCategories, data=self._get(url))

    def get_invoice_item_category(self, category_id):
        url = '/invoice_item_categories/{0}'.format(category_id)
        return from_dict(data_class=InvoiceItemCategory, data=self._get(url))

    def create_invoice_item_category(self, name):
        url = '/invoice_item_categories'
        return from_dict(data_class=InvoiceItemCategory, data=self._post(url, data={'name': name}))

    def update_invoice_item_category(self, category_id, name):
        url = '/invoice_item_categories/{0}'.format(category_id)
        return from_dict(data_class=InvoiceItemCategory, data=self._patch(url, data={'name': name}))

    def delete_invoice_item_category(self, invoice_category_id):
        self._delete('/invoice_item_categories/{0}'.format(invoice_category_id))

     ## Estimates

    def estimate_messages(self, estimate_id, page=1, per_page=100, updated_since=None):
        url = '/estimates/{0}/messages'.format(estimate_id)
        url = '{0}?page={1}'.format(url, page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=EstimateMessages, data=self._get(url))

    # recipients is a list of Recipient
    def create_estimate_message(self, estimate_id, recipients, **kwargs):
        url  = '/estimates/{0}/messages'.format(estimate_id)
        kwargs.update({'recipients': recipients})
        response = self._post(url, data=kwargs)

        if 'message' in response.keys():
            return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=EstimateMessage, data=response)

    def delete_estimate_message(self, estimate_id, message_id):
        self._delete('/estimates/{0}/messages/{1}'.format(estimate_id, message_id))

    def mark_draft_estimate(self, estimate_id, event_type):
        url  = '/estimates/{0}/messages'.format(estimate_id)
        return from_dict(data_class=EstimateMessage, data=self._post(url, data={'event_type': event_type}))

    def mark_draft_estimate_as_sent(self, estimate_id):
        return self.mark_draft_estimate(estimate_id, 'send')

    def mark_open_estimate_as_accepted(self, estimate_id):
        return self.mark_draft_estimate(estimate_id, 'accept')

    def mark_open_estimate_as_declined(self, estimate_id):
        return self.mark_draft_estimate(estimate_id, 'decline')

    def reopen_a_closed_estimate(self, estimate_id):
        return self.mark_draft_estimate(estimate_id, 're-open')

    def estimates(self, page=1, per_page=100, client_id=None, updated_since=None, from_date=None, to_date=None, state=None):
        url = '/estimates?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if client_id is not None:
            url = '{0}&client_id={1}'.format(url, client_id)
        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)
        if from_date is not None:
            url = '{0}&from={1}'.format(url, from_date)
        if to_date is not None:
            url = '{0}&to={1}'.format(url, to_date)

        return from_dict(data_class=Estimates, data=self._get(url))

    def get_estimte(self, estimate_id):
        url = '/estimates/{0}'.format(estimate_id)
        return from_dict(data_class=Estimate, data=self._get(url))

    def create_estimate(self, client_id, **kwargs):
        url  = '/estimates'
        kwargs.update({'client_id': client_id})

        return from_dict(data_class=Estimate, data=self._post(url, data=kwargs))

    def update_estimate(self, estimate_id, **kwargs):
        url = '/estimates/{0}'.format(estimate_id)
        return from_dict(data_class=Estimate, data=self._patch(url, data=kwargs))

    def create_estimate_line_item(self, estimate_id, line_items):
        if not isinstance(line_items, list):
            return ErrorMessage(message="line_items is not a list")
        return self.update_estimate(estimate_id, line_items=line_items)

    def update_estimate_line_item(self, estimate_id, line_item):
        if not isinstance(line_item, dict):
            return ErrorMessage(message="line_items is not a dictionary")
        return self.update_estimate(estimate_id, line_items=[line_item])

    # line_items is a list of LineItem.id's
    def delete_estimate_line_items(self, estimate_id, line_items):
        url = '/estimates/{0}'.format(estimate_id)

        delete_line_item = []
        for item in line_items:
            delete_line_item.append({'id':item.id, '_destroy':True})

        return from_dict(data_class=Estimate, data=self._patch(url, data={'line_items': delete_line_item}))

    def delete_estimate(self, estimate_id):
        self._delete('/estimates/{0}'.format(estimate_id))

    def estimate_item_categories(self, page=1, per_page=100, updated_since=None):
        url = '/estimate_item_categories?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=EstimateItemCategories, data=self._get(url))

    def get_estimate_item_category(self, estimate_item_category_id):
        url = '/estimate_item_categories/{0}'.format(estimate_item_category_id)
        return from_dict(data_class=EstimateItemCategory, data=self._get(url))

    def create_estimate_item_category(self, name):
        url = '/estimate_item_categories'
        return from_dict(data_class=EstimateItemCategory, data=self._post(url, data={'name': name}))

    def update_estimate_item_category(self, estimate_item_category_id, name):
        url = '/estimate_item_categories/{0}'.format(estimate_item_category_id)
        return from_dict(data_class=EstimateItemCategory, data=self._patch(url, data={'name': name}))

    def delete_estimate_item_category(self, estimate_item_id):
        self._delete('/estimate_item_categories/{0}'.format(estimate_item_id))

    ## Expenses

    def expenses(self, **kwargs):
        """
        :param page: Page number to return, defaults to `1`
        :type page: int
        :param per_page: Number of clients to return per page, defaults to `100`
        :type per_page: int
        :param user_id: Only return expenses belonging to the user with the given ID, defaults to None
        :type user_id: int
        :param client_id: Only return expenses belonging to the client with the given ID, defaults to None
        :type client_id: int
        :param project_id: Only return expenses belonging to the project with the given ID, defaults to None
        :type project_id: int
        :param is_billed: Pass true to only return expenses that have been invoiced and false to return expenses that have not been invoiced, defaults to None
        :type is_billed: bool
        :param updated_since: Only return expenses that have been updated since the given date and time, defaults to None
        :type updated_since: datetime
        :param from_date: Only return expenses with a spent_date on or after the given date, defaults to None
        :type from_date: date
        :param to_date: Only return expenses with a spent_date on or before the given date, defaults to None
        :type to_date: date
        :return: Return a list of client objects.
        :rtype: list
        """
        baseurl = '/expenses?'

        from_date = kwargs.pop("from_date", None)
        if from_date is not None:
            kwargs["from"] = from_date

        to_date = kwargs.pop("to_date", None)
        if to_date is not None:
            kwargs["to"] = to_date

        query_string = assemble_query_string(**kwargs)
        url = f"{baseurl}{query_string}"

        return from_dict(data_class=Expenses, data=self._get(url))

    def get_expense(self, expense_id):
        return from_dict(data_class=Expense, data=self._get('/expenses/{0}'.format(expense_id)))

    def create_expense(self, project_id, expense_category_id, spent_date, **kwargs):
        url = '/expenses'
        kwargs.update({'project_id': project_id, 'expense_category_id': expense_category_id, 'spent_date': spent_date})

        if 'receipt' in kwargs.keys():
            receipt = kwargs.pop('receipt')
            response = self._post(url, data=kwargs, files=receipt['files'])
        else:
            response = self._post(url, data=kwargs)

            if 'message' in response.keys():
                return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=Expense, data=response)

    def update_expense(self, expense_id, **kwargs):
        url = '/expenses/{0}'.format(expense_id)

        if 'receipt' in kwargs.keys():
            receipt = kwargs.pop('receipt')
            response = self._patch(url, data=kwargs, files=receipt['files'])
        else:
            response = self._patch(url, data=kwargs)

        return from_dict(data_class=Expense, data=response)

    def delete_expense(self, expense_id):
        self._delete('/expenses/{0}'.format(expense_id))

    def expense_categories(self, **kwargs):
        """
        :param page: Page number to return, defaults to `1`
        :type page: int
        :param per_page: Number of expense categories to return per page, defaults to `100`
        :type per_page: int
        :param is_active: Include archived expense categories in return, defaults to `None`
        :type is_active: bool or None
        :param updated_since: Include expense categories updated since, defaults to `None`
        :type updated_since: datetime or None
        :return: Return a list of client objects.
        :rtype: list
        """
        baseurl = '/expense_categories?'
        query_string = assemble_query_string(**kwargs)
        url = f"{baseurl}{query_string}"

        return from_dict(data_class=ExpenseCategories, data=self._get(url))

    def get_expense_category(self, expense_category_id):
        return from_dict(data_class=ExpenseCategory, data=self._get('/expense_categories/{0}'.format(expense_category_id)))

    def create_expense_category(self, name, **kwargs):
        url = '/expense_categories'
        kwargs.update({'name': name})
        return from_dict(data_class=ExpenseCategory, data=self._post(url, data=kwargs))

    def update_expense_category(self, expense_category_id, **kwargs):
        url = '/expense_categories/{0}'.format(expense_category_id)
        return from_dict(data_class=ExpenseCategory, data=self._patch(url, data=kwargs))

    def delete_expense_category(self, expense_category_id):
        self._delete('/expense_categories/{0}'.format(expense_category_id))

    ## Tasks
    def tasks(self, **kwargs):
        """
        :param page: Page number to return, defaults to `1`
        :type page: int
        :param per_page: Number of tasks to return per page, defaults to `100`
        :type per_page: int
        :param is_active: Include archived tasks in return, defaults to `None`
        :type is_active: bool or None
        :param updated_since: Include tasks updated since, defaults to `None`
        :type updated_since: datetime or None
        :return: Return a list of client objects.
        :rtype: list
        """
        baseurl = '/tasks?'
        query_string = assemble_query_string(**kwargs)
        url = f"{baseurl}{query_string}"

        return from_dict(data_class=Tasks, data=self._get(url))

    def get_task(self, task_id):
        return from_dict(data_class=Task, data=self._get('/tasks/{0}'.format(task_id)))

    def create_task(self, name, **kwargs):
        url = '/tasks'
        kwargs.update({'name': name})
        return from_dict(data_class=Task, data=self._post(url, data=kwargs))

    def update_task(self, task_id, **kwargs):
        url = '/tasks/{0}'.format(task_id)
        return from_dict(data_class=Task, data=self._patch(url, data=kwargs))

    def delete_task(self, task_id):
        self._delete('/tasks/{0}'.format(task_id))

    ## Time Entries

    def time_entries(self, **kwargs):
        """
        :param page: Page number to return, defaults to `1`
        :type page: int
        :param per_page: Number of tasks to return per page, defaults to `100`
        :type per_page: int
        :param user_id: Only return time entries belonging to the user with the given ID, defaults to `None`
        :type user_id: int or None
        :param client_id: Only return time entries belonging to the client with the given ID, defaults to `None`
        :type client_id: int or None
        :param project_id: Only return time entries belonging to the project with the given ID, defaults to `None`
        :type project_id: int or None
        :param task_id: Only return time entries belonging to the task with the given ID, defaults to `None`
        :type task_id: int or None
        :param external_reference_id: Only return time entries with the given external_reference ID, defaults to `None`
        :type external_reference_id: string or None
        :param is_billed: Pass true to only return time entries that have been invoiced and false to return time entries that have not been invoiced, defaults to `None`
        :type is_billed: bool or None
        :param is_running: Pass true to only return running time entries and false to return non-running time entries, defaults to `None`
        :type is_running: bool or None
        :param updated_since: Only return time entries that have been updated since the given date and time. Use the ISO 8601 Format, defaults to `None`
        :type updated_since: datetime or None
        :param from_date: Only return time entries with a spent_date on or after the given date, defaults to `None`
        :type from_date: date or None
        :param to_date: Only return time entries with a spent_date on or before the given date, defaults to `None`
        :type to_date: date or None
        :return: Return a list of client objects.
        :rtype: list
        """
        baseurl = '/time_entries?'

        from_date = kwargs.pop("from_date", None)
        if from_date is not None:
            kwargs["from"] = from_date

        to_date = kwargs.pop("to_date", None)
        if to_date is not None:
            kwargs["to"] = to_date
            
        query_string = assemble_query_string(**kwargs)
        url = f"{baseurl}{query_string}"

        return from_dict(data_class=TimeEntries, data=self._get(url))

    def get_time_entry(self, time_entry_id):
        return from_dict(data_class=TimeEntry, data=self._get('/time_entries/{0}'.format(time_entry_id)))

    def create_time_entry(self, wants_timestamp_timers, project_id, task_id, spent_date, **kwargs):
        company = self.company()

        if company.wants_timestamp_timers == wants_timestamp_timers:
            url = '/time_entries'
            kwargs.update({'project_id': project_id, 'task_id': task_id, 'spent_date': spent_date})
            response = self._post(url, data=kwargs)

            if 'message' in response.keys():
                return from_dict(data_class=ErrorMessage, data=response)

            return from_dict(data_class=TimeEntry, data=response)
        else:
            return ErrorMessage("Your user account does not have permission to create a time entry this way.")

    def create_time_entry_via_start_and_end_time(self, project_id, task_id, spent_date, **kwargs):
        return self.create_time_entry(True, project_id, task_id, spent_date, **kwargs)

    def create_time_entry_via_duration(self, project_id, task_id, spent_date, **kwargs):
        return self.create_time_entry(False, project_id, task_id, spent_date, **kwargs)

    def update_time_entry(self, time_entry_id, **kwargs):
        url = '/time_entries/{0}'.format(time_entry_id)
        return from_dict(data_class=TimeEntry, data=self._patch(url, data=kwargs))

    def delete_time_entry_external_reference(self, time_entry_id):
        self._delete('/time_entries/{0}/external_reference'.format(time_entry_id))

    def delete_time_entry(self, time_entry_id):
        self._delete('/time_entries/{0}'.format(time_entry_id))

    def restart_a_stopped_time_entry(self, time_entry_id):
        return from_dict(data_class=TimeEntry, data=self._patch('/time_entries/{0}/restart'.format(time_entry_id)))

    def stop_a_running_time_entry(self, time_entry_id):
        return from_dict(data_class=TimeEntry, data=self._patch('/time_entries/{0}/stop'.format(time_entry_id)))

    ## Projects
    def user_assignments(self, **kwargs):
        """
        :param page: Page number to return, defaults to `1`
        :type page: int
        :param per_page: Number of user assignments to return per page, defaults to `100`
        :type per_page: int
        :param is_active: Include archived user assignments in return, defaults to `None`
        :type is_active: bool or None
        :param updated_since: Include user assignments updated since, defaults to `None`
        :type updated_since: datetime or None
        :return: Return a list of client objects.
        :rtype: list
        """
        baseurl = '/user_assignments?'
        query_string = assemble_query_string(**kwargs)
        url = f"{baseurl}{query_string}"

        return from_dict(data_class=UserAssignments, data=self._get(url))

    def project_user_assignments(self, project_id, **kwargs):
        """
        :param page: Page number to return, defaults to `1`
        :type page: int
        :param per_page: Number of project user assignments to return per page, defaults to `100`
        :type per_page: int
        :param is_active: Include archived project user assignments in return, defaults to `None`
        :type is_active: bool or None
        :param updated_since: Include project user assignments updated since, defaults to `None`
        :type updated_since: datetime or None
        :return: Return a list of client objects.
        :rtype: list
        """
        baseurl = '/projects/{0}/user_assignments?'.format(project_id)
        query_string = assemble_query_string(**kwargs)
        url = f"{baseurl}{query_string}"

        return from_dict(data_class=UserAssignments, data=self._get(url))

    def get_user_assignment(self, project_id, user_assignment_id):
        return from_dict(data_class=UserAssignment, data=self._get('/projects/{0}/user_assignments/{1}'.format(project_id, user_assignment_id)))

    def create_user_assignment(self, project_id, user_id, **kwargs):
        url = '/projects/{0}/user_assignments'.format(project_id)
        kwargs.update({'user_id': user_id})
        return from_dict(data_class=UserAssignment, data=self._post(url, data=kwargs))

    def update_user_assignment(self, project_id, user_assignment_id, **kwargs):
        url = '/projects/{0}/user_assignments/{1}'.format(project_id, user_assignment_id)
        return from_dict(data_class=UserAssignment, data=self._patch(url, data=kwargs))

    def delete_user_assignment(self, project_id, user_assignment_id):
        self._delete('/projects/{0}/user_assignments/{1}'.format(project_id, user_assignment_id))

    def task_assignments(self, **kwargs):
        """
        :param page: Page number to return, defaults to `1`
        :type page: int
        :param per_page: Number of assignments to return per page, defaults to `100`
        :type per_page: int
        :param is_active: Include archived assignments in return, defaults to `None`
        :type is_active: bool or None
        :param updated_since: Include assignments updated since, defaults to `None`
        :type updated_since: datetime or None
        :return: Return a list of client objects.
        :rtype: list
        """
        baseurl = '/task_assignments?'
        query_string = assemble_query_string(**kwargs)
        url = f"{baseurl}{query_string}"

        return from_dict(data_class=TaskAssignments, data=self._get(url))

    def project_task_assignments(self, project_id, **kwargs):
        """
        :param page: Page number to return, defaults to `1`
        :type page: int
        :param per_page: Number of task assignments to return per page, defaults to `100`
        :type per_page: int
        :param is_active: Include archived task assignments in return, defaults to `None`
        :type is_active: bool or None
        :param updated_since: Include task assignments updated since, defaults to `None`
        :type updated_since: datetime or None
        :return: Return a list of client objects.
        :rtype: list
        """
        baseurl = '/projects/{0}/task_assignments?'.format(project_id)
        query_string = assemble_query_string(**kwargs)
        url = f"{baseurl}{query_string}"

        return from_dict(data_class=TaskAssignments, data=self._get(url))

    def get_task_assignment(self, project_id, task_assignment_id):
        return from_dict(data_class=TaskAssignment, data=self._get('/projects/{0}/task_assignments/{1}'.format(project_id, task_assignment_id)))

    def create_task_assignment(self, project_id, task_id, **kwargs):
        url = '/projects/{0}/task_assignments'.format(project_id)
        kwargs.update({'task_id': task_id})

        response = self._post(url, data=kwargs)

        if 'message' in response.keys():
            return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=TaskAssignment, data=response)

    def update_task_assignment(self, project_id, task_assignment_id, **kwargs):
        url = '/projects/{0}/task_assignments/{1}'.format(project_id, task_assignment_id)
        return from_dict(data_class=TaskAssignment, data=self._patch(url, data=kwargs))

    def delete_task_assignment(self, project_id, task_assignment_id):
        self._delete('/projects/{0}/task_assignments/{1}'.format(project_id, task_assignment_id))

    def projects(self, **kwargs):
        """
        :param page: Page number to return, defaults to `1`
        :type page: int
        :param per_page: Number of projects to return per page, defaults to `100`
        :type per_page: int
        :param is_active: Include archived projects in return, defaults to `None`
        :type is_active: bool or None
        :param updated_since: Include projects updated since, defaults to `None`
        :type updated_since: datetime or None
        :return: Return a list of client objects.
        :rtype: list
        """
        baseurl = '/projects?'
        query_string = assemble_query_string(**kwargs)
        url = f"{baseurl}{query_string}"

        return from_dict(data_class=Projects, data=self._get(url))

    def get_project(self, project_id):
        return from_dict(data_class=Project, data=self._get('/projects/{0}'.format(project_id)))

    def create_project(self, client_id, name, is_billable, bill_by, budget_by, **kwargs):
        url = '/projects'
        kwargs.update({'client_id': client_id, 'name': name, 'is_billable': str(is_billable).lower(), 'bill_by': bill_by, 'budget_by': budget_by})
        return from_dict(data_class=Project, data=self._post(url, data=kwargs))

    def update_project(self, project_id, **kwargs):
        url = '/projects/{0}'.format(project_id)
        return from_dict(data_class=Project, data=self._patch(url, data=kwargs))

    def delete_project(self, project_id):
        self._delete('/projects/{0}'.format(project_id))

     ## Roles

    def roles(self, page=1, per_page=100):
        url = '/roles?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        return from_dict(data_class=Roles, data=self._get(url))

    def get_role(self, role_id):
        return from_dict(data_class=Role, data=self._get('/roles/{0}'.format(role_id)))

    def create_role(self, name, **kwargs):
        url = '/roles'
        kwargs.update({'name': name})
        return from_dict(data_class=Role, data=self._post(url, data=kwargs))

    def update_role(self, role_id, name, **kwargs):
        url = '/roles/{0}'.format(role_id)
        kwargs.update({'name': name})
        return from_dict(data_class=Role, data=self._patch(url, data=kwargs))

    def delete_role(self, role_id):
        self._delete('/roles/{0}'.format(role_id))

     ## Users

    def billable_rates(self, user_id, page=1, per_page=100):
        url = '/users/{0}/billable_rates'.format(user_id)
        url = '{0}?page={1}'.format(url, page)
        url = '{0}&per_page={1}'.format(url, per_page)

        return from_dict(data_class=BillableRates, data=self._get(url))

    def get_billable_rate(self, user_id, billable_rate_id):
        url = '/users/{0}/billable_rates/{1}'.format(user_id, billable_rate_id)
        return from_dict(data_class=BillableRate, data=self._get(url))

    def create_billable_rate(self, user_id, amount, **kwargs):
        url = '/users/{0}/billable_rates'.format(user_id)
        kwargs.update({'amount': amount})
        return from_dict(data_class=BillableRate, data=self._post(url, data=kwargs))

    def user_cost_rates(self, user_id, page=1, per_page=100):
        url = '/users/{0}/cost_rates'.format(user_id)
        url = '{0}?page={1}'.format(url, page)
        url = '{0}&per_page={1}'.format(url, per_page)

        return from_dict(data_class=UserCostRates, data=self._get(url))

    def get_user_cost_rate(self, user_id, cost_rate_id):
        url = '/users/{0}/cost_rates/{1}'.format(user_id, cost_rate_id)
        return from_dict(data_class=CostRate, data=self._get(url))

    def create_user_cost_rate(self, user_id, amount, **kwargs):
        url = '/users/{0}/cost_rates'.format(user_id)
        kwargs.update({'amount': amount})
        return from_dict(data_class=CostRate, data=self._post(url, data=kwargs))

    def project_assignments(self, user_id, page=1, per_page=100, updated_since=None):
        url = '/users/{0}/project_assignments'.format(user_id)
        url = '{0}?page={1}'.format(url, page)
        url = '{0}&per_page={1}'.format(url, per_page)

        if updated_since is not None:
            url = '{0}&updated_since={1}'.format(url, updated_since)

        return from_dict(data_class=ProjectAssignments, data=self._get(url))

    def my_project_assignments(self, page=1, per_page=100):
        url = '/users/me/project_assignments?page={0}'.format(page)
        url = '{0}&per_page={1}'.format(url, per_page)

        return from_dict(data_class=ProjectAssignments, data=self._get(url))

    def users(self, **kwargs):
        """
        :param page: Page number to return, defaults to `1`
        :type page: int
        :param per_page: Number of users to return per page, defaults to `100`
        :type per_page: int
        :param is_active: Include archived users in return, defaults to `None`
        :type is_active: bool or None
        :param updated_since: Include users updated since, defaults to `None`
        :type updated_since: datetime or None
        :return: Return a list of client objects.
        :rtype: list
        """
        baseurl = '/users?'
        query_string = assemble_query_string(**kwargs)
        url = f"{baseurl}{query_string}"

        return from_dict(data_class=Users, data=self._get(url))

    def get_user(self, user_id):
        return from_dict(data_class=User, data=self._get('/users/{0}'.format(user_id)))

    def get_currently_authenticated_user(self):
        return from_dict(data_class=User, data=self._get('/users/me'))

    def create_user(self, first_name, last_name, email, **kwargs):
        url = '/users'
        kwargs.update({'first_name': first_name, 'last_name': last_name, 'email': email})
        response = self._post(url, data=kwargs)

        if 'message' in response.keys():
            return from_dict(data_class=ErrorMessage, data=response)

        return from_dict(data_class=User, data=response)

    def update_user(self, user_id, **kwargs):
        url = '/users/{0}'.format(user_id)
        return from_dict(data_class=User, data=self._patch(url, data=kwargs))

    def delete_user(self, user_id):
        self._delete('/users/{0}'.format(user_id))

    ## Reports

    def reports_expenses_clients(self, from_date, to_date, page=1, per_page=1000):
        url = '/reports/expenses/clients?from={0}&to={1}&page={2}&per_page={3}'.format(from_date, to_date, page, per_page)
        return from_dict(data_class=ExpenseReportResults, data=self._get(url))

    def reports_expenses_projects(self, from_date, to_date, page=1, per_page=1000):
        url = '/reports/expenses/projects?from={0}&to={1}&page={2}&per_page={3}'.format(from_date, to_date, page, per_page)
        return from_dict(data_class=ExpenseReportResults, data=self._get(url))

    def reports_expenses_categories(self, from_date, to_date, page=1, per_page=1000):
        url = '/reports/expenses/categories?from={0}&to={1}&page={2}&per_page={3}'.format(from_date, to_date, page, per_page)
        return from_dict(data_class=ExpenseReportResults, data=self._get(url))

    def reports_expenses_team(self, from_date, to_date, page=1, per_page=1000):
        url = '/reports/expenses/team?from={0}&to={1}&page={2}&per_page={3}'.format(from_date, to_date, page, per_page)
        return from_dict(data_class=ExpenseReportResults, data=self._get(url))

    def reports_uninvoiced(self, from_date, to_date, page=1, per_page=1000):
        url = '/reports/uninvoiced?from={0}&to={1}&page={2}&per_page={3}'.format(from_date, to_date, page, per_page)
        return from_dict(data_class=UninvoicedReportResults, data=self._get(url))

    def reports_time_clients(self, from_date, to_date, page=1, per_page=1000):
        url = '/reports/time/clients?from={0}&to={1}&page={2}&per_page={3}'.format(from_date, to_date, page, per_page)
        return from_dict(data_class=TimeReportResults, data=self._get(url))

    def reports_time_projects(self, from_date, to_date, page=1, per_page=1000):
        url = '/reports/time/projects?from={0}&to={1}&page={2}&per_page={3}'.format(from_date, to_date, page, per_page)
        return from_dict(data_class=TimeReportResults, data=self._get(url))

    def reports_time_tasks(self, from_date, to_date, page=1, per_page=1000):
        url = '/reports/time/tasks?from={0}&to={1}&page={2}&per_page={3}'.format(from_date, to_date, page, per_page)
        return from_dict(data_class=TimeReportResults, data=self._get(url))

    def reports_time_team(self, from_date, to_date, page=1, per_page=1000):
        url = '/reports/time/team?from={0}&to={1}&page={2}&per_page={3}'.format(from_date, to_date, page, per_page)
        return from_dict(data_class=TimeReportResults, data=self._get(url))

    def reports_project_budget(self, page=1, per_page=1000):
        url = '/reports/project_budget?page={0}&per_page={1}'.format(page, per_page)
        return from_dict(data_class=ProjectBudgetReportResults, data=self._get(url))

    def _get(self, path='/', data=None):
        return self._request('GET', path, data)

    def _post(self, path='/', data=None, files=None):
        return self._request('POST', path, data, files)

    def _delete(self, path='/', data=None):
        return self._request('DELETE', path, data)

    def _patch(self, path='/', data=None, files=None):
        return self._request('PATCH', path, data, files)

    def _request(self, method='GET', path='/', data=None, files=None):
        url = '{self.uri}{path}'.format(self=self, path=path)

        kwargs = {
            'method': method,
            'url': '{self.uri}{path}'.format(self=self, path=path),
            'headers': copy.deepcopy(self.__headers)
        }

        # patch to get the file object working
        if files is not None:
            del(kwargs['headers']['Content-Type'])
            kwargs['files'] = files
            kwargs['data'] = data
        else:
            kwargs['data'] = json.dumps(data)

        requestor = requests


        # request throttling
        if '/reports/' in url:
            # Reports requests have a limit of 100 request in 15 mins
            now = datetime.now()
            self.reports_throttle.append(now)
            oldest_time = self.reports_throttle.popleft()
            aged_delta = now - oldest_time
            if aged_delta <= self.reports_time_limit:
                self.reports_throttle.appendleft(oldest_time)

                if (len(self.reports_throttle) > self.RATE_LIMIT_REQUEST_COUNT):
                    time.sleep(self.RATE_LIMIT_REPORTS_DURATION_SECONDS * (aged_delta / self.reports_time_limit))
        else:
            # General requests have a limit of 100 request in 15 seconds
            now = datetime.now()
            self.request_throttle.append(now)
            oldest_time = self.request_throttle.popleft()
            aged_delta = now - oldest_time
            if aged_delta <= self.request_time_limit:
                self.request_throttle.appendleft(oldest_time)

                if (len(self.request_throttle) > self.RATE_LIMIT_REQUEST_COUNT):
                    time.sleep(self.RATE_LIMIT_REQUESTS_DURATION_SECONDS * (aged_delta / self.request_time_limit))

        # "auto" refresh_token. Currently only works on Authorization Code flow
        if isinstance(self.__auth, OAuth2_ServerSide) and (datetime.utcfromtimestamp(self.__auth.token.expires_at) <= datetime.now()):
            new_session = OAuth2Session(client_id=self.__auth.client_id, token=asdict(self.__auth.token))
            oauth_token = new_session.refresh_token(self.__auth.refresh_url, client_id=self.__auth.client_id, client_secret=self.__auth.client_secret)
            self.__auth = from_dict(data_class=OAuth2_ServerSide_Token, data=oauth_token)

        resp = requestor.request(**kwargs)

        if resp.status_code == 500:
            raise HarvestError('There was a server error for your request. Contact support@getharvest.com for help. url: {0}'.format(resp.url))

        elif resp.status_code == 429:
            raise HarvestError('Your request has been throttled. Raise an issue on the project in GitHub. https://github.com/bradbase/python-harvest_apiv2')

        elif resp.status_code == 422:
            raise HarvestError('There were errors processing your request. {0} {1}'.format(resp.url, resp.text))

        elif resp.status_code == 404:
            raise HarvestError('The object you requested can’t be found. {0}'.format(resp.url))

        elif resp.status_code == 403:
            raise HarvestError('The object you requested was found but you don’t have authorization to perform your request. {0}'.format(resp.url))

        elif resp.status_code in [200, 201]:

            if 'DELETE' not in method:
                try:
                    return resp.json()
                except:
                    return resp
            return resp

        else:
            raise HarvestError('Unsupported HTTP response code. {0} {1}'.format(resp.status_code, resp.url))
