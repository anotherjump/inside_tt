import re
import mariadb
from flask import Flask, request, jsonify
import flask_jwt_extended as fjwt
import time


def connect_db():
    """Возвращает подключение к базе данных"""
    conn = mariadb.connect(
        user="root",
        password="dbpass",
        host="mariadb",
        port=3306,
        database="msgsrv"
        )
    return conn


# инициализация flask и jwt manager
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "not_so_secret"
jwt = fjwt.JWTManager(app)


@app.route("/login", methods=["POST"])
def login():
    """"Проверяет имя/пароль, при успешной проверке возвращает токен авторизации,
    иначе возвращает информацию об ошибке"""
    status = None
    try:
        conn = connect_db()
        db_cursor = conn.cursor()
        name = request.json.get("name", None)
        password = request.json.get("password", None)
        db_cursor.execute("SELECT password FROM users WHERE name=?", (name,))
        db_password = db_cursor.fetchone()
        if not db_password:
            raise Exception("wrong name")
        if password == db_password[0]:
            jwt_access_token = fjwt.create_access_token(identity=name)
            status = jsonify(access_token=jwt_access_token)
        conn.close()
    except Exception as e:
        status = str(e)
        return jsonify(msg="login failed", error=status), 401
    return status, 200


@app.route('/messages', methods=["POST"])
@fjwt.jwt_required()
def messages_ep():
    """Эндпойнт обработки сообщений.
    Принимает сообщения авторизованных пользователей.
    Возвращает N последних сообщений пользователя по команде 'history [N]' """
    try:
        conn = connect_db()
        db_cursor = conn.cursor()
        name = request.json.get("name", None)
        message = request.json.get("message", None)
        if not name:
            raise Exception("name field is mandatory")
        assert name == fjwt.get_jwt_identity(), "wrong name"
        assert message, "empty message"

        # попытка спарсить команду history из сообщения
        history_cmd_template = r"^(history)\s+(\d+)$"
        history_cmd = re.match(history_cmd_template, message)
        if history_cmd:
            db_cursor.execute("SELECT message FROM messages WHERE name=? ORDER BY msgid DESC LIMIT ?",
                              (name, history_cmd.groups()[1]))
            messages = db_cursor.fetchall()
            return jsonify(messages), 200

        # сохранение сообщения в базу
        db_cursor.execute("INSERT INTO messages (message, name) VALUES (?, ?)", (message, name))
        conn.commit()
        conn.close()
        status = "message received"
    except Exception as e:
        status = str(e)
    return jsonify(msg=status), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0')
