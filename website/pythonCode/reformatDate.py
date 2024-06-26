"""
This module contains functions to reformat a date and change the format of a date

 """
from datetime import datetime
import pytz
from tzlocal import get_localzone

def reformat_date(last_updated: datetime):
    """ 
    input:
        - last_updated: a datetime object
    output:
        - a string with the time since the last update
    In essence, this function takes a datetime object and returns a string with the time since the last update
    The goal is to have a more human-readable format for the date
    """

    # if the date is None, return None
    if last_updated is None:
        return None

    # Sometimes, datetime.now() is delayed by a few seconds. In case that this happens
    # we will return 'just now' if the difference is less than 60 seconds
    if (datetime.now() - last_updated).total_seconds() < 0:
        return "just now"
    
    # if the number of years is +1, return years
    if (datetime.now() - last_updated).days >= 365:
        years = round((datetime.now() - last_updated).days // 365, 0)
        if years == 1:
            return "1 year ago"
        return str(years) + "years ago"

    # if the number of months is +1, return months
    elif (datetime.now() - last_updated).days >= 30:
        months = round((datetime.now() - last_updated).days // 30, 0)
        if months == 1:
            return "1 month ago"
        return str(months) + " months ago"

    # if the number of weeks is +1, return weeks
    elif (datetime.now() - last_updated).days >= 7:
        weeks = round((datetime.now() - last_updated).days // 7, 0)
        if weeks == 1:
            return "last week"
        return str(weeks) + " weeks ago"

    # if the number of days is +1, return days
    elif (datetime.now() - last_updated).days >= 1:
        days = round((datetime.now() - last_updated).days, 0)
        if days == 1:
            return "yesterday"
        return str(days) + " days ago"

    # if the number of hours is +1, return hours
    elif (datetime.now() - last_updated).total_seconds() >= 3600:
        hours = round((datetime.now() - last_updated).seconds // 3600, 0)
        if hours == 1:
            return "1 hour ago"
        return str(hours) + " hours ago"

    # if the number of minutes is +1, return minutes
    elif (datetime.now() - last_updated).seconds >= 60:
        minutes = round((datetime.now() - last_updated).seconds // 60, 0)
        if minutes == 1:
            return "1 minute ago"
        return str(minutes) + " minutes ago"
    
    else: # if the difference is less than 60 seconds, return 'just now'
        return "just now"


def change_format_date(date: datetime):
    """ 
    input:
        - date: a datetime object
    output:
        - a string with the date in the format 'dd/mm/yyyy hh:mm', or False if an error occurred
    This function takes a datetime object and returns a string with the date in the format 'dd/mm/yyyy hh:mm'
    """

    try:

        date = date.astimezone(pytz.utc) # change the date to UTC

        local_timezone = get_localzone() # get the local timezone
        converted_date = date.astimezone(local_timezone) # change the date to the local timezone

        converted_date = converted_date.replace(tzinfo=None) # remove the timezone information

        return reformat_date(converted_date) # return the date in the new format
    
    except Exception:
        return False