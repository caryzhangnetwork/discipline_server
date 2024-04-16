import sys
sys.path.append('..')
from allModel import create_session
from utils import tools
from sqlalchemy import text
from controler.user import update_user_daily_score
from controler.score_board import get_target_score_board, get_over_night_score_board
import datetime


def create_time_slot(data):
    try:
        session = create_session()
        target_score_board_obj_id = -1
        last_score = 0
        score = 0

        ac_select_query = text("SELECT id, counting_type FROM action_type WHERE id = :actionType")
        target_action_type = session.execute(ac_select_query, {'actionType': data['actionType']}).fetchone()
        counting_type = target_action_type[1]

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







# is not using right now, will add partial logic in night batch
def over_night_time_slot_handler(session, create_time, time_slots, action_type):
    # identify if current time is between 00:00 and before over nighttime
    if tools.isAM(f'{create_time.hour}:{create_time.minute}') and create_time.hour > tools.over_night_counter:
        # in the morning(next day)
        if len(time_slots) == 0:
            # if user don't have any record for this type in today
            return get_over_night_score_board(session, action_type)
        else:
            return get_target_score_board(session, create_time, action_type)
    else:
        # still in today late night(today late night)
        return get_target_score_board(session, create_time, action_type)



