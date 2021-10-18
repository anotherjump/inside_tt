## Структура проекта

## mariadb
Содержит Dockerfile для сборки контейнера с базой данных и файл для инициализации базы данных dbinit.sql.  
При сборке контейнера создаются тестовые пользователи:  
|uid|name|password|
|---|---|---|
|1|testuser1|passwd1
|2|testuser2|passwd2|
|3|testuser3|passwd3|

Для подключения используется имя пользователя root и пароль dbpass.

## msgsrv
Содержит Dockerfile для сборки контейнера с сервером.   
В файле requirements.txt перечислены зависимости для установки из PyPI. Использовано одно окружение и для сервера и для тестов. Код сервера находится в main.py.  
Сервер основан на Flask, в контейнере запускается автоматически командой `python main.py`.  
Сервер использует адрес `0.0.0.0:5000`.  

### Реализованные эндпойнты:  
1. **Добавление пользователя**  
Эндпойнт принимает из POST запросов данные в виде:  
`{ name: "имя отправителя", password: "пароль" }` 
В случае совпадения имени с уже имеющимся в базе возвращается ошибка (поле `name` имеет ограничение UNIQUE).
В случае успешного добавления пользователя возвращается сообщение `user "имя пользователя" added`.
Эндпойнт может принимать запросы DELETE для удаления пользователя с данными в виде:  
`{ name: "имя отправителя", password: "пароль" }`  
Запрос должен содерать токен авторизации. Сервер проверяет соответствие токена и имени удаляемого пользователя.

2. **Авторизация** (/login)  
Эндпойнт принимает из POST запросов данные в виде:  
`{ name: "имя отправителя", password: "пароль" }`  
В случае совпадении имени и пароля с данным из базы возвращается токен авторизации ('jwt').  
В случае не совпадения - сообщение об ошибке.  
  
3. **Обработка сообщений** (/messages)  
Эндпойнт принимает из POST запросов данные в виде:  
`{ name: "имя отправителя", message: "текст сообщение"}`  
При обработке проверяется наличие токена авторизации ('Bearer') и проверяется соответствие токена и поля 'name' из запроса.   
В случае успешной проверки сервер пытается распознать в сообщении команду вида 'history 10' с помощью регулярного выражения.  
По распознанной команде сервер возвращает последние 10 (или любое другое указанное в команде число) сообщений пользователя.  
Иначе сервер записывает сообщение в базу данных.  
Сервер обрабатывает сообщения, содержащие хотя бы 1 любой символ.   
Пустые сообщения не обрабатываются. Сообщения без поля `name` не обрабатываются.  
В случае записи сообщения в базу сервер возвращает ответ `message received`, иначе возвращается информация об ошибке.

### Установка и запуск
Скачать этот репозиторий.  
В директории `inside_tt` собрать проект командой `docker-compose build`.
После этого запустить командой `docker-compose up`.
Можно использовать собранные образы из репозиториев `anotherjmp/inside_tt_mariadb` и `anotherjmp/inside_tt_msgsrv` на Docker Hub.


## tests
Содержит тесты, написаны с помощью фреймворка **PyTest**. 
В тестах используются случайно сгенерированные данные с помощью пакета **Faker**.  
Для конфигурации тестов используются параметры командной строки:  
`-U [N]` количество генерируемых пользователей, по умолчанию 1;  
`-M [K]` количество генерируемых сообщений, по умолчанию 1;  
`-C` очистка базы банных от записанных во время тестов пользователей и сообщений, по умолчанию False.  
Тесты описаны в файле `test_api.py`:  
1. Тест регистрации сгенерированных пользователей `test_addusers`.
2. Тест успешной авторизации `test_login_success`.  
3. Тест неудачной авторизации `test_login_fail`. Отмечен опцией XFAIL, т.е. ожидается что его выполнение вернёт ошибку.  
4. Тест добавления всех сгенерированных сообщений каждым из сгенерированных пользователей `test_post_random_messages`.  
5. Тест получения истории сообщений каждым из сгенерированных пользователей `test_get_messages`.  
6. Тест удаления всех сгенерированных пользователей и сообещний (каскадно по ключам FOREIGN KEY) `test_delusers`. Выполняется только в случае указания параметра `-C` при запуске.

**Запуск тестов**
Тесты запускаются из командной строки в корневом каталоге проекта (`/inside_tt`).
Фреймворк pytest сам находит папку `tests` и файлы в ней, начинающиеся с `test`, все функции внутри, начинающиеся на `test` выполняются как тесты.
Для запуска тестов необходимы пакеты `pytest` и `faker`.
Примеры команд для запуска тестов

|Команда|Значение|
|---|--------------------------|
|`pytest`|Запуск тестов с параметрами по умолчанию (генерируются 1 пользователь и 1 сообщение), после выполнения данные останутся в базе.|
|`pytest -U 4 -M 10`|Запуск тестов с 4 сгенерированными пользователями и 10 сообщениями, после выполнения данные останутся в базе.|
|`pytest -U 10 -M 20 -C`|Запуск тестов с 10 сгенерированными пользователями и 20 сообщениями, после выполнения данные удалятся.|   

Есть небольшая вероятность неудачного завершения тестов, если `faker` генерирует имя пользователя, которое уже присутствует в базе (у меня так 1 раз произошло).

## docker-compose.yml
Файл для сборки проекта с помощью docker-compose. Для тестов и отладки сервис `mariadb` открыт на внешний порт 3307.  
Сервис `msgsrv` обращается к базе данных через внутреннюю сеть Docker по хостнейму и порту 3306.  
Собранные образы можно взять в репозиториях `anotherjmp/inside_tt_mariadb` и `anotherjmp/inside_tt_msgsrv` на Docker Hub.

---
Проект собирался и тестировался в Fedora 34, использовался Python 3.9.7.


