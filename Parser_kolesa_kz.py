import requests as rq
import ast
from bs4 import BeautifulSoup
import csv
import telebot
import os
import unidecode

PORT = int(os.environ.get('PORT', 5000))
HEADER = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36','accept':'*/*'}#making sure that website will not take us for bot
FILE='cars.csv'

def my_html(url, params=None):
    r = rq.get(url,headers=HEADER,params=params)
    return r
def parse_content(html):
    soup = BeautifulSoup(html,'html.parser')
    div = soup.find_all('div',class_="row vw-item list-item a-elem")
    #div_link = soup.find_all()
    print(len(div))
    cars = []
    for i in range(len(div)):
        try:
            cars.append({
                'link':div[i].find('a',class_="list-link ddl_product_link").get('href'),
                'make':ast.literal_eval(div[i].attrs['data-ga-params'])['dimension15'],
                'model':ast.literal_eval(div[i].attrs['data-ga-params'])['dimension16'],
                'price':ast.literal_eval(div[i].attrs['data-ga-params'])['dimension17'],
                'year':ast.literal_eval(div[i].attrs['data-ga-params'])['metric18'],
                'region':ast.literal_eval(div[i].attrs['data-ga-params'])['dimension13'],
                'city':ast.literal_eval(div[i].attrs['data-ga-params'])['dimension12']
            })
        except KeyError:
            cars.append({
                'link':div[i].find('a',class_="list-link ddl_product_link").get('href'),
                #'make':div[i].find('a',class_="list-link ddl_product_link").get_text(),
                #'model':div[i].find('a',class_="list-link ddl_product_link").get_text(),
                'price':div[i].find('span',class_="price").get_text("|", strip=True),
                #'year':div[i].find('a',class_="list-link ddl_product_link").get_text(),
                #'region':div[i].find('a',class_="list-link ddl_product_link").get_text(),
                #'city':div[i].find('a',class_="list-link ddl_product_link").get_text()
            })
        except:
            continue
    for i in cars:
        if (type(i['price']) is str):
            i['price']=(i['price'].replace("|₸",""))
            i['price'] = unidecode.unidecode(i['price'])
            i['price']=(i['price'].replace(" ",""))
            int(i['price'])
    return cars


def save_file_and_compare(items,path1,path2,chatid):
    with open(path1,mode='w') as file1:
        writer=csv.writer(file,dialect='excel',delimiter=',')
        writer.writerow(['make','model','price','year','region','city'])
        for item in items:
            writer.writerow([item['make'],item['model'],item['price'],item['year'],item['region'],item['city']])
            if(lowest_price1>item['price']):
                lowest_price1=item

    with open(path2,mode='r') as file2:
        reader=csv.DictReader(file2)
        for row in reader:
            if(lowest_price2>row['price']):
                lowest_price2=row
    if(lowest_price1['price']<lowest_price2['price']):
        bot.send_message(chatid,"I found a new car: "+"https://kolesa.kz"+lowest_price1['url'])

def parsing(URL,chatid):
    html = my_html(URL)
    if html.status_code ==200: #it means that we successfully reached page
        cars = parse_content(html.text)
        save_file(cars,FILE)
        bot.send_message(chatid,"Done!")
    else:
        bot.send_message(chatid,"Error")

TOKEN ='1672802092:AAE1F97xVEUrJjSCYoev5RukbVMnpCFmQNg'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def f_start(message):
    bot.reply_to(message,'Hello, I am a parsing bot! If this is your first time enter /help')

@bot.message_handler(commands=['help'])
def f_help(message):
    bot.reply_to(message,'This bot is parsing kolesa.kz website. To start type /url')

@bot.message_handler(commands=['url'])
def f_url(message):
    bot.reply_to(message,'send url of the page:')
    @bot.message_handler(func=lambda message:True)
    def run_function(message):
        url=(message).text
        chatid = message.chat.id
        parsing(url,chatid)
        
updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
updater.bot.setWebhook('https://enigmatic-peak-19607.herokuapp.com/' + TOKEN)