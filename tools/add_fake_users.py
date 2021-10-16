import mariadb
import faker
NUMBER_OF_USERS_TO_ADD = 100


def connect_db():
    conn = mariadb.connect(
        user="root",
        password="dbpass",
        host="127.0.0.1",
        port=3306,
        database="msgsrv"
        )
    return conn


def fake_user_passwd(faker_factory):
    return faker_factory.profile(fields=['username']).get('username'), faker_factory.password()


if __name__ == "__main__":
    ff = faker.Faker()
    conn = connect_db()
    assert conn, "no connection"
    cur = conn.cursor()
    for i in range(NUMBER_OF_USERS_TO_ADD):
        data = fake_user_passwd(ff)
        cur.execute("INSERT INTO users (name, password) VALUES (?, ?)", (data[0], data[1]))
        conn.commit()
        print(f"added fake user: {data}")
