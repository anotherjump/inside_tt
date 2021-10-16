# Структура проекта

### mariadb:
Содержит Dockerfile для сборки контейнера с базой данных и файл для инициализации базы данных dbinit.sql.

### msgsrv
Содержит Dockerfile для сборки контейнера с Flask сервером.
В файле requirements.txt перечислены зависимости для работы сервера и для тестов. 
Код сервера находится в main.py. Реализованы эндпойнты:
1. #### Авторизация (/login)

Сервер принимает данные в виде

`{ name: "имя отправителя", password: "пароль" }`

В случае совпадении имени и пароля с данным из базы возвращается токен авторизации (jwt).
В случае не совпадения - сообщение об ошибке.

3. #### Обработка сообщений (/messages)

Сервер принимает сообщения в виде

`{ name:       "имя отправителя", message:    "текст сообщение"}`


