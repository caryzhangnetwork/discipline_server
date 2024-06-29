import schedule
import time
import controler.user as user_control
import controler.timeSlot as time_slot_control



from utils import tools


def daily_job():
    print("daily job batch start counting...")

    # update total score for every user at over_night_counter + 1
    (schedule.every().day.at(f'{tools.get_double_digit(tools.over_night_counter + 1)}:00').do(user_control.update_all_user_total_score)
            .do(time_slot_control.remove_redundance_time_slot_for_all_users))
    while True:
        schedule.run_pending()  # 运行所有可运行的任务
        time.sleep(1)


