from aiohttp import ClientSession
from asyncio import gather, run, create_task
from bs4 import BeautifulSoup
import csv
from json import dump

news = []

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Alt-Used': 'visit-russia.ru'
}

url = 'https://visit-russia.ru'


def write_csv(items: list, page, one_file=False):
    if one_file is not True:
        with open(f'./r/{int(page / 20)}.csv', 'w', newline='') as csv_f:
            writer = csv.writer(csv_f)
            writer.writerow((
                'Имя',
                'Ссылка',
                'Изображение',
                'Дата публикации',
                'Время публикации',
                'Описание'
            ))
        for item in items:
            with open(f'./r/{int(page / 20)}.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow((
                    item['name'],
                    item['link'],
                    item['image'],
                    item['published']['date'],
                    item['published']['time'],
                    item['description']
                ))
    else:
        for item in items:
            with open(f'./result.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow((
                    item['name'],
                    item['link'],
                    item['image'],
                    item['published']['date'],
                    item['published']['time'],
                    item['description']
                ))


async def get_news(session, page):
    async with session.get(url=f'{url}/ru/novosti.html?start={page}', headers=headers) as resp:
        try:
            soup = BeautifulSoup(await resp.text(), 'lxml')
            items_leading = soup.find_all(name='article')
            for item in items_leading:
                news_item = {}
                try:
                    news_item['name'] = BeautifulSoup(str(item), 'lxml').find(name='h2').text.strip()
                except Exception as ex:
                    news_item['name'] = 'Имя не найдено'
                    print(ex, page)

                try:
                    news_item['link'] = f"{url}{BeautifulSoup(str(item), 'lxml').find('a')['href']}"
                except Exception as ex:
                    news_item['link'] = 'Ссылка на новость не найдена'
                    print(ex, page)

                try:
                    news_item['published'] = {
                        'date': BeautifulSoup(str(item), 'lxml').find(name='dd', class_='published').text.strip().split(
                            ' ')[1],
                        'time': BeautifulSoup(str(item), 'lxml').find(name='dd', class_='published').text.strip().split(
                            ' ')[2]
                    }
                except Exception as ex:
                    news_item['published'] = {'date': 'Дата не найдена', 'time': 'Время не найдено'}
                    print(ex, page)

                try:
                    news_item['image'] = f"{url}{BeautifulSoup(str(item), 'lxml').find(name='img')['src']}"
                except Exception as ex:
                    news_item['image'] = f"Изображение не найдено"
                    print(ex, page)

                try:
                    news_item['description'] = BeautifulSoup(str(item), 'lxml').find(name='p',
                                                                                     class_='readmore').previous_sibling.strip() + "..."
                except Exception as ex:
                    news_item['description'] = 'Описание не найдено'
                    print(ex, page)

                news.append(news_item)
        except Exception as ex:
            print(ex, page)
    write_csv(news, page, True)


async def get_gather_data():
    async with ClientSession() as session:
        tasks = []
        async with session.get(url=f'{url}/ru/novosti.html', headers=headers) as response:
            pagination = int(
                BeautifulSoup(await response.text(), 'lxml').find(name='p', class_='counter').text.split(' ')[
                    -1].strip())
            for page in range(0, pagination * 20, 20):
                task = create_task(get_news(session, page))
                tasks.append(task)
        await gather(*tasks)


def main():
    with open(f'./result.csv', 'w', newline='') as csv_f:
        writer = csv.writer(csv_f)
        writer.writerow((
            'Имя',
            'Ссылка',
            'Изображение',
            'Дата публикации',
            'Время публикации',
            'Описание'
        ))
    run(get_gather_data())


if __name__ == '__main__':
    main()
