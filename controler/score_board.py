import sys

sys.path.append('..')
from allModel import create_session
from utils import tools
from sqlalchemy import text
from collections import namedtuple, defaultdict


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

def get_duration_score_board(session, action_type, duration):
    sb_select_query = text(
        "SELECT id, action_type, reward_type, time, duration, score FROM score_board "
        "WHERE action_type = :actionType AND duration = :duration")
    score_board = session.execute(sb_select_query, {'actionType': action_type, 'duration': duration}).fetchone()
    return score_board


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

def get_all_sorted_score_board(data):
    try:
        session = create_session()
        ScoreRecord = namedtuple('ScoreRecord', ['score', 'reward_type', 'action_type', 'counting_line'])
        sb_select_query = text(
            "SELECT sb.action_type, sb.reward_type, sb.time, sb.duration, sb.score, at.name, at.counting_type FROM score_board sb "
            "JOIN action_type at ON sb.action_type = at.id")
        score_board = session.execute(sb_select_query).fetchall()
        # 使用 defaultdict 按 action_type 分类
        sorted_score_board = defaultdict(list)
        for row in score_board:
            action_type, reward_type, time, duration, score, name, counting_type = row

            # set score to be negative if reward_type is 2(minus)
            if reward_type == 2:
                score = 0 - score

            # set counting_line as time value if counting_type is 1(time), set counting_line as duraction if counting_type is 2(duration)
            # set counting_line as name if counting_type is 0(notype, normally as reward)
            if counting_type == 1:
                score_record = ScoreRecord(score, reward_type, action_type, time)
            elif counting_type == 2:
                score_record = ScoreRecord(score, reward_type, action_type, duration)
            elif counting_type == 0:
                score_record = ScoreRecord(score, reward_type, action_type, name)

            # set the record to reward property if reward type 3
            if reward_type != 3 and reward_type != 4 and data['type'] == 'daily':
                sorted_score_board[name].append(score_record._asdict())
            elif reward_type == 3 and data['type'] == 'reward':
                sorted_score_board['reward'].append(score_record._asdict())

        # 对每个 action_type 下的数据根据 score 排序
        for name, data in sorted_score_board.items():
            sorted_score_board[name] = sorted(data, key=lambda x: x['score'], reverse=True)

        return {
            'status': 1,
            'msg': "query success",
            'score_board': sorted_score_board
        }
    except Exception as e:
        print("An error occurred:", str(e))
        return {
            'status': 0,
            'msg': "query fail",
            'score_board': 0
        }