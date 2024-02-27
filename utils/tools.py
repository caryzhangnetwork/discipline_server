import datetime

# parameter time format as %HH:%MM
def isAM(time):
  # 将时间字符串转换为 datetime 对象
  time_obj = datetime.datetime.strptime(time, "%H:%M")
  # 获取时间的小时部分
  hour = time_obj.hour
  # 判断上午还是下午
  if hour < 12:
    return True
  else:
    return False


# both parameter baseTime & subTime format as %HH:%MM
def getDate(baseTime, subTime):
    subTimeDate = datetime.datetime.now().date()
    yesterday = subTimeDate - datetime.timedelta(days=1)
    tomorrow = subTimeDate + datetime.timedelta(days=1)

    if isAM(baseTime):
        if not isAM(subTime):
            subTimeDate = yesterday
    else:
        if isAM(subTime):
            subTimeDate = tomorrow
    return subTimeDate