# 从flask框架中导入Flask类
import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS, cross_origin
from allModel import create_all_model
from allApis import all_api

app = Flask(__name__)
CORS(app, supports_credentials=True)  # 跨域支持

create_all_model(app)
all_api(app)


@app.route("/api/books")
def books():
    data = {'message': 'Hello from Flask backend!'}
    return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
