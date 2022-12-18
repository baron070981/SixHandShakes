from pathlib import Path
import os, os.path
from rich import print


class ReadWriteSecretError(Exception):
    pass


class ReadWriteSecret:
    
    '''Класс записи и чтения конфидециальных данных
    логина, пароля, токена и т.п.'''
    
    # fields = ['LOG', 'PAS', 'TOK', 'APP', 'CNT', 'SIZ', 'MAX']
    fields = {'LOG': None, 'PAS': None, 
              'TOK': None, 'APP': None, 
              'CNT': 100, 'SIZ': 4, 'MAX': 1}
    
    def __init__(self):
        self.__filename = Path(__file__).resolve().parent / "secretdata.txt"
        self.__secret_data = dict()
    
    
    def __split_string(self, string):
        key, val = None, None
        sp_s = string.split(' : ')
        if len(sp_s) != 2:
            return None, None
        key, val = list(map(str.strip, sp_s))
        return key if key in ReadWriteSecret.fields else None, val
    
    
    def write(self, login, password, **kwargs):
        # запись данных в файл
        # записываются ключ - значение
        # если файл не существует, то создается новый
        # если существует, то значеия вимеющихся ключах перезаписываются
        # если ключ передан, если переданого ключа нет в файле, то
        # файл дополняеся ключом и значением
        latest_data = dict()
        fields = ReadWriteSecret.fields.copy()
        
        
        if self.__filename.exists():
            # получение из файла старых значений и сохранение в latest_data
            latest_data = self.__read()
            latest_data['LOG'] = login
            latest_data['PAS'] = password
            
            # запись в файл измененных значений или добавление новых
            for key, val in kwargs.items():
                latest_data[key] = val
            self.__write(**latest_data)
            return
        
        with open(str(self.__filename), 'w') as f:
            f.write(f'LOG : {login}\n')
            f.write(f'PAS : {password}\n')
            self.__secret_data['LOG'] = str(login)
            self.__secret_data['PAS'] = str(password)
            for key, val in fields.items():
                value = kwargs.get(key, val)
                if value:
                    f.write(f'{key} : {value}\n')
                    self.__secret_data[str(key)] = str(value)
    
    
    def update_setting(self, **kwargs):
        if not self.__filename.exists():
            return
        latest_data = self.__read()
        
        for key, val in kwargs.items():
            if key in ReadWriteSecret.fields and key not in ['LOG', 'PAS']:
                latest_data[key] = val
        self.__write(**latest_data)
    
    
    def __read(self):
        data = {}
        if self.__filename.exists():
            with open(str(self.__filename), 'r') as f:
                while True:
                    s = f.readline().strip()
                    if not s:
                        break
                    key, val = self.__split_string(s)
                    if not key or not val:
                        continue
                    data[key] = val
        return data
    
    
    def __write(self, **kwargs):
        with open(str(self.__filename), 'w') as f:
            for key, val in kwargs.items():
                if not key or not val:
                    continue
                f.write(f'{key} : {val}\n')
    
    
    def read(self):
        # чтение файла и сохранение данных в __secret_data (словарь)
        if not self.__filename.exists():
            raise ReadWriteSecretError('Нет файла конфигурации')
        self.__secret_data = self.__read()
        return self.__secret_data.copy()
    
    
    def get_value_by_key(self, key):
        data = self.__read()
        return data.get(key, None)
    
    
    def delete_key(self, *keys):
        data = self.__read().copy()
        for key in keys:
            if key in data:
                del data[key]
        return data
    
    

    




