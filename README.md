# Video Transcription + PT-BR Translation Pipeline

Pipeline local em **Python 3.10+** para:
1. Receber vídeo (`.mp4`, `.mov`, `.avi`)
2. Extrair áudio com `ffmpeg`
3. Transcrever com Whisper (`faster-whisper`)
4. Traduzir opcionalmente EN → PT-BR (modelo local `Helsinki-NLP/opus-mt-en-pt`)
5. Salvar saída em `.txt` e `.srt` com timestamps

## Estrutura sugerida

```text
Video-transcription-and-PT-BR-translation-pipeline/
├── main.py
├── requirements.txt
├── pipeline/
│   ├── __init__.py
│   ├── logging_config.py
│   └── video_pipeline.py
└── README.md
```

## Bibliotecas utilizadas

- [ffmpeg](https://ffmpeg.org/) (binário instalado no sistema)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [PyTorch](https://pytorch.org/) (detecção de GPU)
- [transformers](https://github.com/huggingface/transformers) + `sentencepiece`
- [tqdm](https://github.com/tqdm/tqdm)

## Instalação

> Requisito: `ffmpeg` disponível no PATH (`ffmpeg -version`).

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Execução passo a passo

### 1) Transcrição + tradução (recomendado)

```bash
python main.py \
  --input-file ./samples/meeting.mp4 \
  --output-dir ./outputs \
  --mode transcribe_translate \
  --model-size medium \
  --device auto
```

### 2) Apenas transcrição

```bash
python main.py \
  --input-file ./samples/meeting.mp4 \
  --output-dir ./outputs \
  --mode transcribe
```

### 3) Processamento em lote

```bash
python main.py \
  --input-dir ./samples \
  --output-dir ./outputs \
  --mode transcribe_translate
```

## Exemplo de input/output

### Input
- `samples/meeting.mp4`

### Output (`outputs/`)
- `meeting.wav` (áudio extraído)
- `meeting.txt` (texto puro)
- `meeting.srt` (legenda sincronizada)

Exemplo de trecho `.srt`:

```srt
1
00:00:00,000 --> 00:00:03,100
Olá, pessoal. Obrigado por participarem da reunião.

2
00:00:03,100 --> 00:00:05,700
Hoje vamos revisar os resultados do trimestre.
```

## Tratamento de erros cobertos

- Arquivo de entrada inexistente
- Extensão inválida
- Falha no `ffmpeg` / ausência de trilha de áudio
- Falha ao carregar modelo local
- Nenhuma fala detectada

## Melhorias futuras (opcional)

- Exportar também JSON com metadados por segmento
- Diarização de speaker (`pyannote.audio`)
- Pós-processamento de pontuação/capitalização com LLM local
- Interface Web simples (Streamlit)

