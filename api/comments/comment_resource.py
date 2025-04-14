from flask import jsonify
from flask_restful import Resource
from werkzeug.exceptions import NotFound

from data import db_session
from data.models.comments import Comments
from api.comments.reqparse_comment import parser
from data.models.users import User


class CommentsResource(Resource):
    def get(self, comment_id):
        session = db_session.create_session()
        comment = session.get(Comments, comment_id)
        if not comment:
            raise NotFound('Комментарий не найден!')
        return jsonify(
            {'comments': [
                comment.to_dict(only=('id', 'user_id', 'text', 'scheme_name'))]

            }
        )

    def delete(self, comment_id):
        db_sess = db_session.create_session()
        comment = db_sess.get(Comments, comment_id)
        if not comment:
            raise NotFound('Комментарий не найден!')
        db_sess.delete(comment)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    def put(self, comment_id):
        args = parser.parse_args()
        session = db_session.create_session()

        comment = session.get(Comments, comment_id)
        if not comment:
            raise NotFound('Комментарий не найден!')
        comment.text = args['text']
        comment.user_id = args['user_id']
        comment.scheme_name = args['scheme_name']
        session.commit()
        return jsonify(
            {'comments': [
                comment.to_dict(only=('text',))]}
        )


class CommentsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        comments = session.query(Comments).all()
        return jsonify(
            {'comments': (
                [item.to_dict(only=('id', 'user_id', 'text', 'scheme_name')) for item in comments])

            }
        )

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        if not session.get(User, args['user_id']):
            raise NotFound(f'Пользователь с индексом {args["user_id"]} не найден')
        comment = Comments(
            user_id=args['user_id'],
            text=args['text'],
            scheme_name=args['scheme_name']
        )
        session.add(comment)
        session.commit()
        return jsonify(
            {'comments': [
                comment.to_dict(only=('id', 'user_id', 'text', 'scheme_name'))]

            }
        )
