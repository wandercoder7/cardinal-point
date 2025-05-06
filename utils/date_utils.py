def getCurrentTime():
    """
    Get the current time in the format YYYY-MM-DD HH:MM:SS
    """
    from datetime import datetime
    import pytz

    local_tz = pytz.timezone('Asia/Kolkata')  # Change timezone as needed
    dt = datetime.now(local_tz)
    return datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)