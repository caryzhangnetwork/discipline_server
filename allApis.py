from apis.scoreBoard import scoreBoardApis
from apis.timeSlot import timeSlotApis
from apis.user import userApis


def all_api(app):
    with app.app_context():
        app.register_blueprint(scoreBoardApis)
        app.register_blueprint(timeSlotApis)
        app.register_blueprint(userApis)
