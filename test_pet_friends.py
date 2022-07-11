from api import PetFriends
from settings import *
import os

pf = PetFriends()


def test_get_api_key_from_invalid_user(email=invalid_email, password=invalid_password):
    """Проверяем можно ли  получить api_key с невалидными данными """

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    status, result = pf.get_api_key(email, password)

    # Сверяем полученный статус ответа с ожидаемым результатом
    assert status == 403
    assert 'key' is not result


def test_get_all_pets_with_none_key(filter=''):
    """Проверяем возможность получения списка питомцев передавая в метод auth_key невалидный email и password"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    status, auth_key = pf.get_api_key(invalid_email, invalid_password)

    # Проверяем, что в переменной auth_key нет ключа 'key'
    assert 'key' is not auth_key

    # Проверяем, что метод pf.get_list_of_pets если в него не передать auth_key вызывает исключение TypeError
    try:
        pf.get_list_of_pets(auth_key, filter)
    except TypeError as e:
        assert e


def test_get_all_pets_with_invalid_filter(filter='filter'):
    """Проверяем возможность получения списка питомцев передавая в метод get_list_of_pets невалидный filter"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    status, auth_key = pf.get_api_key(valid_email, valid_password)

    # Запрашиваем список питомцев и сохраняем в переменые status, result
    status, result = pf.get_list_of_pets(auth_key, filter)
    # Проверяем что ствтус ответа 500
    assert status == 500


def test_adding_new_pet_with_empty_data(name=' ', animal_type=' ',
                                     age=' ', pet_photo='images/photo_dog.jpg'):
    """Проверяем что можно добавить питомца без указания имени, вида животного и возраста """

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Добавляем питомца
    status, result = pf.post_add_new_pet(auth_key, name, animal_type, age, pet_photo)
    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == age


def test_add_new_pet_with_valid_data_none_photo(name='Ummi', animal_type='Dog',
                                     age='0', pet_photo=' '):
    """Проверяем что можно ли добавить питомца с валидными данными без фото """

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Проверяем, что в переменной auth_key есть ключ 'key'
    assert 'key' in auth_key

    # Проверяем что метод pf.post_add_new_pet если в него не фото вызывает исключение FileNotFoundError
    try:
        pf.post_add_new_pet(auth_key, name, animal_type, age, pet_photo)
    except FileNotFoundError as e:
        assert e


def test_add_new_pet_with_valid_data(name='Юмми', animal_type='Собака',
                                     age='-100,0', pet_photo='images/photo_dog.jpeg'):
    """Проверяем что можно добавить питомца возрастом с отрицательным вещественным числом"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.post_add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['age'] == age


def test_update_self_pet_info_with_invalid_id(name='!"№;%:?*(){}[]', animal_type='Dog', age='Один'):
    """Проверяем отсутствие возможности обновления информации о питомце с неправильным id"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить  имя, тип и возраст первого питомца
    if len(my_pets['pets']) > 0:
        invalid_id = my_pets['pets'][0]['id'] + '123456789'  # создаем неправильный id
        status, result = pf.update_pet_info(auth_key, invalid_id, name, animal_type, age)

        # Проверяем, что статус ответа = 400
        assert status == 400

    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_successful_update_self_pet_info_invalid_data(name='!"№;%:?*(){}[]', animal_type='Dog', age='Один'):
    """Проверяем возможность обновления информации о питомце c не валидными данными"""

    # Получаем ключ auth_key и в фильтр передаем пустое значение
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert result['name'] == name
        assert result['animal_type'] == animal_type

    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_delete_pet_in_empty_list():
    """Проверяем возможность удаления питомца из пустого списка."""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Удаление всех своих питомцев
    if len(my_pets['pets']) > 0:
        for i in range(len(my_pets['pets'])):
            pet_id = my_pets['pets'][i]['id']
            _ = pf.delete_pet(auth_key, pet_id)

    # Проверяем, что список питомцев пустой
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    assert len(my_pets['pets']) == 0
    if len(my_pets['pets']) == 0:
        # Если список питомцев пустой, передаём в pet_id пустую строку
        pet_id = ""
        # Попытка удаления питомца из пустого списка
        status, _ = pf.delete_pet(auth_key, pet_id)
        assert status == 404




def test_update_self_pet_info_with_invalid_filter_and_key(name='name', animal_type='dog', age='0.3', filter='filter'):
    """Проверяем отсутствие возможности обновления информации о питомце с неправильным ключом и без фильтра"""

    # Создаем невалидный ключ и сохраняем его в переменую auth_key
    auth_key = {"key": "auth_key"}

    # Передаем в метод pf.get_list_of_pets невалидный ключ и фильтр
    _, my_pets = pf.get_list_of_pets(auth_key, filter)

    # Проверяем , что список не пустой
    if len(my_pets) != 0:
        # Проверяем возможность обновления данных у первого питомца в списке
        status, result = pf.update_pet_info(auth_key, my_pets[0], name, animal_type, age)

        # Проверяем, что статус ответа = 403
        assert status == 403
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")
