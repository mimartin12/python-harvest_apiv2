
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

from harvest import Harvest
from harvest.detailedreports import DetailedReports
from harvest.harvestdataclasses import *

class TestDetailedReports(unittest.TestCase):

    def setUp(self):
        personal_access_token = PersonalAccessToken('ACCOUNT_NUMBER', 'PERSONAL_ACCESS_TOKEN')
        self.detailed_reports = DetailedReports('https://api.harvestapp.com/api/v2', personal_access_token)
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*") # There's a bug in httpretty ATM.
        httpretty.enable()

    # def teardown(self):
    #     httpretty.reset()
    #     httpretty.disable()

    def test_timeframe_this_week(self, ):
        with patch('harvest.detailedreports.datetime') as datetime_mock:

            now = datetime.strptime('1970-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            from_date = datetime.strptime('1969-12-29 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            to_date = datetime.strptime('1970-01-04 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f')

            datetime_mock.return_value = now
            datetime_mock.now.return_value = now

            detailed_reports_this_week = self.detailed_reports.timeframe('This Week')

            this_week = {'from_date': from_date.date(), 'to_date': to_date.date()}

            self.assertEqual(detailed_reports_this_week, this_week)

    def test_timeframe_last_week(self):
        with patch('harvest.detailedreports.datetime') as datetime_mock:

            now = datetime.strptime('1970-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            from_date = datetime.strptime('1969-12-22 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            to_date = datetime.strptime('1969-12-28 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f')

            datetime_mock.return_value = now
            datetime_mock.now.return_value = now

            detailed_reports_last_week = self.detailed_reports.timeframe('Last Week')

            last_week = {'from_date': from_date.date(), 'to_date': to_date.date()}

            self.assertEqual(detailed_reports_last_week, last_week)

    def test_timeframe_this_semimonth(self):
        with patch('harvest.detailedreports.datetime') as datetime_mock:

            now = datetime.strptime('1970-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            from_date = datetime.strptime('1970-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            to_date = datetime.strptime('1970-01-15 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f')

            datetime_mock.return_value = now
            datetime_mock.now.return_value = now

            detailed_reports_this_semimonth = self.detailed_reports.timeframe('This Semimonth')

            this_semimonth = {'from_date': from_date.date(), 'to_date': to_date.date()}

            self.assertEqual(detailed_reports_this_semimonth, this_semimonth)

    def test_timeframe_last_semimonth(self):
        with patch('harvest.detailedreports.datetime') as datetime_mock:

            now = datetime.strptime('1970-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            from_date = datetime.strptime('1969-12-16 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            to_date = datetime.strptime('1969-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f')

            datetime_mock.return_value = now
            datetime_mock.now.return_value = now

            detailed_reports_last_semimonth = self.detailed_reports.timeframe('Last Semimonth')

            last_semimonth = {'from_date': from_date.date(), 'to_date': to_date.date()}

            self.assertEqual(detailed_reports_last_semimonth, last_semimonth)

    def test_timeframe_this_month(self):
        with patch('harvest.detailedreports.datetime') as datetime_mock:

            now = datetime.strptime('1970-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            from_date = datetime.strptime('1970-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            to_date = datetime.strptime('1970-01-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f')

            datetime_mock.return_value = now
            datetime_mock.now.return_value = now

            detailed_reports_this_month = self.detailed_reports.timeframe('This Month')

            this_month = {'from_date': from_date.date(), 'to_date': to_date.date()}

            self.assertEqual(detailed_reports_this_month, this_month)

    def test_timeframe_last_month(self):
        with patch('harvest.detailedreports.datetime') as datetime_mock:

            now = datetime.strptime('1970-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            from_date = datetime.strptime('1969-12-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            to_date = datetime.strptime('1969-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f')

            datetime_mock.return_value = now
            datetime_mock.now.return_value = now

            detailed_reports_last_month = self.detailed_reports.timeframe('Last Month')

            last_month = {'from_date': from_date.date(), 'to_date': to_date.date()}

            self.assertEqual(detailed_reports_last_month, last_month)

    def test_timeframe_this_quarter(self):
        with patch('harvest.detailedreports.datetime') as datetime_mock:

            now = datetime.strptime('1970-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            from_date = datetime.strptime('1970-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            to_date = datetime.strptime('1970-03-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f')

            datetime_mock.return_value = now
            datetime_mock.now.return_value = now

            detailed_reports_this_quarter = self.detailed_reports.timeframe('This Quarter')

            this_quarter = {'from_date': from_date.date(), 'to_date': to_date.date()}

            self.assertEqual(detailed_reports_this_quarter, this_quarter)

    def test_timeframe_last_quarter(self):
        with patch('harvest.detailedreports.datetime') as datetime_mock:

            now = datetime.strptime('1970-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            from_date = datetime.strptime('1969-10-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            to_date = datetime.strptime('1969-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f')

            datetime_mock.return_value = now
            datetime_mock.now.return_value = now

            detailed_reports_last_quarter = self.detailed_reports.timeframe('Last Quarter')

            last_quarter = {'from_date': from_date.date(), 'to_date': to_date.date()}

            self.assertEqual(detailed_reports_last_quarter, last_quarter)

    def test_timeframe_this_year(self):
        with patch('harvest.detailedreports.datetime') as datetime_mock:

            now = datetime.strptime('1970-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            from_date = datetime.strptime('1970-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            to_date = datetime.strptime('1970-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f')

            datetime_mock.return_value = now
            datetime_mock.now.return_value = now

            detailed_reports_this_year = self.detailed_reports.timeframe('This Year')

            this_year = {'from_date': from_date.date(), 'to_date': to_date.date()}

            self.assertEqual(detailed_reports_this_year, this_year)

    def test_timeframe_last_year(self):
        with patch('harvest.detailedreports.datetime') as datetime_mock:

            now = datetime.strptime('1970-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            from_date = datetime.strptime('1969-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
            to_date = datetime.strptime('1969-12-31 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f')

            datetime_mock.return_value = now
            datetime_mock.now.return_value = now

            detailed_reports_last_year = self.detailed_reports.timeframe('Last Year')

            last_year = {'from_date': from_date.date(), 'to_date': to_date.date()}

            self.assertEqual(detailed_reports_last_year, last_year)

    def test_timeframe_all_time(self):
        with patch('harvest.detailedreports.datetime') as datetime_mock:

            detailed_reports_all_time = self.detailed_reports.timeframe('All Time')
            all_time = {}

            self.assertEqual(detailed_reports_all_time, all_time)
