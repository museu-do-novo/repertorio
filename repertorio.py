#!/home/nad/myenv/bin/python3
# -*- coding: utf-8 -*-
# pip install yt-dlp ppadb InquirerPy rich beautifulsoup4 pandas tqdm pyperclip pychord

from pathlib import Path
import time
from InquirerPy import inquirer
from rich.rule import Rule
from rich.table import Table
# from utils import clear, cyber_panel, cyber_print, banner, os, colorama, console
from utils import *
from downloader import interactive_download_flow
from cifraclub import manipule_printer, pesquisa_artista
from adb_sync import get_adb_client, list_devices, push_files_to_device, ensure_CELL_dirs
from transposer import carregar_e_transpor_cifra
from config import *
import pandas as pd




def ensure_PC_dirs():
    ok = True
    for p in PC_PATHS_TO_VERIFY:
        try:
            Path(p).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            cyber_panel(f"❌ Falha ao criar diretório {p}: {e}", "red")
            ok = False
    return ok

def show_repertory(csv_path: Path) -> None:
    """Mostra o repertório e permite adicionar/remover músicas via InquirerPy."""
    if not csv_path.exists():
        cyber_panel(f"⚠️ Arquivo CSV não encontrado: {csv_path}", "yellow")
        return

    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            cyber_panel("⚠️ O repertório está vazio.", "yellow")
        else:
            # ----- Tabela -----
            table = Table(
                title="[bold magenta]🎵 REPERTÓRIO ATUAL[/bold magenta]",
                show_lines=True,
                header_style="bold cyan",
                border_style="bright_magenta",
                title_style="bold bright_magenta",
                pad_edge=True,
                expand=True
            )
            for col in df.columns:
                table.add_column(col, style="bright_green", justify="center")
            for _, row in df.iterrows():
                values = [str(x).center(20) for x in row.values]
                table.add_row(*values)

            console.clear()
            try:
                banner(title="🎼 REPERTÓRIO 🎼")
            except Exception:
                pass
            console.print("\n")
            console.print(table, justify="center")
            console.print("\n")

    except Exception as e:
        cyber_panel(f"❌ Erro ao ler CSV: {e}", "red")
        return

    # ================================
    #  MENU DE EDIÇÃO DO CSV
    # ================================
    acao = inquirer.select(
        message="O que deseja fazer?",
        choices=[
            "➕ Adicionar música",
            "➖ Remover música",
            "⬅️ Voltar"
        ],
        pointer="👉 "
    ).execute()

    # --------------------------------
    # ADICIONAR MÚSICA
    # --------------------------------
    if acao == "➕ Adicionar música":
        autor = inquirer.text(message="Autor:").execute().strip()
        nome = inquirer.text(message="Nome da música:").execute().strip()
        tonalidade = inquirer.text(message="Tonalidade:").execute().strip()
        duracao = inquirer.text(message="Duração:").execute().strip()
        estilo = inquirer.text(message="Estilo:").execute().strip()

        nova_linha = {
            "autor": autor,
            "nome": nome,
            "tonalidade": tonalidade,
            "duracao": duracao,
            "estilo": estilo
        }

        try:
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
            else:
                df = pd.DataFrame([nova_linha])

            df.to_csv(csv_path, index=False, encoding="utf8")
            cyber_panel("✅ Música adicionada ao repertório!", "green")

        except Exception as e:
            cyber_panel(f"❌ Erro ao adicionar música: {e}", "red")
        return

    # --------------------------------
    # REMOVER MÚSICA
    # --------------------------------
    if acao == "➖ Remover música":
        df = pd.read_csv(csv_path)
        if df.empty:
            cyber_panel("⚠️ O repertório está vazio.", "yellow")
            return

        escolhas = [f"{row['autor']} - {row['nome']}" for _, row in df.iterrows()]
        escolhas.append("Cancelar")

        alvo = inquirer.select(
            message="Selecione a música para remover:",
            choices=escolhas,
            pointer="👉 "
        ).execute()

        if alvo == "Cancelar":
            cyber_panel("Operação cancelada.", "yellow")
            return

        autor, nome = alvo.split(" - ", 1)
        df = df[~((df["autor"] == autor) & (df["nome"] == nome))]

        try:
            df.to_csv(csv_path, index=False, encoding="utf8")
            cyber_panel("🗑️ Música removida!", "green")
        except Exception as e:
            cyber_panel(f"❌ Erro ao remover música: {e}", "red")

        return

    # --------------------------------
    # VOLTAR
    # --------------------------------
    if acao == "⬅️ Voltar":
        return

# Handlers restored from original
def handle_download_flow():
    result = interactive_download_flow(default_out_dir=PC_SONGS_PATH)
    if result:
        cyber_panel(f"✅ Download finalizado: {result.get('title')} -> {result.get('filepath')}", "green")
    else:
        cyber_panel("⚠️ Operação cancelada ou falhou.", "yellow")
    return True

def handle_cifraclub_flow():
    clear()
    cyber_panel("🎸 Cifra Club (busca interativa com fuzzy finder)", "cyan")

    entrada = inquirer.text(message="Digite artista ou artista/música:").execute().strip()
    if not entrada:
        cyber_panel("⚠️ Entrada vazia.", "yellow")
        return False

    if "/" in entrada:
        manipule_printer(entrada, show=True, openfile=False)
        return True

    cyber_print(f"🔎 Pesquisando músicas do artista '{entrada}'...", "magenta")
    musicas = pesquisa_artista(entrada)
    if not musicas:
        cyber_panel("❌ Nenhuma música encontrada para esse artista.", "red")
        return False

    opcoes = [f"{m['title']}  →  {m['href']}" for m in musicas]
    opcoes.append("Voltar")

    cyber_panel("🎶 Digite parte do nome da música para filtrar (fuzzy search ativo):", "cyan")
    escolha = inquirer.fuzzy(
        message="Selecione uma música:",
        choices=opcoes,
        multiselect=False,
        max_height="70%",
        instruction="Digite para filtrar | ↑↓ navega | Enter seleciona"
    ).execute()

    if not escolha or escolha == "Voltar":
        return False

    musica_escolhida = next((m for m in musicas if m["title"] in escolha), None)
    if not musica_escolhida:
        cyber_panel("❌ Erro ao processar seleção.", "red")
        return False

    urlpath = musica_escolhida["href"].replace("https://www.cifraclub.com.br/", "").strip("/")
    manipule_printer(urlpath, show=True, openfile=False)
    return True

def handle_adb_sync_flow():
    clear()
    cyber_panel("📱 Sincronizar com Android (ADB)", "magenta")

    client = get_adb_client()
    if client is None:
        cyber_panel("❌ Servidor ADB não encontrado. Certifique-se de que 'adb' está rodando.", "red")
        return

    # Detecta dispositivos
    devices = list_devices(client)
    if not devices:
        cyber_panel("⚠️ Nenhum dispositivo encontrado via ADB.", "yellow")
        if inquirer.confirm(message="Tentar reconectar?", default=False).execute():
            time.sleep(2)
            devices = list_devices(client)

    if not devices:
        cyber_panel("❌ Nenhum dispositivo conectado.", "red")
        return

    # Escolha de dispositivo
    if len(devices) == 1:
        device = devices[0]
        cyber_panel(f"📱 Dispositivo conectado: {device.get_serial_no()}", "green")
    else:
        serials = [d.get_serial_no() for d in devices]
        chosen = inquirer.select(message="Selecione o dispositivo:", choices=serials, qmark="⚙️  ").execute()
        device = next(d for d in devices if d.get_serial_no() == chosen)
        cyber_panel(f"📱 Dispositivo selecionado: {chosen}", "green")

    ensure_CELL_dirs(device)

    # ---------------------------------------------------------------------
    # 📦 COLETA DE ARQUIVOS (PC → celular)
    # ---------------------------------------------------------------------
    songs = sorted([p for p in PC_SONGS_PATH.glob("*.mp3")], key=lambda p: p.name)
    chords = sorted([p for p in PC_CHORDS_PATH.glob("*.txt")], key=lambda p: p.name)
    repertorio_exists = REPERTORY_CSV.exists()

    # ---------------------------------------------------------------------
    # 📊 TABELA ÚNICA — resumo TOTAL do que está disponível
    # ---------------------------------------------------------------------

    table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="bright_magenta",
    )

    table.add_column("Tipo", justify="left", style="bold yellow")
    table.add_column("Quantidade", justify="left", style="bold magenta")
    table.add_column("Diretório", justify="left", style="bright_green")

    table.add_row("🎧 MP3", str(len(songs)), str(PC_SONGS_PATH))
    table.add_row("📝 Cifras TXT", str(len(chords)), str(PC_CHORDS_PATH))
    table.add_row("📋 Repertório CSV", "1" if repertorio_exists else "0", str(REPERTORY_CSV.parent))

    console.clear()
    banner("SINCRONIZAÇÃO ADB — RESUMO")
    console.print(table, justify="center")
    console.print("\n")

    # Se nada existe → encerra
    if not songs and not chords and not repertorio_exists:
        cyber_panel("⚠️ Não há nada disponível para enviar ao dispositivo.", "yellow")
        return

    # ---------------------------------------------------------------------
    # 🔽 CHECKBOX ÚNICO PARA SELEÇÃO
    # ---------------------------------------------------------------------
    options = []
    if songs:
        options.append("Enviar MP3")
    if chords:
        options.append("Enviar cifras")
    if repertorio_exists:
        options.append("Enviar repertório CSV")

    cyber_panel("🔽 Escolha o que deseja enviar ao dispositivo:", "magenta")
    selected = inquirer.checkbox(
        message="Selecione os itens para sincronizar:",
        choices=options,
        instruction="Espaço seleciona | Enter confirma",
        max_height="100%",
        pointer="👉  "
    ).execute()

    if not selected:
        cyber_panel("⚠️ Nenhuma opção selecionada.", "yellow")
        return

    # ---------------------------------------------------------------------
    # 🚀 ENVIO DOS ARQUIVOS
    # ---------------------------------------------------------------------
    if "Enviar MP3" in selected:
        push_files_to_device(device, songs, str(CELL_SONGS_PATH), oque="Musicas")
        cyber_panel("✅ MP3 enviados com sucesso.", "green")

    if "Enviar cifras" in selected:
        push_files_to_device(device, chords, str(CELL_CHORDS_PATH), oque="Cifras")
        cyber_panel("✅ Cifras enviadas com sucesso.", "green")

    if "Enviar repertório CSV" in selected:
        push_files_to_device(device, REPERTORY_CSV, str(CELL_REPERTORY_CSV), oque="Repertorio")
        cyber_panel("✅ Repertório enviado com sucesso.", "green")

    cyber_panel("🌐 SINCRONIZAÇÃO COMPLETA.", "magenta")

def handle_open_music_flow():
    clear()
    cyber_panel("🎧 Abrir músicas (MPV)", "cyan")

    files = sorted([p for p in PC_SONGS_PATH.glob("*.mp3")], key=lambda p: p.name)
    if not files:
        cyber_panel("⚠️ Nenhum arquivo MP3 encontrado.", "yellow")
        return False

    choices = [f.name for f in files]
    cyber_panel("🎶 Selecione as músicas para tocar (pode selecionar várias):", "magenta")

    selected = inquirer.fuzzy(
        message="Escolha as músicas:",
        choices=choices,
        multiselect=True,
        max_height="70%",
        instruction="Digite para filtrar | Espaço seleciona | Enter confirma"
    ).execute()

    if not selected:
        cyber_panel("⚠️ Nenhuma música selecionada.", "yellow")
        return False

    cyber_panel(f"🎵 Reproduzindo {len(selected)} arquivo(s)...", "green")
    file_paths = [str(PC_SONGS_PATH.joinpath(f)) for f in selected]
    os.system(f"mpv --no-video --force-window=no {' '.join(f'\"{p}\"' for p in file_paths)}")
    return True

def handle_open_chords_flow():
    clear()
    cyber_panel("📝 Abrir cifras (Sublime Text)", "cyan")

    files = sorted([p for p in PC_CHORDS_PATH.glob("*.txt")], key=lambda p: p.name)
    if not files:
        cyber_panel("⚠️ Nenhum arquivo de cifra encontrado.", "yellow")
        return False

    choices = [f.name for f in files]
    cyber_panel("🎶 Selecione as cifras para abrir (pode selecionar várias):", "magenta")

    selected = inquirer.fuzzy(
        message="Escolha as cifras:",
        choices=choices,
        multiselect=True,
        max_height="70%",
        instruction="Digite para filtrar | Espaço seleciona | Enter confirma"
    ).execute()

    if not selected:
        cyber_panel("⚠️ Nenhuma cifra selecionada.", "yellow")
        return False

    cyber_panel(f"🪶 Abrindo {len(selected)} cifra(s)...", "green")
    file_paths = [str(PC_CHORDS_PATH.joinpath(f)) for f in selected]
    os.system(f"subl {' '.join(f'\"{p}\"' for p in file_paths)}")
    return True

def handle_transpose_flow():
    clear()
    cyber_panel("🎼 Transposição de Cifras", "cyan")

    files = sorted([p for p in PC_CHORDS_PATH.glob("*.txt")], key=lambda p: p.name)
    if not files:
        cyber_panel("⚠️ Nenhuma cifra .txt encontrada em PC_CHORDS_PATH", "yellow")
        return True

    choices = [f.name for f in files]
    escolha = inquirer.fuzzy(
        message="Selecione a cifra para transpor:",
        choices=choices,
        multiselect=False,
        max_height="70%",
        instruction="Digite para filtrar | ↑↓ navega | Enter seleciona"
    ).execute()

    if not escolha:
        cyber_panel("⚠️ Nenhuma cifra selecionada.", "yellow")
        return True

    caminho = PC_CHORDS_PATH / escolha

    semitons = int(inquirer.number(
        message="Quantos semitons deseja transpor? (negativo ou positivo)",
        float_allowed=False,
        min_allowed=-11,
        max_allowed=11,
        default=0
    ).execute())

    cyber_panel(f"🎵 Transpondo '{escolha}' em {semitons:+} semitons...", "magenta")
    try:
        resultado = carregar_e_transpor_cifra(caminho, semitons)
    except Exception as e:
        cyber_panel(f"❌ Erro ao transpor cifra: {e}", "red")
        return True

    clear()
    try:
        banner("CIFRA TRANPOSTA")
    except Exception:
        pass
    print()
    print(resultado)
    print()

    if inquirer.confirm(message="Deseja salvar a cifra transposta como novo arquivo?", default=True).execute():
        stem = caminho.stem
        novo_nome = f"{stem}{'+' if semitons >= 0 else ''}{semitons}.txt"
        novo_caminho = PC_CHORDS_PATH / novo_nome
        novo_caminho.write_text(resultado, encoding="utf8")
        cyber_panel(f"💾 Arquivo salvo como: {novo_nome}", "green")

    return True

def main():
    # Comecar a bagaceira
    ensure_PC_dirs()

    while True:
        # 🔹 Limpa a tela e exibe o banner a cada retorno ao menu
        console.clear()
        banner(title="MUSEU_DO_NOVO")
        console.print(Rule("[bold magenta]FERRAMENTAS DO REPERTÓRIO[/bold magenta]"))
        time.sleep(0.3)

        # 🔹 Menu principal
        choice = inquirer.select(
            message="Selecione uma opção:",
            choices=[
                "🎵 Baixar áudio (YouTube / URL)",
                "🎧 Abrir músicas (MPV)",
                "🎸 Buscar e salvar cifra (Cifra Club)",
                "🪶 Abrir cifras (Sublime Text)",
                "🎼 Transpor cifra (TXT)",
                "📋 Mostrar repertório (CSV)",
                "📱 Sincronizar com Android (ADB)",
                "🔧 Verificar / Criar diretórios locais",
                "❌ Sair"
            ],
            default="🎵 Baixar áudio (YouTube / URL)",
            pointer="👉  ",
            qmark="⚙️  "
        ).execute()

        # 🔹 Roteamento de opções ---------------------------------------------
        match choice:
            case "🎵 Baixar áudio (YouTube / URL)":
                handle_download_flow()

            case "🎧 Abrir músicas (MPV)":
                handle_open_music_flow()

            case "🎸 Buscar e salvar cifra (Cifra Club)":
                handle_cifraclub_flow()

            case "🪶 Abrir cifras (Sublime Text)":
                handle_open_chords_flow()

            case "🎼 Transpor cifra (TXT)":
                handle_transpose_flow()

            case "📋 Mostrar repertório (CSV)":
                console.clear()
                banner(title="REPERTÓRIO ATUAL")
                show_repertory(REPERTORY_CSV)

            case "📱 Sincronizar com Android (ADB)":
                handle_adb_sync_flow()

            case "🔧 Verificar / Criar diretórios locais":
                ok = ensure_PC_dirs()
                if ok:
                    cyber_panel("✅ Diretórios verificados/criados.", "green")
                else:
                    cyber_panel("❌ Falha ao verificar/criar diretórios.", "red")

            case "❌ Sair":
                cyber_panel("👋 Encerrando ferramenta. Até mais!", "yellow")
                break

            case _:
                cyber_panel("⚠️ Opção desconhecida.", "red")

        # 🔹 Pausa breve e confirmação antes de voltar ao menu
        time.sleep(0.4)
        if not inquirer.confirm(message="Voltar ao menu principal?", default=True).execute():
            cyber_panel("👋 Encerrando ferramenta. Até mais!", "yellow")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        try:
            banner(title="ENCERRADO PELO USUÁRIO")
        except Exception:
            pass
