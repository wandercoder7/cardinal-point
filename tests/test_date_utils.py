import unittest
from utils.date_utils import get_start_date, get_last_business_day, get_last_business_friday, get_end_date, is_market_time, get_current_time
from utils.logger import get_logger
from datetime import datetime, timedelta
from unittest.mock import patch

log = get_logger(__name__)


class TestDateUtils(unittest.TestCase):

    def test_start_data(self):

        as_of_date = datetime(2023, 10, 1)

        # Test for 1 year
        start_date = get_start_date("1y", as_of_date)
        expected_start_date = as_of_date - timedelta(days=365)
        self.assertEqual(start_date.date(), expected_start_date.date())

        # Test for 2 years
        start_date = get_start_date("2y", as_of_date)
        expected_start_date = as_of_date - timedelta(days=730)
        self.assertEqual(start_date.date(), expected_start_date.date())

        # Test for 6 months
        start_date = get_start_date("6mo", as_of_date)
        expected_start_date = as_of_date - timedelta(days=183)
        self.assertEqual(start_date.date(), expected_start_date.date())

        # Test for 5 years
        start_date = get_start_date("5y", as_of_date)
        expected_start_date = as_of_date - timedelta(days=1825)
        self.assertEqual(start_date.date(), expected_start_date.date())

        # Test for 10 years
        start_date = get_start_date("10y", as_of_date)
        expected_start_date = as_of_date - timedelta(days=3650)
        self.assertEqual(start_date.date(), expected_start_date.date())

    def test_last_business_day(self):
        # Test for a weekday
        # Thursday -> Wednesday
        date, expected_date = datetime(2025, 7, 24), datetime(2025, 7, 23)
        last_business_day = get_last_business_day(date)
        self.assertEqual(last_business_day.date(), expected_date.date())

        # Monday -> Friday
        date, expected_date = datetime(2025, 7, 28), datetime(2025, 7, 25)
        last_business_day = get_last_business_day(date)
        self.assertEqual(last_business_day.date(), expected_date.date())

        # Sunday -> Friday
        date, expected_date = datetime(2025, 7, 27), datetime(2025, 7, 25)
        last_business_day = get_last_business_day(date)
        self.assertEqual(last_business_day.date(), expected_date.date())

    def test_last_business_friday(self):
        # Test for a weekday
        # Monday -> Friday
        date, expected_date = datetime(2025, 7, 21), datetime(2025, 7, 18)
        last_business_friday = get_last_business_friday(date)
        self.assertEqual(last_business_friday.date(), expected_date.date())

        # Tuesday -> Friday
        date, expected_date = datetime(2025, 7, 22), datetime(2025, 7, 18)
        last_business_friday = get_last_business_friday(date)
        self.assertEqual(last_business_friday.date(), expected_date.date())

        # Friday -> Previous Friday
        date, expected_date = datetime(2025, 7, 25), datetime(2025, 7, 25)
        last_business_friday = get_last_business_friday(date)
        self.assertEqual(last_business_friday.date(), expected_date.date())

    @patch('utils.date_utils.get_current_time')
    def test_is_market_time(self, current_time_mock):
        # Test within market hours
        current_time_mock.return_value = datetime(2025, 7, 24, 11, 0)
        date = datetime(2025, 7, 24, 10, 0)
        self.assertTrue(is_market_time(date))

        # Test before market hours
        date = datetime(2025, 7, 24, 8, 59)
        self.assertFalse(is_market_time(date))

        # Test after market hours
        date = datetime(2025, 7, 24, 16, 0)
        self.assertFalse(is_market_time(date))

    @patch('utils.date_utils.get_current_time')
    def test_get_end_date_day_interval(self, current_time_mock):
        current_time_mock.return_value = datetime(2025, 7, 24, 11, 0)
        
        # Test for 1 Day interval, before market hours
        as_of_date, expected_date = datetime(2025, 7, 23, 8, 30), datetime(2025, 7, 24)
        self.assertEqual(get_end_date(as_of_date, "1d").date(), expected_date.date())

        # Test for 1 Day interval, before market hours
        as_of_date, expected_date = datetime(2025, 7, 24, 8, 30), datetime(2025, 7, 24)
        self.assertEqual(get_end_date(as_of_date, "1d").date(), expected_date.date())

        # Test for 1 Day interval, during market hours
        as_of_date, expected_date = datetime(2025, 7, 24, 13, 0), datetime(2025, 7, 24)
        self.assertEqual(get_end_date(as_of_date, "1d").date(), expected_date.date())

        # Test for 1 Day interval, after market hours
        as_of_date, expected_date = datetime(2025, 7, 24, 16, 0), datetime(2025, 7, 25)
        self.assertEqual(get_end_date(as_of_date, "1d").date(), expected_date.date())

    @patch('utils.date_utils.get_current_time')
    def test_get_end_date_week_interval_non_friday(self, current_time_mock):
        # Test when current day not friday
        current_time_mock.return_value = datetime(2025, 7, 24, 11, 0)

        # Test for 1 Week interval, before market hours
        as_of_date, expected_date = datetime(2025, 7, 23, 8, 30, 0), datetime(2025, 7, 19)
        self.assertEqual(get_end_date(as_of_date, "1wk").date(), expected_date.date())

        # Test for 1 Week interval, before market hours
        as_of_date, expected_date = datetime(2025, 7, 24, 8, 30, 0), datetime(2025, 7, 19)
        self.assertEqual(get_end_date(as_of_date, "1wk").date(), expected_date.date())

        # Test for 1 Week interval, during market hours
        as_of_date, expected_date = datetime(2025, 7, 24, 13, 0, 0), datetime(2025, 7, 19)
        self.assertEqual(get_end_date(as_of_date, "1wk").date(), expected_date.date())

        # Test for 1 Week interval, after market hours
        as_of_date, expected_date = datetime(2025, 7, 24, 16, 0, 0), datetime(2025, 7, 19)
        self.assertEqual(get_end_date(as_of_date, "1wk").date(), expected_date.date())

    @patch('utils.date_utils.get_current_time')
    def test_get_end_date_week_interval_friday(self, current_time_mock):
        # Test when current day is friday
        current_time_mock.return_value = datetime(2025, 7, 25, 11, 0)

        # Test for 1 Week interval, before market hours
        as_of_date, expected_date = datetime(2025, 7, 24, 8, 30, 0), datetime(2025, 7, 19)
        self.assertEqual(get_end_date(as_of_date, "1wk").date(), expected_date.date())

        # Test for 1 Week interval, before market hours
        as_of_date, expected_date = datetime(2025, 7, 25, 8, 30, 0), datetime(2025, 7, 19)
        self.assertEqual(get_end_date(as_of_date, "1wk").date(), expected_date.date())

        # Test for 1 Week interval, during market hours
        as_of_date, expected_date = datetime(2025, 7, 25, 13, 0, 0), datetime(2025, 7, 19)
        self.assertEqual(get_end_date(as_of_date, "1wk").date(), expected_date.date())

        # Test for 1 Week interval, after market hours
        as_of_date, expected_date = datetime(2025, 7, 25, 16, 0, 0), datetime(2025, 7, 26)
        self.assertEqual(get_end_date(as_of_date, "1wk").date(), expected_date.date())
