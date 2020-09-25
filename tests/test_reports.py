
# Copyright 2020 Bradbase

import os, sys
import unittest
import configparser
from dataclasses import asdict
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import MobileApplicationClient, WebApplicationClient
import httpretty
import warnings
from dacite import from_dict
import json

sys.path.insert(0, sys.path[0]+"/..")

import harvest
from harvest.harvestdataclasses import *

"""
There is a sample test config.

Copy it, name it test_config.ini and fill it out with your test details.

tests/test_config.ini is already in .gitignore

Just in case, the test config file looks like this:

[PERSONAL ACCESS TOKEN]
url = https://api.harvestapp.com/api/v2
put_auth_in_header = True
personal_token = Bearer 1234567.pt.somebunchoflettersandnumbers
account_id = 1234567

[OAuth2 Implicit Code Grant]
uri = https://api.harvestapp.com/api/v2
client_id = aclientid
auth_url = https://id.getharvest.com/oauth2/authorize

[OAuth2 Authorization Code Grant]
uri = https://api.harvestapp.com/api/v2
client_id = aclientid
client_secret = itsmysecret
auth_url = https://id.getharvest.com/oauth2/authorize
token_url = https://id.getharvest.com/api/v2/oauth2/token
account_id = 1234567
"""

"""
Those who tread this path:-

These tests currently really only test that the default URL has been formed
correctly and that the datatype that gets returned can be typed into the dataclass.
Probably enough but a long way from "comprehensive".
"""

class TestReports(unittest.TestCase):

    def setUp(self):
        personal_access_token = PersonalAccessToken('ACCOUNT_NUMBER', 'PERSONAL_ACCESS_TOKEN')
        self.harvest = harvest.Harvest('https://api.harvestapp.com/api/v2', personal_access_token)
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*") # There's a bug in httpretty ATM.
        httpretty.enable()

    def teardown(self):
        httpretty.reset()
        httpretty.disable()


    def test_report_expenses_client(self):

        client_5735776 = {
          "client_id": 5735776,
          "client_name": "123 Industries",
          "total_amount": 100,
          "billable_amount": 100,
          "currency": "EUR"
        }

        client_5735774 = {
          "client_id": 5735774,
          "client_name": "ABC Corp",
          "total_amount": 133.35,
          "billable_amount": 133.35,
          "currency": "USD"
        }

        report_results_dict = {
                "results":[client_5735776, client_5735774],
                "per_page":1000,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/api/v2/reports/expenses/clients?from=20170101&page=1&per_page=1000&to=20171231",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/api/v2/reports/expenses/clients?from=20170101&page=1&per_page=1000&to=20171231"
                    }
            }

        # reports_expenses_clients
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/reports/expenses/clients?from=20170101&to=20171231",
                body=json.dumps(report_results_dict),
                status=200
            )
        report_expenses_clients = from_dict(data_class=ExpenseReportResults, data=report_results_dict)
        requested_report_expenses_clients = self.harvest.reports_expenses_clients(from_date=20170101, to_date=20171231)

        self.assertEqual(requested_report_expenses_clients, report_expenses_clients)

    def test_report_expenses_projects(self):

        project_14307913 = {
          "client_id": 5735774,
          "client_name": "ABC Corp",
          "project_id": 14307913,
          "project_name": "[MW] Marketing Website",
          "total_amount": 133.35,
          "billable_amount": 133.35,
          "currency": "USD"
        }

        project_14308069 = {
          "client_id": 5735776,
          "client_name": "123 Industries",
          "project_id": 14308069,
          "project_name": "[OS1] Online Store - Phase 1",
          "total_amount": 100,
          "billable_amount": 100,
          "currency": "EUR"
        }

        project_results_dict = {
                "results":[project_14307913, project_14308069],
                "per_page":1000,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/api/v2/reports/expenses/projects?from=20170101&page=1&per_page=1000&to=20171231",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/api/v2/reports/expenses/projects?from=20170101&page=1&per_page=1000&to=20171231"
                    }
            }

        # reports_expenses_projects
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/reports/expenses/projects?from=20170101&to=20171231",
                body=json.dumps(project_results_dict),
                status=200
            )
        report_expenses_projects = from_dict(data_class=ExpenseReportResults, data=project_results_dict)
        requested_report_expenses_projects = self.harvest.reports_expenses_projects(from_date=20170101, to_date=20171231)

        self.assertEqual(requested_report_expenses_projects, report_expenses_projects)


    def test_report_expenses_categories(self):

        category_4197501 = {
          "expense_category_id": 4197501,
          "expense_category_name": "Lodging",
          "total_amount": 100,
          "billable_amount": 100,
          "currency": "EUR"
        }

        category_4195926 = {
          "expense_category_id": 4195926,
          "expense_category_name": "Meals",
          "total_amount": 100,
          "billable_amount": 100,
          "currency": "EUR"
        }

        category_4195926 = {
          "expense_category_id": 4195926,
          "expense_category_name": "Meals",
          "total_amount": 33.35,
          "billable_amount": 33.35,
          "currency": "USD"
        }

        categories_results_dict = {
                "results":[category_4197501, category_4195926, category_4195926],
                "per_page":1000,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/api/v2/reports/expenses/categories?from=20170101&page=1&per_page=1000&to=20171231",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/api/v2/reports/expenses/categories?from=20170101&page=1&per_page=1000&to=20171231"
                    }
            }

        # reports_expenses_categories
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/reports/expenses/categories?from=20170101&to=20171231",
                body=json.dumps(categories_results_dict),
                status=200
            )
        report_expenses_categories = from_dict(data_class=ExpenseReportResults, data=categories_results_dict)
        requested_report_expenses_categories = self.harvest.reports_expenses_categories(from_date=20170101, to_date=20171231)

        self.assertEqual(requested_report_expenses_categories, report_expenses_categories)


    def test_report_expenses_team(self):

        user_id_1782884 = {
          "user_id": 1782884,
          "user_name": "Bob Powell",
          "is_contractor": False,
          "total_amount": 100,
          "billable_amount": 100,
          "currency": "USD"
        }

        user_id_1782959 = {
          "user_id": 1782959,
          "user_name": "Kim Allen",
          "is_contractor": False,
          "total_amount": 100,
          "billable_amount": 100,
          "currency": "EUR"
        }

        user_id_1782959 = {
          "user_id": 1782959,
          "user_name": "Kim Allen",
          "is_contractor": False,
          "total_amount": 33.35,
          "billable_amount": 33.35,
          "currency": "USD"
        }

        team_results_dict = {
                "results":[user_id_1782884, user_id_1782959, user_id_1782959],
                "per_page":1000,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/api/v2/reports/expenses/team?from=20170101&page=1&per_page=1000&to=20171231",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/api/v2/reports/expenses/team?from=20170101&page=1&per_page=1000&to=20171231"
                    }
            }

        # reports_expenses_team
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/reports/expenses/team?from=20170101&to=20171231",
                body=json.dumps(team_results_dict),
                status=200
            )
        report_expenses_team = from_dict(data_class=ExpenseReportResults, data=team_results_dict)
        requested_report_expenses_team = self.harvest.reports_expenses_team(from_date=20170101, to_date=20171231)

        self.assertEqual(requested_report_expenses_team, report_expenses_team)

    def test_report_uninvoiced(self):

        client_id_5735776 = {
          "client_id": 5735776,
          "client_name": "123 Industries",
          "project_id": 14308069,
          "project_name": "Online Store - Phase 1",
          "currency": "EUR",
          "total_hours": 4,
          "uninvoiced_hours": 0,
          "uninvoiced_expenses": 100,
          "uninvoiced_amount": 100
        }

        client_id_5735776 = {
          "client_id": 5735776,
          "client_name": "123 Industries",
          "project_id": 14808188,
          "project_name": "Task Force",
          "currency": "EUR",
          "total_hours": 0.5,
          "uninvoiced_hours": 0.5,
          "uninvoiced_expenses": 0,
          "uninvoiced_amount": 50
        }

        client_id_5735774 = {
          "client_id": 5735774,
          "client_name": "ABC Corp",
          "project_id": 14307913,
          "project_name": "Marketing Website",
          "currency": "USD",
          "total_hours": 2,
          "uninvoiced_hours": 0,
          "uninvoiced_expenses": 0,
          "uninvoiced_amount": 0
        }

        uninvoiced_results_dict = {
                "results":[client_id_5735776, client_id_5735776, client_id_5735774],
                "per_page":1000,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/api/v2/reports/uninvoiced?from=20170101&page=1&per_page=1000&to=20171231",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/api/v2/reports/uninvoiced?from=20170101&page=1&per_page=1000&to=20171231"
                    }
            }

        # reports_reports_uninvoiced
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/reports/uninvoiced?from=20170101&to=20171231",
                body=json.dumps(uninvoiced_results_dict),
                status=200
            )
        report_uninvoiced = from_dict(data_class=UninvoicedReportResults, data=uninvoiced_results_dict)
        requested_report_uninvoiced = self.harvest.reports_uninvoiced(from_date=20170101, to_date=20171231)

        self.assertEqual(requested_report_uninvoiced, report_uninvoiced)

    def test_report_time_clients(self):

        client_5735776 = {
          "client_id": 5735776,
          "client_name": "123 Industries",
          "total_hours": 4.5,
          "billable_hours": 3.5,
          "currency": "EUR",
          "billable_amount": 350
        }

        client_5735774 = {
          "client_id": 5735774,
          "client_name": "ABC Corp",
          "total_hours": 2,
          "billable_hours": 2,
          "currency": "USD",
          "billable_amount": 200
        }

        time_clients_results_dict = {
                "results":[client_5735776, client_5735774],
                "per_page":1000,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/api/v2/reports/time/clients?from=20170101&page=1&per_page=1000&to=20171231",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/api/v2/reports/time/clients?from=20170101&page=1&per_page=1000&to=20171231"
                    }
            }

        # reports_time_clients
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/reports/time/clients?from=20170101&to=20171231",
                body=json.dumps(time_clients_results_dict),
                status=200
            )
        report_time_clients = from_dict(data_class=TimeReportResults, data=time_clients_results_dict)
        requested_report_time_clients = self.harvest.reports_time_clients(from_date=20170101, to_date=20171231)

        self.assertEqual(requested_report_time_clients, report_time_clients)

    def test_report_time_projects(self):

        project_14307913 = {
          "project_id": 14307913,
          "project_name": "[MW] Marketing Website",
          "client_id": 5735774,
          "client_name": "ABC Corp",
          "total_hours": 2,
          "billable_hours": 2,
          "currency": "USD",
          "billable_amount": 200
        }

        project_14308069 = {
          "project_id": 14308069,
          "project_name": "[OS1] Online Store - Phase 1",
          "client_id": 5735776,
          "client_name": "123 Industries",
          "total_hours": 4,
          "billable_hours": 3,
          "currency": "EUR",
          "billable_amount": 300
        }

        project_14808188 = {
          "project_id": 14808188,
          "project_name": "[TF] Task Force",
          "client_id": 5735776,
          "client_name": "123 Industries",
          "total_hours": 0.5,
          "billable_hours": 0.5,
          "currency": "EUR",
          "billable_amount": 50
        }

        time_projects_results_dict = {
                "results":[project_14307913, project_14308069, project_14808188],
                "per_page":1000,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/api/v2/reports/time/projects?from=20170101&page=1&per_page=1000&to=20171231",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/api/v2/reports/time/projects?from=20170101&page=1&per_page=1000&to=20171231"
                    }
            }

        # reports_time_projects
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/reports/time/projects?from=20170101&to=20171231",
                body=json.dumps(time_projects_results_dict),
                status=200
            )
        report_time_projects = from_dict(data_class=TimeReportResults, data=time_projects_results_dict)
        requested_report_time_projects = self.harvest.reports_time_projects(from_date=20170101, to_date=20171231)

        self.assertEqual(requested_report_time_projects, report_time_projects)

    def test_report_time_tasks(self):

        task_8083365 = {
          "task_id": 8083365,
          "task_name": "Graphic Design",
          "total_hours": 2,
          "billable_hours": 2,
          "currency": "USD",
          "billable_amount": 200
        }

        task_8083366 = {
          "task_id": 8083366,
          "task_name": "Programming",
          "total_hours": 1.5,
          "billable_hours": 1.5,
          "currency": "EUR",
          "billable_amount": 150
        }

        task_8083367 = {
          "task_id": 8083367,
          "task_name": "Project Management",
          "total_hours": 1.5,
          "billable_hours": 1.5,
          "currency": "EUR",
          "billable_amount": 150
        }

        task_8083368 = {
          "task_id": 8083368,
          "task_name": "Project Management",
          "total_hours": 0.5,
          "billable_hours": 0.5,
          "currency": "USD",
          "billable_amount": 50
        }

        task_8083369 = {
          "task_id": 8083369,
          "task_name": "Research",
          "total_hours": 1,
          "billable_hours": 0,
          "currency": "EUR",
          "billable_amount": 0
        }

        time_tasks_results_dict = {
                "results":[task_8083365, task_8083366, task_8083367, task_8083368, task_8083369],
                "per_page":1000,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/api/v2/reports/time/tasks?from=20170101&page=1&per_page=1000&to=20171231",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/api/v2/reports/time/tasks?from=20170101&page=1&per_page=1000&to=20171231"
                    }
            }

        # reports_time_tasks
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/reports/time/tasks?from=20170101&to=20171231",
                body=json.dumps(time_tasks_results_dict),
                status=200
            )
        report_time_tasks = from_dict(data_class=TimeReportResults, data=time_tasks_results_dict)
        requested_report_time_tasks = self.harvest.reports_time_tasks(from_date=20170101, to_date=20171231)

        self.assertEqual(requested_report_time_tasks, report_time_tasks)

    def test_report_time_team(self):

        team_1 = {
          "user_id": 1795925,
          "user_name": "Jane Smith",
          "is_contractor": False,
          "total_hours": 0.5,
          "billable_hours": 0.5,
          "currency": "EUR",
          "billable_amount": 50
        }

        team_2 = {
          "user_id": 1782959,
          "user_name": "Kim Allen",
          "is_contractor": False,
          "total_hours": 4,
          "billable_hours": 3,
          "currency": "EUR",
          "billable_amount": 300
        }

        team_3 = {
          "user_id": 1782959,
          "user_name": "Kim Allen",
          "is_contractor": False,
          "total_hours": 2,
          "billable_hours": 2,
          "currency": "USD",
          "billable_amount": 200
        }

        time_team_results_dict = {
                "results":[team_1, team_2, team_3],
                "per_page":1000,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/api/v2/reports/time/team?from=20170101&page=1&per_page=1000&to=20171231",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/api/v2/reports/time/team?from=20170101&page=1&per_page=1000&to=20171231"
                    }
            }

        # reports_time_team
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/reports/time/team?from=20170101&to=20171231",
                body=json.dumps(time_team_results_dict),
                status=200
            )
        report_time_team = from_dict(data_class=TimeReportResults, data=time_team_results_dict)
        requested_report_time_team = self.harvest.reports_time_team(from_date=20170101, to_date=20171231)

        self.assertEqual(requested_report_time_team, report_time_team)

    def test_report_project_budget(self):

        project_14308069 = {
          "project_id": 14308069,
          "project_name": "Online Store - Phase 1",
          "client_id": 5735776,
          "client_name": "123 Industries",
          "budget_is_monthly": False,
          "budget_by": "project",
          "is_active": True,
          "budget": 200,
          "budget_spent": 4,
          "budget_remaining": 196
        }

        project_14307913 = {
          "project_id": 14307913,
          "project_name": "Marketing Website",
          "client_id": 5735774,
          "client_name": "ABC Corp",
          "budget_is_monthly": False,
          "budget_by": "project",
          "is_active": True,
          "budget": 50,
          "budget_spent": 2,
          "budget_remaining": 48
        }

        project_budget_results_dict = {
                "results":[project_14308069, project_14307913],
                "per_page":1000,
                "total_pages":1,
                "total_entries":2,
                "next_page":None,
                "previous_page":None,
                "page":1,
                "links":{
                        "first":"https://api.harvestapp.com/api/v2/reports/project_budget?from=20170101&page=1&per_page=1000&to=20171231",
                        "next":None,
                        "previous":None,
                        "last":"https://api.harvestapp.com/api/v2/reports/project_budget?from=20170101&page=1&per_page=1000&to=20171231"
                    }
            }

        # reports_project_budget
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/reports/project_budget?from=20170101&to=20171231",
                body=json.dumps(project_budget_results_dict),
                status=200
            )
        report_project_budget = from_dict(data_class=ProjectBudgetReportResults, data=project_budget_results_dict)
        requested_report_project_budget = self.harvest.reports_project_budget()

        self.assertEqual(requested_report_project_budget, report_project_budget)
