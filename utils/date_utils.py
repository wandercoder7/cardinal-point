from datetime import datetime, timedelta

def get_current_time():
    """
    Get the current time in the format YYYY-MM-DD HH:MM:SS
    """
    from datetime import datetime
    import pytz

    local_tz = pytz.timezone('Asia/Kolkata')  # Change timezone as needed
    dt = datetime.now(local_tz)
    return datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)


def get_start_date(period, as_of_date):
    start = as_of_date
    # Adjust the start based on the as_of_date and period
    if(period == "1y"):
        start = start - timedelta(days=365)
    elif(period == "2y"):
        start = start - timedelta(days=730)
    elif(period == "6mo"):
        start = start - timedelta(days=183)
    elif(period == "5y"):
        start = start - timedelta(days=1825)
    elif(period == "10y"):  
        start = start - timedelta(days=3650)
    return start

def get_end_date(as_of_date, interval):
    # for interval '1 Day'
    #  if as_of_date is in market hour then return as_of_date
    #  else return the as_of_date + 1 day
    # for interval '1 Week'
    #  if as_of_date is in market hour then return as_of_date
    #  else return the last business friday before the as_of_date + 1 day
    as_of_date = datetime(as_of_date.year, as_of_date.month, as_of_date.day, 0, 0, 0)

    if interval == "1d":
        if is_market_time(as_of_date):
            return as_of_date
        elif is_after_market_time(as_of_date):
            return as_of_date + timedelta(days=1)
        elif is_before_market_time(as_of_date) and is_same_day(as_of_date, get_current_time()):
            return as_of_date
        else:
            return as_of_date + timedelta(days=1)
        
    elif interval == "1wk":
        if is_after_market_time(as_of_date) and is_same_day(as_of_date, get_current_time()):
            return as_of_date + timedelta(days=1)
        elif is_same_day(as_of_date, get_current_time()) and (is_before_market_time(as_of_date) or is_market_time(as_of_date) ):
            as_of_date = as_of_date - timedelta(days=1)
            return get_last_business_friday(as_of_date) + timedelta(days=1)
        else:
            return get_last_business_friday(as_of_date) + timedelta(days=1)

def get_last_business_day(date):
        # find the last working day before the given date excluding weekends
        # if date is a weekend, return the last Friday
        # if date is a monday, return the last Friday
        # if date is a Friday, return the last Thursday
        last_date = date
        while True:
            last_date -= timedelta(days=1)
            if last_date.weekday() in [0, 1, 2, 3, 4]:
                break
        return last_date
    
def get_last_business_friday(date):
    # find the last working day before the given date excluding weekends which is a Friday
    last_date = date    
    
    while last_date.weekday() != 4:
        last_date -= timedelta(days=1)
    return last_date

def is_market_time(date):
    """
    Check if the current time is within market hours (9:15 AM to 3:30 PM IST).
    """
    return not(is_before_market_time(date) or is_after_market_time(date))

def is_before_market_time(date):
    """
    Check if the current time is before market hours (9:15 AM IST).
    """
    current = get_current_time()
    market_start = current.replace(hour=9, minute=15, second=0, microsecond=0)
    return date < market_start

def is_after_market_time(date):
    """
    Check if the current time is after market hours (3:30 PM IST).
    """
    current = get_current_time()
    market_end = current.replace(hour=15, minute=30, second=0, microsecond=0)
    return date > market_end

def is_same_day(date1, date2):
    """
    Check if two dates are the same day.
    """
    return date1.date() == date2.date()