import sys
sys.path.append('..')
from allModel import create_session
from utils import tools
from sqlalchemy import text
from controler.user import update_user_daily_score
from controler.score_board import get_target_score_board, get_sorted_score_board_by_type, get_over_night_score_board
import datetime, re

over_night_counter = 5


def create_time_slot(data):
    try:
        session = create_session()
        ac_select_query = text("SELECT id, counting_type FROM action_type WHERE id = :actionType")
        target_action_type = session.execute(ac_select_query, {'actionType': data['actionType']}).fetchone()
        counting_type = target_action_type[1]
        score = 0
        score_boards = get_sorted_score_board_by_type(session, data['actionType'])
        target_score_board_obj_id = -1

        data_create_time = re.sub(r" GMT[+-]\d{4}.*$", "", data['createDate'])
        create_time = datetime.datetime.strptime(data_create_time, '%a %b %d %Y %H:%M:%S')

        # time sensitive
        if counting_type == 1:
            time_slots = get_time_slot_before_overnight(session, data['createBy'], data['actionType'])
            if tools.isAM(f'{create_time.hour}:{create_time.minute}') and create_time.hour > over_night_counter:
                # identify if current time is between 00:00 and over night time
                print("time_slots tools.isAM ", time_slots)
                if len(time_slots) == 0:
                    # if user don't have any record for this type in today
                    target_score_board_obj = get_over_night_score_board(score_boards)
                    target_score_board_obj_id = target_score_board_obj.id
                else:
                    target_score_board_obj = get_target_score_board(score_boards, create_time)
            else:
                target_score_board_obj = get_target_score_board(score_boards, create_time)

            # compare create time and target time to get if current time is the 'gap time'(time which not adding/minus score)
            target_date = tools.getDate(f'{create_time.hour}:{create_time.minute}', target_score_board_obj.time)
            target_time = datetime.datetime.strptime(str(target_date) + ' ' + target_score_board_obj.time,
                                                     '%Y-%m-%d %H:%M')
            if target_score_board_obj.reward_type == 1 and create_time > target_time:
                target_score_board_obj_id = -1
            else:
                target_score_board_obj_id = target_score_board_obj.id

            # get the score of last update time slot in the same action type within today(before over night)
            last_score = 0
            print("time_slots[-1] out ", time_slots)

            if len(time_slots) != 0 and time_slots[-1]:
                if time_slots[-1].reward_type == 1:
                    last_score = time_slots[-1].score
                else:
                    last_score = 0 - time_slots[-1].score

            update_user_daily_score(session, last_score, target_score_board_obj, data['createBy'])

            # get score with negative/positive
            if target_score_board_obj.reward_type == 1:
                score = target_score_board_obj.score - last_score
            else:
                score = 0 - target_score_board_obj.score - last_score

        insert_query = text(
            "INSERT INTO time_slot (create_date, score_id, create_by) VALUES (:create_date, :score_id, :create_by)")
        session.execute(insert_query, {'create_date': create_time, 'score_id': target_score_board_obj_id,
                                       'create_by': data['createBy']})
        session.commit()

        return {
            'status': 1,
            'msg': "query success",
            'score': score
        }
    except Exception as e:
        print("An error occurred:", str(e))
        return "query fail"


# get all timeslot in today before overnight with user id and action type
def get_time_slot_before_overnight(session, user_id, action_type):
    today = datetime.datetime.now().date()
    yesterday = today - datetime.timedelta(days=1)
    ts_select_query = text("SELECT ts.id, ts.create_date, sb.reward_type, sb.score "
                           "FROM time_slot ts "
                           "JOIN score_board sb ON ts.score_id = sb.id "
                           "WHERE (DATE(ts.create_date) = :today OR DATE(ts.create_date) = :yesterday) "
                           "AND ts.create_by = :user_id "
                           "AND sb.action_type = :action_type")
    time_slots = session.execute(ts_select_query,
                                 {'today': today, 'yesterday': yesterday, 'user_id': user_id,
                                  'action_type': action_type}).fetchall()
    print("get_time_slot_before_overnight time_slots ", time_slots)
    return sorted(time_slots, key=lambda x: x.create_date)
