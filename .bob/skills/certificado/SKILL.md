---
name: certificado
description: Use when the user types /certificado with their name and completed track to generate a fictional DIO completion certificate in Markdown.
metadata:
  argument-hint: "[seu nome] | [trilha concluída]"
---

# Certificado DIO — Geração de Certificado Fictício

When this skill is invoked, follow these steps exactly:

## Step 1 — Collect parameters

Check whether the user provided arguments after `/certificado`.

- **User name**: the full name of the person to appear on the certificate.
- **Track name** (trilha): the name or technology of the track they completed.

If either parameter is missing, use `ask_followup_question` to request it before continuing.

## Step 2 — Look up the track in the data file

Use `read_file` on `projeto_final_dio_formacao_bob/dio_explorer/data/trilhas_dio.json`.

- Find the track whose `nome` or `tecnologia` field best matches what the user provided.
- Retrieve: `nome`, `tecnologia`, `nivel`, `numero_de_modulos`, `xp_total`, and `badges_disponiveis`.
- If no match is found, use the user's provided track name as-is and generate reasonable placeholder values.

## Step 3 — Generate the certificate

Generate a **certificate ID** by combining the current date (YYYY-MM-DD format) + a random 6-digit hex string, e.g. `DIO-2025-07-09-4F2A1C`.

Render the complete certificate using this exact Markdown structure:

```markdown
---

<div align="center">

# 🎓 CERTIFICADO DE CONCLUSÃO

## Digital Innovation One — DIO

---

### Este certificado é concedido a

# {NOME DO USUÁRIO EM MAIÚSCULAS}

### pela conclusão com êxito da trilha

## 📚 {nome da trilha}

---

| 🖥️ Tecnologia        | {tecnologia}            |
|----------------------|------------------------|
| 📊 Nível             | {nivel}                |
| 📦 Módulos Concluídos| {numero_de_modulos}    |
| ⭐ XP Conquistado    | {xp_total} XP          |
| 📅 Data de Conclusão | {today's date DD/MM/YYYY} |

---

### 🏅 Badges Conquistadas

{list each badge from badges_disponiveis as: **🏆 Badge Name**}

---

> *"O aprendizado contínuo é o caminho para a inovação."*
> — Digital Innovation One

---

**🆔 Certificado Nº:** `{certificate ID}`
**✅ Válido em:** dio.me

</div>

---
```

Output the certificate exactly as formatted above, inside a Markdown code fence so it renders cleanly in the chat. Then, below the code fence, render the certificate **again without the code fence** so the user can see the final visual result directly.

Do not add commentary beyond the certificate itself.
