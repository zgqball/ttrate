from sanic.response import json
from database import Database
from bs4 import BeautifulSoup
import requests
import datetime
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from async_proxy_pool.webapi import redis_conn

def get_proxy():
    res = []
    for proxy in redis_conn.get_proxies(1):
        if proxy[:5] == "https":
            return {"https": proxy}
        else:
            return {"http": proxy}
    # new_proxy = redis_conn.get_proxies(1)
    # return new_proxy

def get_data():
    currency_types = ['AED', 'AUD', 'BDT', 'BHD', 'BND', 'BRL', 'CAD', 'CHF', 'CNH', 'CNY', 'CZK', 'DKK', 'EGP', 'EUR',
                      'FJD', 'GBP', 'HUF', 'IDR', 'ILS', 'INR', 'JOD', 'JPY', 'KRW', 'KWD', 'LKR', 'MOP', 'MUR', 'MXN',
                      'MYR', 'NOK', 'NZD', 'OMR', 'PGK', 'PHP', 'PLN', 'QAR', 'RUB', 'SAR', 'SEK', 'SGD', 'THB', 'TRY',
                      'TWD', 'USD', 'VND', 'ZAR']
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        # 'Cookie': 'lang=zh_hk; gpref2=h%3D; tid=fS5vKCdPSZHlXTqs; _ga=GA1.2.1204350767.1545110192; _gid=GA1.2.1226676016.1545110192; __AF=0; pref2=b%3D0%26c%3DNZD%26s%3D3%26t%3D3%26f%3D0%26sd%3D0%26m%3D0%26sort_col%3D%26sort_asc%3D0; bank_locks=; menu_state=0; __atuvc=56%7C51; __atuvs=5c1882b06ae72c8c037',
        'Host': 'hk.ttrate.com',
        'Referer': 'https://hk.ttrate.com/zh_hk/?c=NZD',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
    }
    db = Database()
    db.connect()
    url = 'https://hk.ttrate.com/zh_hk/?c='
    way_dict = {1: 'web_buy', 2: 'web_sell', 3: 'cash_buy', 4: 'cash_sell'}

    start_time = datetime.datetime.now()
    for currency in currency_types:
        # print('working with {}!!!!!!!!'.format(currency))
        # time.sleep(1)
        request_url = url + currency
        proxy = get_proxy()
        response = requests.get(request_url,proxies = proxy , headers=header)
        soup = BeautifulSoup(response.text, 'lxml')
        #need to change ip

        if soup.find('title').text[:4] == '使用驗證':
            proxy = get_proxy()
            response = requests.get(request_url, proxies = proxy , headers=header )
            soup = BeautifulSoup(response.text, 'lxml')
        #no rate
        if soup.find('div', class_='rate_table_no_data'):
            continue
        #get dataing
        else:
            content_and_update_time = soup.find_all('div', class_='rate_table_scale')
            content = content_and_update_time[0].text.strip()
            update_time = content_and_update_time[1].text.strip()[3:-4]
            rate_table = soup.find_all('tbody')[0]
            print(update_time)
            for row in rate_table.find_all('tr'):
                table_info = row.find_all('td')
                bank_name = table_info[0].text.strip()
                bank_url = table_info[0].find('a').attrs['href']
                bank_id = table_info[0].find('a').attrs['data-bank-id']
                temp_record = {'bank_name': bank_name,
                               'bank_url': bank_url,
                               'bank_id': bank_id,
                               'update_time': update_time,
                               'content': content,
                               'from_currency': currency,
                               'to_currency': 'HKD',
                               }
                for i in range(1, 5):
                    if table_info[i].find('a'):
                        temp_record.update({way_dict[i]: float(table_info[i].text.strip())})
                db.insert_dict(temp_record, 'raw_currency_rate')
    end_time = datetime.datetime.now()
    print(end_time - start_time)
    db.close()


if __name__ == '__main__':
    # get_data()
    sched = BlockingScheduler()
    sched.add_job(get_data, 'interval', seconds=180)
    sched.start()
