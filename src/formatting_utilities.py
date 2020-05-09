# Global formatting utilities
from typing import List, Set, Dict, Tuple, Optional, Iterable

import datetime
from datetime import date, timedelta
from matplotlib.dates import num2date

BASE_DATE = date.fromisoformat('2020-02-24')

def format_date(xdate, x, p, base_date=BASE_DATE, special={}, rotate=False):
    xday = xdate.day
    outstr = str(xday)
    if rotate:
        outstr = ' ' + outstr
    if (p==0 or xdate==base_date or xday==1):
        if rotate:
            outstr = xdate.strftime('%Y %b') + outstr
        else:
            outstr += xdate.strftime('\n%b\n%Y')
    if p in special:
        outstr = special[p] + outstr
    return outstr
    
def format_dates(x, p):
    return format_date(num2date(x.item()), x, p)

def format_dates_from_numbers(x, p, base_date=BASE_DATE, special={}, rotate=False):
    return format_date(base_date+timedelta(days=x.item()), x, p, base_date=base_date, special=special, rotate=rotate)

def number2date(number: int, base_date: datetime.date = BASE_DATE) -> str:
    return (base_date+timedelta(days=number)).strftime('%d/%m/%Y')

def numbers2dates(numbers: List[int], base_date: datetime.date = BASE_DATE) -> Iterable[str]:
    return map(lambda n: number2date(n, base_date), numbers)

import matplotlib.text as mtext

# Subtitles in legend
class LegendTitle(object):
    def __init__(self, text_props=None):
        self.text_props = text_props or {}
        super(LegendTitle, self).__init__()

    def legend_artist(self, legend, orig_handle, fontsize, handlebox):
        x0, y0 = handlebox.xdescent, handlebox.ydescent
        title = mtext.Text(x0, y0, orig_handle, usetex=False, **self.text_props)
        handlebox.add_artist(title)
        return title