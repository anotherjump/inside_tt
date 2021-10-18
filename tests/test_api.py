import pytest
import requests
import json
import faker


@pytest.fixture(scope='session')
def parameters(request):
    parameters = {"num_users": int(request.config.getoption("-U")),
                  "num_messages": int(request.config.getoption("-M")),
                  "clean_db": bool(request.config.getoption("-C"))}
    return parameters


def pytest_configure(config, parameters):
    config.clean_db = parameters["clean_db"]


@pytest.fixture(scope='session')
def generated_fake_users(parameters):
    ff = faker.Faker()
    users = []
    for i in range(parameters['num_users']):
        currentuser = {}
        userdata = (ff.profile(fields=['username']).get('username'), ff.password())
        currentuser["name"] = userdata[0]
        currentuser["password"] = userdata[1]
        users.append(currentuser)
    return users


@pytest.fixture()
def headers():
    return {'Content-type': 'application/json', 'Accept': 'text/plain'}


@pytest.fixture()
def endpoints():
    address = "http://127.0.0.1:5000"
    ep = {
        "login": address + "/login",
        "adduser": address + "/adduser",
        "messages": address + "/messages"
    }
    return ep


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


def test_addusers(endpoints, generated_fake_users, headers):
    """добавление случайно сгенерированных пользователей"""
    for user in generated_fake_users:
        userdata = json.dumps(user)
        r = requests.post(endpoints["adduser"], data=userdata, headers=headers)
        assert r.json().get("msg") == f"user {user['name']} added"


def test_login_success(endpoints, generated_fake_users, headers):
    """проверка получения токена для каждого зарегистрированного пользователя"""
    for user in generated_fake_users:
        userdata = json.dumps(user)
        r = requests.post(endpoints["login"], data=userdata, headers=headers)
        assert r.json().get("access_token")


@pytest.mark.xfail
def test_login_fail(endpoints, fake_user, headers):
    """проверка попытки получить токен для незарегистрированного пользователя"""
    r = requests.post(endpoints["login"], data=fake_user, headers=headers)
    assert r.json().get("access_token")


def test_post_random_messages(endpoints, generated_fake_users, headers, parameters,
                              random_messages):
    """проверка добавления сообщений каждым пользователем"""
    for user in generated_fake_users:
        userdata = json.dumps(user)
        access_token = requests.post(endpoints["login"], data=userdata, headers=headers).json().get("access_token")
        headers['Authorization'] = f'Bearer {access_token}'
        for i in range(parameters["num_messages"]):
            message_data = json.dumps({'name': user["name"], 'message': random_messages[i]})
            r = requests.post(endpoints["messages"], data=message_data, headers=headers)
            assert r.json().get("msg") == "message received"


def test_get_messages(endpoints, generated_fake_users, headers, parameters, random_messages):
    for user in generated_fake_users:
        userdata = json.dumps(user)
        access_token = requests.post(endpoints["login"], data=userdata, headers=headers).json().get("access_token")
        headers['Authorization'] = f'Bearer {access_token}'
        message_data = json.dumps({'name': user["name"], 'message': f'history {parameters["num_messages"]}'})
        r = requests.post(endpoints["messages"], data=message_data, headers=headers)
        db_messages = r.json()
        assert parameters["num_messages"] == len(db_messages), "количество отправленных и полученных сообщений " \
                                                               "не совпадает "
        for i in range(parameters["num_messages"]):
            assert db_messages[i][0] == random_messages[parameters["num_messages"]-i-1]


def test_delusers(endpoints, generated_fake_users, headers, parameters):
    if parameters["clean_db"]:
        for user in generated_fake_users:
            userdata = json.dumps(user)
            access_token = requests.post(endpoints["login"], data=userdata, headers=headers).json().get("access_token")
            headers['Authorization'] = f'Bearer {access_token}'
            r = requests.delete(endpoints["adduser"], data=userdata, headers=headers)
            assert r.json().get("msg") == f"user {user['name']} deleted"
    else:
        pytest.skip("Cleanup test skipped")


