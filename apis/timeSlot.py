import sys
sys.path.append('..')
from flask import Blueprint, request
import controler.timeSlot as time_slot_control

timeSlotApis = Blueprint('timeSlotApis', __name__)


@timeSlotApis.route('/api/createTimeSlot', methods=['POST'])
def create_time_slot():
    data = request.get_json()
    return time_slot_control.create_time_slot(data)


@timeSlotApis.route('/api/createDurationTimeSlot', methods=['POST'])
def createDurationTimeSlot():
    data = request.get_json()
    return time_slot_control.createDurationTimeSlot(data)

