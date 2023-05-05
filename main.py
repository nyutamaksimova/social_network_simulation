import psycopg2
from psycopg2 import Error


class User:

    def __init__(self, login, role):
        self.login = login
        self.role = role

        query = """SELECT id FROM users WHERE login = %s;"""
        cur = execute_with_parameters(query, [self.login])
        for record in cur:
            self.id = record[0]

    def delete_user(self):
        query = """DELETE FROM users WHERE login = %s;"""
        data = (self.login, )
        execute_with_parameters(query, data)

    def upload_post(self):
        print('Текст поста')
        text = input()
        query = """INSERT INTO posts (id, post) VALUES (%s, %s);"""
        data = (self.id, text,)
        execute_with_parameters(query, data)
        print('Пост успешно создан!')

    def edit_post(self):
        print('...Редактирование поста...')
        print('Введите номер поста')
        uid = int(input())
        query_access = """SELECT id FROM posts WHERE uid = %s;"""
        data_access = [uid]
        for record in execute_with_parameters(query_access, data_access):
            if record[0] == self.id:
                print('Введите исправленный текст')
                new_text = str(input())
                query = """UPDATE posts SET post = %s WHERE uid = %s; """
                data = (new_text, uid,)
                execute_with_parameters(query, data)
                print('Пост отредактирован!')
            else:
                print('Вы не можете редактировать посты других пользователей')

    def delete_post(self):
        print('Номер поста, который вы хотите удалить')
        uid = int(input())
        query_access = """SELECT id FROM posts WHERE uid = %s;"""
        data_access = [uid]
        for record in execute_with_parameters(query_access, data_access):
            if record[0] == self.id:
                query = """DELETE FROM posts WHERE uid = %s;"""
                data = (uid,)
                execute_with_parameters(query, data)
                print('Пост удалён!')
            else:
                print('Вы не можете удалять посты других пользователей')

    def view_posts_with_id(self):
        query = """SELECT uid, post, time FROM posts WHERE id = %s ORDER BY time DESC;"""
        data = (self.id,)
        for record in execute_with_parameters(query, data):
            print(record[0], record[1], record[2])

    def view_posts_with_login(self):
        print('Введите логин')
        user_login = str(input())
        query = """SELECT uid, post, time FROM posts WHERE id in (SELECT id FROM users WHERE login = %s) ORDER BY time DESC;"""
        data = (user_login,)
        for record in execute_with_parameters(query, data):
            print(record[0], record[1], record[2])

    def post_selection(self):
        print('... Просмотр постов пользователя ...')
        print('Введите логин пользователя')
        login = str(input())
        print('Введите количество постов на странице')
        N = int(input())
        print('Введите номер страницы')
        i = int(input())
        query = """SELECT post, number 
                FROM (SELECT post, row_number() 
                over (ORDER BY time DESC) AS number FROM posts WHERE posts.id IN (SELECT id FROM users WHERE login = %s)) 
                AS author_posts 
                WHERE author_posts.number > %s * (%s -1) AND author_posts.number <= %s * %s;"""
        data = (login, N, i, N, i,)
        for record in execute_with_parameters(query, data):
            print(record)

    def subscription(self):
        print('На кого хотите подписаться?')
        login2 = str(input())
        query = """INSERT INTO subs (id1, id2) 
                    SELECT u1.id AS id1, u2.id AS id2 FROM users AS u1, users AS u2 
                    WHERE u1.login= %s AND u2.login= %s;"""
        data = (self.login, login2,)
        execute_with_parameters(query, data)
        print('Вы подписались на ', login2, '!')

    def unsubscription(self):
        print('От кого хотите отписаться?')
        login2 = str(input())
        query = """DELETE FROM subs 
                    WHERE  (id1, id2) IN (
                    SELECT u1.id AS id1, u2.id AS id2 FROM users AS u1, users AS u2 
                    WHERE u1.login= %s AND u2.login= %s);"""
        data = (self.login, login2,)
        execute_with_parameters(query, data)
        print('Вы отписались от, ', login2,' !')

    def subscribers(self):
        query = """SELECT * FROM subs WHERE id2 IN 
                (SELECT users.id AS id2 FROM users 
                WHERE users.login = %s);"""
        data = (self.login,)
        for record in execute_with_parameters(query, data):
            print(record)

    def subscriptions(self):
        query = """SELECT * FROM subs WHERE id1 IN 
                (SELECT users.id AS id1 FROM users 
                WHERE users.login = %s);"""
        data = (self.login,)
        for record in execute_with_parameters(query, data):
            print(record)

    def mutual_subscriptions(self):
        query = """SELECT s1.id1, s1.id2 
                FROM subs AS s1 
                JOIN subs AS s2 ON s1.id2 = s2.id1 AND s1.id1 = s2.id2 
                WHERE s1.id1 IN 
                (SELECT users.id AS id1 FROM users WHERE users.login = %s);"""
        data = (self.login,)
        for record in execute_with_parameters(query, data):
            print(record)

    def subscription_posts(self):
        print('... Просмотр постов из подписок ...')
        print('Введите количество постов на странице')
        N = int(input())
        print('Введите номер страницы')
        i = int(input())
        query = """SELECT post, number
                FROM (SELECT post, row_number()
                over (ORDER BY time DESC) AS number FROM posts 
                WHERE id IN (SELECT id2 FROM subs WHERE id1 in (SELECT id FROM users WHERE login = %s)))
                AS author_posts
                WHERE author_posts.number > %s * (%s -1) AND author_posts.number <= %s * %s;"""
        data = (self.login, N, i, N, i,)
        for record in execute_with_parameters(query, data):
            print(record[1], record[0])


class Moderator(User):

    def edit_post(self):
        print('...Редактирование поста...')
        print('Введите номер поста')
        uid = int(input())
        print('Введите исправленный текст')
        new_text = str(input())
        query = """UPDATE posts SET post = %s WHERE uid = %s; """
        data = (new_text, uid,)
        execute_with_parameters(query, data)
        print('Пост отредактирован!')

    def delete_user(self):
        print('Введите логин пользователя, которого хотите удалить')
        login = str(input())
        query = """DELETE FROM users WHERE login = %s;"""
        data = (login, )
        execute_with_parameters(query, data)
        print('Пользователь удален!')

    def delete_post(self):
        print('Uid поста, который хотите удалить')
        uid = int(input())
        query = """DELETE FROM posts WHERE uid = %s;"""
        data = (uid,)
        execute_with_parameters(query, data)
        print('Пост удален!')


class Administrator(Moderator):

    def change_role(self):
        print('Введите логин')
        login = str(input())
        if login != self.login:
            role_query = """SELECT role FROM users WHERE login = %s;"""
            for record in execute_with_parameters(role_query, [login]):
                print('Роль на данный момент:', record[0])
            print('Введите новую роль')
            new_role = int(input())
            change_role = """ UPDATE users SET role = %s WHERE login = %s;"""
            data = (new_role, login,)
            execute_with_parameters(change_role, data)
            print('Роль изменена!')
        else:
            print('Вы не можете менять свою роль')


def new_connection():
    try:
        connection = psycopg2.connect(database='app',
                                      user='postgres',
                                      password="060601",
                                      host="127.0.0.1",
                                      port="5432")
        return connection
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)


def execute(query):
    conn = new_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()


def execute_with_parameters(query, data):
    try:
        conn = new_connection()
        cursor = conn.cursor()
        cursor.execute(query, data)
        conn.commit()
        try:
            return cursor
        except:
            return 0
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)


def create_user_table():
    query = """CREATE TABLE IF NOT EXISTS users (
     id SERIAL PRIMARY KEY, 
     login VARCHAR UNIQUE NOT NULL,
     password VARCHAR NOT NULL,
     role INT NOT NULL);"""
    execute(query)


def create_posts_table():
    query = """CREATE TABLE IF NOT EXISTS posts (
        uid SERIAL PRIMARY KEY,
        id int NOT NULL,
        post text NOT NULL,
        time timestamp DEFAULT now(),
        FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE
        );
    """
    execute(query)


def create_subs_table():
    query = """CREATE TABLE IF NOT EXISTS subs (
     id1 INT NOT NULL, 
     id2 INT NOT NULL, 
     UNIQUE (id1, id2), 
     FOREIGN KEY (id1) REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE,      
     FOREIGN KEY (id2) REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE
);
    """
    execute(query)


def start():
    create_user_table()
    create_subs_table()
    create_posts_table()

    query = """ CREATE EXTENSION IF NOT EXISTS pgcrypto;
                INSERT INTO users (login, password, role)
                VALUES(%s, crypt(%s, gen_salt('bf')), 0);
                """
    data = ('admin', '123456',)
    execute_with_parameters(query, data)

    change_role('admin', 2)


def user_registration():

    print('... Регистрация ...')
    print('Введите логин:')
    login = str(input())
    query_login = """SELECT id FROM users WHERE login = %s;"""
    data_login = (login, )
    while True:
        for record in execute_with_parameters(query_login, data_login):
            if record:
                print('2')
                print('Логин занят')
                print('Введите логин:')
                login = str(input())
                data_login = (login,)
        break

    print('Введите пароль:')
    password = str(input())

    query = """ CREATE EXTENSION IF NOT EXISTS pgcrypto;
            INSERT INTO users (login, password, role)
            VALUES(%s, crypt(%s, gen_salt('bf')), 0);
            """
    data = (login, password, )
    execute_with_parameters(query, data)
    print('Регистрация прошла успешно!')
    return User(login, 0)


def change_role(login, new_role):
    change_role = """ UPDATE users SET role = %s WHERE login = %s;"""
    data = (new_role, login, )
    execute_with_parameters(change_role, data)


def log_in():
    print('... Вход ...')
    print('Ваш логин:')
    login = str(input())
    login_query = """SELECT id FROM users WHERE login = %s ;"""
    data = (login,)
    print('Ваш пароль:')
    password = str(input())
    query = """SELECT role FROM users WHERE login = %s AND password = crypt(%s, password);"""
    data = (login, password,)

    for record in execute_with_parameters(query, data):
        role = record[0]
    if role == 0:
        print('Вход осуществлён')
        return User(login, role)
    if role == 1:
        print('Вход осуществлён')
        return Moderator(login, role)
    if role == 2:
        print('Вход осуществлён')
        return Administrator(login, role)
    else:
        print('Ошибка входа')


def drop_tables():
    query = """ DROP TABLE subs;
                DROP TABLE posts;
                DROP TABLE users;
    """
    execute(query)


def communication():
    print('.................. Опции ..................')
    print('1 - Войти', '2 - Зарегистрироваться')
    r = int(input())
    if r == 1:
        User = log_in()
    elif r == 2:
        User = user_registration()

    while True:
        print('.................. Опции ..................')
        print('0 - Завершить сеанс')
        print('С постами:')
        print('1 - Создать пост')
        print('2 - Редактировать пост')
        print('3 - Удалить пост')
        print('4 - Посмотреть свои посты')
        print('5 - Посмотреть посты других пользователей')
        print('6 - Посмотреть посты подпиок')
        print('С пользователями:')
        print('7 - Подписаться на пользователя')
        print('8 - Отписаться от пользователя')
        print('9 - Посмотреть подписчиков')
        print('10 - Посмотреть подписки')
        print('11 - Посмотреть взаимные подписки')
        print('12 - Удалить аккаунт')

        if User.role == 2:
            print('13 - Изменить роль')

        r = int(input())
        if r == 0:
            print('До свидания!')
            break
        elif r == 1:
            User.upload_post()
        elif r == 2:
            User.edit_post()
        elif r == 3:
            User.delete_post()
        elif r == 4:
            User.view_posts_with_id()
        elif r == 5:
            User.view_posts_with_login()
        elif r == 6:
            User.subscription_posts()
        elif r == 7:
            User.subscription()
        elif r == 8:
            User.unsubscription()
        elif r == 9:
            User.subscribers()
        elif r == 10:
            User.subscriptions()
        elif r == 11:
            User.mutual_subscriptions()
        elif r == 12:
            User.delete_user()
        elif r == 13:
            User.change_role()







if __name__=='__main__':
    #connection = new_connection()
    #drop_tables(connection)
    #start(connection)
    communication()







