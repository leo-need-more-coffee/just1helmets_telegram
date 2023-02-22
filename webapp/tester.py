import requests

resp = requests.post('http://localhost:8080/users/123/cart/products/0/count/15')
print(resp.json())

resp = requests.put('http://localhost:8080/users/123/cart/products/5/count/12')
print(resp.json())

resp = requests.get('http://localhost:8080/users/123/cart/products/')
print(resp.json())