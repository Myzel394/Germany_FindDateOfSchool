from datetime import date, timedelta

import constants
from dates import get_all_holidays

TODAY = date.today() + timedelta(days=1)
DAYS = 212
STATE_CODE = constants.StateCodes.BAVARIA.value

excludes = get_all_holidays(year=TODAY.year, state_code=STATE_CODE)
# Remove dates that are not in TODAY.year
excludes = set(filter(lambda x: x.year == TODAY.year, excludes))


amount = 365 - len(excludes)
print(amount)
