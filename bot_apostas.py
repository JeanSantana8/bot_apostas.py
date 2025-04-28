import requests
import schedule
import time
from datetime import datetime, timedelta

# CONFIGURAÇÕES
API_FOOTBALL_KEY = '9c6d42f50bb845999771638ed706f05a'
THE_ODDS_API_KEY = 'c9cf4957cd5b008fd435a4834277ca84'
TELEGRAM_BOT_TOKEN = '7862517380:AAHBhIbsJcTdU7iVGu6fxJZGWbpEx3LSZIw'
TELEGRAM_CHAT_ID = '1019103476'

# Ligas alvo (IDs conforme API-Football)
LEAGUE_IDS = {
    'Bundesliga 1': 78,
    'Bundesliga 2': 79,
    'Ligue 1': 61,
    'Serie A': 135,
    'La Liga': 140,
    'Premier League': 39,
    'Brasileirão Série A': 71,
    'Brasileirão Série B': 72,
}

# Função para enviar mensagem ao Telegram
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"Erro ao enviar mensagem: {response.text}")
    else:
        print(f"Mensagem enviada com sucesso!")

# Buscar jogos programados nas ligas
def buscar_jogos():
    hoje = datetime.now().strftime('%Y-%m-%d')
    jogos_filtrados = []

    for liga_nome, liga_id in LEAGUE_IDS.items():
        url = f"https://v3.football.api-sports.io/fixtures?league={liga_id}&season=2024&date={hoje}"
        headers = {
            'x-apisports-key': API_FOOTBALL_KEY
        }
        print(f"Buscando jogos para a liga {liga_nome} (ID: {liga_id})")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('response'):
                for jogo in data['response']:
                    jogos_filtrados.append({
                        'liga': liga_nome,
                        'time_casa': jogo['teams']['home']['name'],
                        'time_fora': jogo['teams']['away']['name'],
                        'horario': jogo['fixture']['date'],
                        'id_jogo': jogo['fixture']['id']
                    })
            else:
                print(f"Nenhum jogo encontrado para a liga {liga_nome} hoje.")
        else:
            print(f"Erro ao buscar jogos para a liga {liga_nome}: {response.status_code}")

    return jogos_filtrados

# Função principal para montar análise
def analisar_e_enviar():
    try:
        print("Iniciando análise de jogos...")
        jogos = buscar_jogos()

        if not jogos:
            send_telegram("⛔ Nenhum jogo qualificado para hoje.")
            return

        mensagens = []

        for jogo in jogos:
            hora_jogo = datetime.strptime(jogo['horario'], "%Y-%m-%dT%H:%M:%S%z") - timedelta(hours=3)  # Ajuste Brasil
            hora_formatada = hora_jogo.strftime('%H:%M')

            texto = f"🏟️ <b>{jogo['liga']}</b>\n"
            texto += f"🕔 {hora_formatada}h\n"
            texto += f"{jogo['time_casa']} x {jogo['time_fora']}\n"

            # Aqui vamos aplicar as análises:
            texto += "✅ Over 1.5 Gols\n"
            texto += "✅ Handicap Asiático (-0.5 favorito)\n"
            texto += "✅ Over 0.5 HT\n"
            texto += "✅ Escanteios Asiáticos (+8.5)\n"
            texto += "──────────────\n"

            mensagens.append(texto)

        mensagem_final = "\n".join(mensagens)
        send_telegram(mensagem_final)

    except Exception as e:
        send_telegram(f"⛔ Erro no bot: {e}")
        print(f"Erro no bot: {e}")

# Executa já na primeira vez (imediato)
analisar_e_enviar()

# Depois agenda para rodar às 5h da manhã
schedule.every().day.at("05:00").do(analisar_e_enviar)

# Loop para agendamento
while True:
    schedule.run_pending()
    time.sleep(60)
