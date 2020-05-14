from datetime import date

import constants
from dates import find_date

TODAY = date.today()
DAYS = 100
STATE_CODE = constants.StateCodes.BAVARIA.value

date = find_date(state_code=STATE_CODE, start=TODAY, days=DAYS)
print(date)
