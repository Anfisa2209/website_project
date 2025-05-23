from flask import render_template


def error_handlers(app):
    @app.errorhandler(401)
    def internal_error(error):
        return render_template('error.html', error_message=f"{error.code} Вы не зарегистрированы!"), 403

    @app.errorhandler(403)
    def access_error(error):
        return render_template('error.html', error_message=f"{error.code} Доступ запрещен..."), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('error.html', error_message=f'{error.code} Страницы пока не существует'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', error_message=f"{error.code} Что-то пошло не так..."), 500
