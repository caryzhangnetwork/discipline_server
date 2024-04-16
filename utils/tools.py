import datetime, re

over_night_counter = 5


# datetime format transform "Sun Mar 31 2024 06:01:25" to "2024-03-31 06:01:25"
def date_time_format_transform(date_time):
    temp_date_time = re.sub(r" GMT[+-]\d{4}.*$", "", date_time)
    temp_date_time = "Sun Apr 8 2024 05:30:25"
    return datetime.datetime.strptime(temp_date_time, '%a %b %d %Y %H:%M:%S')


# parameter time format as %HH:%MM
def isAM(time):
    # 将时间字符串转换为 datetime 对象
    time_obj = datetime.datetime.strptime(get_hours_from_datetime(time), "%H:%M")
    # 获取时间的小时部分
    hour = time_obj.hour
    # 判断上午还是下午
    if hour < 12:
        return True
    else:
        return False


def is_late_night(time):
    # 获取时间的小时部分
    time_format = get_hours_from_datetime(time)

    over_night_time = '0' + str(over_night_counter) + ':00'
    if isAM(time_format) and str(time_format) <= over_night_time:
        return True
    else:
        return False


# format as '%H:%M' for time_a and time_b
def is_time_a_earlier(time_a, time_b):
    if is_late_night(time_a):
        time_a_clone = (str(datetime.datetime.strptime(time_a, "%H:%M").hour + 24) + ":"
                        + get_double_digit(datetime.datetime.strptime(time_a, "%H:%M").minute))
    else:
        time_a_clone = (get_double_digit(datetime.datetime.strptime(time_a, "%H:%M").hour) + ":"
                        + get_double_digit(datetime.datetime.strptime(time_a, "%H:%M").minute))

    if is_late_night(time_b):
        time_b_clone = (str(datetime.datetime.strptime(time_b, "%H:%M").hour + 24) + ":"
                        + get_double_digit(datetime.datetime.strptime(time_b, "%H:%M").minute))
    else:
        time_b_clone = (get_double_digit(datetime.datetime.strptime(time_b, "%H:%M").hour) + ":"
                        + get_double_digit(datetime.datetime.strptime(time_b, "%H:%M").minute))

    if time_a_clone <= time_b_clone:
        return True
    else:
        return False


# add '0' before single digit
def get_double_digit(digit):
    digitStr = str(digit)
    if len(digitStr) == 1:
        return "0" + digitStr
    else:
        return digitStr


def get_hours_from_datetime(time):
    original_format = '%Y-%m-%d %H:%M:%S'
    desired_format = '%H:%M'

    if len(time) > 6:
        datetime_obj = datetime.datetime.strptime(str(time), original_format)
        return datetime_obj.strftime(desired_format)
    else:
        return time


def sort_time_obj_list(filed_index, time_list):
    late_night_list = [sb for sb in time_list if
                       is_late_night(sb[filed_index])]
    not_late_night_list = [sb for sb in time_list if
                           not is_late_night(sb[filed_index])]
    return sorted(not_late_night_list, key=lambda x: x[filed_index]) + sorted(late_night_list, key=lambda x: x[filed_index])


