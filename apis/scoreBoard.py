from flask import Blueprint

scoreBoardApis = Blueprint('scoreBoardApis', __name__)


@scoreBoardApis.route('/api/getScoreBoard')
def get_score_board():
    return 'Hello from API endpoint'
