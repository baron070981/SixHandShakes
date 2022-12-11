import time
from typing import List

import rich
from rich import print
from rich.progress import track
import vk_api

from mvkapi import User, Chain
import secretdata
    







if __name__ == "__main__":
    
    
    first_id = 208412540
    last_id = 269643704
    # last_id = 673836103
    max_trees = 10
    CNT = 150
    STOP = False
    CHAIN_SIZE = 10 # меньше 4 не допускается пока
    chain = Chain()
    ALL_CHAINS = []
    
    token = secretdata.token
    # авторизация
    vk_session = vk_api.VkApi(login=secretdata.login, 
                              password=secretdata.password)
    
    try:
        vk_session.auth(reauth=False)
    except vk_api.exceptions.Captcha as cap:
        # если требуется ввести капчу
        print("Требуется ввести капчу. Перейдите по ссылке и после введите текст капчи.")
        url = cap.get_url() # получение адреса капчи
        captcha = imageproc.CaptchaImage() # создание объекта изображения капчи
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
        print(f'Поиск {i+1} из {len(friends)}\n')
        if STOP:
            break
        
        uid = user.user_id
        # получаю промежуточные звенья
        for j in range(CHAIN_SIZE-1):
            time.sleep(.23)
            intermediate_fr = vk.friends.get(user_id=uid, fields=User.fields, count=CNT)['items']
            intermediate_fr = User.create_users(intermediate_fr, shuffle=True)
            intermediate_fr = list(filter(lambda x: chain.is_not_in_cache(x.user_id), intermediate_fr))
            intermediate_user = intermediate_fr[0]
            chain.add(intermediate_user)
            uid = chain.chain[-1].user_id
        
        last_friends = intermediate_fr.copy()
        intermediate_fr.clear()
        chain.pop_back()
        
        print(f"Кол-во друзей последнего в цепочки пользователя: {len(last_friends)}")
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
                    if len(ALL_CHAINS) >= max_trees:
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
    
    
    
    
    
    
    
    
    

