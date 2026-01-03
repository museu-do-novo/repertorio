import requests
from bs4 import BeautifulSoup as bs
from pathlib import Path
from utils import cyber_panel
from config import PC_CHORDS_PATH

def soup(url: str, save: bool = False, show: bool = False):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except Exception as e:
        cyber_panel(f"❌ Erro ao acessar {url}: {e}", "red")
        return None
    s = bs(response.content, 'html.parser')
    if show:
        print(s.prettify())
    if save:
        with open("index.html", "w", encoding="utf8") as f:
            f.write(s.prettify())
    return s

def salvarcifra(content: str, path: Path):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        cyber_panel(f"❌ Erro ao salvar cifra: {e}", "red")

def pesquisa_artista(artista: str) -> list:
    artista_url = f"https://www.cifraclub.com.br/{artista.replace(' ', '-')}/"
    soupa = soup(artista_url)
    if soupa is None:
        return []
    soupa_list = soupa.find_all('ul', class_='list-links art_musics alf all artistMusics--allSongs')
    infos = []
    for listafaixassite in soupa_list:
        for a in listafaixassite.find_all('a', class_="art_music-link", href=True):
            infos.append({
                "title": a.get('title', a.text).strip(),
                "href": "https://www.cifraclub.com.br" + a['href']
            })
    return infos

def manipule_printer(artista_musica: str, openfile: bool = False, show: bool = False):
    artista_musica = artista_musica.strip("/")
    filename = artista_musica.replace("/", "-").replace(" ", "_").replace(":", "").replace("?", "")
    cifrafile = PC_CHORDS_PATH.joinpath(f"{filename}.txt")
    printer_url = f"https://www.cifraclub.com.br/{artista_musica}/imprimir.html"

    soupa = soup(printer_url)
    if soupa is None:
        cyber_panel("❌ Falha ao acessar a página da cifra.", "red")
        return

    cifra_tag = soupa.find("pre")
    if not cifra_tag:
        cyber_panel("❌ Não foi possível encontrar a cifra nessa página.", "red")
        return

    cifra = cifra_tag.get_text().strip()
    salvarcifra(content=cifra, path=cifrafile)

    if show:
        try:
            from utils import clear, sh  # sh is available via utils import hack
            clear()
        except Exception:
            pass
        print()
        print(cifra)

    cyber_panel(f"✅ Cifra salva em: {cifrafile}", "cyan")
    if openfile:
        try:
            os.system(f'nano "{cifrafile}"')
        except Exception:
            cyber_panel("⚠️ Não foi possível abrir o arquivo com nano.", "yellow")
