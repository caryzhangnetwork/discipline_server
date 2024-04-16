import sys
sys.path.append('..')
from allModel import create_session
from sqlalchemy import text


def login(data):
    try:
        session = create_session()
        select_query = text("SELECT id, name, password, total_score FROM user WHERE name = :username")
        target_user = session.execute(select_query, {'username': data['username']})
        target_user = target_user.fetchone()
        session.commit()
        if target_user:
            if target_user[2] == data['pw']:
                return {
                    'status': 1,
                    'msg': "Login success",
                    'user_id': target_user[0],
                    'name': target_user[1],
                    'total_score': target_user[3]
                }
            else:
                return {
                    'status': 0,
                    'msg': "Wrong Password"
                }
        else:
            return {
                'status': 0,
                'msg': "User Not Found"
            }

    except Exception as e:
        print("An error occurred:", str(e))
        return "query fail"


# get total score by user id, the total score is daily_score + total_score
def get_total_score(user_id):
    try:
        session = create_session()
        user_select_query = text("SELECT * FROM USER WHERE id = :id")
        target_user = session.execute(user_select_query, {'id': user_id}).fetchone()
        session.commit()
        data = {
            'status': 1,
            'msg': "query success",
            'totalScore': target_user.total_score + target_user.daily_score
        }
        return data
    except Exception as e:
        return "query fail"


# edit user total score with user id and a specific score board recorad
def update_user_daily_score(session, last_score, current_score_board_obj, user_id):
    try:
        user_select_query = text("SELECT * FROM USER WHERE id = :id")
        target_user = session.execute(user_select_query, {'id': user_id}).fetchone()
        if current_score_board_obj.reward_type == 1:
            new_daily_score = target_user.daily_score - last_score + current_score_board_obj.score
        else:
            new_daily_score = target_user.daily_score - last_score - current_score_board_obj.score
        update_user_query = text("UPDATE user SET daily_score = :daily_score WHERE id = :id")
        session.execute(update_user_query, {'id': user_id, 'daily_score': new_daily_score})
    except Exception as e:
        return "query fail"


def update_all_user_total_score():
    print("update_all_user_total_score ")
    try:
        session = create_session()
        user_select_query = text("SELECT * FROM USER")
        users = session.execute(user_select_query).fetchall()
        for user in users:
            total_score = user.total_score + user.daily_score
            daily_score = 0
            update_user_query = text("UPDATE user SET daily_score = :daily_score, total_score = :total_score WHERE id = :id")
            session.execute(update_user_query, {'id': user.id, 'total_score': total_score, 'daily_score': daily_score})
        # this is from daily scheduler, will commit the session every time update the user data
        session.commit()
    except Exception as e:
        return "query fail"
