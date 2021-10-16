import pytest
import requests
import json
import mariadb
import faker


@pytest.fixture(scope='session')
def parameters(request):
    parameters = {"num_users": int(request.config.getoption("-U")),
                  "num_messages": int(request.config.getoption("-M")),
                  "clean_db": bool(request.config.getoption("-C"))}
    return parameters


@pytest.fixture(scope='session')
def registered_fake_users(parameters):
    ff = faker.Faker()
    users = []
    for i in range(parameters['num_users']):
        currentuser = {}
        userdata = (ff.profile(fields=['username']).get('username'), ff.password())
        currentuser["name"] = userdata[0]
        currentuser["password"] = userdata[1]
        users.append(currentuser)
    return users


@pytest.fixture(scope='session', autouse=True)
def db_connection():
    conn = mariadb.connect(
        user="root",
        password="dbpass",
        host="127.0.0.1",
        port=3307,
        database="msgsrv"
        )
    cur = conn.cursor()
    return conn, cur


@pytest.fixture(scope='session', autouse=True)
def populate_database(db_connection, registered_fake_users, parameters):
    conn, cursor = db_connection
    for user in registered_fake_users:
        try:
            cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", (user["name"], user["password"]))
            conn.commit()
        except mariadb.IntegrityError as e:
            pass
    yield
    n_rows = parameters["num_messages"]*parameters["num_users"]
    if parameters["clean_db"]:
        cursor.execute("DELETE FROM messages ORDER BY msgid DESC LIMIT ?", (n_rows, ))
        cursor.execute("DELETE FROM users ORDER BY uid DESC LIMIT ?", (parameters["num_users"],))
        conn.commit()
    conn.close()


@pytest.fixture()
def headers():
    return {'Content-type': 'application/json', 'Accept': 'text/plain'}


@pytest.fixture()
def login_endpoint():
    return "http://127.0.0.1:5000/login"


@pytest.fixture()
def message_endpoint():
    return "http://127.0.0.1:5000/messages"


@pytest.fixture()
def fake_user():
    ff = faker.Faker()
    user = ff.profile(fields=['username']).get('username'), ff.password()
    return json.dumps({'name': user[0], 'password': user[1]})


@pytest.fixture(scope='session')
def random_messages(parameters):
    messages = []
    for i in range(parameters["num_messages"]):
        ff = faker.Faker()
        messages.append(ff.sentence(nb_words=10))
    yield messages


def test_login_success(login_endpoint, registered_fake_users, headers):
    """проверка получения токена для каждого зарегистрированного пользователя"""
    for user in registered_fake_users:
        userdata = json.dumps(user)
        r = requests.post(login_endpoint, data=userdata, headers=headers)
        assert r.json().get("access_token")


def test_login_fail(login_endpoint, fake_user, headers):
    """проверка попытки получить токен для незарегистрированного пользователя"""
    r = requests.post(login_endpoint, data=fake_user, headers=headers)
    assert r.json().get("access_token") is None


def test_post_random_messages(login_endpoint, message_endpoint, registered_fake_users, headers, parameters,
                              random_messages):
    """проверка добавления сообщений каждым пользователем"""
    for user in registered_fake_users:
        userdata = json.dumps(user)
        access_token = requests.post(login_endpoint, data=userdata, headers=headers).json().get("access_token")
        headers['Authorization'] = f'Bearer {access_token}'
        for i in range(parameters["num_messages"]):
            message_data = json.dumps({'name': user["name"], 'message': random_messages[i]})
            r = requests.post(message_endpoint, data=message_data, headers=headers)
            assert r.json().get("msg") == "message received"


def test_get_messages(login_endpoint, message_endpoint, registered_fake_users, headers, parameters, random_messages):
    for user in registered_fake_users:
        userdata = json.dumps(user)
        access_token = requests.post(login_endpoint, data=userdata, headers=headers).json().get("access_token")
        headers['Authorization'] = f'Bearer {access_token}'
        message_data = json.dumps({'name': user["name"], 'message': f'history {parameters["num_messages"]}'})
        r = requests.post(message_endpoint, data=message_data, headers=headers)
        db_messages = r.json()
        assert parameters["num_messages"] == len(db_messages), "количество отправленных и полученных сообщений " \
                                                               "не совпадает "
        for i in range(parameters["num_messages"]):
            assert db_messages[i][0] == random_messages[parameters["num_messages"]-i-1]


