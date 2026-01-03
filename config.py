from pathlib import Path

MAIN_WORK_FOLDER = Path(__file__).parent.resolve()

PC_SONGS_PATH = MAIN_WORK_FOLDER.joinpath("musicas/")
PC_CHORDS_PATH = MAIN_WORK_FOLDER.joinpath("cifras/")
REPERTORY_CSV = MAIN_WORK_FOLDER.joinpath("repertorio.csv")

CELL_BACKUP_PATH = Path("/sdcard/Music/repertorio/")
CELL_SONGS_PATH = CELL_BACKUP_PATH.joinpath("musicas/")
CELL_CHORDS_PATH = CELL_BACKUP_PATH.joinpath("cifras/")
CELL_REPERTORY_CSV = CELL_BACKUP_PATH.joinpath("repertorio.csv")

PC_PATHS_TO_VERIFY = [MAIN_WORK_FOLDER, PC_SONGS_PATH, PC_CHORDS_PATH]
CELL_PATHS_TO_VERIFY = [CELL_BACKUP_PATH, CELL_SONGS_PATH, CELL_CHORDS_PATH]

# yt_dlp / ADB defaults
YTDLP_FORMAT = "bestaudio/best"
YTDLP_EXT = "mp3"
YTDLP_QUALITY = "192"

ADB_HOST = "127.0.0.1"
ADB_PORT = 5037
