import scheduler
import time

def job():
    print("I'm working...")


scheduler.every(10).seconds.do(job) # 每10秒执行一次


while True:
    scheduler.run_pending() # 运行所有可运行的任务
    time.sleep(1)