import datetime

import pandas as pd

from WLW.Tools.LoggingEx import logger
from WLW.model import ChinaHolidaysModel

'''
中国法定节假日：
  # 元旦:1月1日 放假1天
  # 春节:农历除夕至正月初三，通常放假4天
  # 清明节：农历清明当日，放假1天
  # 劳动节：5月1日至2日， 放假2天
  # 端午节：农历端午当日，放假1天
  # 中秋节：农历中秋当日，放假1天
  # 国庆节：10月1日至7日，放假7天
'''

'''
    日期处理类
    '''
# formate:YYYYMMDD
ymd_format = '%Y%m%d'
ymd_format_M = '%Y-%m-%d'
# formate:'%H%M%S'
hms_format = '%H%M%S'
hms_format_M = '%H:%M:%S'

# 股市营业日取得，YYYYMMDD
def saleDate():
    # 股市营业开始时间
    sale_am_ed = '090000'
    # 股市营业结束时间
    sale_pm_ed = '150000'
    # 现在日期和时刻
    nowDateTimeDay = nowDateTime()
    # 现在时刻
    nowTime = nowDateTimeDay.strftime(hms_format)
    # 现在日期
    nowDate = nowDateTimeDay.strftime(ymd_format)
    # 节假日
    historyHolidays = [row[2] for row in ChinaHolidaysModel.getData('2025')]

    # 营业时刻结束之前的，取前一天日期
    if nowTime <= sale_pm_ed:
        # 取前一天
        while True:
            nowDateTimeDay = nowDateTimeDay - datetime.timedelta(days=1)
            if (isBusinessDay(todayStr=nowDateTimeDay.strftime(ymd_format), paraHistoryHolidays=historyHolidays)):
                break
        return nowDateTimeDay.strftime(ymd_format)

    # 取节假日之外的日期（星期六，取周日，节假日）
    while True:
        if (isBusinessDay(todayStr=nowDateTimeDay.strftime(ymd_format), paraHistoryHolidays=historyHolidays)):
            break
        nowDateTimeDay = nowDateTimeDay - datetime.timedelta(days=1)

    return nowDateTimeDay.strftime(ymd_format)

# 股市营业日取得，YYYYMMDD
def plateSaleDate():
    # 现在日期和时刻
    nowDateTimeDay = nowDateTime()
    # 节假日
    historyHolidays = [row[2] for row in ChinaHolidaysModel.getData('2025')]

    # 取节假日之外的日期（星期六，取周日，节假日）
    while True:
        if (isBusinessDay(todayStr=nowDateTimeDay.strftime(ymd_format), paraHistoryHolidays=historyHolidays)):
            break
        nowDateTimeDay = nowDateTimeDay - datetime.timedelta(days=1)

    return nowDateTimeDay.strftime(ymd_format)

# 股市营业日取得，YYYYMMDD
def saleHistoryDate(historyDay: str = ''):
    # 节假日
    historyHolidays = [row[2] for row in ChinaHolidaysModel.getData('2025')]

    if historyDay == '':
        nowDate = nowDateTime()
    else:
        nowDate = datetime.datetime.strptime(historyDay, ymd_format)

    # 取节假日之外的日期（星期六，取周日，节假日）
    while True:
        if (isBusinessDay(nowDate.strftime(ymd_format), historyHolidays)):
            break
        nowDate = nowDate - datetime.timedelta(days=1)

    return nowDate.strftime(ymd_format)

# 时刻format
def format_hms(hms: str = '000000'):
    # print(type(hms), hms)
    return datetime.datetime.strptime(hms, hms_format).strftime(hms_format_M)

# 时刻format
def Format_date(ymd: str = '00000000', format: str = '%Y-%m-%d'):
    # print(type(hms), hms)
    return datetime.datetime.strptime(ymd, ymd_format).strftime(format)

def Format_changed(ymd: str = '00000000', f_format: str = '%Y-%m-%d', t_format: str='%Y%m%d'):
    # print(type(hms), hms)
    return datetime.datetime.strptime(ymd, f_format).strftime(t_format)

# 时刻format
def WeekDate(ymd: str = '00000000', format: str = '%Y-%m-%d'):
    # print(type(hms), hms)
    return datetime.datetime.strptime(ymd, format).isocalendar()

# 检索用交易日期
def saleDateCondition(ymd: str = '00000000', format: str = '%Y-%m-%d'):
    return datetime.datetime.strptime(ymd, format)

def Week_Day_Date(weekDay: int = 1):
    ymd = datetime.date.today().strftime('%Y-%m-%d')
    nowDate = Week_Day(ymd, '%Y-%m-%d', weekDay)
    return datetime.datetime.strptime(nowDate, '%Y-%m-%d')

# 周开始/终了日
def Week_Day(ymd: str = '00000000', format: str = '%Y-%m-%d', weekDay: int = 1):
    weekDays = []
    today = datetime.datetime.strptime(ymd, format)
    condWeekDay = today.weekday()
    if condWeekDay == 0:
        weekDays = [(datetime.date(today.year, today.month, today.day) + datetime.timedelta(days=num)).strftime(format) for num in range(0, 5)]
    elif condWeekDay == 1:
        weekDays = [(datetime.date(today.year, today.month, today.day) + datetime.timedelta(days=num)).strftime(format) for num in range(-1, 4)]
    elif condWeekDay == 2:
        weekDays = [(datetime.date(today.year, today.month, today.day) + datetime.timedelta(days=num)).strftime(format) for num in range(-2, 3)]
    elif condWeekDay == 3:
        weekDays = [(datetime.date(today.year, today.month, today.day) + datetime.timedelta(days=num)).strftime(format) for num in range(-3, 2)]
    elif condWeekDay == 4:
        weekDays = [(datetime.date(today.year, today.month, today.day) + datetime.timedelta(days=num)).strftime(format) for num in range(-4, 1)]
    elif condWeekDay == 5:
        weekDays = [(datetime.date(today.year, today.month, today.day) + datetime.timedelta(days=num)).strftime(format) for num in range(-5, 0)]
    elif condWeekDay == 6:
        weekDays = [(datetime.date(today.year, today.month, today.day) + datetime.timedelta(days=num)).strftime(format) for num in range(-6, -1)]

    if weekDay == 1:
        return min(weekDays)
    elif weekDay == 5:
        return max(weekDays)

# 今日日期,return YYYYMMDD
def nowDate():
    # datetime.date.today().strftime(ymd_format)
    return datetime.date.today()

# 今日日期,return hhmmss
@staticmethod
def nowDateTime():
    return datetime.datetime.today()

def isBusinessDay(todayStr:str = '20200101', paraHistoryHolidays: list = None):
    if paraHistoryHolidays == None:
        # print(f'paraHistoryHolidays: {paraHistoryHolidays}')
        # 节假日
        paraHistoryHolidays = [row[2] for row in ChinaHolidaysModel.getData('2025')]

    today = datetime.datetime.strptime(todayStr, '%Y%m%d')
    week = today.weekday()
    if week == 5 or week == 6 or todayStr in paraHistoryHolidays:
        return False
    return True

def BusinessDays(year:int = 2025):
    result = {}
    try:
        if year == '' or year == None:
            year = datetime.date.today().year

        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        weekDay = []
        for month in months:
            startDay = datetime.date(year, month, 1).strftime('%Y%m')
            if month == 12:
                historyDateTime = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
            else:
                historyDateTime = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)

            maxDay = int(historyDateTime.strftime('%d')) + 1
            monthDays = [datetime.date(year, month, day).strftime('%Y%m%d') for day in range(1, maxDay)
                         if isBusinessDay(todayStr=datetime.date(year, month, day).strftime('%Y%m%d'))]

            # print(f'月初{startDay}， 月底{historyDateTime.strftime(ymd_format)}', monthDays)
            result[startDay] = monthDays
    except Exception as ex:
        logger.error(ex)

    return result

def BusinessWeeks(self, year:int = 2025):
    result = pd.DataFrame
    try:
        if year == '' or year == None:
            year = datetime.date.today().year

        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        weekDay = []
        for month in months:
            startDay = datetime.date(year, month, 1).strftime('%Y%m')
            if month == 12:
                historyDateTime = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
            else:
                historyDateTime = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)

            maxDay = int(historyDateTime.strftime('%d')) + 1
            # monthDays = [datetime.date(year, month, day).strftime('%Y%m%d') for day in range(1, maxDay)]
            monthDays = [datetime.date(year, month, day).strftime('%Y%m%d') for day in range(1, maxDay) if
                         isBusinessDay(todayStr=datetime.date(year, month, day).strftime('%Y%m%d'))]

            condtionYear = 0
            condtionWeek = 0
            days = []
            lastDay = monthDays[-1]
            for day in monthDays:
                today = datetime.datetime.strptime(day, '%Y%m%d').isocalendar()
                # 判断条件赋值
                if condtionYear == 0 and condtionWeek == 0:
                    condtionYear = today.year
                    condtionWeek = today.week
                    days.append(int(day))
                    continue

                if condtionYear == today.year:
                    if condtionWeek == today.week:
                        days.append(int(day))
                    else:
                        weekDay.append([condtionYear, condtionWeek, min(days), max(days)])
                        condtionWeek = today.week
                        days.clear()
                        days.append(int(day))
                else:
                    weekDay.append([condtionYear, condtionWeek, min(days), max(days)])
                    condtionYear = today.year
                    condtionWeek = today.week
                    days.clear()
                    days.append(int(day))
                # print(day, today.week, today.weekday, today.year)
                # 最后一周
                if day == lastDay:
                    weekDay.append([condtionYear, condtionWeek, min(days), max(days)])

            # print(f'月初{startDay}， 月底{historyDateTime.strftime(ymd_format)}', monthDays)
        result = pd.DataFrame(weekDay)
        result.columns = ['年度', '第*周', '营业开始日', '营业终了日']
    except Exception as ex:
        logger.error(f'BusinessWeeks 出错了: {ex}')

    return result

def BusinessMonth(self, month):
    pass

def BusinessQuarter(self, quarter):
    pass

def BusinessHalfYear(self, year=None):
    result = {}
    if year == '' or year == None:
        year = datetime.date.today().year

    startDay_A = datetime.date(year, 1, 1).strftime(self.ymd_format)
    endDay_A = datetime.date(year, 6, 30).strftime(self.ymd_format)
    result[f'{year}A'] = [startDay_A, endDay_A]
    startDay_B = datetime.date(year, 7, 1).strftime(self.ymd_format)
    endDay_B = datetime.date(year, 12, 31).strftime(self.ymd_format)
    result[f'{year}B'] = [startDay_B, endDay_B]

    return result

def BusinessYear(self, year=None):
    result = {}
    if year == '' or year == None:
        year = datetime.date.today().year
        # datetime_three_month_ago = today - relativedelta(months=1)

    startDay = datetime.date(year, 1, 1).strftime(self.ymd_format)
    endDay = datetime.date(year, 12, 30).strftime(self.ymd_format)
    result[year] = [startDay, endDay]

    return result

def BusinessDaysOfHistory(historyYear:int = 2020):
    result = {}
    if historyYear =='' or historyYear == None:
        historyYear = datetime.date.today().year

    months = [1,2,3,4,5,6,7,8,9,10,11,12]
    for month in months:
        startDay = datetime.date(historyYear, month, 1).strftime('%Y%m')
        if month == 12:
            historyDateTime = datetime.date(historyYear + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            historyDateTime = datetime.date(historyYear, month + 1, 1) - datetime.timedelta(days=1)

        maxDay = int(historyDateTime.strftime('%d')) + 1
        monthDays = [datetime.date(historyYear, month, day).strftime('%Y%m%d') for day in range(1, maxDay) if isBusinessDay(todayStr=datetime.date(historyYear, month, day).strftime('%Y%m%d'))]

        # print(f'月初{startDay}， 月底{historyDateTime.strftime(ymd_format)}', monthDays)
        result[startDay] = monthDays

    return result

def lastTradingDaysFromIncreaseFive():
    return {0: lastTradingDays(5), 1: lastTradingDays(10), 2: lastTradingDays(20), 3: lastTradingDays(60), 4: lastTradingDays(120), 5: lastTradingDays(250)}

def lastTradingDays(days):
    resutl = {}
    nowSaleDate = saleDate()
    resutl['to'] = nowSaleDate
    nowDate = datetime.datetime.strptime(nowSaleDate, ymd_format)
    for no in range(2, days + 1):
        nowDate = nowDate - datetime.timedelta(days=1)
        resutlDate = saleHistoryDate(nowDate.strftime(ymd_format))
        nowDate = datetime.datetime.strptime(resutlDate, ymd_format)
        if no == days:
            resutl['from'] = resutlDate

    # print(f'resutl: {resutl}')
    return resutl

def get_quarter_dates(reportStrp: str = '%Y-%m-%d', reportDate: str = '', outStrp: str = "%Y%m%d"):
    """计算输入日期所在季度的开始和结束日期"""
    if reportDate == '':
        nowDate = datetime.date.today()
    else:
        nowDate = datetime.datetime.strptime(reportDate, reportStrp).date()

    year = nowDate.year
    month = nowDate.month

    # 确定季度
    if month in [1, 2, 3]:
        quarter = 4
        start_date = datetime.date(year-1, 10, 1)
        end_date = datetime.date(year-1, 12, 31)
    elif month in [4, 5, 6]:
        quarter = 1
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 3, 31)
    elif month in [7, 8, 9]:
        quarter = 2
        start_date = datetime.date(year, 4, 1)
        end_date = datetime.date(year, 6, 30)
    elif month in [10, 11, 12]:
        quarter = 3
        start_date = datetime.date(year, 7, 1)
        end_date = datetime.date(year, 9, 30)

    return {
        "quarter": quarter,
        "start_date": start_date.strftime(outStrp),
        "end_date": end_date.strftime(outStrp)
    }

if __name__ == '__main__':
    print(f'经营日期：{saleDate()}')
    # print(isBusinessDay('20200101'))

