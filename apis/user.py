import sys

sys.path.append('..')
from flask import Blueprint, request
import controler.user as user_control

userApis = Blueprint('userApis', __name__)


@userApis.route('/api/userLogin', methods=['POST'])
def create_time_slot():
    data = request.get_json()
    return user_control.login(data)


@userApis.route('/api/getTotalScore', methods=['POST'])
def get_total_score():
    data = request.get_json()
    return user_control.get_total_score(data['userId'])
