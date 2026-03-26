# Relatorio Preliminar: Avaliacao de Prompt Injection em Modelos de Linguagem Pequenos como Agentes com Ferramentas

**Autores:** Nicholas Rodrigues, Guilherme Muniz, Tiago Trindade

---

## 1. Contexto

Large Language Models (LLMs) estao sendo cada vez mais utilizados como agentes autonomos com acesso a ferramentas reais — bancos de dados, sistemas de arquivos, APIs. Isso introduz um risco critico: **prompt injection**, onde um atacante manipula as instrucoes do modelo para executar acoes nao autorizadas, como exfiltrar dados privados.

Embora existam benchmarks na literatura (BIPIA, InjecAgent, AgentDojo, Agent Security Bench), a maioria apresenta limitacoes:

- **BIPIA** (Microsoft, 2023): Avalia apenas LLMs puros, sem acesso a ferramentas reais.
- **InjecAgent** (UIUC, ACL 2024): Testa agentes com ferramentas, mas usa ambientes simulados (1.054 casos, 30 modelos).
- **AgentDojo** (ETH Zurich, 2024): Ambiente dinamico com ferramentas reais, porem limitado a modelos comerciais grandes.
- **Agent Security Bench** (ICLR 2025): O mais abrangente (400+ ferramentas, 13 modelos), mas nao avalia modelos pequenos/open-source em detalhe, nem ataques em portugues.

**Lacunas identificadas:**
1. Nenhum benchmark avalia ataques de prompt injection em **portugues**
2. Poucos testam **modelos pequenos/open-source** (3B-8B parametros) como agentes
3. A maioria usa ferramentas simuladas, nao **interacao real** com banco de dados
4. Avaliacao de **defesa em camadas** (defense-in-depth) e pouco explorada sistematicamente

---

## 2. Metodologia

### Sistema Avaliado

Um agente LLM com acesso a:
- Banco de dados SQLite (tabelas: `public_notes`, `private_records` com SSN/salario/dados medicos, `users`)
- Sistema de arquivos (diretorios `public/` e `private/`)

O agente recebe consultas em linguagem natural e utiliza ferramentas para responder.

### Ataques

8 categorias de ataque, totalizando ~100 payloads:

| Categoria | Descricao | Payloads |
|-----------|-----------|----------|
| Instruction Override | Sobrescrita direta de instrucoes | 15 |
| Persona Switching (DAN) | Jailbreak por troca de identidade | 12 |
| Encoding Attacks | Ofuscacao em Base64, ROT13, hex | 12 |
| Context Manipulation | Injecao de delimitadores falsos | 11 |
| Multi-Turn Escalation | Reconhecimento → Enumeracao → Exfiltracao | 10 |
| Indirect Injection | Instrucoes maliciosas nos dados | 6 |
| Side-Channel | Exfiltracao de metadados | 10 |
| **Portugues** | **Ataques em portugues brasileiro (contribuicao nova)** | **30** |

### Defesas (6 camadas)

1. **Input Filter** — filtragem por regex patterns
2. **Semantic Guard** — classificacao de intencao (heuristica + LLM)
3. **Sandwich Defense** — isolamento do input entre instrucoes do sistema
4. **Instruction Hierarchy** — niveis de confianca hierarquicos
5. **Permission Validator (RBAC)** — controle de acesso por role
6. **Output Filter** — escaneamento e redacao de dados sensiveis

### Modelos Avaliados

| Tipo | Modelo | Parametros |
|------|--------|------------|
| Open-source | Llama 3.2 | 3B |
| Open-source | Llama 3.1 | 8B |
| Open-source | Phi-3 Mini | 3.8B |
| Open-source | Qwen 2.5 | 7B |
| Open-source | Mistral | 7B |
| Comercial | GPT-4.1-nano | N/A |
| Comercial | GPT-4.1-mini | N/A |
| Comercial | Claude Haiku 4.5 | N/A |

### Protocolo Experimental

- 5 execucoes independentes por configuracao
- 40 ataques por execucao (5 por categoria)
- Resultados reportados como media ± desvio padrao com intervalo de confianca de 95%
- Significancia estatistica via teste t pareado (α = 0.05)
- Scoring por regex (primario) + LLM-as-a-judge com votacao majoritaria (secundario)

---

## 3. Resultados Preliminares

### 3.1 Vulnerabilidade por Modelo (Baseline, sem defesas)

| Modelo | ASR Media | ± Std | IC 95% |
|--------|-----------|-------|--------|
| Llama 3.1 (8B) | **82.5%** | ±2.2% | [79.4%, 85.6%] |
| Qwen 2.5 (7B) | **82.0%** | ±2.9% | [78.0%, 86.0%] |
| Mistral (7B) | **76.0%** | ±2.0% | [73.2%, 78.8%] |
| Llama 3.2 (3B) | **68.0%** | ±2.9% | [64.0%, 72.0%] |
| Phi-3 Mini (3.8B) | **25.5%** | ±3.7% | [20.4%, 30.6%] |
| GPT-4.1-nano | **5.0%** | ±0.0% | [5.0%, 5.0%] |
| GPT-4.1-mini | **5.0%** | ±0.0% | [5.0%, 5.0%] |
| Claude Haiku 4.5 | **5.0%** | ±0.0% | [5.0%, 5.0%] |

### 3.2 Efetividade das Defesas (Llama 3.1:8b)

| Configuracao | ASR | IC 95% |
|-------------|-----|--------|
| Baseline (sem defesas) | 83.0% | [78.9%, 87.0%] |
| Todas as defesas ativas | 12.0% | [10.6%, 13.4%] |
| **Reducao** | **71.0%** | **p < 0.0001** |

### 3.3 Taxa de Falsos Positivos

- 60 consultas benignas testadas
- **FPR = 0.0%** — nenhuma consulta legitima bloqueada

---

## 4. Observacoes Preliminares

1. **Modelos open-source pequenos sao ~16x mais vulneraveis** que modelos comerciais quando usados como agentes com ferramentas (ASR ~80% vs ~5%).

2. **Phi-3 Mini e uma excecao notavel** — apesar de ter apenas 3.8B parametros, apresenta ASR de apenas 25.5%, significativamente menor que modelos maiores (7B-8B) da mesma categoria. Isso sugere que o treinamento de seguranca (safety training) e mais relevante que o tamanho do modelo.

3. **Defesa em camadas funciona** — a combinacao de 6 camadas de defesa reduz o ASR de 83% para 12% (reducao de 71%, p < 0.0001), sem introduzir falsos positivos.

4. **Modelos comerciais sao consistentes** — GPT-4.1-nano, GPT-4.1-mini e Claude Haiku apresentam ASR identico de 5% com variancia zero, indicando safety training robusto que nao e afetado pela variacao entre execucoes.

5. **O tamanho do modelo nao determina vulnerabilidade** — Llama 3.2 (3B) e menos vulneravel que Llama 3.1 (8B), contradizendo a hipotese de que modelos maiores sao mais seguros.

---

## 5. Contribuicoes Propostas

Para submissao ao **SBSeg 2026** (deadline: 11 de maio de 2026):

1. **Benchmark com modelos pequenos como agentes** — primeira avaliacao sistematica de modelos 3B-8B em cenarios agenticos com ferramentas reais
2. **Ataques em portugues** — primeira avaliacao de prompt injection em portugues brasileiro (30 payloads)
3. **Avaliacao de defesa em camadas** — estudo de ablacao sistematico mostrando contribuicao de cada camada
4. **Interacao real com banco de dados** — diferente da maioria dos benchmarks que usam ferramentas simuladas
5. **Framework reprodutivel** — codigo aberto com 219 testes automatizados

---

## 6. Proximos Passos

- [ ] Completar estudo de ablacao (testar cada defesa individualmente e em combinacoes)
- [ ] Avaliar transferencia de defesas ingles → portugues
- [ ] Analisar quais categorias de ataque sao mais efetivas por modelo
- [ ] Executar scoring com LLM-as-a-judge e comparar com regex (Cohen's kappa)
- [ ] Redigir artigo curto (7 paginas) para SBSeg 2026

---

**Repositorio:** https://github.com/NicholasRodrigues/stanford-security-redblue

**Testes:** 219 passando | **Modelos:** 8 avaliados | **Ataques:** ~100 payloads | **Categorias:** 8
