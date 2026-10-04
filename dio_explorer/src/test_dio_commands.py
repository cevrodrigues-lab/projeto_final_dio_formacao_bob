"""
test_dio_commands.py
--------------------
Unit tests for the DIO Explorer skill commands:
  /trilha       — consultar trilhas por tecnologia
  /desafio      — gerar desafio de código para um aluno
  /certificado  — gerar certificado de conclusão para um aluno

Cobertura-alvo: >= 70 %
Execução: python -m pytest test_dio_commands.py -v --tb=short
"""

import json
import os
import re
import sys
import tempfile
import unittest

# ── resolve import regardless of cwd ──────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
import dio_commands as cmd

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

SAMPLE_DATA = {
    "trilhas": [
        {
            "id": 1,
            "nome": "Fullstack Java + Angular do Zero ao Avançado",
            "tecnologia": "Java / Angular",
            "nivel": "Avançado",
            "numero_de_modulos": 18,
            "xp_total": 12500,
            "badges_disponiveis": [
                "Java Master",
                "Angular Developer",
                "Fullstack Hero",
                "Spring Boot Expert",
            ],
            "promocoes": {
                "desconto_percentual": 30,
                "cupom": "JAVAANGULAR30",
                "validade": "2025-08-31",
            },
            "vitalicio": True,
            "lives_ao_vivo": [
                {"titulo": "Introdução ao Ecossistema Java", "data": "2025-07-10", "horario": "19:00"},
                {"titulo": "Angular 17 na Prática", "data": "2025-07-24", "horario": "20:00"},
            ],
        },
        {
            "id": 2,
            "nome": "Bootcamp Python para Data Science",
            "tecnologia": "Python / Pandas / Scikit-learn",
            "nivel": "Intermediário",
            "numero_de_modulos": 14,
            "xp_total": 9800,
            "badges_disponiveis": ["Python Ninja", "Data Scientist", "ML Practitioner"],
            "promocoes": {"desconto_percentual": 25, "cupom": "PYDATA25", "validade": "2025-09-15"},
            "vitalicio": True,
            "lives_ao_vivo": [
                {"titulo": "Pandas na Prática", "data": "2025-07-18", "horario": "19:30"}
            ],
        },
        {
            "id": 3,
            "nome": "Trilha React + TypeScript: Interfaces Modernas",
            "tecnologia": "React / TypeScript",
            "nivel": "Intermediário",
            "numero_de_modulos": 12,
            "xp_total": 8400,
            "badges_disponiveis": ["React Developer", "TypeScript Pro", "Frontend Specialist"],
            "promocoes": {"desconto_percentual": 0, "cupom": None, "validade": None},
            "vitalicio": False,
            "lives_ao_vivo": [],
        },
    ],
    "total_trilhas": 3,
    "ultima_atualizacao": "2025-07-10",
}


def _tmp_json(data: dict) -> str:
    """Write *data* to a temp JSON file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".json", text=True)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False)
    return path


# ============================================================================
# /trilha — buscar_trilha
# ============================================================================

class TestBuscarTrilha(unittest.TestCase):
    """Tests for the buscar_trilha() core search function."""

    def setUp(self):
        self.data = SAMPLE_DATA

    # ── happy path ────────────────────────────────────────────────────────────

    def test_busca_java_retorna_trilha(self):
        """'java' deve retornar pelo menos 1 trilha."""
        results = cmd.buscar_trilha("java", self.data)
        self.assertTrue(len(results) >= 1, "Esperado ao menos 1 resultado para 'java'")

    def test_busca_java_maiusculo(self):
        """Busca deve ser case-insensitive."""
        results = cmd.buscar_trilha("JAVA", self.data)
        self.assertTrue(len(results) >= 1)

    def test_busca_java_retorna_nome_correto(self):
        """A trilha Java retornada deve ter o nome esperado."""
        results = cmd.buscar_trilha("java", self.data)
        nomes = [r["nome"] for r in results]
        self.assertIn("Fullstack Java + Angular do Zero ao Avançado", nomes)

    def test_busca_python_retorna_trilha(self):
        results = cmd.buscar_trilha("python", self.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 2)

    def test_busca_react_retorna_trilha(self):
        results = cmd.buscar_trilha("react", self.data)
        self.assertEqual(len(results), 1)
        self.assertIn("React", results[0]["tecnologia"])

    def test_busca_parcial_match_typescript(self):
        """Partial keyword 'type' should still match TypeScript track."""
        results = cmd.buscar_trilha("type", self.data)
        self.assertTrue(len(results) >= 1)

    # ── edge / error cases ───────────────────────────────────────────────────

    def test_busca_inexistente_retorna_lista_vazia(self):
        results = cmd.buscar_trilha("COBOL", self.data)
        self.assertEqual(results, [])

    def test_busca_string_vazia_retorna_lista_vazia(self):
        results = cmd.buscar_trilha("", self.data)
        self.assertEqual(results, [])

    def test_busca_none_retorna_lista_vazia(self):
        results = cmd.buscar_trilha(None, self.data)
        self.assertEqual(results, [])

    def test_data_sem_trilhas_retorna_lista_vazia(self):
        results = cmd.buscar_trilha("java", {"trilhas": []})
        self.assertEqual(results, [])


# ============================================================================
# /trilha — formatar_trilha
# ============================================================================

class TestFormatarTrilha(unittest.TestCase):
    """Tests for the formatar_trilha() formatting function."""

    def setUp(self):
        self.trilha_java = SAMPLE_DATA["trilhas"][0]
        self.trilha_sem_promo = SAMPLE_DATA["trilhas"][2]

    def test_output_e_string(self):
        result = cmd.formatar_trilha(self.trilha_java)
        self.assertIsInstance(result, str)

    def test_contem_nome_da_trilha(self):
        result = cmd.formatar_trilha(self.trilha_java)
        self.assertIn("Fullstack Java + Angular do Zero ao Avançado", result)

    def test_contem_tecnologia(self):
        result = cmd.formatar_trilha(self.trilha_java)
        self.assertIn("Java / Angular", result)

    def test_contem_nivel(self):
        result = cmd.formatar_trilha(self.trilha_java)
        self.assertIn("Avançado", result)

    def test_contem_xp(self):
        result = cmd.formatar_trilha(self.trilha_java)
        self.assertIn("12500", result)

    def test_contem_vitalicio_sim(self):
        result = cmd.formatar_trilha(self.trilha_java)
        self.assertIn("Sim", result)

    def test_contem_vitalicio_nao(self):
        result = cmd.formatar_trilha(self.trilha_sem_promo)
        self.assertIn("Não", result)

    def test_contem_badge(self):
        result = cmd.formatar_trilha(self.trilha_java)
        self.assertIn("Java Master", result)

    def test_contem_live(self):
        result = cmd.formatar_trilha(self.trilha_java)
        self.assertIn("Introdução ao Ecossistema Java", result)

    def test_sem_lives_mostra_mensagem(self):
        result = cmd.formatar_trilha(self.trilha_sem_promo)
        self.assertIn("Nenhuma live agendada no momento.", result)

    def test_com_promocao_mostra_cupom(self):
        result = cmd.formatar_trilha(self.trilha_java)
        self.assertIn("JAVAANGULAR30", result)

    def test_sem_promocao_mostra_mensagem(self):
        result = cmd.formatar_trilha(self.trilha_sem_promo)
        self.assertIn("Sem promoção ativa no momento.", result)


# ============================================================================
# /trilha — comando_trilha (integration)
# ============================================================================

class TestComandoTrilha(unittest.TestCase):
    """Integration tests for comando_trilha() end-to-end."""

    def setUp(self):
        self.filepath = _tmp_json(SAMPLE_DATA)

    def tearDown(self):
        os.unlink(self.filepath)

    def test_trilha_java_retorna_conteudo(self):
        output = cmd.comando_trilha("java", self.filepath)
        self.assertIn("Java", output)

    def test_trilha_inexistente_retorna_aviso(self):
        output = cmd.comando_trilha("COBOL", self.filepath)
        self.assertIn("Nenhuma trilha encontrada", output)

    def test_trilha_inexistente_lista_tecnologias_disponiveis(self):
        output = cmd.comando_trilha("COBOL", self.filepath)
        self.assertIn("Java / Angular", output)

    def test_trilha_python_retorna_conteudo(self):
        output = cmd.comando_trilha("python", self.filepath)
        self.assertIn("Python", output)


# ============================================================================
# /desafio — gerar_desafio
# ============================================================================

class TestGerarDesafio(unittest.TestCase):
    """Tests for gerar_desafio() challenge generation."""

    def setUp(self):
        self.data = SAMPLE_DATA

    def test_retorna_dict(self):
        d = cmd.gerar_desafio("Java", "Iniciante", self.data, seed=42)
        self.assertIsInstance(d, dict)

    def test_campos_obrigatorios_presentes(self):
        d = cmd.gerar_desafio("Java", "Iniciante", self.data, seed=42)
        for campo in ("tecnologia", "nivel", "numero", "titulo", "enunciado", "entrada", "saida", "dica", "xp", "badge"):
            self.assertIn(campo, d, f"Campo ausente: {campo}")

    def test_nivel_iniciante(self):
        d = cmd.gerar_desafio("Java", "Iniciante", self.data, seed=1)
        self.assertEqual(d["nivel"], "Iniciante")

    def test_nivel_intermediario(self):
        d = cmd.gerar_desafio("Java", "Intermediário", self.data, seed=1)
        self.assertEqual(d["nivel"], "Intermediário")

    def test_nivel_avancado(self):
        d = cmd.gerar_desafio("Java", "Avançado", self.data, seed=1)
        self.assertEqual(d["nivel"], "Avançado")

    def test_nivel_invalido_levanta_excecao(self):
        with self.assertRaises(ValueError):
            cmd.gerar_desafio("Java", "Expert", self.data)

    def test_tecnologia_sem_match_usa_badge_padrao(self):
        d = cmd.gerar_desafio("COBOL", "Iniciante", self.data, seed=42)
        self.assertEqual(d["badge"], "Explorer Badge")

    def test_tecnologia_java_usa_badge_da_trilha(self):
        d = cmd.gerar_desafio("java", "Avançado", self.data, seed=1)
        self.assertIn(d["badge"], SAMPLE_DATA["trilhas"][0]["badges_disponiveis"])

    def test_numero_desafio_dentro_do_range(self):
        d = cmd.gerar_desafio("Java", "Iniciante", self.data, seed=42)
        self.assertGreaterEqual(d["numero"], 100)
        self.assertLessEqual(d["numero"], 999)

    def test_xp_positivo(self):
        d = cmd.gerar_desafio("Java", "Avançado", self.data, seed=5)
        self.assertGreater(d["xp"], 0)

    def test_seed_determinista(self):
        """Mesmo seed => mesmo desafio."""
        d1 = cmd.gerar_desafio("Java", "Iniciante", self.data, seed=99)
        d2 = cmd.gerar_desafio("Java", "Iniciante", self.data, seed=99)
        self.assertEqual(d1["numero"], d2["numero"])
        self.assertEqual(d1["titulo"], d2["titulo"])


# ============================================================================
# /desafio — formatar_desafio
# ============================================================================

class TestFormatarDesafio(unittest.TestCase):

    def setUp(self):
        self.desafio = cmd.gerar_desafio("Java", "Iniciante", SAMPLE_DATA, seed=7)

    def test_output_e_string(self):
        self.assertIsInstance(cmd.formatar_desafio(self.desafio), str)

    def test_contem_tecnologia(self):
        self.assertIn("Java", cmd.formatar_desafio(self.desafio))

    def test_contem_nivel(self):
        self.assertIn("Iniciante", cmd.formatar_desafio(self.desafio))

    def test_contem_enunciado(self):
        result = cmd.formatar_desafio(self.desafio)
        self.assertIn(self.desafio["enunciado"], result)

    def test_contem_xp(self):
        result = cmd.formatar_desafio(self.desafio)
        self.assertIn(str(self.desafio["xp"]), result)

    def test_contem_badge(self):
        result = cmd.formatar_desafio(self.desafio)
        self.assertIn(self.desafio["badge"], result)


# ============================================================================
# /desafio — comando_desafio (integration)
# ============================================================================

class TestComandoDesafio(unittest.TestCase):

    def setUp(self):
        self.filepath = _tmp_json(SAMPLE_DATA)

    def tearDown(self):
        os.unlink(self.filepath)

    def test_java_iniciante(self):
        output = cmd.comando_desafio("Java", "Iniciante", self.filepath)
        self.assertIn("Java", output)
        self.assertIn("Iniciante", output)

    def test_java_avancado(self):
        output = cmd.comando_desafio("Java", "Avançado", self.filepath)
        self.assertIn("Avançado", output)

    def test_nivel_invalido_retorna_mensagem_erro(self):
        output = cmd.comando_desafio("Java", "Expert", self.filepath)
        self.assertIn("inválido", output.lower())


# ============================================================================
# /certificado — gerar_certificado
# ============================================================================

class TestGerarCertificado(unittest.TestCase):

    def setUp(self):
        self.data = SAMPLE_DATA

    def test_retorna_dict(self):
        c = cmd.gerar_certificado("Ana Silva", "Java", self.data)
        self.assertIsInstance(c, dict)

    def test_campos_obrigatorios(self):
        c = cmd.gerar_certificado("Ana Silva", "Java", self.data)
        for campo in ("nome_aluno", "trilha_nome", "tecnologia", "nivel", "modulos", "xp", "badges", "data_conclusao", "cert_id"):
            self.assertIn(campo, c, f"Campo ausente: {campo}")

    def test_nome_em_maiusculo(self):
        c = cmd.gerar_certificado("ana silva", "Java", self.data)
        self.assertEqual(c["nome_aluno"], "ANA SILVA")

    def test_nome_vazio_levanta_excecao(self):
        with self.assertRaises(ValueError):
            cmd.gerar_certificado("", "Java", self.data)

    def test_nome_apenas_espacos_levanta_excecao(self):
        with self.assertRaises(ValueError):
            cmd.gerar_certificado("   ", "Java", self.data)

    def test_trilha_java_encontrada(self):
        c = cmd.gerar_certificado("Carlos", "Java", self.data)
        self.assertIn("Java", c["tecnologia"])

    def test_trilha_inexistente_usa_fallback(self):
        c = cmd.gerar_certificado("Carlos", "COBOL", self.data)
        self.assertEqual(c["trilha_nome"], "COBOL")
        self.assertEqual(c["modulos"], 0)

    def test_cert_id_formato(self):
        c = cmd.gerar_certificado("Maria", "Java", self.data)
        self.assertRegex(c["cert_id"], r"^DIO-\d{4}-\d{2}-\d{2}-[0-9A-F]{6}$")

    def test_data_conclusao_formato(self):
        c = cmd.gerar_certificado("Maria", "Java", self.data)
        self.assertRegex(c["data_conclusao"], r"^\d{2}/\d{2}/\d{4}$")

    def test_badges_sao_lista(self):
        c = cmd.gerar_certificado("Maria", "Java", self.data)
        self.assertIsInstance(c["badges"], list)
        self.assertGreater(len(c["badges"]), 0)


# ============================================================================
# /certificado — formatar_certificado
# ============================================================================

class TestFormatarCertificado(unittest.TestCase):

    def setUp(self):
        self.cert = cmd.gerar_certificado("Bruno Teste", "Java", SAMPLE_DATA)

    def test_output_e_string(self):
        self.assertIsInstance(cmd.formatar_certificado(self.cert), str)

    def test_contem_nome_aluno(self):
        result = cmd.formatar_certificado(self.cert)
        self.assertIn("BRUNO TESTE", result)

    def test_contem_trilha_nome(self):
        result = cmd.formatar_certificado(self.cert)
        self.assertIn("Fullstack Java + Angular do Zero ao Avançado", result)

    def test_contem_tecnologia(self):
        result = cmd.formatar_certificado(self.cert)
        self.assertIn("Java", result)

    def test_contem_cert_id(self):
        result = cmd.formatar_certificado(self.cert)
        self.assertIn(self.cert["cert_id"], result)

    def test_contem_badge(self):
        result = cmd.formatar_certificado(self.cert)
        self.assertIn("Java Master", result)

    def test_contem_xp(self):
        result = cmd.formatar_certificado(self.cert)
        self.assertIn("12500", result)

    def test_contem_dio_me(self):
        result = cmd.formatar_certificado(self.cert)
        self.assertIn("dio.me", result)


# ============================================================================
# /certificado — comando_certificado (integration)
# ============================================================================

class TestComandoCertificado(unittest.TestCase):

    def setUp(self):
        self.filepath = _tmp_json(SAMPLE_DATA)

    def tearDown(self):
        os.unlink(self.filepath)

    def test_gera_certificado_java(self):
        output = cmd.comando_certificado("João Aluno", "Java", self.filepath)
        self.assertIn("JOÃO ALUNO", output)
        self.assertIn("Java", output)

    def test_gera_certificado_python(self):
        output = cmd.comando_certificado("Maria Dev", "Python", self.filepath)
        self.assertIn("MARIA DEV", output)
        self.assertIn("Python", output)

    def test_nome_vazio_retorna_mensagem_erro(self):
        output = cmd.comando_certificado("", "Java", self.filepath)
        self.assertIn("vazio", output.lower())


# ============================================================================
# load_trilhas
# ============================================================================

class TestLoadTrilhas(unittest.TestCase):

    def test_carrega_json_valido(self):
        filepath = _tmp_json(SAMPLE_DATA)
        try:
            data = cmd.load_trilhas(filepath)
            self.assertIn("trilhas", data)
            self.assertEqual(len(data["trilhas"]), 3)
        finally:
            os.unlink(filepath)

    def test_arquivo_inexistente_levanta_excecao(self):
        with self.assertRaises(FileNotFoundError):
            cmd.load_trilhas("/caminho/inexistente/arquivo.json")


# ============================================================================
# gerar_certificado_id
# ============================================================================

class TestGerarCertificadoId(unittest.TestCase):

    def test_formato_correto(self):
        cid = cmd.gerar_certificado_id("2025-07-10")
        self.assertRegex(cid, r"^DIO-2025-07-10-[0-9A-F]{6}$")

    def test_sem_data_usa_hoje(self):
        cid = cmd.gerar_certificado_id()
        import datetime
        hoje = datetime.date.today().strftime("%Y-%m-%d")
        self.assertTrue(cid.startswith(f"DIO-{hoje}-"))

    def test_ids_diferentes_cada_chamada(self):
        ids = {cmd.gerar_certificado_id() for _ in range(20)}
        # Com 20 chamadas e 16 milhões de possibilidades, colisão é improvável
        self.assertGreater(len(ids), 1)


# ============================================================================
# Main runner
# ============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
