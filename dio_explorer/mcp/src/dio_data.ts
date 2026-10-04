/**
 * dio_data.ts
 * -----------
 * Lê e disponibiliza os dados do trilhas_dio.json.
 * Contém toda a lógica de busca, formatação e geração
 * portada do dio_commands.py para TypeScript.
 */

import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { randomInt } from "node:crypto";

const __dirname = dirname(fileURLToPath(import.meta.url));

// Caminho para o JSON de dados (relativo ao build/src)
const DATA_FILE = join(__dirname, "..", "..", "data", "trilhas_dio.json");

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface Live {
  titulo: string;
  data: string;
  horario: string;
}

export interface Promocao {
  desconto_percentual: number;
  cupom: string | null;
  validade: string | null;
}

export interface Trilha {
  id: number;
  nome: string;
  tecnologia: string;
  nivel: string;
  numero_de_modulos: number;
  xp_total: number;
  badges_disponiveis: string[];
  promocoes: Promocao;
  vitalicio: boolean;
  lives_ao_vivo: Live[];
}

export interface DioData {
  trilhas: Trilha[];
  total_trilhas: number;
  ultima_atualizacao: string;
}

// ---------------------------------------------------------------------------
// Loader (lê apenas uma vez, cache em módulo)
// ---------------------------------------------------------------------------

let _cache: DioData | null = null;

export function loadData(): DioData {
  if (!_cache) {
    const raw = readFileSync(DATA_FILE, "utf-8");
    _cache = JSON.parse(raw) as DioData;
  }
  return _cache;
}

// ---------------------------------------------------------------------------
// /trilha
// ---------------------------------------------------------------------------

export function buscarTrilha(tecnologia: string, data: DioData): Trilha[] {
  const kw = tecnologia.trim().toLowerCase();
  return data.trilhas.filter(
    (t) =>
      t.tecnologia.toLowerCase().includes(kw) ||
      t.nome.toLowerCase().includes(kw)
  );
}

export function formatarTrilha(t: Trilha): string {
  const vitalicio = t.vitalicio ? "Sim" : "Não";
  const badges = t.badges_disponiveis.map((b) => `- ${b}`).join("\n") || "Nenhum badge.";
  const lives =
    t.lives_ao_vivo.length > 0
      ? t.lives_ao_vivo.map((l) => `- ${l.titulo} — ${l.data} às ${l.horario}`).join("\n")
      : "Nenhuma live agendada no momento.";
  const promo =
    t.promocoes.desconto_percentual && t.promocoes.cupom
      ? `${t.promocoes.desconto_percentual}% de desconto | Cupom: ${t.promocoes.cupom} | Válido até: ${t.promocoes.validade ?? "N/A"}`
      : "Sem promoção ativa no momento.";

  return [
    `## 📚 Plano de Estudos — ${t.nome}`,
    `Tecnologia: ${t.tecnologia}`,
    `Nível: ${t.nivel}`,
    `Módulos: ${t.numero_de_modulos}`,
    `XP Total: ${t.xp_total} XP`,
    `Vitalício: ${vitalicio}`,
    ``,
    `### Badges Disponíveis`,
    badges,
    ``,
    `### Lives ao Vivo`,
    lives,
    ``,
    `### Promoção Ativa`,
    promo,
  ].join("\n");
}

// ---------------------------------------------------------------------------
// /desafio
// ---------------------------------------------------------------------------

export const LEVELS = ["Iniciante", "Intermediário", "Avançado"] as const;
export type Level = (typeof LEVELS)[number];

const CHALLENGES: Record<Level, [string, string, string, string][]> = {
  Iniciante: [
    ["Soma de Pares", "Dado um array de inteiros, retorne a soma de todos os números pares.", "Array de inteiros", "Soma dos pares"],
    ["FizzBuzz", "Imprima de 1 a N: 'Fizz' se divisível por 3, 'Buzz' por 5, 'FizzBuzz' por ambos.", "Número N", "'1 2 Fizz 4 Buzz ...'"],
  ],
  Intermediário: [
    ["Anagram Checker", "Verifique se duas strings são anagramas uma da outra.", "Duas strings", "True ou False"],
    ["Binary Search", "Implemente busca binária em um array ordenado.", "Array + alvo", "Índice ou -1"],
  ],
  Avançado: [
    ["LRU Cache", "Implemente um LRU Cache com O(1) para get e put.", "Capacidade + operações", "Valores do cache"],
    ["Design Pattern Factory", "Implemente o padrão Factory para criar objetos de veículos.", "Tipo de veículo", "Objeto instanciado"],
  ],
};

export interface Desafio {
  tecnologia: string;
  nivel: string;
  numero: number;
  titulo: string;
  enunciado: string;
  entrada: string;
  saida: string;
  dica: string;
  xp: number;
  badge: string;
}

export function gerarDesafio(tecnologia: string, nivel: Level, data: DioData): Desafio {
  const matches = buscarTrilha(tecnologia, data);
  const trilha = matches[0];
  const badge = trilha?.badges_disponiveis[0] ?? "Explorer Badge";
  const xp = trilha ? Math.floor(trilha.xp_total / trilha.numero_de_modulos) : 500;

  const numero = randomInt(100, 999);
  const pool = CHALLENGES[nivel];
  const [titulo, enunciado, entrada, saida] = pool[randomInt(0, pool.length)];

  return {
    tecnologia,
    nivel,
    numero,
    titulo,
    enunciado,
    entrada,
    saida,
    dica: `Pesquise sobre estruturas de dados em ${tecnologia}.`,
    xp,
    badge,
  };
}

export function formatarDesafio(d: Desafio): string {
  return [
    `## ⚔️ Desafio de Código DIO`,
    ``,
    `**Tecnologia:** ${d.tecnologia}`,
    `**Nível:** ${d.nivel}`,
    `**Desafio #${d.numero}**`,
    ``,
    `### ${d.titulo}`,
    ``,
    `**Enunciado:** ${d.enunciado}`,
    ``,
    `**Entrada:** ${d.entrada}`,
    ``,
    `**Saída:** ${d.saida}`,
    ``,
    `**Dica:** ${d.dica}`,
    ``,
    `**Recompensa:** ${d.xp} XP | Badge: ${d.badge}`,
  ].join("\n");
}

// ---------------------------------------------------------------------------
// /certificado
// ---------------------------------------------------------------------------

export interface Certificado {
  nome_aluno: string;
  trilha_nome: string;
  tecnologia: string;
  nivel: string;
  modulos: number;
  xp: number;
  badges: string[];
  data_conclusao: string;
  cert_id: string;
}

function gerarCertId(): string {
  const today = new Date().toISOString().slice(0, 10);
  const suffix = randomInt(0, 0xffffff).toString(16).padStart(6, "0").toUpperCase();
  return `DIO-${today}-${suffix}`;
}

export function gerarCertificado(nomeAluno: string, tecnologia: string, data: DioData): Certificado {
  if (!nomeAluno.trim()) throw new Error("Nome do aluno não pode ser vazio.");

  const matches = buscarTrilha(tecnologia, data);
  const trilha: Partial<Trilha> = matches[0] ?? {
    nome: tecnologia,
    tecnologia,
    nivel: "N/A",
    numero_de_modulos: 0,
    xp_total: 0,
    badges_disponiveis: [],
  };

  const today = new Date().toLocaleDateString("pt-BR");

  return {
    nome_aluno: nomeAluno.trim().toUpperCase(),
    trilha_nome: trilha.nome!,
    tecnologia: trilha.tecnologia!,
    nivel: trilha.nivel!,
    modulos: trilha.numero_de_modulos!,
    xp: trilha.xp_total!,
    badges: trilha.badges_disponiveis ?? [],
    data_conclusao: today,
    cert_id: gerarCertId(),
  };
}

export function formatarCertificado(c: Certificado): string {
  const badges =
    c.badges.map((b) => `**🏆 ${b}**`).join("\n") || "Nenhum badge registrado.";
  return [
    `# 🎓 CERTIFICADO DE CONCLUSÃO`,
    ``,
    `## Digital Innovation One — DIO`,
    ``,
    `### Este certificado é concedido a`,
    ``,
    `# ${c.nome_aluno}`,
    ``,
    `### pela conclusão com êxito da trilha`,
    ``,
    `## 📚 ${c.trilha_nome}`,
    ``,
    `| Campo | Detalhe |`,
    `|---|---|`,
    `| Tecnologia | ${c.tecnologia} |`,
    `| Nível | ${c.nivel} |`,
    `| Módulos Concluídos | ${c.modulos} |`,
    `| XP Conquistado | ${c.xp} XP |`,
    `| Data de Conclusão | ${c.data_conclusao} |`,
    ``,
    `### 🏅 Badges Conquistadas`,
    ``,
    badges,
    ``,
    `**🆔 Certificado Nº:** \`${c.cert_id}\``,
    `**✅ Válido em:** dio.me`,
  ].join("\n");
}
