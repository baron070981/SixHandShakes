import time
import random
from typing import List, Union
from copy import deepcopy

import rich
from rich import print
from rich.progress import track
from rich.progress import Progress
import vk_api
try:
    import imageproc
except:
    from sixhandshakes import imageproc



class User:
    
    fields = [
        'city', 'country',
        'bdate', 'sex',
        'home_town', 'photo_400',
        'photo_200', 'photo_400_orig',
        'photo_200_orig', 'domain', 'nickname'
    ]
    
    
    def __init__(self, **kwargs):
        
        self.user_id: int = kwargs.get('id') if 'id' in kwargs else kwargs.get('user_id')
        self.can_access_closed: bool = kwargs.get('can_access_closed', False)
        self.is_closed: bool = kwargs.get('is_closed', True)
        self.firstname: str = kwargs.get('first_name', None)
        self.lastname: str = kwargs.get('last_name', None)
        self.bdate: str = kwargs.get('bdate', None)
        self.home_town: str = kwargs.get('home_town', None)
        city = kwargs.get('city', None)
        self.city_title: str = None if city is None else city.get('title', None)
        self.city_id: int = None if city is None else city.get('id', None)
        country = kwargs.get('country', None)
        self.country_title: str = None if country is None else country.get('title', None)
        self.country_id: int = None if country is None else country.get('id', None)
        self.sex: int = kwargs.get('sex', None)
        self.photo_400_orig: str = kwargs.get('photo_400_org', None)
        self.photo_200_orig: str = kwargs.get('photo_200_org', None)
        self.photo_400: str = kwargs.get('photo_400', None)
        self.photo_200: str = kwargs.get('photo_200', None)
        self.domain: str = kwargs.get('domain', None)
        self.nickname: str = kwargs.get('nickname', None)
    
    
    def __str__(self):
        t_data = {
            'user_id': self.user_id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'bdate': self.bdate,
            'city_title': self.city_title,
            'country_title': self.country_title,
            'domain': self.domain,
        }
        data = {}
        for k, v in t_data.items():
            if v:
                data[k] = v
        return f'{data}\n'
    
    
    def __eq__(self, other):
        return self.user_id == other.user_id
    
    def __ne__(self, other):
        return self.user_id != other.user_id
    
    def __gt__(self, other):
        return self.user_id > other.user_id
    
    def __lt__(self, other):
        return self.user_id < other.user_id
    
    def __ge__(self, other):
        return self.user_id >= other.user_id
    
    def __le__(self, other):
        return self.user_id <= other.user_id
    
    
    @property
    def is_accessible(self):
        # проверяет что профиль юзера не скрыт и к нему есть доступ
        return (self.is_closed == True and self.can_access_closed == True)\
                or (self.is_closed == False and self.can_access_closed == True)
    
    
    @staticmethod
    def is_valid_user(user) -> bool:
        # проверяет что профиль юзера не скрыт и к нему есть доступ у
        # текущего пользователя
        if isinstance(user, dict):
            is_closed = user.get('is_closed', True)
            can_access_closed = user.get('can_access_closed')
            return (is_closed == True and can_access_closed == True) or \
                   (is_closed == False and can_access_closed == True)
        elif isinstance(user, User):
            return user.is_accessible
    
    
    @staticmethod
    def create_users(user_list: List[dict], shuffle: bool=False):
        # создание списка объектов User
        user_list = User.filter_users(user_list.copy(), shuffle)
        user_list = list(map(lambda x: User(**x), user_list))
        return user_list
    
    
    @staticmethod
    def filter_users(user_list: List[dict], shuffle: bool=False) -> List[dict]:
        # создает новый список с только валидными профилями
        users = list(filter(lambda x: User.is_valid_user(x), user_list))
        if shuffle:
            random.shuffle(users)
        return users
    
    
    def get(self, key, default):
        d = self.__dict__
        res = d.get(key, None)
        return res if res else default



class Chain:
    
    def __init__(self):
        self.chain = list()
        self.cache = list()
    
    
    def add(self, user: Union[dict, User]) -> None:
        # добавление объекта User
        if isinstance(user, User):
            user = user
        elif isinstance(user, dict):
            user = User(**user)
        else:
            error_msg = "функция is_valid_user принимает dict или объект "
            error_msg += f"объект класса данных User. Передано: {type(user)}"
            raise TypeError(error_msg)
        if user.is_accessible and user.user_id not in self.cache:
            # проверка, что профиль не закрытый и к нему есть доступ
            self.cache.append(user.user_id)
            self.chain.append(user)
    
    
    def add_cache(self, *users: User) -> None:
        #  добавление id юзера в кэш
        #  *users - объекты класса User
        users = list(map(lambda x: x.user_id, users))
        self.cache.extend(list(users))
    
    
    def clear(self) -> None:
        # очистка кэша и цепочки
        self.chain.clear()
        self.cache.clear()
    
    
    def clear_cache(self) -> None:
        # очистка только кэша
        self.cache.clear()
    
    
    def is_not_in_cache(self, user_id: int) -> bool:
        # проверка что id не нахлдится в кэше
        return user_id not in self.cache
    
    
    def pop_back(self):
        try:
            self.chain.pop()
        except:
            pass
    
    
    def copy(self):
        chain = Chain()
        chain.cache = self.cache.copy()
        chain.chain = deepcopy(self.chain)
        return chain



    
    
    
    
    
    
    
    
    
    
    
