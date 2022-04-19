# -*- coding: utf-8 -*-

import os
import re
import json
import io

from datetime import datetime
from PIL import Image
from flask import Flask, g, jsonify, make_response, request, render_template
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from passlib.apps import custom_app_context
import pymysql
import base64

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
    """
    用户类
    """
    __tablename__ = 'users'
    id = db.Column(db.String(20), doc='id', primary_key=True)
    name = db.Column(db.String(30), doc='昵称')
    gender = db.Column(db.String(10), doc='性别')
    fans_count = db.Column(db.Integer, doc='粉丝数')
    follows_count = db.Column(db.Integer, doc='关注数')
    weibo_count = db.Column(db.Integer, doc='微博数')
    description = db.Column(db.String(255), doc='描述')

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


class Weibos(db.Model):
    """
    微博类
    """
    __tablename__ = 'weibos'
    id = db.Column(db.String(20), doc='id', primary_key=True)
    bid = db.Column(db.String(12), doc='bid')
    user_id = db.Column(db.String(20), doc='user_id')
    screen_name = db.Column(db.String(30), doc='screen_name')
    text = db.Column(db.String(2000), doc='text')
    at_users = db.Column(db.String(255), doc='at_users')
    location = db.Column(db.String(100), doc='location')
    created_at = db.Column(db.String(20), doc='created_at')
    full_created_at = db.Column(db.String(20), doc='full_created_at')
    source = db.Column(db.String(30), doc='source')
    attitudes_count = db.Column(db.Integer, doc='attitudes_count')
    comments_count = db.Column(db.Integer, doc='comments_count')
    reposts_count = db.Column(db.Integer, doc='reposts_count')

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


# 微博列表
@app.route('/api/weibos/listpage', methods=['GET'])
@auth.login_required
def get_weibo_list():
    query = db.session.query
    Infos = query(Weibos).all()

    return jsonify({
        'code': 200,
        'infos': [u.to_dict() for u in Infos]
    })


# 生成词云图片接口
@app.route('/api/wordcloud/w2', methods=["GET"])
def wc():
    img_url = basedir + '/app/images/jinkou_comment.png'
    img_stream = ''
    with open(img_url, 'rb') as f:  # 'rb' 允许打开二进制的图片
        img_stream = f.read()
        img_stream = base64.b64encode(img_stream)

    # print(img_stream.decode())
    return img_stream.decode()


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


if __name__ == '__main__':
    db.create_all()
    app.run(host='127.0.0.1')