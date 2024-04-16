import sys

sys.path.append('..')
from allModel import create_session
from utils import tools
from sqlalchemy import text
from collections import namedtuple

Score_board = namedtuple('Score_board', ['id', 'score', 'time', 'reward_type'])
default_score_board = Score_board(id=-1, score=0, time='00:00', reward_type=-1)


# have issue need to check!!!
# find the scoreboard which is match with time slot create time, current_time is format as '%H:%M'
def get_target_score_board(session, current_time, action_type):
    score_boards = get_sorted_score_board_by_type(session, action_type)
    print("score_boards ", score_boards)
    target_score_board_obj = default_score_board

    # if the time is in the gap between scoreboard type 1 and scoreboard 2
    # if is_gap_time(score_boards, current_time):
    #     return target_score_board_obj

    for score_board_obj in score_boards:
        score_board_time = score_board_obj.time
        # positive if reward_type is 1, negative if reward_type is 2
        if score_board_obj.reward_type == 1:
            if ((tools.is_time_a_earlier(current_time, score_board_time) and
                    tools.is_time_a_earlier(target_score_board_obj.time, score_board_time)) or
                    target_score_board_obj.id == -1):
                target_score_board_obj = score_board_obj
        elif score_board_obj.reward_type == 2:
            if ((tools.is_time_a_earlier(score_board_time, current_time) and
                    tools.is_time_a_earlier(target_score_board_obj.time, score_board_time)) or
                    target_score_board_obj.id == -1):
                target_score_board_obj = score_board_obj

    return target_score_board_obj


def get_sorted_score_board_by_type(session, action_type):
    sb_select_query = text(
        "SELECT id, action_type, reward_type, time, duration, score FROM score_board WHERE action_type = :actionType AND reward_type != 4" )
    score_boards = session.execute(sb_select_query, {'actionType': action_type}).fetchall()
    return tools.sort_time_obj_list(3, score_boards)


# get the overnight score board in specific action type
def get_over_night_score_board(score_boards, action_type):
    # overnight score board is with action type -1
    target_score_board = [score_obj for score_obj in score_boards if score_obj['action_type'] == action_type
                          and score_obj['reward_type'] == 4]
    # if there is no matching record
    if len(target_score_board) == 0:
        return Score_board
    else:
        return target_score_board[0]


# identify if the time is gap between add type and minus type(no score board belong),
# the score_board parameter must be sorted by time, current_time is format as '%H:%M'
def is_gap_time(sorted_score_boards, create_time):
    first_minus_type = -1
    for index, board in enumerate(sorted_score_boards):
        if board.reward_type == 2:
            first_minus_type = index
            break
    # first_minus_type - 1 is the last add_type in the score board
    if (first_minus_type != -1 and
            tools.is_time_a_earlier(sorted_score_boards[first_minus_type - 1].time, create_time) and
            tools.is_time_a_earlier(create_time, sorted_score_boards[first_minus_type].time)):
        return True
    else:
        return False
