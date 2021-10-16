# Структура проекта

## mariadb:
Содержит Dockerfile для сборки контейнера с базой данных и файл для инициализации базы данных dbinit.sql.

## msgsrv
Содержит Dockerfile для сборки контейнера с сервером.
В файле requirements.txt перечислены зависимости для установки из PyPI. Использовано одно окружение и для сервера и для тестов. 
Код сервера находится в main.py. 
Сервер основан на Flask, в контейнере запускается автоматически командой `python main.py`.
Реализованне эндпойнты:
1. #### Авторизация (/login)

Эндпойнт принимает из POST запросов данные в виде:

`{ name: "имя отправителя", password: "пароль" }`

В случае совпадении имени и пароля с данным из базы возвращается токен авторизации ('jwt').
В случае не совпадения - сообщение об ошибке.

2. #### Обработка сообщений (/messages)

Эндпойнт принимает из POST запросов данные в виде:

`{ name: "имя отправителя", message: "текст сообщение"}`

При обработке проверяется наличие токена авторизации ('Bearer') и проверяется соответствие токена и поля 'name' из запроса. 
В случае успешной проверки сервер пытается распознать в сообщении команду вида 'history 10' с помощью регулярного выражения.
По распознанной команде сервер возвращает последние 10 (или любое другое указанное в команде число) сообщений пользователя.
Иначе сервер записывает сообщение в базу данных. 

Сервер обрабатывает сообщения, содержащие хотя бы 1 любой символ. Пустые сообщения не обрабатываются. 
Сообщения без поля `name` не обрабатываются. 
В случае записи сообщения в базу сервер возвращает ответ `message received`, иначе возвращается информация об ошибке.

## tests
Содержит тесты, написанные с использованием pytest.
Для конфигурации тестов используются параметры командной строки:
-U [N] количество генерируемых пользователей, по умолчанию 1;
-M [K] количество генерируемых сообщений, по умолчанию 1;
-C     очистка базы банных от записанных во время тестов пользователей и сообщений, по умолчанию False

#### Тесты:
1. Тест успешной авторизации.
2. Тест неудачной авторизации.
3. Тест добавления всех сгенерированных сообщений каждым из сгенерированных пользователей.
4. Тест получения истории сообщений каждым из сгенерированных пользователей.


