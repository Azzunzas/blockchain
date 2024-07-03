from flask import Flask, request, jsonify, redirect
import requests
import random
import threading
import time

app = Flask(__name__)

moedas_seletor = 0

chaves = {"chave1", "chave2", "chave3", "chave4", "chave5",
          "chave6", "chave7", "chave8", "chave9", "chave10",
          "chave11", "chave12", "chave13", "chave14", "chave15",
          "chave16", "chave17", "chave18", "chave19", "chave20"}

validadores = []
expulsos = {}

historico_transacoes = {}
selecoes_consecutivas = {}

nome_seletor = "Juliano_Guilherme_Juan"

def registrar_seletor():
    response = requests.post(f"http://localhost:5000/seletor/{nome_seletor}/127.0.0.1:5001")

    if response.status_code == 200:
        return jsonify("Seletor registrado com sucesso"), 200
    else:
        return jsonify("Erro ao registrar seletor"), 400

@app.route('/hora', methods=['GET'])
def sincronizar_horario():
    response = requests.get("http://localhost:5000/hora")
    if response.status_code == 200:
        horario = response.json()
        print(f"Hora sincronizada com o banco: {horario}")
        return jsonify(f"Hora sincronizada: {horario}"), 200
    else:
        print("Erro ao sincronizar com o banco")
        return jsonify("Hora não sincronizada"), 500

@app.route('/seletor/registrar_validador', methods=['POST'])
def registrar_validador():
    data = request.json
    if data['ip'] in expulsos and expulsos[data['ip']]['tentativas'] > 2:
        return jsonify({"message": "Validador não pode retornar à rede"}), 403

    validadores.append({
        'ip': data['ip'],
        'moedas': data['moedas'],
        'flag': data.get('flag', 0),
        'tentativas': expulsos.get(data['ip'], {}).get('tentativas', 0),
        # 'chave_unica': chaves[random.randint(0, 20)]
    })
    print(f"Validador registrado: {data['ip']}")
    return jsonify({"message": "Validador registrado com sucesso"}), 200

def solicitar_transacao():
    response = requests.get("http://localhost:5000/transacoes")
    if response.status_code == 200:
        transacoes = response.json()
        if transacoes:
            return random.choice(transacoes)
    return None

def processar_transacao(transacao):
    validadores_selecionados = selecionar_validadores()
    
    if validadores_selecionados == 0:
        return []
    elif validadores_selecionados == 1:
        return []

    pausa = 0
    if len(validadores_selecionados) < 3:
        pausa = 1
        print("Aguardando validadores disponíveis...")
    else:
        print(f"\nvalidadores selecionados: {validadores_selecionados}")
        
    antes = time.time()
    tempo = 0
    while pausa:
        tempo = int(time.time()) - int(antes)
        print(f'\rTempo decorrido (sec): {tempo}', end="", flush=True)

        validadores_selecionados = selecionar_validadores()

        if validadores_selecionados == 0:
            return []
        elif validadores_selecionados == 1:
            return []

        if len(validadores_selecionados) >= 3:
            print(f"\nvalidadores selecionados: {validadores_selecionados}")
            break
        
        if tempo >= 60:
            print("\nTempo de espera excedido, cancelando transação...")
            return []
        
    respostas = []
    for validador in validadores_selecionados:
        print(f"Enviando a transação para o validador: {validador['ip']}")
        response = requests.post(f"http://{validador['ip']}/validador/validar_transacao", json=transacao)

        if response.status_code == 200:
            respostas.append(response.json())
    
    resultado = processar_respostas(respostas)
    transacao_id = transacao['id']
    atualizar_status_transacao(transacao_id, resultado)
    atualizar_selecoes(validadores_selecionados)
    redistribuir_moedas(transacao, resultado, validadores_selecionados)

    print("Transação processada com sucesso")
    return jsonify("Transação processada com sucesso"), 200

def selecionar_validadores():
    if not validadores:
        print("Nenhum validador registrado")
        return 0

    validadores_filtrados = [v for v in validadores if selecoes_consecutivas.get(v['ip'], 0) < 5]
    
    if not validadores_filtrados:
        print("Validadores em hold")
        return 1

    validadores_selecionados = []
    while len(validadores_selecionados) < 3 and validadores_filtrados:
        for validador in validadores_filtrados:
            chance = calcular_chance(validador['moedas'], validador['flag'])

            if random.uniform(0, 1) < chance:
                validadores_selecionados.append(validador)
                if len(validadores_selecionados) >= 3:
                    break
        validadores_filtrados = [v for v in validadores_filtrados if v not in validadores_selecionados]

    return validadores_selecionados

def calcular_chance(moedas, flags):
    chance_base = (moedas // 50) * 0.02
    chance = max(0, chance_base)

    if flags == 1:
        chance *= 0.5
    elif flags == 2:
        chance *= 0.25

    return chance

def processar_respostas(respostas):
    status = [resp['status'] for resp in respostas]
    if status.count(1) > status.count(2):
        print(f"\n\n{status.count(1)} AI AI AI QUE DELÍCIA O VERÃO {status.count(2)}\n\n")
        return 1
    else:
        print(f"\n\n{status.count(1)} AI AI AI QUE DELÍCIA O VERÃO {status.count(2)}\n\n")
        return 2

def atualizar_status_transacao(transacao_id, status):
    requests.post(f"http://localhost:5000/transacoes/{transacao_id}/{status}")

def atualizar_selecoes(validadores_selecionados):
    for validador in validadores_selecionados:
        ip = validador['ip']
        if ip in selecoes_consecutivas:
            selecoes_consecutivas[ip] += 1
        else:
            selecoes_consecutivas[ip] = 1
    for validador in selecoes_consecutivas:
        if validador not in [v['ip'] for v in validadores_selecionados]:
            selecoes_consecutivas[validador] = max(0, selecoes_consecutivas[validador] - 1)

def redistribuir_moedas(transacao, resultado, validadores_selecionados):
    total_moedas = transacao['valor']
    seletor_moedas = total_moedas * 0.015
    validador_moedas = total_moedas * 0.005
    distribuicao = (total_moedas - seletor_moedas - validador_moedas) / len(validadores_selecionados)

    global moedas_seletor
    moedas_seletor += seletor_moedas
    print(f"Saldo do seletor após transação: {moedas_seletor}")

    for validador in validadores_selecionados:
        validador['moedas'] += distribuicao
        print(f"Moedas atualizadas do validador {validador['ip']}: {validador['moedas']}")

    for validador in validadores_selecionados:
        if validador['flag'] > 2:
            print(f"Validador expulso: {validador['ip']}")
            expulsar_validador(validador['ip'])
        elif resultado == 2:
            validador['flag'] += 1
            print(f"Validador {validador['ip']} recebeu uma flag, flags totais do validador: {validador['flag']}")
        else:
            validador['flag'] = max(0, validador['flag'] - 0.0001 * historico_transacoes.get(validador['ip'], 0))
            print(f"Validador {validador['ip']} recebeu uma flag, flags totais do validador: {validador['flag']}")

def expulsar_validador(ip):
    global validadores
    validadores = [v for v in validadores if v['ip'] != ip]
    if ip in expulsos:
        expulsos[ip]['tentativas'] += 1
    else:
        expulsos[ip] = {'tentativas': 1}

def seletor_automatico():
    while True:
        transacao = solicitar_transacao()
        if transacao:
            print("Transação adquirida")
            processar_transacao(transacao)
        if not transacao:
            print("Erro, transação vazia")
        time.sleep(5)

@app.route('/', methods=['GET'])
def iniciar_app():
    sincronizar_horario()
    registrar_seletor()
    seletor_automatico()
    return jsonify("Algo inesperado aconteceu"), 500

if __name__ == "__main__":
    app.run(port=5001, debug=False)



