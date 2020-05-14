import json
from datetime import datetime, date, timedelta
from urllib import parse
from urllib.request import urlopen
from http.client import HTTPResponse
from typing import Optional, Set, Tuple
from dateutil.rrule import rrule, DAILY

NOW = datetime.now()
SimpleHolidayReturn = Set[datetime]
HolidayReturn = Set[Tuple[datetime, datetime]]


def get_holidays(
        state_code: str,
        year: int = NOW.year,
        date_format: str = "%Y-%m-%dT00:00",
        base_url: str = "https://ferien-api.de/api/v1/holidays/"
) -> HolidayReturn:
    get_params = {"year": year, "nur_land": state_code}
    url = f"{base_url}{state_code}?{parse.urlencode(get_params)}"
    
    site = urlopen(url)  # type: HTTPResponse
    
    if site.getcode() == 200:
        try:
            holidays = json.loads(site.read())
        except ValueError:
            return set()
        
        return {
            (
                datetime.strptime(holiday["start"], date_format).date(),
                datetime.strptime(holiday["end"], date_format).date(),
            )
            for holiday in holidays
        }


def get_public_holidays(
        state_code: str,
        year: int = NOW.year,
        date_format: str = "%Y-%m-%d",
        base_url: str = "https://feiertage-api.de/api/",
) -> SimpleHolidayReturn:
    get_params = {"year": year, "nur_land": state_code}
    url = base_url + "?" + parse.urlencode(get_params)
    
    site = urlopen(url)  # type: HTTPResponse
    
    if site.getcode() == 200:
        try:
            dates = json.loads(site.read())
        except ValueError:
            return set()
        
        return {
            datetime.strptime(data["datum"], date_format).date()
            for _, data in dates.items()
        }


def get_weekend_holidays(
        year: int = NOW.year,
        exclude_weekdays: Tuple[int] = (5, 6)
) -> SimpleHolidayReturn:
    dt: datetime
    
    return {
        dt.date()
        for dt in rrule(DAILY, dtstart=date(year, 1, 1), until=date(year, 12, 31))
        if dt.weekday() in exclude_weekdays
    }


def get_all_holidays(year: int, state_code: str) -> set:
    return {
        *get_holidays(state_code=state_code, year=year),
        *get_public_holidays(state_code=state_code, year=year),
        *get_weekend_holidays(year=year)
    }


def is_date_excluded(d: date, /, exclude_set: set):
    simple_dates = {
        dt for dt in exclude_set if type(dt) is date
    }

    if d in simple_dates:
        return True

    range_dates = {
        dt_set for dt_set in exclude_set if type(dt_set) is tuple
    }

    for date_range in range_dates:  # type: Tuple[date, date]
        if date_range[0] <= d <= date_range[1]:
            return True

    return False


def find_date(state_code: str, start: Optional[date] = None, days: int = 5) -> date:
    """
    Finds the next school day in `amount` days.
    :param state_code: The state code of the federal state
    :param start: The start date
    :param days: Amount of days
    :return: The found date
    """
    if days == 0:
        return date
    
    if start is None:
        start = date.today()
    
    counter: int = 0
    current: date = start
    current_year: int = current.year - 1
    exclude = set()

    while True:  # Do-While
        current += timedelta(days=1)
    
        # Add exclude dates from current year
        if current_year < (year := current.year):
            current_year = year
            exclude.update(get_all_holidays(year=year, state_code=state_code))
    
        # Check date
        if is_date_excluded(current, exclude):
            continue
    
        counter += 1
    
        if counter > days:  # Do-While
            return current
