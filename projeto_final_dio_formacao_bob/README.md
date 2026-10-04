# 🚀 DIO Explorer — Projeto Final · Formação IBM Bob

> Integração completa entre o assistente de IA **IBM Bob** e o ecossistema de trilhas educacionais da **Digital Innovation One (DIO)**, construída com Skills personalizadas e um servidor MCP em TypeScript.

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Demonstração](#demonstração)
- [Arquitetura](#arquitetura)
- [Estrutura de Arquivos](#estrutura-de-arquivos)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Como Executar](#como-executar)
- [Testes](#testes)
- [Configuração Avançada](#configuração-avançada)
- [Autor](#autor)

---

## Sobre o Projeto

O **DIO Explorer** é o projeto final da **Formação IBM Bob** na Digital Innovation One. O objetivo é construir, do zero, uma integração real entre o assistente de IA **Bob** e as trilhas de estudo da DIO — usando os dois mecanismos de extensibilidade nativos do Bob:

| Mecanismo | Descrição |
|---|---|
| **Skills** | Arquivos `SKILL.md` que ensinam o Bob a executar fluxos específicos quando o usuário digita `/trilha`, `/desafio` ou `/certificado` |
| **MCP Server** | Servidor TypeScript/Node.js que expõe ferramentas e recursos via protocolo MCP, consumidos diretamente pelo Bob |

**Resultado:** um assistente capaz de buscar trilhas de estudo, gerar desafios de código e emitir certificados fictícios — tudo dentro do chat, sem sair do Bob.

---

## Demonstração

```
/trilha Python
```
> Retorna o plano de estudos completo com módulos, XP, badges, lives ao vivo e promoções ativas.

```
/desafio Java Iniciante
```
> Gera um desafio de código com enunciado, entrada, saída esperada, dica e recompensa em XP.

```
/certificado Maria Oliveira | React
```
> Emite um certificado fictício com ID único (`DIO-YYYY-MM-DD-XXXXXXXX`), badges e dados completos da trilha.

Além dos comandos `/`, prompts naturais também funcionam:
- *"Mostre a trilha de Go"*
- *"Gere um desafio avançado de Node.js"*
- *"Emita meu certificado de DevOps"*

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                     Usuário (Chat Bob)                   │
│    /trilha Python  │  /desafio Java  │  /certificado     │
└────────────┬────────────────────────────────────────────┘
             │
     ┌───────▼────────┐          ┌─────────────────────┐
     │  Skills (.bob/ │          │  MCP Server          │
     │  skills/)      │          │  (Node.js / stdio)   │
     │                │          │                      │
     │  - trilha      │◄────────►│  Tools:              │
     │  - desafio     │          │  ├── trilha          │
     │  - certificado │          │  ├── desafio         │
     └───────┬────────┘          │  └── certificado     │
             │                   │                      │
             │                   │  Resource:           │
             │                   │  └── dio://trilhas   │
             │                   └──────────┬───────────┘
             └──────────────────────────────►
                                            │
                               ┌────────────▼──────────┐
                               │  trilhas_dio.json      │
                               │  (10 trilhas, badges,  │
                               │   lives, promoções)    │
                               └───────────────────────┘
```

O Bob atua como **orquestrador**: quando uma Skill é ativada, ela instrui o Bob a chamar as ferramentas do MCP Server. O servidor carrega o JSON em memória (cache de módulo) e responde via `stdio`.

---

## Estrutura de Arquivos

```
projeto_final_dio_formacao_bob/
├── Hello_World.md                    ← Primeiro arquivo do projeto
├── test_results.txt                  ← Relatório de testes (67/67 PASS)
└── dio_explorer/
    ├── data/
    │   └── trilhas_dio.json          ← Base de dados (10 trilhas)
    ├── docs/
    │   └── DOCUMENTACAO.md          ← Documentação completa
    └── mcp/
        ├── src/
        │   ├── index.ts              ← Servidor MCP principal
        │   ├── dio_data.ts           ← Lógica de dados e formatação
        │   └── auth.ts               ← Autenticação (API Key, JWT, SSO)
        ├── build/                    ← Compilado (gerado por npm run build)
        ├── package.json
        ├── tsconfig.json
        └── README.md

# Skills (na raiz do workspace .bob/)
.bob/
├── mcp.json                          ← Registro do MCP Server no Bob
└── skills/
    ├── trilha/SKILL.md
    ├── desafio/SKILL.md
    └── certificado/SKILL.md
```

---

## Funcionalidades

### 🗺️ `/trilha [tecnologia]`
Busca e exibe o plano de estudos completo para uma tecnologia. Suporta busca parcial e case-insensitive (`/trilha type` → encontra TypeScript).

### ⚔️ `/desafio [tecnologia] [nível]`
Gera um desafio de código aleatório. Níveis disponíveis: `Iniciante`, `Intermediário`, `Avançado`. Cada execução produz um desafio diferente — ideal para prática repetida.

### 🏆 `/certificado [nome] | [trilha]`
Emite um certificado fictício de conclusão com ID único no formato `DIO-YYYY-MM-DD-XXXXXXXX`, badges conquistadas, XP total e data de conclusão.

### 📚 Trilhas disponíveis no dataset

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

## Tecnologias

- **[IBM Bob](https://www.ibm.com/bob)** — assistente de IA com suporte a Skills e MCP
- **TypeScript 5.5+** — linguagem principal do MCP Server
- **Node.js 18+** — runtime
- **[@modelcontextprotocol/sdk](https://github.com/modelcontextprotocol/typescript-sdk)** — SDK para construção do servidor MCP
- **[Zod](https://zod.dev)** — validação de schema dos inputs das ferramentas

---

## Como Executar

### Pré-requisitos

- Node.js ≥ 18
- npm ≥ 9
- IBM Bob instalado

### 1. Instalar dependências e compilar

```bash
cd projeto_final_dio_formacao_bob/dio_explorer/mcp
npm install
npm run build
```

### 2. Registrar o servidor no Bob

Verifique se `.bob/mcp.json` contém:

```json
{
  "mcpServers": {
    "dio-explorer": {
      "command": "node",
      "args": ["${workspaceFolder}/projeto_final_dio_formacao_bob/dio_explorer/mcp/build/index.js"]
    }
  }
}
```

### 3. Testar no chat do Bob

```
/trilha Python
/desafio Java Iniciante
/certificado Seu Nome | React
```

### Modo de desenvolvimento (hot-reload)

```bash
npm run dev
```

---

## Testes

O projeto possui **67 testes unitários e de integração**, todos aprovados com **100% de cobertura**.

| Suite | Escopo | Testes | Status |
|---|---|---|---|
| Suite 1 | `/trilha` — busca por tecnologia | 10 | ✅ PASS |
| Suite 2 | `/trilha` — formatação do plano | 11 | ✅ PASS |
| Suite 3 | `/trilha` — integração end-to-end | 6 | ✅ PASS |
| Suite 4 | `/desafio` — geração e validação | 12 | ✅ PASS |
| Suite 5 | `/certificado` — emissão e validação | 15 | ✅ PASS |
| Suite 6 | Carregamento do JSON de trilhas | 7 | ✅ PASS |
| Suite 7 | Geração de ID de certificado | 6 | ✅ PASS |
| **Total** | | **67** | ✅ **100% APROVADO** |

```
Total de testes : 67
Passaram (PASS) : 67
Falharam (FAIL) : 0
Cobertura       : 100%
Status          : APROVADO (>= 70%)
```

---

## Configuração Avançada

### Autenticação (modo HTTP/HTTPS)

| Variável | Descrição |
|---|---|
| `DIO_API_KEY` | Chave de API para autenticação via cabeçalho `X-API-Key` |
| `DIO_JWT_SECRET` | Segredo HMAC para validação JWT HS256 |
| `DIO_JWKS_URL` | URL do JWKS endpoint para validação OIDC/SSO (Azure AD, Okta etc.) |
| `PORT` | Porta HTTP para modo remoto (padrão: `3000`) |

Em modo **stdio** (padrão para Bob Desktop), nenhuma autenticação é necessária.

Para detalhes completos sobre autenticação, deploy via HTTPS e uso remoto, consulte a [documentação completa](dio_explorer/docs/DOCUMENTACAO.md).

---

## Autor

Desenvolvido como **Projeto Final da Formação IBM Bob** na [Digital Innovation One (DIO)](https://dio.me).

---

*Feito com IBM Bob · Digital Innovation One (DIO)*
