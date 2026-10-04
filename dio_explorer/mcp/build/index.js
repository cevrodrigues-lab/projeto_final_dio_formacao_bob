#!/usr/bin/env node
/**
 * index.ts
 * --------
 * DIO Explorer MCP Server
 *
 * Expõe três ferramentas ao Bob (ou qualquer cliente MCP-compatível):
 *   • trilha      — busca planos de estudo por tecnologia
 *   • desafio     — gera desafio de código por tecnologia e nível
 *   • certificado — gera certificado de conclusão fictício
 *
 * Transporte padrão: stdio (para uso direto com Bob Desktop).
 * Para exposição remota via HTTPS, veja os comentários no bloco "HTTP mode".
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { loadData, buscarTrilha, formatarTrilha, gerarDesafio, formatarDesafio, gerarCertificado, formatarCertificado, } from "./dio_data.js";
import { loadAuthConfig } from "./auth.js";
// ---------------------------------------------------------------------------
// Inicialização
// ---------------------------------------------------------------------------
const server = new McpServer({
    name: "dio-explorer",
    version: "1.0.0",
});
const authConfig = loadAuthConfig();
if (authConfig.apiKey || authConfig.jwtSecret || authConfig.jwksUrl) {
    console.error("[dio-explorer] Autenticação configurada via variáveis de ambiente.");
}
else {
    console.error("[dio-explorer] Modo aberto (stdio) — sem autenticação configurada.");
}
// ---------------------------------------------------------------------------
// Ferramenta: trilha
// ---------------------------------------------------------------------------
server.registerTool("trilha", {
    description: "Busca planos de estudo DIO por tecnologia. Retorna dados detalhados da trilha: módulos, XP, badges, lives e promoções.",
    inputSchema: z.object({
        tecnologia: z
            .string()
            .min(1)
            .describe("Nome ou palavra-chave da tecnologia. Ex: 'Python', 'React', 'Java'"),
    }),
}, async ({ tecnologia }) => {
    try {
        const data = loadData();
        const results = buscarTrilha(tecnologia, data);
        if (results.length === 0) {
            const available = data.trilhas.map((t) => t.tecnologia).join(", ");
            return {
                content: [
                    {
                        type: "text",
                        text: `Nenhuma trilha encontrada para '${tecnologia}'.\nTecnologias disponíveis: ${available}`,
                    },
                ],
            };
        }
        const text = results.map(formatarTrilha).join("\n\n---\n\n");
        return { content: [{ type: "text", text }] };
    }
    catch (err) {
        return {
            content: [{ type: "text", text: `Erro ao buscar trilha: ${String(err)}` }],
            isError: true,
        };
    }
});
// ---------------------------------------------------------------------------
// Ferramenta: desafio
// ---------------------------------------------------------------------------
server.registerTool("desafio", {
    description: "Gera um desafio de código DIO para uma tecnologia e nível específicos. Retorna enunciado, dicas, XP e badge.",
    inputSchema: z.object({
        tecnologia: z
            .string()
            .min(1)
            .describe("Tecnologia do desafio. Ex: 'JavaScript', 'Python'"),
        nivel: z
            .enum(["Iniciante", "Intermediário", "Avançado"])
            .describe("Nível de dificuldade do desafio"),
    }),
}, async ({ tecnologia, nivel }) => {
    try {
        const data = loadData();
        const desafio = gerarDesafio(tecnologia, nivel, data);
        return { content: [{ type: "text", text: formatarDesafio(desafio) }] };
    }
    catch (err) {
        return {
            content: [{ type: "text", text: `Erro ao gerar desafio: ${String(err)}` }],
            isError: true,
        };
    }
});
// ---------------------------------------------------------------------------
// Ferramenta: certificado
// ---------------------------------------------------------------------------
server.registerTool("certificado", {
    description: "Gera um certificado fictício de conclusão de trilha DIO para o aluno informado.",
    inputSchema: z.object({
        nome_aluno: z
            .string()
            .min(1)
            .describe("Nome completo do aluno que concluiu a trilha"),
        tecnologia: z
            .string()
            .min(1)
            .describe("Tecnologia da trilha concluída. Ex: 'Java', 'Python'"),
    }),
}, async ({ nome_aluno, tecnologia }) => {
    try {
        const data = loadData();
        const cert = gerarCertificado(nome_aluno, tecnologia, data);
        return { content: [{ type: "text", text: formatarCertificado(cert) }] };
    }
    catch (err) {
        return {
            content: [{ type: "text", text: `Erro ao gerar certificado: ${String(err)}` }],
            isError: true,
        };
    }
});
// ---------------------------------------------------------------------------
// Recurso: lista de trilhas disponíveis (read-only context)
// ---------------------------------------------------------------------------
server.registerResource("trilhas-disponiveis", "dio://trilhas", {
    title: "Trilhas DIO Disponíveis",
    description: "Lista de todas as trilhas de estudo disponíveis no DIO Explorer.",
    mimeType: "application/json",
}, async () => {
    try {
        const data = loadData();
        const summary = data.trilhas.map((t) => ({
            id: t.id,
            nome: t.nome,
            tecnologia: t.tecnologia,
            nivel: t.nivel,
            modulos: t.numero_de_modulos,
            xp_total: t.xp_total,
        }));
        return {
            contents: [
                {
                    uri: "dio://trilhas",
                    mimeType: "application/json",
                    text: JSON.stringify({ total: data.total_trilhas, trilhas: summary }, null, 2),
                },
            ],
        };
    }
    catch (err) {
        return {
            contents: [
                {
                    uri: "dio://trilhas",
                    mimeType: "application/json",
                    text: JSON.stringify({ error: String(err) }),
                },
            ],
        };
    }
});
// ---------------------------------------------------------------------------
// Inicialização do servidor — modo stdio (padrão)
//
// Para HTTP remoto (HTTPS / SSO / API), substitua por:
//
//   import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
//   import express from "express";
//   import { validateRequest } from "./auth.js";
//
//   const app = express();
//   app.use(express.json());
//   app.use((req, res, next) => {
//     const result = validateRequest(req.headers as Record<string, string>, authConfig);
//     if (!result.ok) { res.status(401).json({ error: result.reason }); return; }
//     next();
//   });
//   const transport = new StreamableHTTPServerTransport({ app, path: "/mcp" });
//   await server.connect(transport);
//   app.listen(Number(process.env.PORT ?? 3000));
// ---------------------------------------------------------------------------
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("[dio-explorer] MCP Server rodando via stdio. Pronto para uso com Bob.");
}
main().catch((err) => {
    console.error("[dio-explorer] Erro fatal:", err);
    process.exit(1);
});
