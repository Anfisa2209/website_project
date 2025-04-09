from flask import jsonify
from flask_restful import Resource
from werkzeug.exceptions import NotFound
from werkzeug.security import generate_password_hash

from data import db_session
from data.users import User
from api.users.reqparse_user import parser


def set_password(password):
    return generate_password_hash(password)


class UsersResource(Resource):
    def get(self, user_id):
        session = db_session.create_session()
        user = session.get(User, user_id)
        if not user:
            raise NotFound('Пользователь не найден!')
        return jsonify(
            {'users': [
                user.to_dict(only=('id', 'email'))]}
        )

    def delete(self, user_id):
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        if not user:
            raise NotFound('Пользователь не найден!')
        db_sess.delete(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_id):
        args = parser.parse_args()
        session = db_session.create_session()

        user = session.query(User).get(user_id)
        if not user:
            raise NotFound('Пользователь не найден!')
        user.email = args['email']
        user.hashed_password = args['hashed_password']
        session.commit()
        return jsonify(
            {'users': [
                user.to_dict(only=('id', 'email'))]}
        )


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify(
            {'users': (
                [item.to_dict(only=(
                    'id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email'
                )) for
                    item in users])

            }
        )

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            email=args['email'],
            hashed_password=set_password(args['hashed_password'])
        )
        session.add(user)
        session.commit()
        return jsonify(
            {'users': [
                user.to_dict(only=('id', 'email'))]

            }
        )
