import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from data_file import bd_path
import json

Base = declarative_base()
engine = sq.create_engine(bd_path)
Session = sessionmaker(bind=engine)
session = Session()


# Таблица "User", где будет храниться вся информация по пользователю
class User(Base):
    __tablename__ = 'user'
    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer)
    user_name = sq.Column(sq.String)
    age = sq.Column(sq.String)


# Таблица "DatingUser", где будут храниться все найденные пары для пользователя
class DatingUser(Base):
    __tablename__ = 'datinguser'
    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer)
    user_name = sq.Column(sq.String)
    id_User = sq.Column(sq.Integer, sq.ForeignKey('user.id'))
    user = relationship(User)


# Создать пустые таблицы в БД если их нет
def create_tables():
    Base.metadata.create_all(engine)


# Добавляем пользователя в БД
def add_user(user):
    session.expire_on_commit = False
    session.add(user)
    session.commit()


# Показать всех понравившихся людей из БД
def view_all(user_id):
    links = []
    # id_query = session.query(User.id).order_by(User.id.desc()).filter(User.vk_id == user_id).limit(1)
    # id_query.all()
    q = session.query(DatingUser)
    for c in q:
        links.append(c.vk_id)
    return links

    # id_list = [p.id for p in id_query]
    # id_user = id_list[0]
    # searching_users_query = session.query(DatingUser.vk_id).filter(DatingUser.id_User == id_user).all()
    # searching_users_list = [du.vk_id for du in searching_users_query]
    # for link in searching_users_list:
    #     links.append(link)
    # return links


def write_in_db():
    create_tables()
    with open('info.json', 'r', encoding='utf8') as f:
        data = json.load(f)
        for i in data[0]['people']:
            # запись из файла в бд всех найденных в колонку юзер
            create_tables()
            user = User(vk_id=i['vk_id'], user_name=i['user_name'],
                        age=i['age'])
            add_user(user)

        for i in data[0]['favorite']:
            # запись из файла в бд понравившихся в колонку дэтингюзер
            searching_user = DatingUser(vk_id=i['vk_id'], user_name=i['user_name'],
                                        id_User=user.id)
            add_user(searching_user)


view_all(92562674)
