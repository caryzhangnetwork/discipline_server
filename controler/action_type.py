import sys
sys.path.append('..')
from allModel import create_session
from sqlalchemy import text


def get_all_daily_action_type():
    try:
        session = create_session()
        select_query = text("SELECT id, name, counting_type, color, is_default_type, enable_overnight FROM action_type"
                            " WHERE counting_type = :excludeType")
        # exclude the action type with counting_type = 1('time' which is only for time type)
        target_action_type = session.execute(select_query, {'excludeType': '1'}).fetchall()
        session.commit()
        return target_action_type

    except Exception as e:
        print("An error occurred:", str(e))
        return {
            'status': 0,
            'msg': "query fail",
            'score_board': 0
        }


