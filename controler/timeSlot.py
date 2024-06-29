import sys
sys.path.append('..')
from allModel import create_session
from utils import tools
from sqlalchemy import text
from controler.user import update_user_daily_score
from controler.score_board import get_target_score_board, get_duration_score_board
from controler.action_type import get_all_daily_action_type
import datetime


def create_time_slot(data):
    try:
        session = create_session()
        target_score_board_obj_id = -1
        last_score = 0
        score = 0

        create_date_time = tools.date_time_format_transform(data['createDate'])
        time_slots = get_sorted_time_slot_for_today(session, create_date_time, data['createBy'], data['actionType'])
        target_score_board_obj = get_target_score_board(session, create_date_time.strftime("%H:%M"), data['actionType'])
        target_score_board_obj_id = target_score_board_obj.id

        if target_score_board_obj_id != -1:
            insert_query = text("INSERT INTO time_slot (create_date, score_id, create_by) VALUES (:create_date, :score_id, :create_by)")
            session.execute(insert_query, {'create_date': create_date_time, 'score_id': target_score_board_obj_id,
                                               'create_by': data['createBy']})

            # get the score of last update time slot in the same action type within today(before over night)
            if len(time_slots) != 0 and time_slots[-1]:
                if time_slots[-1].reward_type == 1:
                    last_score = time_slots[-1].score
                else:
                    last_score = 0 - time_slots[-1].score

            # update user latest daily score
            update_user_daily_score(session, last_score, target_score_board_obj, data['createBy'])

            # get score with negative/positive
            if target_score_board_obj.reward_type == 1:
                score = target_score_board_obj.score - last_score
            else:
                score = 0 - target_score_board_obj.score - last_score

        print("target_score_board_obj ", target_score_board_obj)
        print("target_score_board_obj_id ", target_score_board_obj_id)
        print("score ", score)

        session.commit()
        return {
            'status': 1,
            'msg': "query success",
            'score': score
        }
    except Exception as e:
        print("An error occurred:", str(e))
        return {
            'status': 0,
            'msg': "query fail",
            'score': 0
        }


# have issue need to check!!!
# get all timeslot in today before overnight with user id and action type
def get_sorted_time_slot_for_today(session, date_time, user_id, action_type):
    overnight_time = str(tools.over_night_counter) + ":00"
    current_time = date_time.strftime("%H:%M")
    today = date_time.date()
    yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1)

    if tools.is_late_night(current_time):
        # if now is between 00:00 and before overnight time
        day_start = datetime.datetime.strptime(f'{str(yesterday)} {overnight_time}', "%Y-%m-%d %H:%M")
        day_end = datetime.datetime.strptime(f'{str(today)} {overnight_time}', "%Y-%m-%d %H:%M")
    else:
        # if now is not AM but before 00:00 or is AM but after overnight time
        day_start = datetime.datetime.strptime(f'{str(today)} {overnight_time}', "%Y-%m-%d %H:%M")
        day_end = datetime.datetime.strptime(f'{str(tomorrow)} {overnight_time}', "%Y-%m-%d %H:%M")

    print("day_start ", day_start)
    print("day_end ", day_end)

    ts_select_query = text("SELECT ts.id, ts.create_date, sb.reward_type, sb.score "
                           "FROM time_slot ts "
                           "JOIN score_board sb ON ts.score_id = sb.id "
                           "WHERE ts.create_date >= :day_start AND (ts.create_date < :day_end) "
                           "AND ts.create_by = :user_id "
                           "AND sb.action_type = :action_type")
    time_slots = session.execute(ts_select_query,
                                 {'day_start': day_start, 'day_end': day_end, 'user_id': user_id,
                                  'action_type': action_type}).fetchall()

    return tools.sort_time_obj_list(1, time_slots)


def createDurationTimeSlot (data):
    try:
        target_score_board_id = -1
        score = 0
        session = create_session()
        total_last_score = 0
        target_score_board_obj = get_duration_score_board(session, data['actionType'], data['duration'])
        target_score_board_id = target_score_board_obj.id
        if target_score_board_id != -1:
            create_date_time = tools.date_time_format_transform(data['createDate'])
            time_slots = get_sorted_time_slot_for_today(session, create_date_time, data['createBy'], data['actionType'])
            if len(time_slots) != 0:
                for time_slot in time_slots:
                    total_last_score = total_last_score + time_slot.score
                    delete_query = text(
                        "DELETE FROM time_slot WHERE id = :time_slot_id")
                    session.execute(delete_query, {'time_slot_id': time_slot.id})
                score = target_score_board_obj.score - total_last_score
                update_user_daily_score(session, total_last_score, target_score_board_obj, data['createBy'])
            else:
                score = target_score_board_obj.score
                update_user_daily_score(session, total_last_score, target_score_board_obj, data['createBy'])

            insert_query = text(
                "INSERT INTO time_slot (create_date, score_id, create_by) VALUES (:create_date, :score_id, :create_by)")
            session.execute(insert_query, {'create_date': create_date_time, 'score_id': target_score_board_id,
                                   'create_by': data['createBy']})
        session.commit()
        return {
            'status': 1,
            'msg': "query success",
            'score': score
        }
    except Exception as e:
        print("An error occurred:", str(e))
        return {
            'status': 0,
            'msg': "query fail",
            'score': 0
        }

def remove_redundance_time_slot_for_all_users():
    print("remove_redundance_time_slot_for_all_users ")
    try:
        session = create_session()
        user_select_query = text("SELECT * FROM USER")
        users = session.execute(user_select_query).fetchall()
        overnight_time = str(tools.over_night_counter) + ":00"
        today = datetime.date.today()
        today_latest_date_time = datetime.datetime.strptime(f'{str(today)} {overnight_time}', "%Y-%m-%d %H:%M")
        action_types_without_reward = get_all_daily_action_type()

        all_delete_ids = []
        for user in users:
            for action_type in action_types_without_reward:
                today_time_slots = get_sorted_time_slot_for_today(session, today_latest_date_time, user.id, action_type.id)
                # get the score of last update time slot in the same action type within today(before over night)
                length = len(today_time_slots)
                if (length > 1):
                    ids = [item.id for item in today_time_slots[:length-1]]
                    all_delete_ids = all_delete_ids + ids

        delete_query = text(f"DELETE FROM time_slot WHERE id IN ({', '.join(str(id) for id in all_delete_ids)});")
        session.execute(delete_query)


        session.commit()
    except Exception as e:
        return "query fail"




