from pathlib import Path
import re
import unicodedata
from typing import List, Dict, Optional
import logging

import yt_dlp
from InquirerPy import inquirer
# from rich.console import Console
# from rich.panel import Panel
# from transposer import *
from utils import cyber_panel, cyber_print, read_clipboard, is_url, clear, console
from config import PC_SONGS_PATH, YTDLP_FORMAT, YTDLP_EXT, YTDLP_QUALITY


# console = Console()
logging.basicConfig(level=logging.INFO)

# URL regex
URL_RE = re.compile(
    r"^(https?|ftp)://"
    r"([a-zA-Z0-9_-]+\.)+[a-zA-Z]{2,}"
    r"(:\d+)?"
    r"(/[^\s]*)?$",
    re.IGNORECASE,
)

def safe_filename(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r'[\\/:"*?<>|]+', "", s)
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    return s

def yt_search_list(query: str, max_results: int = 10) -> List[Dict]:
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
        "nocheckcertificate": True,
    }
    search_query = f"ytsearch{max_results}:{query}"
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
    except Exception as e:
        cyber_panel(f"❌ Erro na busca do YouTube: {e}", "red")
        return []
    entries = info.get("entries", []) if isinstance(info, dict) else []
    results = []
    for e in entries:
        vid_id = e.get("id")
        results.append({
            "title": e.get("title", "Sem título"),
            "url": f"https://www.youtube.com/watch?v={vid_id}" if vid_id else e.get("url"),
            "duration": e.get("duration"),
            "channel": e.get("uploader") or e.get("channel"),
        })
    return results

def download_audio_from_url(
    url: str,
    out_dir: Path = PC_SONGS_PATH,
    filename_template: str = "%(title)s.%(ext)s",
    silent: bool = False
) -> Optional[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": YTDLP_FORMAT,
        "outtmpl": str(out_dir / filename_template),
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": YTDLP_EXT, "preferredquality": YTDLP_QUALITY}
        ],
        "noplaylist": True,
        "quiet": silent,
        "no_warnings": silent,
        "nopart": True,
        "progress_hooks": [],
    }
    try:
        cyber_panel(f"Iniciando download: {url}", "magenta")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title") if isinstance(info, dict) else None
            if not title and isinstance(info, dict) and "entries" in info and info["entries"]:
                entry = info["entries"][0]
                title = entry.get("title", "audio")
            if not title:
                title = "audio"
            filename = safe_filename(title) + ".mp3"
            output_file = out_dir / filename
            # sometimes yt_dlp saved different name; try to find candidate
            if not output_file.exists():
                candidates = list(out_dir.glob(f"{safe_filename(title)}*.mp3"))
                if candidates:
                    output_file = candidates[0]
            cyber_panel(f"✅ Arquivo salvo: {output_file}", "green")
            return output_file
    except Exception as e:
        cyber_panel(f"❌ Erro no download: {e}", "red")
        logging.exception(e)
        return None

def interactive_download_flow(default_out_dir: Path = PC_SONGS_PATH) -> Optional[Dict]:
    """
    Fluxo completo:
    - tenta ler clipboard automaticamente
    - permite colar manualmente
    - permite pesquisar no YouTube e escolher (fuzzy)
    Retorna dict {title, filepath, url} ou None
    """
    clear()
    cyber_panel("🎵 Baixar Áudio", "magenta")

    clip = read_clipboard()
    if clip and is_url(clip):
        cyber_print(f"📎 Link detectado na área de transferência: {clip}", "cyan")
        do_download = inquirer.confirm(message="Deseja baixar esse link agora?", default=True).execute()
        if do_download:
            fp = download_audio_from_url(clip, default_out_dir, silent=False)
            return {"title": fp.stem if fp else None, "filepath": fp, "url": clip} if fp else None
        else:
            cyber_print("🟡 Download cancelado pelo usuário.", "yellow")

    action = inquirer.select(
        message="Escolha como deseja proceder:",
        choices=[
            "Colar URL manualmente",
            "Pesquisar no YouTube (escolher vídeo)",
            "Voltar"
        ]
    ).execute()

    if action == "Colar URL manualmente":
        manual = inquirer.text(message="Cole a URL:").execute().strip()
        if not is_url(manual):
            cyber_panel("❌ URL inválida.", "red")
            return None
        fp = download_audio_from_url(manual, default_out_dir, silent=False)
        return {"title": fp.stem if fp else None, "filepath": fp, "url": manual} if fp else None

    elif action == "Pesquisar no YouTube (escolher vídeo)":
        query = inquirer.text(message="Termo de busca no YouTube:").execute().strip()
        if not query:
            cyber_panel("❌ Termo de busca vazio.", "red")
            return None

        cyber_panel("🔎 Buscando vídeos no YouTube...", "magenta")
        results = yt_search_list(query)
        if not results:
            cyber_panel("❌ Nenhum vídeo encontrado.", "red")
            return None

        choices = [f"{r['title']}  |  {r['channel']}  ({r['duration']}s)" for r in results]
        choices.append("Voltar")

        escolha = inquirer.fuzzy(
            message="Selecione o vídeo para baixar:",
            choices=choices,
            max_height="70%",
            multiselect=False,
        ).execute()

        if escolha == "Voltar" or not escolha:
            return None

        index = choices.index(escolha)
        url = results[index]["url"]

        cyber_panel(f"🎵 Baixando: {results[index]['title']}", "green")
        fp = download_audio_from_url(url, default_out_dir, silent=False)
        return {"title": results[index]["title"], "filepath": fp, "url": url} if fp else None

    else:
        return None
