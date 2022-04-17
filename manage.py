# -*- coding: utf-8 -*-

import os
import re
import json
from datetime import datetime

from flask import Flask, g, jsonify, make_response, request
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from passlib.apps import custom_app_context
import pymysql

pymysql.install_as_MySQLdb()
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# r'/*' 是通配符，让本服务器所有的 URL 都允许跨域请求
CORS(app, resources=r'/*')
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_RECORD_QUERIES'] = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
#     os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost:3306/weibo'


db = SQLAlchemy(app)
auth = HTTPBasicAuth()
CSRF_ENABLED = True
app.debug = True


class Admin(db.Model):
    # def __init__(self, username, password):
    #     self.username = username
    #     self.password = password

    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)
    password = db.Column(db.String(128))

    # 密码加密
    def hash_password(self, password):
        self.password = custom_app_context.encrypt(password)

    # 密码解析
    def verify_password(self, password):
        return custom_app_context.verify(password, self.password)

    # 获取token，有效时间100min
    def generate_auth_token(self, expiration=6000):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    # 解析token，确认登录的用户身份
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        admin = Admin.query.get(data['id'])
        return admin


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, doc='id', primary_key=True)
    name = db.Column(db.String(64), doc='昵称')
    gender = db.Column(db.String(64), doc='性别')
    description = db.Column(db.String(64), doc='描述')
    fans_count = db.Column(db.Integer, doc='粉丝数')
    follows_count = db.Column(db.Integer, doc='关注数')
    weibos_count = db.Column(db.Integer, doc='微博数')

    def to_dict(self):
        columns = self.__table__.columns.keys()
        result = {}
        for key in columns:
            if key == 'pub_date':
                value = getattr(self, key).strftime("%Y-%m-%d %H:%M:%S")
            else:
                value = getattr(self, key)
            result[key] = value
        return result


@auth.verify_password
def verify_password(name_or_token, password):
    if not name_or_token:
        return False
    name_or_token = re.sub(r'^"|"$', '', name_or_token)
    admin = Admin.verify_auth_token(name_or_token)
    if not admin:
        admin = Admin.query.filter_by(name=name_or_token).first()
        if not admin or not admin.verify_password(password):
            return False
    g.admin = admin
    return True


@app.route('/api/login', methods=['POST'])
@auth.login_required
def get_auth_token():
    token = g.admin.generate_auth_token()
    return jsonify({'code': 200, 'msg': "登录成功", 'token': token.decode('ascii'), 'name': g.admin.name})


@app.route('/api/setpwd', methods=['POST'])
@auth.login_required
def set_auth_pwd():
    data = json.loads(str(request.data, encoding="utf-8"))
    admin = Admin.query.filter_by(name=g.admin.name).first()
    if admin and admin.verify_password(data['oldpass']) and data['confirpass'] == data['newpass']:
        admin.hash_password(data['newpass'])
        return jsonify({'code': 200, 'msg': "密码修改成功"})
    else:
        return jsonify({'code': 500, 'msg': "请检查输入"})


# 用户列表
@app.route('/api/users/listpage', methods=['GET'])
@auth.login_required
def get_user_list():
    query = db.session.query
    Infos = query(Users).all()
    return jsonify({
        'code': 200,
        'infos': [u.to_dict() for u in Infos]
    })


# @app.route('/api/getdrawPieChart', methods=['GET'])
# @auth.login_required
# def getdrawPieChart():
#     query = db.session.query
#     Infos = query(JoinInfos)
#     total = Infos.count()
#     data_value = [0, 0, 0, 0, 0, 0, 0]  # 和下面组别一一对应
#     group_value = ['视觉', '视频', '前端', '办公', '后端', '运营', '移动']
#     for info in Infos:
#         for num in range(0, 7):
#             if group_value[num] in info.group:
#                 data_value[num] += 1
#             else:
#                 pass
#     return jsonify({'code': 200, 'value': data_value, 'total': total})


# @app.route('/api/getdrawLineChart', methods=['GET'])
# @auth.login_required
# def getdrawLineChart():
#     grade_value = []  # 年级汇总
#     profess_value = []  # 学院汇总
#     grade_data = {}  # 年级各学院字典
#     Infos = JoinInfos.query.all()
#     for info in Infos:
#         if info.grade not in grade_value:
#             grade_value.append(info.grade)
#             grade_data[info.grade] = []
#         if info.profess not in profess_value:
#             profess_value.append(info.profess)
#     for grade in grade_value:
#         for profess in profess_value:
#             grade_data[grade].append(0)
#     for info in Infos:
#         for grade in grade_value:
#             for profess_local_num in range(0, len(profess_value)):
#                 if info.profess == profess_value[profess_local_num] and info.grade == grade:
#                     grade_data[grade][profess_local_num] += 1
#                 else:
#                     pass
#     return jsonify({'code': 200, 'profess_value': profess_value, 'grade_value': grade_value, 'grade_data': grade_data})


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


if __name__ == '__main__':
    db.create_all()
    app.run(host='127.0.0.1')