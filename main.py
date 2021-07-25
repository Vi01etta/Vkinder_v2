import db
from random import randrange
import vk_api
import json
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
from data_file import *

vk_session = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk_session)


def write_msg(user_id, message, attachment=''):
    vk_session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7),
                                        'attachment': attachment})


def get_params(add_params: dict = None):
    params = {
        'access_token': user_token,
        'v': '5.131'
    }
    if add_params:
        params.update(add_params)
        pass
    return params


data = [{'people': [], 'favorite': []}]


class VkBot:

    def __init__(self, user_id):
        self.dict_info = []
        self.user = db.User
        self.user_id = user_id
        self.username = self.user_name()
        self.commands = ["привет", "пока", "старт", "список", "далее", "изменить", "запись"]
        self.age = 0
        self.sex = 0
        self.city = 0
        self.sex = 0
        self.searching_user_id = 0
        self.top_photos = ''
        self.offset = 0

    def user_name(self):
        response = requests.get('https://api.vk.com/method/users.get', get_params({'user_ids': self.user_id}))
        for user_info in response.json()['response']:
            self.username = user_info['first_name'] + ' ' + user_info['last_name']
        return self.username

    def file_writer_all(self, my_dict):
        data[0]['people'].append(my_dict)
        with open('info.json', 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2,)

    def file_writer_fav(self, my_dict):
        data[0]['favorite'].append(my_dict)
        with open('info.json', 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2,)

    def menu(self):
        '''
        Вы находитесь в главном меню.
        Команды для бота:
        запись - запишет всех найденных людей в базу данных.
        список - выведет список людей ИЗ БАЗЫ ДАННЫХ, которые Вам понравились.
        изменить - позволит изменить критерии поиска.
        далее - продолжит поиск людей.
        пока - выйти из программы.
        '''

        write_msg(self.user_id, self.menu.__doc__)
        while True:
            for new_event in longpoll.listen():
                if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                    if new_event.message.lower() == self.commands[3]:
                        write_msg(self.user_id, 'Список людей, которые Вам понравились:')
                        dating_users = db.view_all(self.user_id)
                        for dating_user in dating_users:
                            write_msg(self.user_id, f'@id{dating_user}')
                        write_msg(self.user_id, self.menu.__doc__)
                    elif new_event.message.lower() == self.commands[5]:
                        self.offset = 0
                        self.start_program()
                    elif new_event.message.lower() == self.commands[4]:
                        write_msg(self.user_id, 'Идет поиск...')
                        self.offset += 1
                        self.find_user()
                        self.get_top_photos()
                        write_msg(self.user_id,
                                  f'Имя  и Фамилия: {self.username}\n Ссылка на страницу: @id{self.searching_user_id}',
                                  self.top_photos)
                        info = {'vk_id': self.searching_user_id, 'user_name': self.username, 'age': self.age,
                                'url': 'https://vk.com/id' + str(self.searching_user_id)}
                        self.file_writer_all(info)
                        self.searching()
                    elif new_event.message.lower() == self.commands[1]:
                        self.new_message(new_event.message.lower())
                        exit(write_msg(self.user_id, 'До встречи!'))
                    elif new_event.message.lower() == self.commands[6]:
                        write_msg(self.user_id, 'Записываем данные из файла в базу данных')
                        db.write_in_db()
                        write_msg(self.user_id, 'Готово.')
                        write_msg(self.user_id, self.menu.__doc__)
                    else:
                        write_msg(self.user_id, f"Я не понимаю Вас.")
                        self.menu()


    def start_program(self):
        self.user_name()
        write_msg(self.user_id, 'В каком городе будем искать?')
        for new_event in longpoll.listen():
            if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                self.user_city(new_event.message)
                self.user_name()
                self.user_age()
                self.user_sex()
                self.find_user()
                self.get_top_photos()
                people = {'vk_id': self.searching_user_id, 'user_name': self.username, 'age': self.age,
                       'url': 'https://vk.com/id' + str(self.searching_user_id)}
                self.file_writer_all(people)
                write_msg(self.user_id,
                          f'Имя  и Фамилия: {self.username}\n \nСсылка на страницу: @id{self.searching_user_id}',
                          self.top_photos)
                return self.searching()



    def searching(self):
        write_msg(self.user_id, 'Понравился пользователь?')
        while True:
            for new_event in longpoll.listen():
                if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                    if new_event.message.lower() == 'пока':
                        return self.new_message(new_event.message.lower())
                    elif new_event.message.lower() == 'да':
                        people = {'vk_id': self.searching_user_id, 'user_name': self.username, 'age': self.age,
                                  'url': 'https://vk.com/id' + str(self.searching_user_id)}
                        self.file_writer_fav(people)
                        write_msg(self.user_id, 'Пользователь добавлен в базу данных')
                        self.menu()
                    else:
                        write_msg(self.user_id, 'Идет поиск...')
                        self.offset += 1
                        self.find_user()
                        self.get_top_photos()
                        write_msg(self.user_id,
                                  f'Имя  и Фамилия: {self.username}\n Ссылка на страницу: @id{self.searching_user_id}',
                                  self.top_photos)
                        info = {'vk_id': self.searching_user_id, 'user_name': self.username, 'age': self.age,
                               'url': 'https://vk.com/id' + str(self.searching_user_id)}
                        self.file_writer_all(info)
                        write_msg(self.user_id, 'Понравился пользователь?')

    def user_age(self):
        try:
            write_msg(self.user_id, 'Введите желаемый возраст кандидата')
            for new_event in longpoll.listen():
                if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                    self.age = int(new_event.message)
                    if 17 < self.age <= 60:
                        return self.age
                    else:
                        write_msg(self.user_id, 'Некорректное значение, \n Введите пожалуйста числовое значение от 18 до 60 лет')
                        return self.user_age()
        except ValueError:
            write_msg(self.user_id, 'Некорректное значение, \n Введите пожалуйста числовое значение от 18 до 60 лет')
            return self.user_age()

    def user_sex(self):
        try:
            find_message = f'Какой пол будем искать? Введите: \n 1 - женский\n 2 - мужской\n 3 - любой\n'
            write_msg(self.user_id, find_message)
            for new_event in longpoll.listen():
                if new_event.type == VkEventType.MESSAGE_NEW and new_event.to_me:
                    self.sex = new_event.message
                    if int(self.sex) in [1, 2, 3]:
                        return self.sex
                    else:
                        write_msg(self.user_id, f'Некорректное значение')
                        return self.user_sex()
        except ValueError:
            write_msg(self.user_id, f'Некорректное значение')
            self.user_sex()

    def user_city(self, city):
        try:
            response = requests.get('https://api.vk.com/method/database.getCities',
                                    get_params({'country_id': 1, 'count': 1, 'q': city}))
            user_info = response.json()['response']
            self.city = user_info['items'][0]['id']
        except IndexError:
            write_msg(self.user_id, f'Некорректное значение')
            self.start_program()
        return self.city

    def find_user(self):
        try:
            response = requests.get('https://api.vk.com/method/users.search',
                                    get_params({'count': 1,
                                                'offset': self.offset,
                                                'city': self.city,
                                                'country': 1,
                                                'sex': self.sex,
                                                'age_from': self.age,
                                                'age_to': self.age,
                                                'fields': 'is_closed',
                                                'status': 6,
                                                'has_photo': 1}
                                               )
                                    )
            if response.json()['response']['items']:
                for searching_user_id in response.json()['response']['items']:
                    private = searching_user_id['is_closed']
                    if private:
                        self.offset += 1
                        self.find_user()
                    else:
                        self.searching_user_id = searching_user_id['id']
                        self.username = searching_user_id['first_name'] + ' ' + searching_user_id['last_name']
            else:
                self.offset += 1
                self.find_user()
        except KeyError:
            write_msg(self.user_id, f' попробуйте ввести другие критерии поиска')
            self.start_program()

    def get_top_photos(self):
        photos = []
        response = requests.get(
            'https://api.vk.com/method/photos.get',
            get_params({'owner_id': self.searching_user_id,
                        'album_id': 'profile',
                        'extended': 1}))
        try:
            sorted_response = sorted(response.json()['response']['items'],
                                     key=lambda x: x['likes']['count'], reverse=True)
            for photo_id in sorted_response:
                photos.append(f'''photo{self.searching_user_id}_{photo_id['id']}''')
            self.top_photos = ','.join(photos[:3])
            return self.top_photos
        except:
            pass

    def new_message(self, message):
        # Привет
        if message.lower() == self.commands[0]:
            return f"Здравствуйте, Вас приветствует чат-бот знакомств Vkinder! \n" \
                   f"Отправьте слово 'СТАРТ' чтобы начать подбор. \n" \
                   f"Чтобы завершить программу, напишите 'пока'."
        # Пока
        elif message.lower() == self.commands[1]:
            return f"До свидания!"
        # Старт
        elif message.lower() == self.commands[2]:
            return self.start_program()
        else:
            return f"Я не понимаю что Вы хотите, {self.username}."


if __name__ == '__main__':
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            bot = VkBot(event.user_id)
            write_msg(event.user_id, bot.new_message(event.text))