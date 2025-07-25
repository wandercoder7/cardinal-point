#write test for utils/data_fetching.py
import unittest
from utils.data_fetching import fetch_stock_data
from utils.date_utils import get_last_business_day, get_last_business_friday
from utils.constants import TIMEFRAMES
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class TestDataFetching(unittest.TestCase):

    def test_daily_tf_data(self):
        ticker = "ABB.NS"
        interval, period = TIMEFRAMES.get('1 Day')
        as_of_date = datetime.now()
        data = fetch_stock_data(ticker, period=period, interval=interval, as_of_date=as_of_date)
        self.assertIsNotNone(data)
        self.assertIn('Close', data.columns)
        log.info(f"as of date: {as_of_date}")
        expected_last_date = get_last_business_day(as_of_date)
        log.info(f"Expected last date: {expected_last_date}")
        self.assertEqual(data.index[-1].date(), expected_last_date.date())

    def test_weekly_tf_data(self):
        ticker = "ABB.NS"
        interval, period = TIMEFRAMES.get('1 Week')
        as_of_date = datetime.now()
        data = fetch_stock_data(ticker, period=period, interval=interval, as_of_date=as_of_date)
        self.assertIsNotNone(data)
        self.assertIn('Close', data.columns)
        expected_last_date = get_last_business_friday(as_of_date)
        self.assertEqual(data.index[-1].date(), expected_last_date.date())

    

if __name__ == '__main__':
    unittest.main()