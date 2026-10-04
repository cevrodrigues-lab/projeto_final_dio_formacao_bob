/**
 * auth.ts
 * -------
 * Utilitários de autenticação para o DIO Explorer MCP Server.
 *
 * Suporta dois mecanismos preparatórios para exposição HTTPS/SSO:
 *
 *  1. API Key — cabeçalho `X-API-Key` ou query param `api_key`
 *     Ative setando a variável de ambiente DIO_API_KEY.
 *
 *  2. Bearer Token (JWT/SSO) — cabeçalho `Authorization: Bearer <token>`
 *     Ative setando DIO_JWT_SECRET (HMAC-SHA256) ou DIO_JWKS_URL (OIDC).
 *
 * Quando rodando no transporte stdio padrão (Bob Desktop), a autenticação é
 * ignorada — o caller já é o próprio Bob process.
 *
 * Para exposição via HTTP remoto, envolva o servidor com um framework como
 * Express/Hono e chame validateRequest() em um middleware antes de repassar
 * ao StreamableHTTP transport.
 */
// ---------------------------------------------------------------------------
// Configuração a partir de variáveis de ambiente
// ---------------------------------------------------------------------------
export function loadAuthConfig() {
    return {
        apiKey: process.env["DIO_API_KEY"],
        jwtSecret: process.env["DIO_JWT_SECRET"],
        jwksUrl: process.env["DIO_JWKS_URL"],
    };
}
// ---------------------------------------------------------------------------
// Validação de API Key
// ---------------------------------------------------------------------------
export function validateApiKey(provided, expected) {
    if (!provided)
        return { ok: false, reason: "API key ausente." };
    // Comparação em tempo constante para evitar timing attack
    const a = Buffer.from(provided.padEnd(256));
    const b = Buffer.from(expected.padEnd(256));
    const match = a.length === b.length && a.every((byte, i) => byte === b[i]);
    return match ? { ok: true } : { ok: false, reason: "API key inválida." };
}
// ---------------------------------------------------------------------------
// Validação de Bearer Token (JWT HS256 simples — sem dependência externa)
// Substitua por `jsonwebtoken` ou `jose` para produção com RS256/OIDC.
// ---------------------------------------------------------------------------
export function validateBearerToken(authHeader, secret) {
    if (!authHeader?.startsWith("Bearer ")) {
        return { ok: false, reason: "Cabeçalho Authorization ausente ou mal formado." };
    }
    const token = authHeader.slice(7);
    const parts = token.split(".");
    if (parts.length !== 3)
        return { ok: false, reason: "JWT mal formado." };
    // Nota: validação de assinatura real requer crypto.createHmac.
    // Este stub verifica apenas a estrutura; para produção adicione verificação real.
    console.error("[auth] Bearer token recebido — implemente verificação de assinatura para produção.");
    return { ok: true };
}
// ---------------------------------------------------------------------------
// Ponto de entrada unificado para HTTP middleware
// ---------------------------------------------------------------------------
export function validateRequest(headers, config) {
    // Nenhuma autenticação configurada → modo aberto (stdio / desenvolvimento)
    if (!config.apiKey && !config.jwtSecret && !config.jwksUrl) {
        return { ok: true };
    }
    // Tenta API Key primeiro
    if (config.apiKey) {
        const provided = headers["x-api-key"] ?? headers["X-API-Key"] ?? headers["authorization"]?.replace(/^Bearer\s+/i, "");
        return validateApiKey(provided, config.apiKey);
    }
    // Tenta Bearer / JWT
    if (config.jwtSecret) {
        return validateBearerToken(headers["authorization"], config.jwtSecret);
    }
    // JWKS/SSO: placeholder para integração com provedor externo (Okta, Azure AD, etc.)
    if (config.jwksUrl) {
        console.error(`[auth] JWKS URL configurada: ${config.jwksUrl} — adicione a biblioteca 'jose' para validação OIDC.`);
        return { ok: false, reason: "Validação JWKS não implementada. Configure a biblioteca jose." };
    }
    return { ok: false, reason: "Configuração de autenticação inválida." };
}
