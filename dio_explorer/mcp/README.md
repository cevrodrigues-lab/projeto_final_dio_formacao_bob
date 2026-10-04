# DIO Explorer — MCP Server

Servidor MCP que expõe as funcionalidades do **DIO Explorer** para o Bob (IBM Bob) e qualquer cliente compatível com o Model Context Protocol.

---

## Ferramentas disponíveis

| Ferramenta | Descrição |
|---|---|
| `trilha` | Busca planos de estudo por tecnologia |
| `desafio` | Gera desafio de código por tecnologia e nível |
| `certificado` | Gera certificado fictício de conclusão |

Além disso, expõe o **recurso** `dio://trilhas` com a lista completa das trilhas disponíveis em JSON.

---

## Pré-requisitos

- Node.js ≥ 18
- npm ≥ 9

---

## Instalação e build

```bash
cd dio_explorer/mcp
npm install
npm run build
```

O artefato compilado fica em `build/index.js`.

---

## Uso local com Bob (stdio — padrão)

Após o build, registre no `mcp.json` do workspace (`.bob/mcp.json`):

```json
{
  "mcpServers": {
    "dio-explorer": {
      "command": "node",
      "args": ["<caminho-absoluto>/dio_explorer/mcp/build/index.js"]
    }
  }
}
```

Bob detecta automaticamente e carrega as ferramentas. Você pode então usar:

- **"Mostre a trilha de Python"** → ferramenta `trilha`
- **"Gere um desafio Avançado de JavaScript"** → ferramenta `desafio`
- **"Gere meu certificado de Java"** → ferramenta `certificado`

---

## Exposição via HTTPS / API Key / SSO

### 1. API Key

Defina a variável de ambiente `DIO_API_KEY` antes de iniciar o servidor:

```bash
export DIO_API_KEY="sua-chave-secreta"
node build/index.js
```

Clientes devem enviar o cabeçalho:
```
X-API-Key: sua-chave-secreta
```

No `mcp.json` remoto, use:
```json
{
  "mcpServers": {
    "dio-explorer": {
      "url": "https://seu-servidor/mcp",
      "headers": {
        "X-API-Key": "${env:DIO_API_KEY}"
      }
    }
  }
}
```

### 2. Bearer Token / JWT (HS256)

```bash
export DIO_JWT_SECRET="seu-segredo-jwt"
node build/index.js
```

> Para produção com RS256/OIDC, instale a biblioteca [`jose`](https://github.com/panva/jose) e implemente a verificação em `src/auth.ts`.

### 3. SSO / OIDC (ex: Azure AD, Okta)

Defina `DIO_JWKS_URL` com o endpoint do provedor:

```bash
export DIO_JWKS_URL="https://login.microsoftonline.com/<tenant>/discovery/v2.0/keys"
```

Adicione a biblioteca `jose` e implemente `validateBearerToken` em `src/auth.ts` para validar tokens via JWKS.

### 4. Modo HTTP completo (Express)

Para expor o servidor via HTTPS com o transporte Streamable HTTP, siga o bloco comentado no final de `src/index.ts`:

```typescript
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import express from "express";
import { validateRequest } from "./auth.js";

const app = express();
app.use(express.json());
app.use((req, res, next) => {
  const result = validateRequest(req.headers as Record<string, string>, authConfig);
  if (!result.ok) { res.status(401).json({ error: result.reason }); return; }
  next();
});
const transport = new StreamableHTTPServerTransport({ app, path: "/mcp" });
await server.connect(transport);
app.listen(Number(process.env.PORT ?? 3000));
```

Instale as dependências adicionais:
```bash
npm install express @types/express
```

---

## Estrutura do projeto

```
mcp/
├── src/
│   ├── index.ts       # Servidor MCP principal (ferramentas + recurso)
│   ├── dio_data.ts    # Lógica de dados, busca e formatação
│   └── auth.ts        # Utilitários de autenticação (API Key, JWT, SSO)
├── build/             # Artefatos compilados (gerado pelo build)
├── package.json
├── tsconfig.json
└── README.md
```

---

## Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `DIO_API_KEY` | Chave de API para autenticação por cabeçalho |
| `DIO_JWT_SECRET` | Segredo HMAC para validação JWT HS256 |
| `DIO_JWKS_URL` | URL do JWKS endpoint para validação OIDC/SSO |
| `PORT` | Porta HTTP para modo remoto (padrão: 3000) |

Quando nenhuma variável de autenticação é definida, o servidor opera em **modo aberto**, adequado para uso via stdio com o Bob Desktop.

---

## Desenvolvimento

```bash
npm run build        # Compila TypeScript
npm run dev          # Executa com --watch para hot-reload
```
