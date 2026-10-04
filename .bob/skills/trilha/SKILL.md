---
name: trilha
description: Use when the user types /trilha followed by a technology name to display a formatted study plan from the DIO tracks file.
metadata:
  argument-hint: "[nome da tecnologia]"
---

# Trilha DIO — Plano de Estudos

When this skill is invoked, follow these steps exactly:

## Step 1 — Read the tracks data file

Use the `read_file` tool to read the file at:
`projeto_final_dio_formacao_bob/dio_explorer/data/trilhas_dio.json`

## Step 2 — Identify the requested technology

- The user will have provided a technology name after `/trilha` (e.g. `/trilha Python`).
- If no argument was given, ask the user which technology they want using `ask_followup_question`.
- Search the JSON `trilhas` array for entries whose `tecnologia` field contains the given term (case-insensitive partial match is fine).
- If multiple matches are found, show all of them.
- If no match is found, inform the user and list the available technologies from the file.

## Step 3 — Format and display the study plan

For each matching track, render the following formatted plan in the chat using Markdown:

```
---
## 📚 Plano de Estudos — {nome}

| Campo              | Detalhe                        |
|--------------------|-------------------------------|
| 🖥️ Tecnologia      | {tecnologia}                   |
| 📊 Nível           | {nivel}                        |
| 📦 Módulos         | {numero_de_modulos} módulos    |
| ⭐ XP Total        | {xp_total} XP                  |
| ♾️ Vitalício       | Sim / Não                      |

### 🏅 Badges Disponíveis
- Badge 1
- Badge 2
- ...

### 🎯 Roteiro Sugerido de Estudos
Divide {numero_de_modulos} into roughly equal weekly blocks and suggest a week-by-week progression.
For example, if 12 modules: Week 1–2 (modules 1–3: Fundamentos), Week 3–4 (modules 4–6: Prática), etc.
Adapt the names of the phases to the technology context.

### 🎥 Lives ao Vivo Programadas
List each live with its title, date and time.
If the list is empty, write "Nenhuma live agendada no momento."

### 🏷️ Promoção Ativa
Show discount percentage, coupon code and validity.
If desconto_percentual is 0 or cupom is null, write "Sem promoção ativa no momento."
---
```

Do not add any extra commentary beyond the formatted plan unless the user asks a follow-up question.
