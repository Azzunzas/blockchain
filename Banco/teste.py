import requests

#Criando clientes
# response = requests.post('http://localhost:5000/cliente/1/juliano/1234/500')
# response = requests.post('http://localhost:5000/cliente/2/guilherme/1234/500')
# response = requests.post('http://localhost:5000/cliente/claytin/1234/500')

#mostrar cliente
# response = requests.get('http://localhost:5000/cliente/15')

#Editando clientes
# response = requests.post('http://localhost:5000/juliano/2/300')
# response = requests.post('http://localhost:5000/guilherme/1/300')
# response = requests.delete('http://localhost:5000/cliente/1')

#Criando seletores
# response = requests.post('http://localhost:5000/seletor/seletor2/122.122')

#mostrar seletores criados
# response = requests.get('http://localhost:5000/seletor')

#Editando seletores
# response = requests.post('http://localhost:5000/seletor/1/seletorB/111111')
# response = requests.post('http://localhost:5000/seletor/2/seletorA/222222')
# response = requests.delete('http://localhost:5000/seletor/2')

# criar trasacao
# response = requests.post('http://localhost:5000/transacoes/1/2/50')
response = requests.get('http://localhost:5000/cliente')

# response = requests.post('http://localhost:5260/validador/validar_transacao')


print(response.text)