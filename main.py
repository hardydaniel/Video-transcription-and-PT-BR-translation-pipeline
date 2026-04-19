from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from pipeline.logging_config import setup_logger

LOGGER = logging.getLogger(__name__)
SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pipeline local para transcrição e tradução EN->PT-BR de vídeos."
    )
    parser.add_argument("--input-file", type=Path, help="Caminho de um arquivo de vídeo")
    parser.add_argument(
        "--input-dir",
        type=Path,
        help="Diretório contendo vídeos (.mp4, .mov, .avi) para processamento em lote",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Diretório de saída para .wav, .txt e .srt",
    )
    parser.add_argument(
        "--mode",
        choices=["transcribe", "transcribe_translate"],
        default="transcribe_translate",
        help="transcribe = só transcrição, transcribe_translate = transcrição + tradução PT-BR",
    )
    parser.add_argument("--model-size", default="medium", help="tiny/base/small/medium/large-v3")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument(
        "--assume-language",
        default=None,
        help="Força idioma de entrada (ex.: en). Se omitido, detecta automaticamente.",
    )
    parser.add_argument("--beam-size", type=int, default=5)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def collect_videos(input_file: Path | None, input_dir: Path | None) -> list[Path]:
    if input_file and input_dir:
        raise ValueError("Use apenas --input-file OU --input-dir, não ambos.")
    if not input_file and not input_dir:
        raise ValueError("Informe --input-file ou --input-dir.")

    if input_file:
        return [input_file]

    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Diretório inválido: {input_dir}")

    videos = [
        p
        for p in sorted(input_dir.iterdir())
        if p.is_file() and p.suffix.lower() in SUPPORTED_VIDEO_EXTENSIONS
    ]
    if not videos:
        raise FileNotFoundError(
            f"Nenhum vídeo encontrado em {input_dir} com extensões {sorted(SUPPORTED_VIDEO_EXTENSIONS)}"
        )
    return videos


def main() -> int:
    args = parse_args()
    setup_logger(verbose=args.verbose)

    try:
        from pipeline.video_pipeline import PipelineConfig, VideoPipeline
    except Exception as exc:
        LOGGER.error("Dependências não disponíveis. Instale requirements.txt. Detalhe: %s", exc)
        return 1

    try:
        videos = collect_videos(args.input_file, args.input_dir)
    except Exception as exc:
        LOGGER.error("Erro de validação de entrada: %s", exc)
        return 1

    config = PipelineConfig(
        model_size=args.model_size,
        device=args.device,
        task=args.mode,
        assume_language=args.assume_language,
        beam_size=args.beam_size,
    )

    try:
        pipeline = VideoPipeline(config)
    except Exception as exc:
        LOGGER.error("Falha ao inicializar pipeline/modelo: %s", exc)
        return 1

    failures = 0
    for video in videos:
        try:
            LOGGER.info("Processando vídeo: %s", video)
            result = pipeline.process_video(video, args.output_dir)
            LOGGER.info(
                "Sucesso | segmentos=%s | idioma=%s | txt=%s | srt=%s",
                result["segments"],
                result["detected_language"],
                result["txt"],
                result["srt"],
            )
        except Exception as exc:
            failures += 1
            LOGGER.error("Falha ao processar %s: %s", video, exc)

    if failures:
        LOGGER.error("Processamento concluído com %s falha(s).", failures)
        return 1

    LOGGER.info("Processamento concluído com sucesso para %s vídeo(s).", len(videos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
