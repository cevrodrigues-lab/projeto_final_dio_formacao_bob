---
name: desafio
description: Use when the user types /desafio to generate a random coding challenge based on a chosen level and technology.
metadata:
  argument-hint: "[tecnologia] [nível]"
---

# Desafio de Código DIO

When this skill is invoked, follow these steps exactly:

## Step 1 — Collect parameters

Check whether the user provided arguments after `/desafio`.

- **Technology**: look for a technology name in the arguments (e.g. `Python`, `Java`, `React`).
- **Level**: look for one of the three levels: `Iniciante`, `Intermediário`, or `Avançado`.

If either parameter is missing, use `ask_followup_question` to ask the user before continuing.

## Step 2 — Read the tracks file to align with available technologies

Use `read_file` on `projeto_final_dio_formacao_bob/dio_explorer/data/trilhas_dio.json` and check whether the chosen technology exists in the file. If it doesn't exist as an exact match, find the closest match or list available technologies and ask the user to confirm. Use the matching track's name and badges for flavor in the challenge output.

## Step 3 — Generate a random coding challenge

Using your knowledge of the chosen technology and level, generate **one** coding challenge that fits the following structure. Randomise the challenge theme each invocation so the user gets a different challenge every time they call `/desafio`.

Render the challenge with this exact Markdown structure:

```
---
## ⚔️ Desafio de Código DIO

**🖥️ Tecnologia:** {tecnologia}
**📊 Nível:** {nivel}
**🎲 Desafio #{random 3-digit number}**

---

### 📋 Enunciado

{A clear, self-contained problem description of 3–6 sentences appropriate for the level.
 Iniciante  → basic syntax / logic (loops, conditions, functions)
 Intermediário → data structures, algorithms, OOP, APIs
 Avançado  → design patterns, performance, architecture, security}

### 📥 Entrada Esperada

{Describe the input format the solution should accept.}

### 📤 Saída Esperada

{Describe the expected output with 1–2 concrete examples.}

### 💡 Dica

{One short hint that guides without giving away the answer.}

### 🏅 Recompensa ao Completar
- **XP:** {a realistic XP value between 200–2000 depending on level}
- **Badge desbloqueável:** {one badge name from the matching track, or a fitting invented badge}

---
*Use `/certificado` após completar a trilha para gerar seu certificado DIO!*
```

Do not provide the solution. The goal is to challenge the user to solve it themselves.
