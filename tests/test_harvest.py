
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
from mock import patch, Mock
from datetime import datetime, timedelta, date

sys.path.insert(0, sys.path[0]+"/..")

from harvest import Harvest, HarvestError, assemble_query_string
from harvest.detailedreports import DetailedReports
from harvest.harvestdataclasses import *

class TestHarvest(unittest.TestCase):

    def setUp(self):
        personal_access_token = PersonalAccessToken('ACCOUNT_NUMBER', 'PERSONAL_ACCESS_TOKEN')
        self.harvest = Harvest('https://api.harvestapp.com/api/v2', personal_access_token)
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*") # There's a bug in httpretty ATM.
        httpretty.enable()

    def teardown(self):
        httpretty.reset()
        httpretty.disable()

    def test_HTTP_500(self):

        user_1782884_dict = {
                "id":1782884,
                "first_name":"Bob",
                "last_name":"Powell",
                "email":"bobpowell@example.com",
                "telephone":"",
                "timezone":"Mountain Time (US & Canada)",
                "has_access_to_all_future_projects":False,
                "is_contractor":False,
                "is_admin":True,
                "is_project_manager":False,
                "can_see_rates":True,
                "can_create_projects":True,
                "can_create_invoices":True,
                "is_active":True,
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T20:42:25Z",
                "weekly_capacity":126000,
                "default_hourly_rate":100.0,
                "cost_rate":75.0,
                "roles":["Founder", "CEO"],
                "avatar_url":"https://cache.harvestapp.com/assets/profile_images/allen_bradley_clock_tower.png?1498509661"
            }
        me = from_dict(data_class=User, data=user_1782884_dict)

        # get_currently_authenticated_user
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/users/me",
                body=json.dumps(user_1782884_dict),
                status=500
            )

        with self.assertRaises(HarvestError) as context:
            self.harvest.get_currently_authenticated_user()

        self.assertTrue('There was a server error for your request.' in str(context.exception))

        httpretty.reset()

    def test_HTTP_429(self):

        user_1782884_dict = {
                "id":1782884,
                "first_name":"Bob",
                "last_name":"Powell",
                "email":"bobpowell@example.com",
                "telephone":"",
                "timezone":"Mountain Time (US & Canada)",
                "has_access_to_all_future_projects":False,
                "is_contractor":False,
                "is_admin":True,
                "is_project_manager":False,
                "can_see_rates":True,
                "can_create_projects":True,
                "can_create_invoices":True,
                "is_active":True,
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T20:42:25Z",
                "weekly_capacity":126000,
                "default_hourly_rate":100.0,
                "cost_rate":75.0,
                "roles":["Founder", "CEO"],
                "avatar_url":"https://cache.harvestapp.com/assets/profile_images/allen_bradley_clock_tower.png?1498509661"
            }
        me = from_dict(data_class=User, data=user_1782884_dict)

        # get_currently_authenticated_user
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/users/me",
                body=json.dumps(user_1782884_dict),
                status=429
            )

        with self.assertRaises(HarvestError) as context:
            self.harvest.get_currently_authenticated_user()

        self.assertTrue('Your request has been throttled.' in str(context.exception))

        httpretty.reset()

    def test_HTTP_422(self):

        user_1782884_dict = {
                "id":1782884,
                "first_name":"Bob",
                "last_name":"Powell",
                "email":"bobpowell@example.com",
                "telephone":"",
                "timezone":"Mountain Time (US & Canada)",
                "has_access_to_all_future_projects":False,
                "is_contractor":False,
                "is_admin":True,
                "is_project_manager":False,
                "can_see_rates":True,
                "can_create_projects":True,
                "can_create_invoices":True,
                "is_active":True,
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T20:42:25Z",
                "weekly_capacity":126000,
                "default_hourly_rate":100.0,
                "cost_rate":75.0,
                "roles":["Founder", "CEO"],
                "avatar_url":"https://cache.harvestapp.com/assets/profile_images/allen_bradley_clock_tower.png?1498509661"
            }
        me = from_dict(data_class=User, data=user_1782884_dict)

        # get_currently_authenticated_user
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/users/me",
                body=json.dumps(user_1782884_dict),
                status=422
            )

        with self.assertRaises(HarvestError) as context:
            self.harvest.get_currently_authenticated_user()

        self.assertTrue('There were errors processing your request.' in str(context.exception))

        httpretty.reset()

    def test_HTTP_404(self):

        user_1782884_dict = {
                "id":1782884,
                "first_name":"Bob",
                "last_name":"Powell",
                "email":"bobpowell@example.com",
                "telephone":"",
                "timezone":"Mountain Time (US & Canada)",
                "has_access_to_all_future_projects":False,
                "is_contractor":False,
                "is_admin":True,
                "is_project_manager":False,
                "can_see_rates":True,
                "can_create_projects":True,
                "can_create_invoices":True,
                "is_active":True,
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T20:42:25Z",
                "weekly_capacity":126000,
                "default_hourly_rate":100.0,
                "cost_rate":75.0,
                "roles":["Founder", "CEO"],
                "avatar_url":"https://cache.harvestapp.com/assets/profile_images/allen_bradley_clock_tower.png?1498509661"
            }
        me = from_dict(data_class=User, data=user_1782884_dict)

        # get_currently_authenticated_user
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/users/me",
                body=json.dumps(user_1782884_dict),
                status=404
            )

        with self.assertRaises(HarvestError) as context:
            self.harvest.get_currently_authenticated_user()

        self.assertTrue('The object you requested can’t be found.' in str(context.exception))

        httpretty.reset()

    def test_HTTP_403(self):

        user_1782884_dict = {
                "id":1782884,
                "first_name":"Bob",
                "last_name":"Powell",
                "email":"bobpowell@example.com",
                "telephone":"",
                "timezone":"Mountain Time (US & Canada)",
                "has_access_to_all_future_projects":False,
                "is_contractor":False,
                "is_admin":True,
                "is_project_manager":False,
                "can_see_rates":True,
                "can_create_projects":True,
                "can_create_invoices":True,
                "is_active":True,
                "created_at":"2017-06-26T20:41:00Z",
                "updated_at":"2017-06-26T20:42:25Z",
                "weekly_capacity":126000,
                "default_hourly_rate":100.0,
                "cost_rate":75.0,
                "roles":["Founder", "CEO"],
                "avatar_url":"https://cache.harvestapp.com/assets/profile_images/allen_bradley_clock_tower.png?1498509661"
            }
        me = from_dict(data_class=User, data=user_1782884_dict)

        # get_currently_authenticated_user
        httpretty.register_uri(httpretty.GET,
                "https://api.harvestapp.com/api/v2/users/me",
                body=json.dumps(user_1782884_dict),
                status=403
            )

        with self.assertRaises(HarvestError) as context:
            self.harvest.get_currently_authenticated_user()

        self.assertTrue('The object you requested was found but you don’t have authorization to perform your request.' in str(context.exception))

        httpretty.reset()

    def test_assemble_query_string_bool_lower(self):
        target_query_string = "is_active=false&is_billed=true&page=1&per_page=100"
        key_words = {"is_active":False, "is_billed":True}
        query_string = assemble_query_string(**key_words)
        self.assertEqual(query_string, target_query_string)

    def test_assemble_query_string_page(self):
        target_query_string = "page=10&per_page=100"
        key_words = {'page':10}
        query_string = assemble_query_string(**key_words)
        self.assertEqual(query_string, target_query_string)

    def test_assemble_query_string_per_page(self):
        target_query_string = "per_page=10&page=1"
        key_words = {'per_page':10}
        query_string = assemble_query_string(**key_words)
        self.assertEqual(query_string, target_query_string)
