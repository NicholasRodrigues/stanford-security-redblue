"""Brazilian Portuguese UI strings. Technical terms stay in English."""

T = {
    # Navigation
    "nav_overview": "\U0001f5fa Visao Geral",
    "nav_arena": "\u2694\ufe0f Arena Interativa",
    "nav_suite": "\U0001f4a3 Suite de Ataques",
    "nav_multi_turn": "\U0001f50d Multi-Turn",
    "nav_benchmark": "\U0001f4ca Benchmark",
    "nav_report": "\U0001f4c4 Relatorio",

    # Sidebar
    "sidebar_title": "Red Team vs Blue Team",
    "sidebar_subtitle": "Avaliacao de Prompt Injection",
    "mock_label": "Modo Mock (sem API key)",
    "quick_label": "Modo Rapido",
    "model_label": "Modelo LLM",
    "team_label": "Nicholas Rodrigues, Guilherme Muniz, Tiago Trindade",

    # Overview
    "hero_title": "Red Team vs Blue Team",
    "hero_subtitle": "Avaliacao Quantitativa de Seguranca em Agentes de IA com Prompt Injection",
    "what_is_title": "O Que E Prompt Injection?",
    "what_is_text": (
        "Prompt Injection e uma classe de vulnerabilidade onde um atacante manipula "
        "as instrucoes de um modelo de linguagem (LLM) para que ele execute acoes nao autorizadas. "
        "Similar a SQL Injection em aplicacoes web, o atacante injeta instrucoes maliciosas "
        "que sobrescrevem o comportamento pretendido do sistema."
    ),
    "arch_title": "Arquitetura do Sistema",
    "attacks_section": "Categorias de Ataque (Red Team)",
    "defenses_section": "Camadas de Defesa (Blue Team)",

    # Arena
    "arena_title": "Arena Interativa",
    "arena_subtitle": "Digite um ataque e compare a resposta do agente baseline vs defendido",
    "baseline_header": "\U0001f534 BASELINE (Sem Defesas)",
    "defended_header": "\U0001f7e2 DEFENDIDO (Blue Team Ativo)",
    "chat_placeholder": "Digite seu prompt de ataque...",
    "quick_attacks_label": "Ataques Rapidos:",
    "verdict_leaked": "\U0001f480 DADOS VAZADOS",
    "verdict_blocked": "\U0001f6e1\ufe0f ATAQUE BLOQUEADO",
    "evidence_label": "Evidencia",
    "judge_label": "LLM Judge",
    "defenses_fired": "Defesas Ativadas",

    # Attack Suite
    "suite_title": "Suite Automatizada de Ataques",
    "suite_subtitle": "Execute todos os ataques contra baseline e defendido, com resultados em tempo real",
    "run_button": "\u25b6\ufe0f Executar Ataques",
    "stop_button": "\u23f9\ufe0f Parar",
    "phase1_label": "Fase 1: Atacando BASELINE (sem defesas)...",
    "phase2_label": "Fase 2: Atacando DEFENDIDO (blue team ativo)...",
    "category_select": "Selecione categorias:",
    "col_id": "ID",
    "col_category": "Categoria",
    "col_verdict": "Veredicto",
    "col_confidence": "Confianca",
    "col_evidence": "Evidencia",

    # Multi-Turn
    "multi_turn_title": "Ataques Multi-Turn",
    "multi_turn_subtitle": "Visualize as fases de reconhecimento, enumeracao e exfiltracao",
    "phase_recon": "\U0001f50d Reconhecimento",
    "phase_enum": "\U0001f4cb Enumeracao",
    "phase_exfil": "\U0001f480 Exfiltracao",
    "next_step": "Proximo Passo \u25b6",
    "reset_demo": "\U0001f504 Reiniciar",
    "indirect_tab": "Injecao Indireta por Dados Envenenados",
    "multi_turn_tab": "Escalacao Multi-Turn",

    # Benchmark
    "bench_title": "Benchmark de Modelos",
    "bench_subtitle": "Compare a taxa de sucesso de ataques entre diferentes LLMs",
    "bench_run": "\u25b6\ufe0f Executar Benchmark",
    "bench_models": "Modelos para comparar:",

    # Report
    "report_title": "Relatorio de Avaliacao",
    "report_subtitle": "Metricas e graficos interativos da avaliacao de seguranca",
    "baseline_asr": "ASR Baseline",
    "defended_asr": "ASR Defendido",
    "asr_reduction": "Reducao de ASR",
    "chart_overall": "Taxa de Sucesso de Ataques (ASR)",
    "chart_category": "ASR por Categoria de Ataque",
    "chart_radar": "Radar de Efetividade das Defesas",
    "chart_defense_layers": "Camadas de Defesa Ativadas",
    "no_data": "Execute a Suite de Ataques primeiro para gerar dados.",
    "download_report": "\U0001f4e5 Baixar Relatorio",

    # Common
    "leaked": "VAZADO",
    "blocked": "BLOQUEADO",
    "success": "Sucesso",
    "failed": "Falhou",
    "total_attacks": "Total de Ataques",
    "successful_attacks": "Ataques com Sucesso",
}
