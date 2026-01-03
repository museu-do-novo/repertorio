"""
Módulo: cifra_transposer
Funções para:
 - analisar cifra (detectar acordes, TAB, letra)
 - transpor acordes
 - reconstruir texto final
 - função de alto nível para carregar e transpor arquivo

Pronto para importação no repertorio.py
"""

import re
from pathlib import Path
from pychord import Chord


# ---------------------------------------------------------
# Configurações e tabelas
# ---------------------------------------------------------

CHORD_REGEX = r"\b[A-G][A-Za-z0-9#b()\/]*\b"

# Conversão de bemóis → sustenidos
ENHARMONIC_SHARP = {
    "Db": "C#",
    "Eb": "D#",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#",
}


# ---------------------------------------------------------
# Funções utilitárias
# ---------------------------------------------------------

def acorde_para_sustenido(acorde: str) -> str:
    """Força grafia sustenido nos acordes já transpostos."""
    for bemol, sust in ENHARMONIC_SHARP.items():
        if acorde.startswith(bemol):
            acorde = acorde.replace(bemol, sust, 1)

    # baixo do acorde
    if "/" in acorde:
        base, baixo = acorde.split("/", 1)
        for bemol, sust in ENHARMONIC_SHARP.items():
            if baixo.startswith(bemol):
                baixo = baixo.replace(bemol, sust, 1)
                acorde = f"{base}/{baixo}"

    return acorde


def is_tab_line(linha: str) -> bool:
    """Detecta se a linha representa TAB de guitarra."""
    linha_strip = linha.strip()

    if re.match(r"^[EBGDAe]\|", linha_strip):
        return True

    if re.match(r"^[\-\d\|hHpPsSlrx~\\\/]+$", linha_strip):
        return True

    return False


# ---------------------------------------------------------
# Parser de cifra
# ---------------------------------------------------------

def parse_cifra(texto: str):
    """
    Analisa uma cifra em texto e retorna estrutura intermediária:
    [
        { "type": "tab", "content": "E|----" },
        { "type": "acordes", "acordes": [(col, "Am"), ...], "letra": "a letra..." }
    ]
    """
    linhas = texto.split("\n")
    estrutura = []

    i = 0
    while i < len(linhas):
        linha = linhas[i]

        # TAB
        if is_tab_line(linha):
            estrutura.append({
                "type": "tab",
                "content": linha
            })
            i += 1
            continue

        # Acordes
        acordes = []
        for match in re.finditer(CHORD_REGEX, linha):
            candidato = match.group(0)
            col = match.start()

            try:
                Chord(candidato)  # valida acorde
                acordes.append((col, candidato))
            except Exception:
                pass

        if acordes:
            letra = linhas[i+1] if i + 1 < len(linhas) else ""
            estrutura.append({
                "type": "acordes",
                "acordes": acordes,
                "letra": letra
            })
            i += 2
            continue

        i += 1

    return estrutura


# ---------------------------------------------------------
# Transposição
# ---------------------------------------------------------

def transpor_estrutura(estrutura, semitons: int):
    """Aplica transposição à estrutura analisada."""
    nova = []

    for bloco in estrutura:

        if bloco["type"] == "tab":
            nova.append(bloco)
            continue

        novos_acordes = []
        for col, acordestr in bloco["acordes"]:
            c = Chord(acordestr)
            c.transpose(semitons)
            acorde_str = acorde_para_sustenido(str(c))
            novos_acordes.append((col, acorde_str))

        nova.append({
            "type": "acordes",
            "acordes": novos_acordes,
            "letra": bloco["letra"]
        })

    return nova


# ---------------------------------------------------------
# Reconstrução
# ---------------------------------------------------------

def reconstruir(estrutura) -> str:
    """Gera texto final a partir da estrutura normalizada."""
    saida = []

    for bloco in estrutura:

        if bloco["type"] == "tab":
            saida.append(bloco["content"])
            continue

        if bloco["type"] == "acordes":
            largura = max(col + len(ac) for col, ac in bloco["acordes"]) + 1
            linha = [" "] * largura

            for col, acorde in bloco["acordes"]:
                for i, ch in enumerate(acorde):
                    linha[col + i] = ch

            saida.append("".join(linha))
            saida.append(bloco["letra"])

    return "\n".join(saida)


# ---------------------------------------------------------
# Função de alto nível (opcional, para facilitar integração)
# ---------------------------------------------------------

def carregar_e_transpor_cifra(caminho: Path, semitons: int) -> str:
    """
    Carrega uma cifra do disco, transpõe e devolve o texto final.
    Ideal para ser usado direto no repertorio.py.
    """
    texto = Path(caminho).read_text(encoding="utf8")
    estrutura = parse_cifra(texto)
    transposta = transpor_estrutura(estrutura, semitons)
    return reconstruir(transposta)
