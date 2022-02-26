import requests
import time
import json
from bs4 import BeautifulSoup
from random import randrange
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

hearders = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
}


def get_venuecard(url):
    s = requests.Session()
    response = s.get(url=url, headers=hearders)

    soup = BeautifulSoup(response.text, 'lxml')
    # with open('index.html', 'w' , encoding='utf-8') as file:
    #     file.write(response.text)
    block_url_list = []
    for page in range(1, 8):
        response = s.get(url=f'https://burgas.zavedenia.com/restaurant_9/{page}', headers=hearders)
        soup = BeautifulSoup(response.text, 'lxml')

        block_url = soup.find_all('a', class_='item-link-desktop ellipsis')
        for bu in block_url:
            bl_url = "https://burgas.zavedenia.com" + bu.get('href')
            block_url_list.append(bl_url)
        print(f'Обработал {page}')

        time.sleep(randrange(2, 5))
    with open('block_urls.txt', 'w', encoding='utf-8') as file:
        for url in block_url_list:
            file.write(f'{url}\n')
    return 'Работа по сбору ссылок выполнена'


def get_data(file_path):
    data_dict = []
    with open(file_path) as file:
        urls_list = [line.strip() for line in file.readlines()]
    s = requests.Session()
    for url in urls_list[:]:
        print(url)

        s = Service(r'C:\Users\belou\Desktop\Python\parc\chromedriver\chromedriver.exe')
        driver = webdriver.Chrome(service=s)
        driver.maximize_window()
        try:
            driver.get(url=url)
            title = driver.find_element(By.ID, "zavedenie-title").text
            logo = driver.find_element(By.CLASS_NAME, 'profile-logo').get_attribute("src")
            type = driver.find_element(By.CLASS_NAME, 'type').find_element(By.TAG_NAME, 'a').text
            rating, visits, votes_up, votes_down = driver.find_element(By.CLASS_NAME,
                                                                       'venue-rating-socials').find_element(
                By.CLASS_NAME, "rating-stats").text.replace("\n", " ").split(" ")

            try:
                cl = driver.find_elements(By.CLASS_NAME, 'info-text')[3].find_element(By.TAG_NAME, "a")
                cl.click()
            except Exception as er:
                pass

            info = driver.find_elements(By.CLASS_NAME, 'ellipsis')[:-1]
            count_of_seats = info[0].text
            price = info[1].text
            time_open = info[2].text
            if len(info) >= 4 and len(info[3].text) < 12:
                phone = info[3].text
            else:
                phone = "Номера нет"
            try:
                ck = driver.find_element(By.CLASS_NAME, 'profile-additional-info').find_element(By.TAG_NAME, 'a')
                ck.click()
                desc = driver.find_element(By.CLASS_NAME, 'profile-additional-info').find_element(By.TAG_NAME,
                                                                                                  'p').text[:-21]
            except Exception as er:
                pass
            desc = driver.find_element(By.CLASS_NAME, 'profile-additional-info').find_element(By.TAG_NAME,'p').text[:-21]
            try:
                information = driver.find_elements(By.CLASS_NAME, 'text-small')
                try:
                    suitable_for = information[0].text
                except:
                    suitable_for = None
                try:
                    music = information[1].text
                except:
                    music = None
                try:
                    type_of_institution = information[2].text
                except:
                    type_of_institution = None
                try:
                    kitchen = information[3].text
                except:
                    kitchen = None
                try:
                    more = information[4].text
                except:
                    more = None
            except Exception as er:
                pass

            data = {
                'url': url,
                'title': title,
                'logo': logo,
                'type': type,
                'rating': rating,
                'visits': visits,
                'votes_up': votes_up,
                'votes_down': votes_down,
                'count_of_seats': count_of_seats,
                'price': price,
                'time_open': time_open,
                'phone': phone,
                'desc': desc,
                'suitable_for': suitable_for,
                'music': music,
                'type_of_institution': type_of_institution,
                'kitchen': kitchen,
                'more': more,
            }

            data_dict.append(data)

            time.sleep(3)
        except Exception as _ex:
            print(_ex)
        finally:
            driver.close()
            driver.quit()

    with open('data.json', 'w', encoding='utf-8',) as json_file:
        json.dump(data_dict, json_file, indent=4, ensure_ascii=False)


def main():
    # print(get_venuecard(url='https://burgas.zavedenia.com/restaurant_9/'))
    get_data('block_urls.txt')


if __name__ == '__main__':
    main()
