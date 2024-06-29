# 从flask框架中导入Flask类
from flask import Flask
from flask_cors import CORS
from allModel import create_all_model
from allApis import all_api
from job_batch.daily_schedule import daily_job
import threading

app = Flask(__name__)
CORS(app, supports_credentials=True)  # 跨域支持

create_all_model(app)
all_api(app)


if __name__ == '__main__':
    # start daily job
    thread = threading.Thread(target=daily_job)
    thread.start()

    app.run(host='0.0.0.0', debug=True)



