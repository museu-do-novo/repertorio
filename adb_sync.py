import os
from pathlib import Path
from tqdm import tqdm
from ppadb.client import Client as AdbClient
from config import CELL_SONGS_PATH, CELL_CHORDS_PATH, CELL_REPERTORY_CSV, PC_SONGS_PATH, PC_CHORDS_PATH, REPERTORY_CSV, ADB_HOST, ADB_PORT
from utils import cyber_panel
import shutil

def get_adb_client(host: str = ADB_HOST, port: int = ADB_PORT) -> AdbClient | None:
    try:
        client = AdbClient(host=host, port=port)
        _ = client.version()
        return client
    except Exception as e:
        cyber_panel(f"⚠️ Não foi possível conectar ao servidor ADB: {e}", "yellow")
        return None

def list_devices(client: AdbClient) -> list:
    try:
        return client.devices()
    except Exception as e:
        cyber_panel(f"⚠️ Erro ao listar dispositivos ADB: {e}", "yellow")
        return []

def ensure_CELL_dirs(device) -> bool:
    """
    Cria os diretórios no /sdcard usando comandos compatíveis com Android.
    (mkdir -p não funciona em /sdcard)
    """
    try:
        for p in [CELL_SONGS_PATH, CELL_CHORDS_PATH]:
            device.shell(f"mkdir '{p}'")           # Tenta criar diretório
            device.shell(f"mkdir '{p}' 2>/dev/null")  # Ignora erros de 'File exists'
        return True
    except Exception as e:
        cyber_panel(f"⚠️ Falha ao criar diretórios no dispositivo: {e}", "yellow")
        return False

def push_files_to_device(device, local_files: list[Path], remote_dir: str, oque: str) -> None:
    """Envia arquivos para Android com barra de progresso (tqdm)."""
    try:
        device.shell(f"mkdir -p '{remote_dir}'")
    except Exception as e:
        cyber_panel(f"⚠️ Falha ao criar diretório remoto: {e}", "yellow")

    if isinstance(local_files, (Path, str)):
        local_files = [Path(local_files)]

    with tqdm(total=len(local_files), desc=f"📤 Enviando {oque}", ncols=shutil.get_terminal_size().columns, colour="magenta", bar_format="{desc:<12} {percentage:3.0f}% |{bar}|") as pbar:
        for p in local_files:
            try:
                device.push(str(p), f"{remote_dir}/{p.name}")
            except Exception as e:
                cyber_panel(f"Erro ao enviar {p.name}: {e}", "red")
            finally:
                pbar.update(1)

def sync_android_flow():
    cyber_panel("📱 Sincronizar com Android (ADB)", "magenta")
    client = get_adb_client()
    if client is None:
        cyber_panel("❌ Servidor ADB não encontrado. Certifique-se de que 'adb' está rodando.", "red")
        return

    devices = list_devices(client)
    if not devices:
        cyber_panel("⚠️ Nenhum dispositivo encontrado via ADB.", "yellow")
        return

    device = devices[0] if len(devices) == 1 else None
    if device is None:
        choices = [d.get_serial_no() for d in devices]
        # interactive selection moved to caller to keep module pure; return device list
        return devices

    cyber_panel(f"📱 Dispositivo conectado: {device.get_serial_no()}", "green")

    ensure_CELL_dirs(device)

    songs = sorted([p for p in PC_SONGS_PATH.glob("*.mp3")], key=lambda p: p.name)
    if songs:
        if True:
            push_files_to_device(device, songs, str(CELL_SONGS_PATH))
            cyber_panel("✅ Upload de áudio concluído.", "green")
    else:
        cyber_panel(f"⚠️ Não há arquivos MP3 em {PC_SONGS_PATH}", "yellow")

    chords = sorted([p for p in PC_CHORDS_PATH.glob("*.txt")], key=lambda p: p.name)
    if chords:
        if True:
            push_files_to_device(device, chords, str(CELL_CHORDS_PATH))
            cyber_panel("✅ Upload de cifras concluído.", "green")
    else:
        cyber_panel(f"⚠️ Não há arquivos de cifras em {PC_CHORDS_PATH}", "yellow")

    if REPERTORY_CSV.exists():
        push_files_to_device(device, [REPERTORY_CSV], str(CELL_REPERTORY_CSV))
        cyber_panel("✅ Repertório enviado.", "green")
    else:
        cyber_panel(f"⚠️ Arquivo de repertório não encontrado: {REPERTORY_CSV}", "yellow")

    cyber_panel("🌐 SINCRONIZAÇÃO COMPLETA.", "magenta")
