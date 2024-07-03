from flask import Flask, request, jsonify
import random
import time
import requests

app = Flask(__name__)

historico_transacoes = {}

port = random.randint(5002, 6002)

def sincronizar_horario():
    response = requests.get("http://localhost:5001/hora")
    if response.status_code == 200:
        print("Horário sincronizado com o seletor")
        horario = response.json()
        return horario
    else:
        print("Erro ao sincronizar com o seletor")
        return None

def registrar_validador():
    porta = input("Qual a porta iniciada? ")
    moedas = random.randint(50, 1000)
    data = {
        'ip': f'localhost:{porta}',
        'moedas': moedas,
        'flag': 0
    }
    response = requests.post("http://localhost:5001/seletor/registrar_validador", json=data)
    if response.status_code == 200:
        return jsonify(f"Validador registrado com sucesso no seletor. Porta: {porta}", f"Status code: {response.status_code}"), 200
    else:
        return jsonify(f"Falha ao registrar validador no seletor. Status code: {response.status_code}"), 500

@app.route('/validador/validar_transacao', methods=['POST'])
def validar_transacao():
    print("Validando transação......")

    transacao = request.json
    print(f"Transação adquirida: {transacao}")

    remetente = transacao['remetente']
    print(f"Remetente: {remetente}")

    valor = transacao['valor']
    print(f"Valor da transação: {valor}")

    # if verificar_saldo(remetente, valor) and verificar_horario(transacao) and verificar_limite_transacoes(remetente):
    # if verificar_saldo(remetente, valor) and verificar_limite_transacoes(remetente):
    if verificar_saldo(remetente, valor):
        registrar_transacao(remetente, transacao['horario'])
        print("Transação aprovada")
        return jsonify({"status": 1}), 200
    else:
        print("Transação não aprovada")
        return jsonify({"status": 2}), 200

def verificar_saldo(remetente, valor):
    response = requests.get(f"http://localhost:5000/cliente/{remetente}")

    if response.status_code == 200:
        cliente = response.json()
        print(f"Cliente: {cliente}")

        if cliente == None:
            print("Cliente não existe")
            return False

        saldo_remetente = cliente['qtdMoeda']
        taxas = valor * 0.015
        return saldo_remetente >= valor + taxas
    return False

def verificar_horario(transacao):
    horario_atual = sincronizar_horario()

    if horario_atual is None:
        return False
    
    horario_transacao = transacao['horario']
    ultimo_horario = historico_transacoes.get(transacao['remetente'], [0])[-1]
    print(f"Horário da transação: {horario_transacao}\nÚltimo horário registrado: {ultimo_horario}")

    if horario_transacao > ultimo_horario:
        print("True")

    if horario_transacao < ultimo_horario:
        print("False")

    return horario_transacao <= horario_atual and horario_transacao > ultimo_horario

def verificar_limite_transacoes(remetente):
    agora = sincronizar_horario()
    transacoes_recentes = [t for t in historico_transacoes.get(remetente, []) if agora - t < 60]
    return len(transacoes_recentes) <= 100

def registrar_transacao(remetente, horario):
    if remetente not in historico_transacoes:
        historico_transacoes[remetente] = []

    historico_transacoes[remetente].append(horario)

    return jsonify("horário da transação registrada com sucesso"), 200

@app.route('/')
def iniciar_validador():
    registrar_validador()
    return jsonify("Validador iniciado"), 200

if __name__ == "__main__":
    app.run(port=port, debug=True)    




