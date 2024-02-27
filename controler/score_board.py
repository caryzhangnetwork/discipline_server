import sys

sys.path.append('..')
from allModel import create_session
from utils import tools
from sqlalchemy import text
import datetime, re


# find the scoreboard which is match with time slot create time
def get_target_score_board(score_boards, create_time):
    if score_boards[0]:
        target_score_board_obj = score_boards[0]
    for score_obj in score_boards:
        temp_score_date = tools.getDate(f'{create_time.hour}:{create_time.minute}', score_obj.time)
        temp_target_date = tools.getDate(f'{create_time.hour}:{create_time.minute}',
                                         target_score_board_obj.time)

        # 将时间字符串转换为 datetime 对象
        temp_time = datetime.datetime.strptime(str(temp_score_date) + ' ' + score_obj.time,
                                               '%Y-%m-%d %H:%M')
        target_time = datetime.datetime.strptime(str(temp_target_date) + ' ' + target_score_board_obj.time,
                                                 '%Y-%m-%d %H:%M')

        if score_obj.reward_type == 1:
            if create_time <= temp_time and target_time <= temp_time:
                target_score_board_obj = score_obj
        elif score_obj.reward_type == 2:
            if create_time >= temp_time >= target_time:
                target_score_board_obj = score_obj

    return target_score_board_obj


# get score board records by action type and return an array sort by time
def get_sorted_score_board_by_type(session, action_type):
    sb_select_query = text(
        "SELECT id, action_type, reward_type, time, duration, score FROM score_board WHERE action_type = :actionType OR action_type = -1")
    score_boards = session.execute(sb_select_query, {'actionType': action_type}).fetchall()
    return sorted(score_boards, key=lambda x: x.time)


def get_over_night_score_board(score_boards):
    # over night score board is with action type -1
    target_score_board = [score_obj for score_obj in score_boards if score_obj.action_type == -1]
    return target_score_board[0]
