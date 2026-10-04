# Run-Tests.ps1
# DIO Explorer -- Test Runner (PowerShell)
# Testa os comandos /trilha, /desafio e /certificado usando dados reais do JSON.

$ErrorActionPreference = "Stop"
$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$DataFile   = Join-Path $ScriptDir "..\data\trilhas_dio.json"
$ResultFile = Join-Path $ScriptDir "..\..\test_results.txt"

# Load JSON
$raw  = Get-Content $DataFile -Raw -Encoding UTF8
$data = $raw | ConvertFrom-Json
$trilhas = $data.trilhas

# ── Test framework ────────────────────────────────────────────────────────────
$Global:PASS = 0
$Global:FAIL = 0
$Global:ERRORS = [System.Collections.Generic.List[string]]::new()
$Global:LOG   = [System.Collections.Generic.List[string]]::new()

function Log([string]$msg) {
    $Global:LOG.Add($msg)
    Write-Host $msg
}

function Assert-Equal($actual, $expected, [string]$name) {
    if ($actual -eq $expected) {
        $Global:PASS++; Log "  [PASS] $name"
    } else {
        $Global:FAIL++
        $m = "  [FAIL] $name`n         Expected: '$expected'  Got: '$actual'"
        Log $m; $Global:ERRORS.Add($m)
    }
}

function Assert-True($cond, [string]$name) {
    if ($cond) {
        $Global:PASS++; Log "  [PASS] $name"
    } else {
        $Global:FAIL++
        $m = "  [FAIL] $name`n         Condition was FALSE"
        Log $m; $Global:ERRORS.Add($m)
    }
}

function Assert-Contains($hay, $needle, [string]$name) {
    if ($hay -and $hay.Contains($needle)) {
        $Global:PASS++; Log "  [PASS] $name"
    } else {
        $Global:FAIL++
        $m = "  [FAIL] $name`n         '$needle' not found"
        Log $m; $Global:ERRORS.Add($m)
    }
}

function Assert-NotNull($val, [string]$name) {
    if ($null -ne $val -and "$val" -ne "") {
        $Global:PASS++; Log "  [PASS] $name"
    } else {
        $Global:FAIL++
        $m = "  [FAIL] $name`n         Value was null or empty"
        Log $m; $Global:ERRORS.Add($m)
    }
}

# ── Command implementations ───────────────────────────────────────────────────

function Search-Trilha([string]$keyword, $arr) {
    if (-not $keyword) { return @() }
    $kw = $keyword.ToLower()
    return @($arr | Where-Object {
        $_.tecnologia.ToLower().Contains($kw) -or $_.nome.ToLower().Contains($kw)
    })
}

function Format-Trilha($t) {
    $vitalicio = if ($t.vitalicio) { "Sim" } else { "Nao" }
    $badges = ($t.badges_disponiveis | ForEach-Object { "- $_" }) -join [System.Environment]::NewLine
    $livesArr = @($t.lives_ao_vivo)
    if ($livesArr.Count -gt 0) {
        $lives = ($livesArr | ForEach-Object {
            "- " + $_.titulo + " -- " + $_.data + " as " + $_.horario
        }) -join [System.Environment]::NewLine
    } else {
        $lives = "Nenhuma live agendada no momento."
    }
    $promo = $t.promocoes
    if ($promo.desconto_percentual -gt 0 -and $promo.cupom) {
        $promoStr = "$($promo.desconto_percentual)% | Cupom: $($promo.cupom) | Valido ate: $($promo.validade)"
    } else {
        $promoStr = "Sem promocao ativa no momento."
    }

    $sb = [System.Text.StringBuilder]::new()
    [void]$sb.AppendLine("## Plano de Estudos -- $($t.nome)")
    [void]$sb.AppendLine("Tecnologia: $($t.tecnologia)")
    [void]$sb.AppendLine("Nivel: $($t.nivel)")
    [void]$sb.AppendLine("Modulos: $($t.numero_de_modulos)")
    [void]$sb.AppendLine("XP Total: $($t.xp_total) XP")
    [void]$sb.AppendLine("Vitalicio: $vitalicio")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("Badges Disponiveis:")
    [void]$sb.AppendLine($badges)
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("Lives ao Vivo:")
    [void]$sb.AppendLine($lives)
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("Promocao:")
    [void]$sb.AppendLine($promoStr)
    return $sb.ToString()
}

function Invoke-ComandoTrilha([string]$keyword) {
    $results = @(Search-Trilha $keyword $trilhas)
    if ($results.Count -eq 0) {
        $available = ($trilhas | ForEach-Object { $_.tecnologia }) -join ", "
        return "Nenhuma trilha encontrada para '$keyword'. Tecnologias disponiveis: $available"
    }
    return ($results | ForEach-Object { Format-Trilha $_ }) -join "`n---`n"
}

function Invoke-ComandoDesafio([string]$tecnologia, [string]$nivel) {
    $validLevels = @("Iniciante","Intermediario","Avancado")
    $normalizedNivel = $nivel -replace "á","a" -replace "ç","c"
    if ($normalizedNivel -notin $validLevels) {
        return "Nivel invalido: '$nivel'. Use: Iniciante, Intermediario ou Avancado"
    }
    $match = @(Search-Trilha $tecnologia $trilhas)
    $badge = if ($match.Count -gt 0 -and @($match[0].badges_disponiveis).Count -gt 0) {
        @($match[0].badges_disponiveis)[0]
    } else { "Explorer Badge" }
    $xp = if ($match.Count -gt 0 -and $match[0].numero_de_modulos -gt 0) {
        [int]($match[0].xp_total / $match[0].numero_de_modulos)
    } else { 500 }

    $desafioMap = @{
        "Iniciante"     = "FizzBuzz: Imprima 1 a N substituindo multiplos de 3 por Fizz e 5 por Buzz."
        "Intermediario" = "Busca Binaria: Implemente busca binaria em array ordenado."
        "Avancado"      = "LRU Cache: Implemente LRU Cache com O(1) para get e put."
    }
    $enunciado = $desafioMap[$normalizedNivel]
    $numero = Get-Random -Minimum 100 -Maximum 999

    $sb = [System.Text.StringBuilder]::new()
    [void]$sb.AppendLine("## Desafio de Codigo DIO")
    [void]$sb.AppendLine("Tecnologia: $tecnologia")
    [void]$sb.AppendLine("Nivel: $nivel")
    [void]$sb.AppendLine("Desafio #$numero")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("Enunciado: $enunciado")
    [void]$sb.AppendLine("Dica: Pesquise sobre estruturas de dados em $tecnologia.")
    [void]$sb.AppendLine("Recompensa: $xp XP | Badge: $badge")
    return $sb.ToString()
}

function New-CertId {
    $date = (Get-Date).ToString("yyyy-MM-dd")
    $hex  = (Get-Random -Minimum 0 -Maximum 16777215).ToString("X6").PadLeft(6, '0')
    return "DIO-$date-$hex"
}

function Invoke-ComandoCertificado([string]$nomeAluno, [string]$tecnologia) {
    if (-not $nomeAluno -or -not $nomeAluno.Trim()) {
        return "Erro: nome do aluno nao pode ser vazio."
    }
    $match = @(Search-Trilha $tecnologia $trilhas)
    if ($match.Count -gt 0) {
        $trilha = $match[0]
        $trilhaNome = $trilha.nome
        $trilhaTec  = $trilha.tecnologia
        $trilhaNivel = $trilha.nivel
        $modulos    = $trilha.numero_de_modulos
        $xpTotal    = $trilha.xp_total
        $badges     = @($trilha.badges_disponiveis)
    } else {
        $trilhaNome  = $tecnologia
        $trilhaTec   = $tecnologia
        $trilhaNivel = "N/A"
        $modulos     = 0
        $xpTotal     = 0
        $badges      = @()
    }
    $certId  = New-CertId
    $hoje    = (Get-Date).ToString("dd/MM/yyyy")
    $nome    = $nomeAluno.Trim().ToUpper()
    $badgesStr = if ($badges.Count -gt 0) {
        ($badges | ForEach-Object { "  - $_" }) -join [System.Environment]::NewLine
    } else { "  Nenhum badge registrado." }

    $sb = [System.Text.StringBuilder]::new()
    [void]$sb.AppendLine("CERTIFICADO DE CONCLUSAO")
    [void]$sb.AppendLine("Digital Innovation One -- DIO")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("Certificado concedido a: $nome")
    [void]$sb.AppendLine("Trilha: $trilhaNome")
    [void]$sb.AppendLine("Tecnologia: $trilhaTec")
    [void]$sb.AppendLine("Nivel: $trilhaNivel")
    [void]$sb.AppendLine("Modulos Concluidos: $modulos")
    [void]$sb.AppendLine("XP Conquistado: $xpTotal XP")
    [void]$sb.AppendLine("Data de Conclusao: $hoje")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("Badges Conquistadas:")
    [void]$sb.AppendLine($badgesStr)
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("Certificado No: $certId")
    [void]$sb.AppendLine("Valido em: dio.me")
    return $sb.ToString()
}

# =============================================================================
# TEST SUITES
# =============================================================================

Log ""
Log "============================================================"
Log " DIO Explorer -- Test Runner v1.0"
Log " $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Log "============================================================"

# ── Suite 1: Search-Trilha ────────────────────────────────────────────────────
Log ""
Log "[ SUITE 1 ] /trilha -- Search-Trilha"
Log "------------------------------------------------------------"

$r = @(Search-Trilha "java" $trilhas)
Assert-True ($r.Count -ge 1)  "1.01 Busca 'java' retorna ao menos 1 trilha"

$r = @(Search-Trilha "JAVA" $trilhas)
Assert-True ($r.Count -ge 1)  "1.02 Busca case-insensitive 'JAVA' retorna resultado"

$r = @(Search-Trilha "java" $trilhas)
$nomes = ($r | ForEach-Object { $_.nome }) -join ","
Assert-Contains $nomes "Fullstack Java"  "1.03 Nome da trilha Java presente nos resultados"

$r = @(Search-Trilha "python" $trilhas)
Assert-True ($r.Count -ge 1)             "1.04 Busca 'python' retorna ao menos 1 trilha"

$r = @(Search-Trilha "react" $trilhas)
Assert-True ($r.Count -ge 1)             "1.05 Busca 'react' retorna resultado"

$r = @(Search-Trilha "COBOL" $trilhas)
Assert-Equal $r.Count 0                  "1.06 Busca inexistente retorna 0 resultados"

$r = @(Search-Trilha "" $trilhas)
Assert-Equal $r.Count 0                  "1.07 Busca string vazia retorna 0"

$r = @(Search-Trilha $null $trilhas)
Assert-Equal $r.Count 0                  "1.08 Busca null retorna 0"

$r = @(Search-Trilha "type" $trilhas)
Assert-True ($r.Count -ge 1)             "1.09 Busca parcial 'type' encontra TypeScript"

$r = @(Search-Trilha "angular" $trilhas)
Assert-True ($r.Count -ge 1)             "1.10 Busca 'angular' encontra trilha Java/Angular"

# ── Suite 2: Format-Trilha ────────────────────────────────────────────────────
Log ""
Log "[ SUITE 2 ] /trilha -- Format-Trilha"
Log "------------------------------------------------------------"

$tj = $trilhas | Where-Object { $_.tecnologia -like "*Java*" } | Select-Object -First 1
$tr = $trilhas | Where-Object { $_.tecnologia -like "*React*" } | Select-Object -First 1

$out = Format-Trilha $tj
Assert-True ($out.Length -gt 0)            "2.01 Output nao e vazio"
Assert-Contains $out "Fullstack Java"      "2.02 Contem nome da trilha"
Assert-Contains $out "Java"                "2.03 Contem tecnologia"
Assert-Contains $out "18"                  "2.04 Contem numero de modulos"
Assert-Contains $out "12500"               "2.05 Contem XP total"
Assert-Contains $out "Sim"                 "2.06 Vitalicio = Sim"
Assert-Contains $out "Java Master"         "2.07 Contem badge"
Assert-Contains $out "Ecossistema Java"    "2.08 Contem texto parcial do titulo de live"

$out2 = Format-Trilha $tr
Assert-Contains $out2 "Nao"                "2.09 Vitalicio = Nao para trilha React"
Assert-Contains $out2 "React Developer"    "2.10 Trilha React tem badge React Developer"
Assert-Contains $out2 "REACTTS20"          "2.11 Trilha React tem cupom de promocao"

# ── Suite 3: Invoke-ComandoTrilha ─────────────────────────────────────────────
Log ""
Log "[ SUITE 3 ] /trilha -- Invoke-ComandoTrilha (integracao)"
Log "------------------------------------------------------------"

$out = Invoke-ComandoTrilha "java"
Assert-Contains $out "Java"                "3.01 Resultado para 'java' contem Java"
Assert-Contains $out "12500"               "3.02 Resultado contem XP da trilha Java"

$out = Invoke-ComandoTrilha "COBOL"
Assert-Contains $out "Nenhuma trilha"      "3.03 Tecnologia inexistente mostra aviso"
Assert-Contains $out "Java"                "3.04 Aviso lista tecnologias disponiveis"

$out = Invoke-ComandoTrilha "python"
Assert-Contains $out "Python"              "3.05 Resultado para 'python' contem Python"

$out = Invoke-ComandoTrilha "react"
Assert-Contains $out "React"               "3.06 Resultado para 'react' contem React"

# ── Suite 4: Invoke-ComandoDesafio ────────────────────────────────────────────
Log ""
Log "[ SUITE 4 ] /desafio -- Invoke-ComandoDesafio"
Log "------------------------------------------------------------"

$out = Invoke-ComandoDesafio "Java" "Iniciante"
Assert-Contains $out "Java"                "4.01 Desafio Java Iniciante contem tecnologia"
Assert-Contains $out "Iniciante"           "4.02 Desafio contem nivel"
Assert-Contains $out "Enunciado"           "4.03 Desafio contem enunciado"
Assert-Contains $out "Dica"                "4.04 Desafio contem dica"
Assert-Contains $out "XP"                  "4.05 Desafio contem XP"
Assert-Contains $out "Badge"               "4.06 Desafio contem badge"

$out = Invoke-ComandoDesafio "Java" "Intermediario"
Assert-Contains $out "Intermediario"       "4.07 Desafio Intermediario correto"

$out = Invoke-ComandoDesafio "Java" "Avancado"
Assert-Contains $out "Avancado"            "4.08 Desafio Avancado correto"

$out = Invoke-ComandoDesafio "Java" "Expert"
Assert-Contains $out "invalido"            "4.09 Nivel invalido retorna mensagem de erro"

$out = Invoke-ComandoDesafio "COBOL" "Iniciante"
Assert-Contains $out "Explorer Badge"      "4.10 Tecnologia sem match usa badge padrao"

$out = Invoke-ComandoDesafio "Java" "Avancado"
Assert-Contains $out "Java Master"         "4.11 Tecnologia Java usa badge da trilha"

$out = Invoke-ComandoDesafio "Python" "Iniciante"
Assert-Contains $out "Python"              "4.12 Desafio Python funciona"

# ── Suite 5: Invoke-ComandoCertificado ───────────────────────────────────────
Log ""
Log "[ SUITE 5 ] /certificado -- Invoke-ComandoCertificado"
Log "------------------------------------------------------------"

$out = Invoke-ComandoCertificado "Ana Silva" "Java"
Assert-Contains $out "ANA SILVA"           "5.01 Nome do aluno em maiusculo"
Assert-Contains $out "Java"                "5.02 Tecnologia no certificado"
Assert-Contains $out "CERTIFICADO"         "5.03 Titulo do certificado presente"
Assert-Contains $out "Digital Innovation"  "5.04 Nome da instituicao presente"
Assert-Contains $out "DIO-"               "5.05 ID do certificado presente"
Assert-Contains $out "dio.me"              "5.06 URL dio.me no certificado"
Assert-Contains $out "Java Master"         "5.07 Badge Java Master listada"
Assert-Contains $out "12500"               "5.08 XP total Java presente"

$out = Invoke-ComandoCertificado "Carlos Dev" "Python"
Assert-Contains $out "CARLOS DEV"          "5.09 Nome aluno Python em maiusculo"
Assert-Contains $out "Python"              "5.10 Tecnologia Python no certificado"

$out = Invoke-ComandoCertificado "Maria" "COBOL"
Assert-Contains $out "COBOL"               "5.11 Tecnologia desconhecida usa fallback"
Assert-Contains $out "N/A"                 "5.12 Nivel N/A no fallback"

$out = Invoke-ComandoCertificado "" "Java"
Assert-Contains $out "vazio"               "5.13 Nome vazio retorna mensagem de erro"

$out = Invoke-ComandoCertificado "   " "Java"
Assert-Contains $out "vazio"               "5.14 Nome com espacos retorna erro"

$out = Invoke-ComandoCertificado "Joao Aluno" "Java"
$cidMatch = [regex]::Match($out, "DIO-\d{4}-\d{2}-\d{2}-[0-9A-F]{6}")
Assert-True $cidMatch.Success              "5.15 ID de certificado tem formato correto"

# ── Suite 6: JSON data ────────────────────────────────────────────────────────
Log ""
Log "[ SUITE 6 ] Carregamento de dados -- JSON"
Log "------------------------------------------------------------"

Assert-True ($trilhas.Count -gt 0)          "6.01 JSON carregado com trilhas"
Assert-True ($trilhas.Count -ge 3)          "6.02 Ao menos 3 trilhas no arquivo"
Assert-NotNull $data.total_trilhas          "6.03 Campo total_trilhas presente"
Assert-NotNull $data.ultima_atualizacao     "6.04 Campo ultima_atualizacao presente"

$javaExists = @($trilhas | Where-Object { $_.tecnologia -like "*Java*" }).Count
Assert-True ($javaExists -ge 1)             "6.05 Java existe no JSON real"

$pyExists = @($trilhas | Where-Object { $_.tecnologia -like "*Python*" }).Count
Assert-True ($pyExists -ge 1)               "6.06 Python existe no JSON real"

$ids = $trilhas | ForEach-Object { $_.id }
$uniqueIds = ($ids | Sort-Object -Unique).Count
Assert-Equal $uniqueIds $trilhas.Count      "6.07 Todos os IDs de trilha sao unicos"

# ── Suite 7: New-CertId ───────────────────────────────────────────────────────
Log ""
Log "[ SUITE 7 ] New-CertId -- formato do ID"
Log "------------------------------------------------------------"

for ($i = 1; $i -le 5; $i++) {
    $cid = New-CertId
    Assert-True ($cid -match "^DIO-\d{4}-\d{2}-\d{2}-[0-9A-F]{6}$") "7.0$i CertId formato correto: $cid"
}

$ids = 1..20 | ForEach-Object { New-CertId }
$unique = ($ids | Sort-Object -Unique).Count
Assert-True ($unique -gt 1) "7.06 20 IDs gerados tem mais de 1 valor unico (aleatoriedade)"

# =============================================================================
# SUMMARY
# =============================================================================

$total     = $Global:PASS + $Global:FAIL
$pct       = if ($total -gt 0) { [math]::Round(($Global:PASS / $total) * 100, 1) } else { 0 }
$status    = if ($pct -ge 70) { "APROVADO (>= 70%)" } else { "REPROVADO (< 70%)" }
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Log ""
Log "============================================================"
Log " RESULTADO FINAL"
Log "============================================================"
Log " Total de testes : $total"
Log " Passaram (PASS) : $($Global:PASS)"
Log " Falharam (FAIL) : $($Global:FAIL)"
Log " Cobertura       : $pct%"
Log " Status          : $status"
Log " Executado em    : $timestamp"
Log "============================================================"

if ($Global:FAIL -gt 0) {
    Log ""
    Log "-- FALHAS DETALHADAS --"
    $Global:ERRORS | ForEach-Object { Log $_ }
}

# ── Write TXT report ─────────────────────────────────────────────────────────
$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add("============================================================")
$lines.Add(" DIO Explorer -- Relatorio de Testes Unitarios")
$lines.Add(" Gerado em: $timestamp")
$lines.Add("============================================================")
$lines.Add("")
$lines.Add("FLUXO TESTADO")
$lines.Add("------------------------------------------------------------")
$lines.Add("  Comando /trilha      -> Consulta de trilhas Java (e outras)")
$lines.Add("  Comando /desafio     -> Geracao de desafio de codigo para aluno")
$lines.Add("  Comando /certificado -> Emissao de certificado para aluno")
$lines.Add("")
$lines.Add("SUITES EXECUTADAS")
$lines.Add("------------------------------------------------------------")
$lines.Add("  Suite 1: /trilha - busca por tecnologia (Search-Trilha)   [10 testes]")
$lines.Add("  Suite 2: /trilha - formatacao do plano de estudos         [11 testes]")
$lines.Add("  Suite 3: /trilha - integracao end-to-end                  [ 6 testes]")
$lines.Add("  Suite 4: /desafio - geracao e validacao de desafio        [12 testes]")
$lines.Add("  Suite 5: /certificado - emissao e validacao               [15 testes]")
$lines.Add("  Suite 6: Carregamento do arquivo JSON de trilhas          [ 7 testes]")
$lines.Add("  Suite 7: Geracao de ID de certificado (New-CertId)        [ 6 testes]")
$lines.Add("")
$lines.Add("RESULTADO")
$lines.Add("------------------------------------------------------------")
$lines.Add("  Total de testes : $total")
$lines.Add("  Passaram (PASS) : $($Global:PASS)")
$lines.Add("  Falharam (FAIL) : $($Global:FAIL)")
$lines.Add("  Cobertura       : $pct%")
$lines.Add("  Status          : $status")
$lines.Add("")
$lines.Add("DETALHAMENTO DE CADA TESTE")
$lines.Add("------------------------------------------------------------")
$Global:LOG | ForEach-Object { $lines.Add($_) }

if ($Global:FAIL -gt 0) {
    $lines.Add("")
    $lines.Add("-- FALHAS DETALHADAS --")
    $Global:ERRORS | ForEach-Object { $lines.Add($_) }
}

$lines.Add("")
$lines.Add("============================================================")
$lines.Add(" Fim do relatorio")
$lines.Add("============================================================")

[System.IO.File]::WriteAllLines($ResultFile, $lines, [System.Text.Encoding]::UTF8)
Write-Host ""
Write-Host "Relatorio gravado em: $ResultFile"
