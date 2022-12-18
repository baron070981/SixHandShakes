import time
import argparse
import rich
from rich import print
from rich.progress import track
import vk_api


from sixhandshakes.mvkapi import User, Chain
from sixhandshakes.imageproc import CaptchaImage
import sixhandshakes.secretdata as secret
from sixhandshakes.writereadfiles import (
                                    ReadWriteSecret,
                                    ReadWriteSecretError,
                                )


conf_help = '''
Команда записи данных в файл конфигурации.
Логин и пароль передаются обязательно.
'''
run_help = '''
Команда запуска поиска. ID первого и последнего
пользователей в цепочки являются обязательными. Другие переданные
аргументы перезапишут значения в конфигурации.
'''

read_help = '''
Команда вывода содержимого файла конфигурации.
'''

parser = argparse.ArgumentParser(description='Поиск цепочек друзей между двумя пользователями ВК')
sub = parser.add_subparsers(title='sub')

confparser = sub.add_parser('conf', help=conf_help)
confparser.set_defaults(command='conf')
confparser.add_argument('login', help='логин в вк')
confparser.add_argument('password', help='пароль от страницы в вк')
confparser.add_argument('-t', '--token', help='token')
confparser.add_argument('-a', '--appid', help='id приложения', type=int)


runparser = sub.add_parser('run', help=run_help)
runparser.set_defaults(command='run')
runparser.add_argument('first_id', help='id первого профиля', type=int)
runparser.add_argument('last_id',  help='id последнего профиля', type=int)
runparser.add_argument('-s', '--size', help='колчество профилей в цепочке', type=int)
runparser.add_argument('-m', '--maxnum', help='максимальное количество найденых цепочек', type=int)
runparser.add_argument('-c', '--cnt', help='максимальное число друзей профилей', type=int)


readparser = sub.add_parser('read', help=read_help)
readparser.set_defaults(command='read')



if __name__ == "__main__":
    
    args = parser.parse_args(['--help'])
    readwriter = ReadWriteSecret()
    
    if args.command == 'conf':
        # запись в файл логина и пароля(обязательно)
        # токен и app_id по ситуации
        kwargs = {
                'TOK': args.token,
                'APP': args.appid,
            }
        readwriter.write(args.login, args.password, **kwargs)
        print(readwriter.read())
    
    
    elif args.command == 'run':
        # запуск поиска с заданными параметрами
        # переданные параметры и значения записываются в файл
        # значение параметра, который не передан, берется из файла
        
        data_from_file = readwriter.read()
        
        login = data_from_file['LOG']
        password = data_from_file['PAS']
        
        if not login or not password:
            raise Exception('Не переданы лог')
        
        first_id = args.first_id
        last_id = args.last_id
        max_mum_chains = args.maxnum if args.maxnum else data_from_file['MAX']
        CNT = int(args.cnt) if args.cnt else int(data_from_file['CNT'])
        STOP = False
        CHAIN_SIZE = int(args.size) if args.size else int(data_from_file['SIZ']) # меньше 4 не допускается пока
        chain = Chain()
        ALL_CHAINS = []
        MISBEHAVIOR = False
        
        data_to_file = {
                    'MAX': max_mum_chains,
                    'CNT': CNT,
                    'SIZ': CHAIN_SIZE,
                }
        
        readwriter.update_setting(**data_to_file)
        
        vk_session = vk_api.VkApi(login=login, 
                                  password=password)
    
        try:
            vk_session.auth(reauth=False)
        except vk_api.exceptions.Captcha as cap:
            # если требуется ввести капчу
            print("Требуется ввести капчу. Перейдите по ссылке и после введите текст капчи.")
            url = cap.get_url() # получение адреса капчи
            captcha = CaptchaImage() # создание объекта изображения капчи
            captcha.show_captcha(url) # получение и вывод в окне капчи
            print('Ссылка на капчу:', url)
            resp = input('Введите ответ: ')
            res = cap.try_again(resp) # отправка ответа с капчи
        except vk_api.exceptions.AuthError as err:
            print('='*60)
            print(err)
        # подключение API
        vk = vk_session.get_api()
        
        # первый юзер в цепочке
        first_user = vk.users.get(user_id=first_id, fields=User.fields)[0]
        first_user = User(**first_user)
        
        # последний юзер в цепочке
        end_user = vk.users.get(user_id=last_id, fields=User.fields)[0]
        end_user = User(**end_user)
        
        # получение списка друзей первого юзера
        friends = vk.friends.get(user_id=first_id, fields=User.fields)['items']
        print(f"Получено {len(friends)} друзей\n")
        # конвертирование списка словарей в объекты User
        friends = User.create_users(friends, True)
        CHAIN_SIZE -= 2
        
        # перебор списка друзей первого юзера
        for i, user in enumerate(friends):
            # очистка Chain
            chain.clear()
            # добавление юзеров в цепочку
            chain.add(first_user)
            chain.add(user)
            temp_chain = chain.copy()
            print(f'\nПоиск {i+1} из {len(friends)}\n')
            print(f'Найдено цепочек {len(ALL_CHAINS)} из {max_mum_chains}')
            if STOP:
                break
            
            uid = user.user_id
            intermediate_fr = []
            # получаю промежуточные звенья
            for j in range(CHAIN_SIZE-1):
                time.sleep(.23)
                intermediate_fr = vk.friends.get(user_id=uid, fields=User.fields, count=CNT)['items']
                intermediate_fr = User.create_users(intermediate_fr, shuffle=True)
                intermediate_fr = list(filter(lambda x: chain.is_not_in_cache(x.user_id), intermediate_fr))
                if not intermediate_fr:
                    MISBEHAVIOR = True
                    break
                intermediate_user = intermediate_fr[0]
                chain.add(intermediate_user)
                uid = chain.chain[-1].user_id
            if MISBEHAVIOR:
                MISBEHAVIOR = False
                continue
            last_friends = intermediate_fr.copy()
            intermediate_fr.clear()
            chain.pop_back()
            
            print(f"Кол-во друзей последнего в цепочки пользователя: {len(last_friends)}")
            if len(last_friends) == 0:
                continue
            tr = track(range(len(last_friends)), description='Поик по друзьям последнего пользователя:')
            tr.send(None)
            for j, luser in enumerate(last_friends):
                try:
                    tr.send(luser)
                except:
                    tr.close()
                if STOP:
                    break
                
                mutual = vk.friends.getMutual(source_uid=luser.user_id, target_uid=last_id)
                # print(f'{j}. Получено общих друзей {len(mutual)}')
                
                if mutual:
                    print(f'Найдено друзей: {len(mutual)}')
                    print(f'Найдено цепочек: {len(ALL_CHAINS)+len(mutual)}')
                    for m in mutual:
                        if not chain.is_not_in_cache(m):
                            continue
                        temp_chain = chain.copy()
                        temp_chain.add(luser)
                        time.sleep(.23)
                        mutual_user = vk.users.get(user_id=m, fields=User.fields)[0]
                        mutual_user = User(**mutual_user)
                        if not mutual_user.is_accessible:
                            continue
                        else:
                            temp_chain.add(mutual_user)
                            temp_chain.add(end_user)
                            ALL_CHAINS.append(temp_chain)
                        if len(ALL_CHAINS) >= max_mum_chains:
                            tr.close()
                            STOP = True
                            break
            print('\n==================================================\n')
        
        print("\n\nРезультат поиска:\n")
        if not ALL_CHAINS:
            print('Ничего не получилось найти...')
        else:
            for chain in ALL_CHAINS:
                for i, user in enumerate(chain.chain):
                    print(f'{i+1}. {user.user_id}'.ljust(10), end=': ')
                    print(f'{user.firstname} {user.lastname}'.ljust(35), end=' ')
                    print(f'{user.get("bdate", "---")}', end=' ')
                    print(f', {user.get("city_title", "---")}', end='')
                    print()
                print()
                print('='*45)
                print()
        
        
    elif args.command == 'read':
        # чтение и вывод содержимого файла в консоль
        # логин, пароль, токен и app_id не выводятся
        data = readwriter.read()
        for key, val in data.items():
            print(f'{key} : {val}')














