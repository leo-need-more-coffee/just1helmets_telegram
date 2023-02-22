from bs4 import BeautifulSoup
import requests
import db

headers = {
    'User-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582'
}

resp = requests.get('https://just1helmets.ru/helmets_for_kids', headers=headers)
html = resp.text
soup = BeautifulSoup(html, 'html.parser')
#print(soup.prettify())
a=[]
for el in soup.find_all('div', class_='t-item')[:-1]:
    name=el.find('div', class_='t-name').text.replace('\n', '')
    description=el.find('div', class_='t-descr').text
    price=int(el.find('div', class_='js-product-price').text.replace(' ', ''))
    image=el.find('div', class_='t-bgimg').get('data-original')
    a.append({"name": name, "description": description, "price": price, 'image': image})
    print(name, description, price)


for i, el in enumerate(soup.find_all('div', class_='t-descr')[13:19:2]):
    a[i]['full_description'] = el.text
    print(i, el.text+'\n\n')

for el in a:
    db.Product.add(el['name'], el['full_description'], el['image'], el['price'], 2, ["YL"])