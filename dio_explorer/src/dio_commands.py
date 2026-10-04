"""
dio_commands.py
---------------
Core logic for the DIO Explorer skill commands:
  /trilha   — searches and returns study tracks by technology keyword
  /desafio  — generates a coding challenge for a given technology and level
  /certificado — generates a completion certificate for a student
"""

import json
import os
import re
import random
import datetime

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

DATA_FILE = os.path.join(
    os.path.dirname(__file__), "..", "data", "trilhas_dio.json"
)


def load_trilhas(filepath: str = DATA_FILE) -> dict:
    """Load the trilhas_dio.json data file and return the parsed dict."""
    with open(filepath, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# /trilha command
# ---------------------------------------------------------------------------

def buscar_trilha(tecnologia: str, data: dict) -> list:
    """
    Search trilhas by technology keyword (case-insensitive partial match).

    Returns a list of matching trilha dicts. Returns an empty list when no
    match is found.
    """
    if not tecnologia or not isinstance(tecnologia, str):
        return []

    keyword = tecnologia.strip().lower()
    return [
        t for t in data.get("trilhas", [])
        if keyword in t.get("tecnologia", "").lower()
        or keyword in t.get("nome", "").lower()
    ]


def formatar_trilha(trilha: dict) -> str:
    """Format a single trilha dict as a Markdown study plan string."""
    vitalicio = "Sim" if trilha.get("vitalicio") else "Não"

    badges = "\n".join(
        f"- {b}" for b in trilha.get("badges_disponiveis", [])
    )

    lives = trilha.get("lives_ao_vivo", [])
    if lives:
        lives_str = "\n".join(
            f"- {l['titulo']} — {l['data']} às {l['horario']}"
            for l in lives
        )
    else:
        lives_str = "Nenhuma live agendada no momento."

    promo = trilha.get("promocoes", {})
    if promo.get("desconto_percentual", 0) and promo.get("cupom"):
        promo_str = (
            f"{promo['desconto_percentual']}% de desconto | "
            f"Cupom: {promo['cupom']} | Válido até: {promo.get('validade', 'N/A')}"
        )
    else:
        promo_str = "Sem promoção ativa no momento."

    return (
        f"## 📚 Plano de Estudos — {trilha['nome']}\n"
        f"Tecnologia: {trilha['tecnologia']}\n"
        f"Nível: {trilha['nivel']}\n"
        f"Módulos: {trilha['numero_de_modulos']}\n"
        f"XP Total: {trilha['xp_total']} XP\n"
        f"Vitalício: {vitalicio}\n\n"
        f"### Badges Disponíveis\n{badges}\n\n"
        f"### Lives ao Vivo\n{lives_str}\n\n"
        f"### Promoção Ativa\n{promo_str}"
    )


def comando_trilha(tecnologia: str, filepath: str = DATA_FILE) -> str:
    """Entry point for /trilha command. Returns formatted Markdown or error."""
    data = load_trilhas(filepath)
    results = buscar_trilha(tecnologia, data)

    if not results:
        available = [t["tecnologia"] for t in data.get("trilhas", [])]
        return (
            f"Nenhuma trilha encontrada para '{tecnologia}'.\n"
            f"Tecnologias disponíveis: {', '.join(available)}"
        )

    return "\n\n---\n\n".join(formatar_trilha(t) for t in results)


# ---------------------------------------------------------------------------
# /desafio command
# ---------------------------------------------------------------------------

LEVELS = ["Iniciante", "Intermediário", "Avançado"]

CHALLENGES = {
    "Iniciante": [
        ("Soma de Pares", "Dado um array de inteiros, retorne a soma de todos os números pares.", "Array de inteiros", "Soma dos pares"),
        ("FizzBuzz", "Imprima de 1 a N: 'Fizz' se divisível por 3, 'Buzz' por 5, 'FizzBuzz' por ambos.", "Número N", "'1 2 Fizz 4 Buzz ...'"),
    ],
    "Intermediário": [
        ("Anagram Checker", "Verifique se duas strings são anagramas uma da outra.", "Duas strings", "True ou False"),
        ("Binary Search", "Implemente busca binária em um array ordenado.", "Array + alvo", "Índice ou -1"),
    ],
    "Avançado": [
        ("LRU Cache", "Implemente um LRU Cache com O(1) para get e put.", "Capacidade + operações", "Valores do cache"),
        ("Design Pattern Factory", "Implemente o padrão Factory para criar objetos de veículos.", "Tipo de veículo", "Objeto instanciado"),
    ],
}


def gerar_desafio(tecnologia: str, nivel: str, data: dict, seed: int = None) -> dict:
    """
    Generate a coding challenge dict for the given technology and level.

    Returns a dict with keys: tecnologia, nivel, numero, titulo, enunciado,
    entrada, saida, dica, xp, badge.
    """
    if nivel not in LEVELS:
        raise ValueError(f"Nível inválido: '{nivel}'. Use: {', '.join(LEVELS)}")

    # Find matching track for badge/XP flavor
    matches = buscar_trilha(tecnologia, data)
    if matches:
        trilha = matches[0]
        badge = trilha["badges_disponiveis"][0] if trilha["badges_disponiveis"] else "Explorer Badge"
        xp = trilha["xp_total"] // trilha["numero_de_modulos"]
    else:
        badge = "Explorer Badge"
        xp = 500

    rng = random.Random(seed)
    numero = rng.randint(100, 999)
    pool = CHALLENGES.get(nivel, CHALLENGES["Iniciante"])
    titulo, enunciado, entrada, saida = rng.choice(pool)

    return {
        "tecnologia": tecnologia,
        "nivel": nivel,
        "numero": numero,
        "titulo": titulo,
        "enunciado": enunciado,
        "entrada": entrada,
        "saida": saida,
        "dica": f"Pesquise sobre estruturas de dados em {tecnologia}.",
        "xp": xp,
        "badge": badge,
    }


def formatar_desafio(d: dict) -> str:
    """Format a challenge dict as a Markdown string."""
    return (
        f"## ⚔️ Desafio de Código DIO\n\n"
        f"**Tecnologia:** {d['tecnologia']}\n"
        f"**Nível:** {d['nivel']}\n"
        f"**Desafio #{d['numero']}**\n\n"
        f"### {d['titulo']}\n\n"
        f"**Enunciado:** {d['enunciado']}\n\n"
        f"**Entrada:** {d['entrada']}\n\n"
        f"**Saída:** {d['saida']}\n\n"
        f"**Dica:** {d['dica']}\n\n"
        f"**Recompensa:** {d['xp']} XP | Badge: {d['badge']}"
    )


def comando_desafio(tecnologia: str, nivel: str, filepath: str = DATA_FILE) -> str:
    """Entry point for /desafio command. Returns formatted Markdown or error."""
    data = load_trilhas(filepath)
    try:
        desafio = gerar_desafio(tecnologia, nivel, data)
    except ValueError as exc:
        return str(exc)
    return formatar_desafio(desafio)


# ---------------------------------------------------------------------------
# /certificado command
# ---------------------------------------------------------------------------

def gerar_certificado_id(date_str: str = None) -> str:
    """Generate a certificate ID like DIO-YYYY-MM-DD-XXXXXX."""
    if date_str is None:
        date_str = datetime.date.today().strftime("%Y-%m-%d")
    suffix = format(random.randint(0, 0xFFFFFF), "06X")
    return f"DIO-{date_str}-{suffix}"


def gerar_certificado(nome_aluno: str, tecnologia: str, data: dict) -> dict:
    """
    Generate a certificate dict for a student.

    Returns a dict with all fields needed to render the certificate.
    """
    if not nome_aluno or not nome_aluno.strip():
        raise ValueError("Nome do aluno não pode ser vazio.")

    matches = buscar_trilha(tecnologia, data)
    if matches:
        trilha = matches[0]
    else:
        trilha = {
            "nome": tecnologia,
            "tecnologia": tecnologia,
            "nivel": "N/A",
            "numero_de_modulos": 0,
            "xp_total": 0,
            "badges_disponiveis": [],
        }

    today = datetime.date.today().strftime("%d/%m/%Y")
    cert_id = gerar_certificado_id()

    return {
        "nome_aluno": nome_aluno.strip().upper(),
        "trilha_nome": trilha["nome"],
        "tecnologia": trilha["tecnologia"],
        "nivel": trilha["nivel"],
        "modulos": trilha["numero_de_modulos"],
        "xp": trilha["xp_total"],
        "badges": trilha.get("badges_disponiveis", []),
        "data_conclusao": today,
        "cert_id": cert_id,
    }


def formatar_certificado(c: dict) -> str:
    """Format a certificate dict as a Markdown certificate string."""
    badges_str = "\n".join(f"**🏆 {b}**" for b in c["badges"]) or "Nenhum badge registrado."
    return (
        f"# 🎓 CERTIFICADO DE CONCLUSÃO\n\n"
        f"## Digital Innovation One — DIO\n\n"
        f"### Este certificado é concedido a\n\n"
        f"# {c['nome_aluno']}\n\n"
        f"### pela conclusão com êxito da trilha\n\n"
        f"## 📚 {c['trilha_nome']}\n\n"
        f"| Campo | Detalhe |\n"
        f"|---|---|\n"
        f"| Tecnologia | {c['tecnologia']} |\n"
        f"| Nível | {c['nivel']} |\n"
        f"| Módulos Concluídos | {c['modulos']} |\n"
        f"| XP Conquistado | {c['xp']} XP |\n"
        f"| Data de Conclusão | {c['data_conclusao']} |\n\n"
        f"### 🏅 Badges Conquistadas\n\n{badges_str}\n\n"
        f"**🆔 Certificado Nº:** `{c['cert_id']}`\n"
        f"**✅ Válido em:** dio.me"
    )


def comando_certificado(nome_aluno: str, tecnologia: str, filepath: str = DATA_FILE) -> str:
    """Entry point for /certificado command. Returns formatted Markdown or error."""
    data = load_trilhas(filepath)
    try:
        cert = gerar_certificado(nome_aluno, tecnologia, data)
    except ValueError as exc:
        return str(exc)
    return formatar_certificado(cert)
