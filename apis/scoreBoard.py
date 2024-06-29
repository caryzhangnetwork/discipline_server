from flask import Blueprint, request
import controler.score_board as score_board

scoreBoardApis = Blueprint('scoreBoardApis', __name__)


@scoreBoardApis.route('/api/getScoreBoard', methods=['POST'])
def get_score_board():
    data = request.get_json()
    return score_board.get_all_sorted_score_board(data)

