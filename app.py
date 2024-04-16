# 从flask框架中导入Flask类
from flask import Flask
from flask_cors import CORS
from allModel import create_all_model
from allApis import all_api
from scheduler import daily_schedule

app = Flask(__name__)
CORS(app, supports_credentials=True)  # 跨域支持

create_all_model(app)
all_api(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)