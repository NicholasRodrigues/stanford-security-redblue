# Red Team vs Blue Team

Avaliacao quantitativa de Prompt Injection em agentes de IA com acesso a ferramentas (SQLite + filesystem).

**Equipe:** Nicholas Rodrigues, Guilherme Muniz, Tiago Trindade

## O que e

Um agente LLM com acesso real a banco de dados e arquivos e atacado com ~90 variantes de prompt injection (7 categorias), depois defendido com 6 camadas de seguranca. O sistema mede a taxa de sucesso dos ataques (ASR) antes e depois das defesas.

**Resultados reais (gpt-4.1-nano):**

| Metrica | Baseline | Defendido |
|---------|----------|-----------|
| ASR | 76.2% | 9.5% |
| Reducao | - | 87.5% |

## Categorias de Ataque

| Categoria | Analogia |
|-----------|----------|
| Instruction Override | Privilege Escalation |
| Persona Switching (DAN) | Social Engineering / Trojans |
| Encoding Attacks | Payload Obfuscation |
| Context Manipulation | Spoofing / DMZ Violation |
| Multi-Turn Escalation | Pentesting Lifecycle (Recon → Exfil) |
| Indirect Injection | Supply Chain / Worms |
| Side-Channel | Passive Reconnaissance |

## Camadas de Defesa

| Defesa | Analogia |
|--------|----------|
| Input Filter | Firewall (Packet Filtering) |
| Semantic Guard | NGFW (Deep Packet Inspection) |
| Sandwich Defense | DMZ |
| Instruction Hierarchy | Defense in Depth |
| Permission Validator (RBAC) | Access Control + IDS |
| Output Filter | DLP (Data Loss Prevention) |

## Setup

```bash
# Instalar dependencias
make install-ui

# Copiar e configurar API keys
cp .env.example .env
# Editar .env com suas chaves OpenAI e/ou Anthropic
```

## Como usar

### Streamlit UI (recomendado para demos)

```bash
make streamlit
# Abre em http://localhost:8501
```

6 paginas: Visao Geral, Arena Interativa, Suite de Ataques, Multi-Turn, Benchmark de Modelos, Relatorio.

### CLI

```bash
# Chat interativo
python -m src.demo chat --mode baseline
python -m src.demo chat --mode defended

# Suite automatizada de ataques
python -m src.demo attack --quick

# Gerar relatorio com graficos
python -m src.demo report --quick

# Comparacao lado a lado
python -m src.demo compare
```

### Testes

```bash
make test
# 152 testes passando
```

## Arquitetura

```
src/
├── agent/          # Agentes LangGraph (baseline + defendido)
├── blue_team/      # 6 camadas de defesa
├── red_team/       # 7 categorias de ataque (~90 payloads)
├── evaluation/     # Metricas, comparacao, benchmark multi-modelo
├── core/           # LLM wrapper, tools, RBAC, sandbox
├── data/           # SQLite manager + seed data
├── visualization/  # Terminal (Rich) + charts (Matplotlib)
└── streamlit_app/  # Interface web interativa (Plotly)
```

## Benchmark Multi-Modelo

| Modelo | ASR (Baseline) |
|--------|---------------|
| gpt-4.1-nano | 85.7% |
| gpt-4.1-mini | 42.9% |
| claude-haiku-4.5 | 14.3% |

## Stack

Python 3.11+ · LangGraph · LiteLLM · Streamlit · Plotly · SQLite · Rich
