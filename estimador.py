import os
import json
import statistics

data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcript_data.json")

# 🔥 Mapeamento inteligente entre os modelos personalizados e os suportados pelo Whisper
MODELOS_WHISPER = {
    "preciso": "large",
    "moderado": "medium",
    "rápido": "small"
}

MODELOS_REVERSO = {v: k for k, v in MODELOS_WHISPER.items()}

def carregar_dados():
    """Carrega os dados do JSON ou retorna um dicionário vazio se o arquivo não existir."""
    if not os.path.exists(data_file):
        salvar_dados({})  # Cria o arquivo vazio se não existir
    
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def salvar_dados(data):
    """Salva os dados no JSON."""
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def registrar_transcricao(modelo, dispositivo, duracao_audio):
    """Registra uma nova transcrição no JSON, aguardando o tempo real depois."""
    data = carregar_dados()
    modelo = MODELOS_REVERSO.get(modelo, modelo)  # Converte para nome personalizado
    
    if modelo not in data:
        data[modelo] = {"GPU": [], "CPU": []}
    
    data[modelo][dispositivo].append({
        "audio_duracao": round(duracao_audio, 2),  # 🔥 Arredondando para evitar problemas de precisão
        "tempo_real": None  # Ainda não sabemos o tempo real
    })
    
    # Limita a 10 registros mais recentes por modelo e dispositivo
    data[modelo][dispositivo] = data[modelo][dispositivo][-10:]
    
    salvar_dados(data)

def atualizar_tempo_real(modelo, dispositivo, duracao_audio, tempo_real):
    """Atualiza o tempo real de uma transcrição no JSON."""
    data = carregar_dados()
    modelo = MODELOS_REVERSO.get(modelo, modelo)  # Converte para nome personalizado
    
    print(f"🔍 Tentando atualizar tempo real: modelo={modelo}, dispositivo={dispositivo}, duracao_audio={duracao_audio}, tempo_real={tempo_real}")
    
    atualizado = False  # Flag para saber se algum valor foi atualizado

    if modelo in data and dispositivo in data[modelo]:
        for item in data[modelo][dispositivo]:
            print(f"🧐 Comparando: JSON_duracao={item['audio_duracao']} VS Novo_duracao={round(duracao_audio, 2)}")
            
            # 🔥 Comparação aproximada para evitar erro de precisão
            if abs(item["audio_duracao"] - round(duracao_audio, 2)) < 0.1 and item["tempo_real"] is None:
                print(f"✅ Correspondência encontrada! Atualizando tempo_real para {tempo_real} segundos.")
                item["tempo_real"] = tempo_real
                atualizado = True
                break
        else:
            print("⚠️ Nenhuma correspondência exata foi encontrada. O tempo real não foi salvo.")
    else:
        print(f"⚠️ Modelo ({modelo}) ou dispositivo ({dispositivo}) não encontrado no JSON.")
    
    # 🔥 Se foi atualizado, salvar os dados e imprimir o JSON atualizado
    if atualizado:
        print(f"📝 JSON atualizado antes de salvar: {json.dumps(data, indent=4, ensure_ascii=False)}")
        salvar_dados(data)
        print("💾 JSON salvo com sucesso!")

def estimar_tempo(modelo, dispositivo, duracao_audio):
    """Estima o tempo de transcrição com base nos registros anteriores, arredondando e adicionando 15% de margem."""
    data = carregar_dados()
    modelo = MODELOS_REVERSO.get(modelo, modelo)  # Converte para nome personalizado
    
    if modelo not in data or dispositivo not in data[modelo]:
        return None  # Sem dados suficientes
    
    tempos_anteriores = [item["tempo_real"] / item["audio_duracao"] for item in data[modelo][dispositivo] if item["tempo_real"]]
    
    if not tempos_anteriores:
        return None  # Nenhuma transcrição completa ainda
    
    # 🔥 Removendo outliers se houver mais de 5 registros
    tempos_anteriores.sort()
    if len(tempos_anteriores) > 5:
        tempos_anteriores = tempos_anteriores[1:-1]  # Remove o maior e o menor valor
    
    # 🔥 Média ponderada para dar mais peso aos registros mais recentes
    pesos = [i+1 for i in range(len(tempos_anteriores))]
    fator_medio = sum(t * p for t, p in zip(tempos_anteriores, pesos)) / sum(pesos)
    
    # Calcula o tempo estimado, arredonda e adiciona 15% de margem
    tempo_estimado = fator_medio * duracao_audio
    tempo_com_margem = round(tempo_estimado * 1.15)
    
    return tempo_com_margem
