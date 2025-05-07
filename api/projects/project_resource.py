from flask import jsonify
from flask_restful import Resource
from werkzeug.exceptions import NotFound

from data import db_session
from data.models.projects import Projects
from api.projects.reqparse_project import parser


class ProjectsResource(Resource):
    def get(self, project_id):
        session = db_session.create_session()
        project = session.get(Projects, project_id)
        if not project:
            raise NotFound('Проект не найден!')
        return jsonify(
            {'projects': [
                project.to_dict(only=('id', 'name'))]

            }
        )

    def delete(self, project_id):
        db_sess = db_session.create_session()
        project = db_sess.get(Projects, project_id)
        if not project:
            raise NotFound('Проект не найден!')
        db_sess.delete(project)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    def put(self, project_id):
        args = parser.parse_args()
        session = db_session.create_session()

        project = session.get(Projects, project_id)
        if not project:
            raise NotFound('Проект не найден!')
        project.name = args['name']
        session.commit()
        return jsonify(
            {'projects': [
                project.to_dict(only=('name',))]}
        )


class ProjectsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        projects = session.query(Projects).all()
        return jsonify(
            {'projects': (
                [item.to_dict(only=('id', 'name')) for item in projects])

            }
        )

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        project = Projects(name=args['name'])
        session.add(project)
        session.commit()
        return jsonify(
            {'projects': [
                project.to_dict(only=('id', 'name'))]
            }
        )
