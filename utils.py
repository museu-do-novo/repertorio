from pathlib import Path
import sys
import os
import re
import random


from colorama import Fore, Back, Style
import pyperclip
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def clear():
    """Clear the terminal screen (like 'clear')"""
    os.system('cls' if os.name == 'nt' else 'clear')
    # essa aqui spawna linhas ate ficar "em branco"
    # console.clear()

def message(message, color=Fore.WHITE, verbose=True) -> None:
    """
    Imprime uma mensagem com cores para melhor visualizacao.
    Args:
        message (str): A mensagem a ser impressa.
        color (str, optional): A cor da mensagem (padrao: branco).
        verbose (bool, optional): Se a mensagem deve ser impressa (padrao: False).

    Returns:
        None

    """
    print(f"{color}{message}{Style.RESET_ALL}")

def random_color(
    normal_color=True,
    bright_color=True,
    contrast_color=True,
    use_styles=True,
    special_combinations=True
) -> str:
    """
    Retorna uma cor aleatória customizável com base nos tipos de cores disponíveis no colorama.

    Args
        normal_color=(bool): Incluir cores normais (Fore.RED, Fore.GREEN, ...)
        bright_color= (bool): Incluir cores brilhantes (Fore.LIGHTRED_EX, ...)
        contrast_color=(bool): Incluir combinações de Fore + Back
        usar_estilos (bool): Incluir estilos com Style.BRIGHT
        usar_combinacoes_especiais (bool): Incluir misturas visuais únicas com Style + Back

    Returns:
        str: Sequência de estilo/colorama pronta para uso
    """
    cores = []

    if normal_color:
        cores.extend([
            Fore.BLACK, Fore.RED, Fore.GREEN, Fore.YELLOW,
            Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE
        ])

    if bright_color:
        cores.extend([
            Fore.LIGHTBLACK_EX, Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX,
            Fore.LIGHTYELLOW_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTMAGENTA_EX,
            Fore.LIGHTCYAN_EX, Fore.LIGHTWHITE_EX
        ])

    if contrast_color:
        cores.extend([
            Fore.RED + Back.CYAN,
            Fore.GREEN + Back.MAGENTA,
            Fore.YELLOW + Back.BLUE,
            Fore.BLUE + Back.YELLOW,
            Fore.MAGENTA + Back.GREEN,
            Fore.CYAN + Back.RED,
            Fore.WHITE + Back.BLACK
        ])

    if use_styles:
        cores.extend([
            Style.BRIGHT + Fore.RED,
            Style.BRIGHT + Fore.GREEN,
            Style.BRIGHT + Fore.YELLOW,
            Style.BRIGHT + Fore.BLUE,
            Style.BRIGHT + Fore.MAGENTA,
            Style.BRIGHT + Fore.CYAN
        ])

    if special_combinations:
        cores.extend([
            Style.BRIGHT + Fore.WHITE + Back.RED,
            Style.BRIGHT + Fore.YELLOW + Back.BLUE,
            Style.BRIGHT + Fore.CYAN + Back.MAGENTA
        ])

    if not cores:
        return Fore.WHITE  # fallback seguro

    return random.choice(cores)

# BANNER DE MILHOES
def banner(title: str, verbose: bool = True) -> None:
    """
    Mostra o banner colorido com a largura do terminal
    Args:
        title (str): Titulo do banner
        verbose (bool): Flag para habilitar ou desabilitar a impressao das mensagens
    Returns:
        None
    """
    try:
        term_width = os.get_terminal_size().columns
    except:
        term_width = 80  # Fallback width if terminal size can't be determined
    
    title = title.upper()
    title_length = len(title)
        
    # BANNER ELEMENTS
    random_elements = False

    symbols = ['✦', '✧', '✩', '✪', '✫', '✬', '✭', '✮', '✯', '★', '☆',
           '◆', '◇', '◈', '◉', '◎', '○', '●', '⬣', '⬢', '☯', '☀', '☁', '☂',
           '⚙', '⚔', '⚡', '❖', '✻', '✼', '✽']
        # Unicode ranges com símbolos gráficos
    ranges = [
        (0x2500, 0x257F),  # Box-drawing characters ─ ┼ ║ ╔ ╗ etc.
        (0x2580, 0x259F),  # Block elements ▀ ▄ █ ░ ▒ ▓
        (0x25A0, 0x25FF),  # Geometric shapes ■ ▲ ● ◆ etc.
    ]

    def random_symbol():
        start, end = random.choice(ranges)
        return chr(random.randint(start, end))
    
    def rand_or(char):
        # return chr(random.randint(32, 126)) if random_elements else char
        return random_symbol() if random_elements else char
    
    CORNER_CHAR  = rand_or('✻')
    TOP_BORDER_CHAR = rand_or('═')
    BOTTOM_BORDER_CHAR = TOP_BORDER_CHAR
    SIDE_CHAR = rand_or('║')
    PADDING_CHAR = rand_or(' ')

    # Calculate available space for title (subtracting corners and side chars)
    available_width = term_width - 4  # 2 corners + 2 side chars
    
    # Create the top and bottom borders
    top_border = CORNER_CHAR + TOP_BORDER_CHAR * (term_width - 2) + CORNER_CHAR
    bottom_border = CORNER_CHAR + BOTTOM_BORDER_CHAR * (term_width - 2) + CORNER_CHAR
    
    # Create title line with centered text
    if title_length > available_width:
        title = title[:available_width-3] + "..."
        title_length = len(title)
    
    padding_total = available_width - title_length
    left_padding = padding_total // 2
    right_padding = padding_total - left_padding
    # MODIFICADO: Formatação simétrica da linha do título
    title_line = f"{SIDE_CHAR}{PADDING_CHAR}{' ' * left_padding}{title}{' ' * right_padding}{PADDING_CHAR}{SIDE_CHAR}"

    
    # Create decorative lines above and below title
    decorative_line = SIDE_CHAR + '─' * (term_width - 2) + SIDE_CHAR
    
    # Print the banner with random colors
    color1 = random_color(
    bright_color=True,
    normal_color=True,
    contrast_color=False,
    use_styles=False,
    special_combinations=False
)
    color2 = random_color(
    bright_color=True,
    normal_color=True,
    contrast_color=False,
    use_styles=False,
    special_combinations=False
)
    color3 = random_color(
    bright_color=True,
    normal_color=True,
    contrast_color=False,
    use_styles=False,
    special_combinations=False
)
    
    message('\n' + top_border, color=color1, verbose=verbose)
    message(decorative_line, color=color2, verbose=verbose)
    message(title_line, color=color3, verbose=verbose)
    message(decorative_line, color=color2, verbose=verbose)
    message(bottom_border, color=color1, verbose=verbose)

# === Core shell utilities ===




















def cyber_print(msg: str, color: str = "magenta") -> None:
    console.print(f"[bold {color}]▌ {msg}[/bold {color}]")

def cyber_panel(msg: str, color: str = "cyan") -> None:
    console.print(Panel(Text(msg, justify="center", style=f"bold {color}"), border_style=color))

def read_clipboard() -> str | None:
    try:
        text = pyperclip.paste()
        return text.strip() if text else None
    except Exception:
        return None

# url validator (same as original)
def is_url(text: str) -> bool:
    if not text:
        return False
    pattern = re.compile(
        r"^(https?|ftp)://"
        r"([a-zA-Z0-9_-]+\.)+[a-zA-Z]{2,}"
        r"(:\d+)?"
        r"(/[^\s]*)?$",
        re.IGNORECASE,
    )
    return bool(pattern.match(text.strip()))
