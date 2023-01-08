import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(autouse=True)
def testing():
    """Фикстура, осуществляющая логин на сайт, выполнение теста и закрытие браузера"""
    pytest.driver = webdriver.Chrome(r'e:\chromedriver.exe')
    # Переходим на страницу авторизации
    pytest.driver.get('http://petfriends1.herokuapp.com/login')
    # Вводим email
    pytest.driver.find_element_by_id('email').send_keys('joker@rambler.ru')
    # Вводим пароль
    pytest.driver.find_element_by_id('pass').send_keys('12345')
    # Нажимаем на кнопку входа в аккаунт
    pytest.driver.find_element_by_css_selector('button[type="submit"]').click()

    # Проверяем, что мы оказались на главной странице пользователя
    assert pytest.driver.find_element_by_tag_name('h1').text == "PetFriends"

    yield

    pytest.driver.quit()


def test_all_pets():
    """Тестирует карточки всех питомцев"""
    # Задаем период неявного ожидания
    pytest.driver.implicitly_wait(20)
    pytest.driver.get('http://petfriends1.herokuapp.com/all_pets')
    images = pytest.driver.find_elements_by_css_selector('.card-deck .card-img-top')
    names = pytest.driver.find_elements_by_css_selector('.card-deck .card-title')
    descriptions = pytest.driver.find_elements_by_css_selector('.card-deck .card-text')
    for i in range(len(names)):
        assert images[i].get_attribute('src') != ''
        assert names[i].text != ''
        assert descriptions[i].text != ''
        assert ', ' in descriptions[i]
        parts = descriptions[i].text.split(", ")
        assert len(parts[0]) > 0
        assert len(parts[1]) > 0


def test_my_pets():
    """Тестирует карточки в разделе 'Мои питомцы'"""
    # Переходим к списку своих питомцев
    pytest.driver.get('http://petfriends1.herokuapp.com/my_pets')
    # Ищем текст с количеством питомцев
    pets_text = WebDriverWait(pytest.driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class=".col-sm-4 left"]'))
    )

    assert 'Питомцев:' in pets_text.text

    # Получаем количество питомцев в статистике
    pets_amount = int(pets_text.text.split('\n')[1].split(':')[1])
    # Проверяем, что количество строк в таблице питомцев равно количеству питомцев в статистике
    rows = WebDriverWait(pytest.driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH,
                                             '//div[@id="all_my_pets"]/table[@class="table table-hover"]/tbody/tr'))
    )
    rows_amount = len(rows)

    assert pets_amount == rows_amount

    # Проверяем, что фото есть хотя бы у половины питомцев
    rows = WebDriverWait(pytest.driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH,
                                        '//div[@id="all_my_pets"]/table[@class="table table-hover"]/tbody/tr/th/img'))
    )
    photo_amount = 0
    for row in rows:
        if row.get_attribute('src') != '':
            photo_amount += 1

    assert photo_amount >= pets_amount / 2

    # Проверяем, что у всех питомцев есть имя, возраст и порода
    # Элементов /tbody/tr/td должно быть ровно в 4 раза больше (т.к. 4 колонки в таблице), чем количество питомцев,
    # и все эти элементы должны иметь непустой текст
    elements = WebDriverWait(pytest.driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH,
                                             '//div[@id="all_my_pets"]/table[@class="table table-hover"]/tbody/tr/td'))
    )

    assert pets_amount * 4 == len(elements)

    data_filled = True
    for element in elements:
        text = element.text
        if text.isspace():
            data_filled = False
            break

    assert data_filled

    # Проверяем, что нет повторяющихся питомцев (с одинаковыми именем, породой и возрастом)
    data_list = []
    rows = WebDriverWait(pytest.driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH,
                                             '//div[@id="all_my_pets"]/table[@class="table table-hover"]/tbody/tr'))
    )
    for row in rows:
        cells = row.text.split()
        data = tuple([cells[0], cells[1], cells[2]])
        data_list.append(data)
    # Преобразование списка во множество уберет повторяющиеся элементы
    data_set = set(data_list)

    assert len(data_list) == len(data_set)

    # Проверяем, что у всех питомцев разные имена
    name_list = []
    rows = WebDriverWait(pytest.driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH,
                                             '//div[@id="all_my_pets"]/table[@class="table table-hover"]/tbody/tr'))
    )
    for row in rows:
        cells = row.text.split()
        name_list.append(cells[0])
    # Преобразование списка во множество уберет повторяющиеся элементы
    name_set = set(name_list)

    assert len(name_list) == len(name_set)
