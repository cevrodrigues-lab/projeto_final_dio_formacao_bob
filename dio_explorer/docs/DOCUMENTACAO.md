# DIO Explorer — Documentação Completa do Projeto

> Formação IBM Bob · Projeto final: criação de um MCP Server com Skills personalizadas, integrado ao assistente de IA Bob.

**Tags:** IBM Bob · MCP Server · TypeScript · Node.js · Skills · DIO · 67 testes · 100%

---

## Índice

1. [Visão Geral do Projeto](#1-visão-geral-do-projeto)
2. [Arquitetura](#2-arquitetura)
3. [Estrutura de Arquivos](#3-estrutura-de-arquivos)
4. [Skills Bob — Prompts e Modos de Uso](#4-skills-bob--prompts-e-modos-de-uso)
5. [MCP Server — Ferramentas e Recursos](#5-mcp-server--ferramentas-e-recursos)
6. [Dados — trilhas_dio.json](#6-dados--trilhas_diojson)
7. [Autenticação](#7-autenticação)
8. [Testes](#8-testes)
9. [Como Configurar e Executar](#9-como-configurar-e-executar)
10. [Dicas de Uso](#10-dicas-de-uso)
11. [Insights para Futuros Profissionais](#11-insights-para-futuros-profissionais)
12. [Referências Rápidas](#12-referências-rápidas)

---

## 1. Visão Geral do Projeto

O **DIO Explorer** é o projeto final da formação **IBM Bob**, desenvolvido na Digital Innovation One (DIO). O objetivo é construir, do zero, uma integração real entre o assistente de IA **Bob** e o ecossistema de trilhas educacionais da DIO — usando os dois mecanismos de extensibilidade nativos do Bob:

| Mecanismo | Descrição |
|---|---|
| **Skills** | Instruções em Markdown que ensinam o Bob a executar fluxos específicos quando o usuário digita um comando como `/trilha`, `/desafio` ou `/certificado`. |
| **MCP Server** | Servidor TypeScript/Node.js que expõe ferramentas (`trilha`, `desafio`, `certificado`) e recursos (`dio://trilhas`) via protocolo MCP, consumidos diretamente pelo Bob. |

**Resultado:** um assistente capaz de buscar trilhas de estudo, gerar desafios de código e emitir certificados fictícios — tudo dentro do chat, sem sair do Bob.

---

## 2. Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                     Usuário (Chat Bob)                   │
│    /trilha Python  │  /desafio Java  │  /certificado     │
└────────────┬────────────────────────────────────────────┘
             │
     ┌───────▼────────┐          ┌─────────────────────┐
     │  Skills (.bob/ │          │  MCP Server          │
     │  skills/)      │          │  (Node.js / stdio)   │
     │  SKILL.md      │          │                      │
     │  - trilha      │          │  Tools:              │
     │  - desafio     │◄────────►│  ├── trilha          │
     │  - certificado │          │  ├── desafio         │
     └───────┬────────┘          │  └── certificado     │
             │                   │                      │
             │                   │  Resource:           │
             │                   │  └── dio://trilhas   │
             │                   └──────────┬───────────┘
             │                              │
             └──────────────────────────────►
                                            │
                               ┌────────────▼──────────┐
                               │  trilhas_dio.json      │
                               │  (10 trilhas, badges,  │
                               │   lives, promoções)    │
                               └───────────────────────┘
```

O Bob atua como **orquestrador**: quando uma Skill é ativada, ela instrui o Bob a chamar as ferramentas do MCP Server ou a ler arquivos de dados diretamente. O MCP Server carrega o JSON em memória (cache de módulo) e responde via `stdio`.

---

## 3. Estrutura de Arquivos

```
Curso_BOB/
├── .bob/
│   ├── mcp.json                   ← Registro do MCP Server no Bob
│   └── skills/
│       ├── trilha/SKILL.md        ← Skill /trilha
│       ├── desafio/SKILL.md       ← Skill /desafio
│       └── certificado/SKILL.md  ← Skill /certificado
│
└── projeto_final_dio_formacao_bob/
    ├── Hello_World.md             ← Primeiro arquivo do projeto
    ├── test_results.txt           ← Relatório de testes (67/67 PASS)
    └── dio_explorer/
        ├── data/
        │   └── trilhas_dio.json  ← Base de dados (10 trilhas)
        ├── docs/
        │   └── DOCUMENTACAO.md  ← Este arquivo
        └── mcp/
            ├── src/
            │   ├── index.ts      ← Servidor MCP principal
            │   ├── dio_data.ts   ← Lógica de dados e formatação
            │   └── auth.ts       ← Autenticação (API Key, JWT, SSO)
            ├── build/            ← Compilado (gerado por `npm run build`)
            ├── package.json
            ├── tsconfig.json
            └── README.md
```

---

## 4. Skills Bob — Prompts e Modos de Uso

As **Skills** são arquivos `SKILL.md` que definem instruções passo-a-passo para o Bob. Ficam em `.bob/skills/<nome>/SKILL.md`.

### 4.1 Skill `/trilha`

- **Arquivo:** `.bob/skills/trilha/SKILL.md`
- **Descrição:** Busca e exibe um plano de estudos formatado para uma tecnologia.

**Prompt usado para criação:**

> "Crie uma skill no Bob chamada **trilha** que, quando o usuário digitar `/trilha [tecnologia]`, leia o arquivo `trilhas_dio.json`, encontre a trilha correspondente e exiba um plano de estudos formatado em Markdown com tabela, badges, roteiro semanal, lives e promoções."

**Como usar:**

| Comando | Exemplo | Resultado |
|---|---|---|
| `/trilha [tecnologia]` | `/trilha Python` | Plano de estudos completo com tabela, badges, roteiro, lives e promoção ativa |
| `/trilha` (sem argumento) | `/trilha` | Bob pergunta qual tecnologia você quer |
| Busca parcial | `/trilha type` | Encontra TypeScript por correspondência parcial |

---

### 4.2 Skill `/desafio`

- **Arquivo:** `.bob/skills/desafio/SKILL.md`
- **Descrição:** Gera um desafio de código aleatório por tecnologia e nível de dificuldade.

**Prompt usado para criação:**

> "Crie uma skill chamada **desafio** que gere um desafio de código para `/desafio [tecnologia] [nível]`. Os níveis são Iniciante, Intermediário e Avançado. O desafio deve ter enunciado, entrada, saída esperada, dica e recompensa em XP e badge da trilha. Não fornecer a solução."

**Como usar:**

| Comando | Exemplo |
|---|---|
| `/desafio [tecnologia] [nível]` | `/desafio Java Iniciante` |
| `/desafio` (sem args) | Bob pede tecnologia e nível interativamente |
| Nível Intermediário | `/desafio Python Intermediário` |
| Nível Avançado | `/desafio JavaScript Avançado` |

---

### 4.3 Skill `/certificado`

- **Arquivo:** `.bob/skills/certificado/SKILL.md`
- **Descrição:** Gera um certificado fictício de conclusão de trilha em Markdown.

**Prompt usado para criação:**

> "Crie uma skill chamada **certificado** que, ao receber `/certificado [nome] | [trilha]`, leia o JSON de trilhas, encontre os dados e emita um certificado visual em Markdown com nome do aluno em maiúsculas, tecnologia, módulos, XP, badges conquistadas, data de conclusão e um ID único no formato `DIO-YYYY-MM-DD-XXXXXXXX`."

**Como usar:**

| Comando | Exemplo |
|---|---|
| `/certificado [nome] \| [trilha]` | `/certificado João Silva \| Python` |
| `/certificado` (sem args) | Bob pede nome e trilha interativamente |
| Trilha desconhecida | Bob usa o nome fornecido como fallback |

---

## 5. MCP Server — Ferramentas e Recursos

O servidor MCP é um projeto **TypeScript + Node.js** que implementa o protocolo MCP via `@modelcontextprotocol/sdk`. Roda via **stdio** (padrão para Bob Desktop) e pode ser exposto via HTTPS com Express.

### 5.1 Ferramentas registradas

| Ferramenta | Input Schema | Descrição |
|---|---|---|
| `trilha` | `{ tecnologia: string }` | Busca trilha por tecnologia (correspondência parcial, case-insensitive). Retorna plano formatado ou lista de tecnologias disponíveis. |
| `desafio` | `{ tecnologia: string, nivel: "Iniciante"\|"Intermediário"\|"Avançado" }` | Gera desafio aleatório com enunciado, entrada, saída, dica, XP e badge da trilha. |
| `certificado` | `{ nome_aluno: string, tecnologia: string }` | Emite certificado fictício com ID único (`DIO-YYYY-MM-DD-XXXXXX`) e dados completos da trilha. |

### 5.2 Recurso registrado

| URI | MIME | Descrição |
|---|---|---|
| `dio://trilhas` | `application/json` | Lista de todas as trilhas disponíveis (id, nome, tecnologia, nível, módulos, XP) — contexto somente-leitura injetado no Bob. |

### 5.3 Módulos de código

| Módulo | Responsabilidade |
|---|---|
| `index.ts` | Ponto de entrada. Instancia o `McpServer`, registra as 3 ferramentas e o recurso, e inicia o transporte stdio. Contém o bloco comentado para modo HTTP. |
| `dio_data.ts` | Toda a lógica de negócio: carregamento do JSON (com cache), busca de trilhas, formatação, geração de desafios e certificados. Zero dependências externas. |
| `auth.ts` | Utilitários de autenticação preparatórios: API Key (comparação em tempo constante), Bearer Token JWT e stub para OIDC/JWKS. Usado apenas no modo HTTP. |
| `trilhas_dio.json` | Base de dados com 10 trilhas completas: badges, promoções, lives ao vivo, módulos, XP e flag vitalício. Única fonte de verdade do projeto. |

### 5.4 Registro no Bob (`.bob/mcp.json`)

```json
{
  "mcpServers": {
    "dio-explorer": {
      "command": "node",
      "args": ["${workspaceFolder}/projeto_final_dio_formacao_bob/dio_explorer/mcp/build/index.js"],
      "env": {
        "DIO_API_KEY":    "${env:DIO_API_KEY}",
        "DIO_JWT_SECRET": "${env:DIO_JWT_SECRET}",
        "DIO_JWKS_URL":   "${env:DIO_JWKS_URL}"
      },
      "disabled": false
    }
  }
}
```

---

## 6. Dados — trilhas_dio.json

O arquivo `dio_explorer/data/trilhas_dio.json` é a base de dados do projeto. Contém **10 trilhas** com a seguinte estrutura:

```json
{
  "id": 1,
  "nome": "Fullstack Java + Angular do Zero ao Avançado",
  "tecnologia": "Java / Angular",
  "nivel": "Avançado",
  "numero_de_modulos": 18,
  "xp_total": 12500,
  "badges_disponiveis": ["Java Master", "Angular Developer", "Fullstack Hero", "Spring Boot Expert"],
  "promocoes": {
    "desconto_percentual": 30,
    "cupom": "JAVAANGULAR30",
    "validade": "2025-08-31"
  },
  "vitalicio": true,
  "lives_ao_vivo": [
    { "titulo": "Introdução ao Ecossistema Java", "data": "2025-07-10", "horario": "19:00" }
  ]
}
```

### Tecnologias incluídas no dataset

| Tecnologia | Nível | Módulos | XP Total |
|---|---|---|---|
| Java / Angular | Avançado | 18 | 12.500 |
| Python / Pandas / Scikit-learn | Intermediário | 14 | 9.800 |
| React / TypeScript | Intermediário | 12 | 8.400 |
| Cloud AWS / Azure | Avançado | 20 | 15.000 |
| Node.js / Express / MongoDB | Intermediário | 10 | 7.200 |
| Kotlin / Android | Intermediário | 11 | 7.800 |
| Flutter / Dart | Iniciante | 8 | 5.500 |
| DevOps / Docker / Kubernetes | Avançado | 16 | 11.200 |
| C# / .NET / ASP.NET | Intermediário | 13 | 9.100 |
| Go / Microserviços | Avançado | 15 | 10.800 |

---

## 7. Autenticação

O módulo `auth.ts` prepara o servidor para exposição segura via HTTPS. Em modo **stdio** (padrão), a autenticação é ignorada — o chamador é o próprio processo Bob.

| Mecanismo | Variável de Ambiente | Como funciona |
|---|---|---|
| API Key | `DIO_API_KEY` | Cabeçalho `X-API-Key`. Comparação em tempo constante (evita timing attack). |
| Bearer JWT | `DIO_JWT_SECRET` | Cabeçalho `Authorization: Bearer <token>`. Stub HS256 — para produção, integrar `jsonwebtoken` ou `jose`. |
| OIDC / SSO | `DIO_JWKS_URL` | Placeholder para Azure AD, Okta etc. Requer implementação da biblioteca `jose`. |

---

## 8. Testes

O projeto possui **67 testes unitários e de integração**, todos aprovados com **100% de cobertura**.

| Suite | Escopo | Testes | Status |
|---|---|---|---|
| Suite 1 | /trilha — busca por tecnologia | 10 | ✅ PASS |
| Suite 2 | /trilha — formatação do plano | 11 | ✅ PASS |
| Suite 3 | /trilha — integração end-to-end | 6 | ✅ PASS |
| Suite 4 | /desafio — geração e validação | 12 | ✅ PASS |
| Suite 5 | /certificado — emissão e validação | 15 | ✅ PASS |
| Suite 6 | Carregamento do JSON de trilhas | 7 | ✅ PASS |
| Suite 7 | Geração de ID de certificado | 6 | ✅ PASS |
| **Total** | | **67** | ✅ **APROVADO ≥ 70%** |

**Destaques dos testes:** busca case-insensitive, busca parcial (`type` → TypeScript), fallback para tecnologia desconhecida, validação de nome vazio, unicidade dos IDs de certificado, aleatoriedade dos IDs.

---

## 9. Como Configurar e Executar

### Passo 1 — Instalar dependências e compilar o MCP Server

```bash
cd projeto_final_dio_formacao_bob/dio_explorer/mcp
npm install
npm run build
```

### Passo 2 — Verificar o registro no Bob

Confirme que `.bob/mcp.json` aponta para o arquivo compilado `build/index.js` com o caminho correto. O Bob detecta automaticamente ao abrir o workspace.

### Passo 3 — Verificar as Skills

As Skills já estão em `.bob/skills/`. O Bob as carrega automaticamente. Nenhuma configuração adicional é necessária.

### Passo 4 — Testar no chat

```
/trilha Python
/desafio Java Iniciante
/certificado Maria Oliveira | React
```

### Modo de desenvolvimento (hot-reload)

```bash
npm run dev   # Executa com --watch, reinicia ao salvar
```

---

## 10. Dicas de Uso

### Combine Skills em sequência

Use `/trilha` para escolher sua tecnologia → `/desafio` para praticar → `/certificado` ao concluir. É o fluxo completo de aprendizado DIO dentro do Bob.

### Busca parcial na /trilha

Não precisa digitar o nome exato. `/trilha cloud` encontra a trilha de Cloud AWS/Azure. `/trilha type` encontra TypeScript. A busca é case-insensitive e parcial.

### Reexecute /desafio para variação

Cada chamada a `/desafio` usa aleatoriedade (`randomInt`). Digite o mesmo comando várias vezes para desafios diferentes. Ideal para praticar até fixar o conceito.

### Prompts naturais também funcionam

Além dos comandos `/`, você pode usar linguagem natural:

- *"Mostre a trilha de Go"* → ferramenta `trilha`
- *"Gere um desafio avançado de Node.js"* → ferramenta `desafio`
- *"Emita meu certificado de DevOps"* → ferramenta `certificado`

O Bob chama as ferramentas MCP automaticamente.

### Recurso MCP como contexto silencioso

O recurso `dio://trilhas` injeta a lista de trilhas no contexto do Bob sem que você precise pedir. O Bob pode responder perguntas sobre tecnologias disponíveis mesmo sem acionar uma ferramenta explicitamente.

### Variáveis de ambiente com segredos

Use `${env:DIO_API_KEY}` no `mcp.json` para nunca expor segredos no arquivo de configuração. O Bob resolve as variáveis do ambiente do sistema operacional automaticamente.

---

## 11. Insights para Futuros Profissionais

### Skills vs. MCP Server — quando usar cada um?

Use **Skills** quando o fluxo depende do raciocínio do Bob (interpretação, formatação rica, perguntas interativas). Use **MCP Server** quando há lógica computacional determinística (busca, transformação de dados, geração de IDs únicos). Neste projeto, usamos os dois juntos: a Skill orquestra o UX, o MCP Server executa a lógica.

### O protocolo MCP é a nova camada de extensibilidade para LLMs

MCP (Model Context Protocol) é um padrão aberto para conectar LLMs a ferramentas externas de forma estruturada. Aprender a construir servidores MCP é uma habilidade diferenciadora em 2025 — qualquer cliente MCP-compatível (não só o Bob) pode consumir suas ferramentas.

### Cache de módulo é sua melhor primeira otimização em Node.js

O padrão `let _cache: DioData | null = null;` em `dio_data.ts` evita que o JSON seja lido do disco a cada chamada. Para dados que não mudam em runtime, essa técnica simples elimina I/O desnecessário sem complexidade adicional.

### Segurança: timing attack e comparação de chaves

Em `auth.ts`, a comparação de API Keys usa lógica byte-a-byte em tempo constante. A comparação com `===` vaza informação sobre onde as strings divergem (timing attack). Pequeno detalhe, grande impacto em segurança real.

### Valide entrada com Zod, não com if/else

O MCP Server usa `zod` para definir o schema de input das ferramentas. Isso garante validação automática antes mesmo do handler ser chamado, e gera documentação legível para o cliente MCP. Padrão de ouro para APIs TypeScript.

### Separe dados de lógica de apresentação

O projeto tem separação clara: `trilhas_dio.json` (dados), `dio_data.ts` (lógica), `index.ts` (transporte/API). Isso permite trocar o formato dos dados ou o protocolo de transporte sem reescrever a lógica central — o princípio da responsabilidade única na prática.

### Stdio primeiro, HTTP depois — estratégia de deploy incremental

O servidor nasceu em modo stdio (zero config, zero rede). O suporte HTTP com Express está pronto no código como bloco comentado. Essa abordagem permite desenvolver e testar localmente com velocidade, e promover para produção HTTPS somente quando necessário.

### Testes como documentação executável

Os 67 testes do projeto são autoexplicativos: *"Busca parcial 'type' encontra TypeScript"*, *"Nome vazio retorna mensagem de erro"*. Bons nomes de teste eliminam a necessidade de comentários e servem como contrato de comportamento para qualquer pessoa que entre no projeto.

### Prompts de qualidade geram código de qualidade

Os melhores resultados vieram de prompts que especificavam *formato de saída exato*, *comportamento para casos de borda* (argumento ausente, tecnologia não encontrada) e *restrições* (não fornecer a solução nos desafios). Prompts vagos geram código que precisa de retrabalho.

### O Bob é um parceiro de desenvolvimento, não apenas um assistente

Neste projeto, o Bob foi usado nos modos **Agent** (implementação), **Plan** (arquitetura) e **Ask** (dúvidas sobre o produto). Aprender a alternar entre modos conforme o contexto é uma habilidade meta que amplifica todos os outros aprendizados.

---

## 12. Referências Rápidas

### Dependências do MCP Server

```
@modelcontextprotocol/sdk  ^1.0.0
zod                        ^3.23.8
typescript                 ^5.5.0  (devDependency)
```

- Node.js ≥ 18
- npm ≥ 9

### Variáveis de Ambiente

| Variável | Descrição |
|---|---|
| `DIO_API_KEY` | Chave de API para autenticação por cabeçalho |
| `DIO_JWT_SECRET` | Segredo HMAC para validação JWT HS256 |
| `DIO_JWKS_URL` | URL do JWKS endpoint para validação OIDC/SSO |
| `PORT` | Porta HTTP para modo remoto (padrão: 3000) |

### Scripts npm

| Script | Descrição |
|---|---|
| `npm run build` | Compila TypeScript → `build/` |
| `npm run dev` | Executa com `--watch` para hot-reload |

### Resultado dos Testes

```
Total de testes : 67
Passaram (PASS) : 67
Falharam (FAIL) : 0
Cobertura       : 100%
Status          : APROVADO (>= 70%)
```

---

*Documentação gerada com IBM Bob — Digital Innovation One (DIO)*
