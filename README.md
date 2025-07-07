# Transcritor de Oitivas

O Transcritor de Oitivas é uma aplicação desktop desenvolvida em Python com PyQt6, voltada para a transcrição automática de arquivos de áudio ou vídeo utilizados em procedimentos formais como declarações, depoimentos e interrogatórios. A ferramenta visa automatizar e simplificar o processo de transcrição, oferecendo recursos de personalização, controle de desempenho e integração com modelos de inteligência artificial.

## Funcionalidades

- Interface gráfica simples e funcional desenvolvida com PyQt6
- Suporte à transcrição de arquivos de áudio e vídeo (MP3, WAV, MP4, MKV, entre outros)
- Integração com os modelos Whisper (OpenAI) nas versões small, medium e large
- Suporte ao uso de CPU ou GPU para processamento (com detecção automática via WMI e NVML)
- Estimativa dinâmica de tempo de transcrição com base em histórico real (aprendizado incremental)
- Barra de progresso adaptativa baseada na duração do áudio
- Copia automática da transcrição formatada com informações do procedimento e prompt específico
- Editor integrado de prompts JSON, com suporte aos tipos: declaração, depoimento e interrogatório
- Conversão automática de mídia para WAV utilizando FFmpeg
- Armazenamento de dados históricos em JSON para otimização futura de tempo

## Requisitos

- Python 3.10 ou superior
- FFmpeg instalado e presente no PATH do sistema
- PyTorch com suporte a GPU (opcional, para acelerar a transcrição)
- Drivers de CUDA e GPU compatíveis (se for utilizar aceleração via GPU)
- Dependências listadas no arquivo `requirements.txt` (não incluído neste repositório)

## Bibliotecas principais utilizadas

- PyQt6
- OpenAI Whisper
- Torch
- py3nvml
- pyperclip
- wmi
- subprocess / os / json

## Estrutura do sistema

- `app.py`: Interface principal e orquestração das funcionalidades
- `transcritor.py`: Thread de transcrição assíncrona e conversão de arquivos
- `estimador.py`: Módulo de estimativa de tempo com base em histórico de uso
- `prompt.py`: Editor visual de prompts
- `popup.py`: Sistema de notificações e mensagens estilizadas
- `functions.py`: Funções utilitárias (seletor de arquivos, clipboard)
- `debug.py`: Verificador de presença do FFmpeg
- `prompts/`: Contém os arquivos JSON com os templates de prompt por tipo de procedimento
- `transcript_data.json`: Histórico de transcrições realizadas, utilizado para predição de tempo

## Uso

1. Execute o arquivo `app.py`
2. Selecione um arquivo de áudio ou vídeo compatível
3. Escolha o modelo Whisper (Rápido, Moderado ou Preciso)
4. Selecione o dispositivo de execução (CPU ou GPU)
5. Informe o nome da parte ouvida e o tipo de procedimento
6. Inicie a transcrição
7. O resultado será exibido na interface e poderá ser copiado com o prompt correspondente

## Observações

- O sistema faz uso intensivo de recursos de processamento e pode demandar tempo em máquinas com desempenho limitado.
- Todos os prompts podem ser editados diretamente pela interface gráfica.
