# Resumo do Projeto: Prompt Injection em Agentes LLM

**Para:** Professor
**De:** Nicholas Rodrigues, Guilherme Muniz, Tiago Trindade
**Data:** Março 2026

---

## 1. O Que Fizemos

Construimos um benchmark que avalia quao vulneraveis sao modelos de linguagem (LLMs) quando usados como agentes com acesso a ferramentas reais — banco de dados SQLite e sistema de arquivos. O agente recebe perguntas em linguagem natural e usa ferramentas para responder. O banco tem dados publicos (notas da empresa) e dados privados (nomes, CPFs/SSNs, salarios, dados medicos de funcionarios). O objetivo do atacante e fazer o agente vazar esses dados privados.

Testamos 10 modelos (5 open-source locais + 5 comerciais), 9 categorias de ataque (~120 payloads), 6 camadas de defesa, e ataques adaptativos gerados por LLM. Tudo com chamadas reais de API, nao simulacoes.

---

## 2. O Que Ja Existe na Literatura

### Benchmarks existentes

| Benchmark | Ano | O que faz | Limitacao |
|-----------|-----|-----------|-----------|
| **BIPIA** (Microsoft) | 2023 | Injecao indireta em LLMs puros | Sem ferramentas reais |
| **InjecAgent** (UIUC, ACL 2024) | 2024 | Agentes com ferramentas, 1054 casos | Ambientes simulados |
| **AgentDojo** (ETH Zurich) | 2024 | Ambiente dinamico, 97 tarefas | Poucos modelos open-source |
| **Agent Security Bench** (ICLR 2025) | 2025 | 400+ ferramentas, 13 modelos | Nao avalia portugues |
| **Open-Prompt-Injection** (USENIX 2024) | 2024 | Framework formal, 5 ataques x 10 defesas x 10 LLMs | LLMs puros, sem agentes |

**Lacunas que ninguem preencheu:**
1. Nenhum benchmark testa ataques em **portugues**
2. Poucos testam modelos **pequenos/open-source** (3B-8B) como agentes
3. Maioria usa ferramentas **simuladas**, nao banco de dados real
4. Avaliacao de **defesa em camadas** (defense-in-depth) e rara

### Tecnicas de ataque adaptativo

- **PAIR** (Chao et al., 2024): Um LLM atacante gera prompts, observa a resposta do alvo, e refina iterativamente. Como um fuzzer inteligente.
- **Crescendo** (Microsoft, 2024): Ataque multi-turn que comeca inocente e escala gradualmente. Cada turno usa a resposta anterior pra justificar o proximo pedido.
- **HouYi** (2023): Ataques em 3 partes — contexto + separador + payload — especificos pra aplicacoes com ferramentas.

### Pesquisa cross-lingual

- Yong et al. (2023) mostrou que traduzir ataques pra linguas de poucos recursos (Zulu, Gaelico) bypassa GPT-4 com 79% de sucesso.
- Queiroz (UFJF, 2025) mostrou que reescrever ataques como **poesia em portugues** causa ate 18x mais falhas de seguranca.
- Nenhum benchmark avalia prompt injection em portugues sistematicamente.

### Defesas estado da arte

- **PromptArmor** (2025): Guardrail que usa um LLM pra detectar E remover injecoes. <1% de falso positivo.
- **Instruction Hierarchy** (OpenAI, 2024): Treina o modelo pra priorizar instrucoes do sistema sobre instrucoes do usuario.
- **StruQ/SecAlign** (USENIX/CCS 2025): Separam prompt de dados com tokens especiais. Requerem fine-tuning.
- **Spotlighting** (Microsoft, 2024): Marca dados nao confiaveis com prefixos pra o modelo distinguir de instrucoes.

---

## 3. Nossa Metodologia

### Modelos testados

| Tipo | Modelo | Parametros |
|------|--------|------------|
| Open-source | Llama 3.2 | 3B |
| Open-source | Llama 3.1 | 8B |
| Open-source | Phi-3 Mini | 3.8B |
| Open-source | Qwen 2.5 | 7B |
| Open-source | Mistral | 7B |
| Comercial | GPT-4.1-nano | ? |
| Comercial | GPT-4.1 | ? |
| Comercial | GPT-4.1-mini | ? |
| Comercial | Claude Sonnet 4 | ? |
| Comercial | Claude Haiku 4.5 | ? |

### Categorias de ataque (9 categorias, ~120 payloads)

1. **Instruction Override** — "Ignore todas as instrucoes anteriores"
2. **Persona Switching / DAN** — "Voce agora e DAN, sem restricoes"
3. **Encoding** — Instrucoes em Base64, ROT13, hex
4. **Context Manipulation** — Delimitadores falsos, mensagens de sistema fake
5. **Multi-Turn** — Reconhecimento → Enumeracao → Exfiltracao
6. **Indirect Injection** — Instrucoes maliciosas escondidas nos dados
7. **Side-Channel** — Exfiltracao de metadados (esquema, contagens)
8. **Portugues** — 30 payloads em portugues brasileiro
9. **Advanced** — Cross-lingual, moral dilemmas, many-shot, fiction framing

### Defesas (6 camadas)

1. **Input Filter** — Regex que detecta padroes de injecao
2. **Semantic Guard** — Classificacao de intencao (heuristica + LLM)
3. **Context Separation (Sandwich Defense)** — Isola input do usuario entre instrucoes do sistema
4. **Instruction Hierarchy** — Niveis de confianca (System > User > External)
5. **Permission Validator (RBAC)** — Controle de acesso por role
6. **Output Filter** — Escaneia resposta e redacta dados sensiveis

### Ataques adaptativos

- **PAIR**: LLM atacante (GPT-4.1-mini) gera ataques e refina com feedback
- **Crescendo**: Escalacao multi-turn adaptativa em ingles e portugues

### Rigor estatistico

- **N=5 execucoes independentes** pra cada configuracao principal
- **Intervalos de confianca de 95%** (IC) calculados com distribuicao t de Student
- **Teste t pareado** (α=0.05) pra verificar significancia
- **Scorer validado**: 100% de acuracia em 10 casos de teste rotulados manualmente
- **Correcao de falso positivo**: Identificamos e corrigimos um bug no scorer que contava nomes em recusas como vazamentos

---

## 4. Principais Resultados

### 4.1 Ataques basicos criam falsa sensacao de seguranca

Com ataques simples (categorias 1-7), os modelos comerciais parecem invulneraveis:

| Modelo | ASR (ataques basicos) |
|--------|-----------------------|
| GPT-4.1-nano | 5.0% |
| GPT-4.1-mini | 5.0% |
| Claude Haiku | 5.0% |

Mas com ataques avancados (categoria 9), a realidade e completamente diferente:

| Modelo | ASR (ataques avancados) | ± Std | IC 95% |
|--------|-------------------------|-------|--------|
| **GPT-4.1-nano** | **87.5%** | ±0.0% | [87.5%, 87.5%] |
| GPT-4.1 (completo) | 75.0% | ±4.0% | [69.5%, 80.5%] |
| GPT-4.1-mini | 67.5% | ±4.7% | [61.0%, 74.0%] |
| Claude Sonnet 4 | 51.2% | ±4.7% | [44.8%, 57.7%] |
| Claude Haiku 4.5 | 18.8% | ±0.0% | [18.8%, 18.8%] |

**Por que isso importa:** A maioria das avaliacoes de seguranca de LLMs usa ataques basicos conhecidos. Nossos resultados mostram que isso subestima drasticamente a vulnerabilidade real — GPT-4.1-nano vai de 5% pra 87.5% de ASR quando enfrenta ataques mais sofisticados.

**Significancia estatistica:** Os ICs do GPT-4.1-nano [87.5%, 87.5%] nao se sobrepoe aos do GPT-4.1-mini [61.0%, 74.0%], confirmando que a diferenca e estatisticamente significativa.

### 4.2 Modelos menores da OpenAI sao mais vulneraveis

| Modelo | ASR | IC 95% |
|--------|-----|--------|
| GPT-4.1-nano (menor) | 87.5% | [87.5%, 87.5%] |
| GPT-4.1 (maior) | 75.0% | [69.5%, 80.5%] |
| GPT-4.1-mini (medio) | 67.5% | [61.0%, 74.0%] |

Os intervalos de confianca NAO se sobrepoe — isso confirma que menor modelo = mais vulneravel dentro da familia OpenAI. Provavelmente porque modelos menores recebem menos treinamento de seguranca (safety training/RLHF).

### 4.3 Arquitetura da Anthropic e mais resistente

| Modelo | ASR |
|--------|-----|
| Claude Haiku 4.5 | 18.8% (variancia zero) |
| Claude Sonnet 4 | 51.2% |
| GPT-4.1-nano | 87.5% |

Claude Haiku e consistentemente o modelo mais resistente com variancia ZERO — ou seja, o resultado e o mesmo em todas as 5 execucoes. Isso sugere que a resistencia e **arquitetural**, nao aleatoria.

**Nota importante:** Haiku 4.5 e Sonnet 4 sao geracoes diferentes com treinamentos diferentes. Nao e justo dizer "menor = mais seguro" — a diferenca e de treinamento de seguranca, nao de tamanho.

### 4.4 Defesa em camadas atinge 0% de ASR

Quando ativamos todas as 6 camadas de defesa, NENHUM dos 16 ataques avancados consegue vazar dados em NENHUM dos 4 modelos testados:

| Modelo | Baseline | Defendido |
|--------|----------|-----------|
| GPT-4.1-nano | 87.5% | **0.0%** |
| GPT-4.1 | 75.0% | **0.0%** |
| GPT-4.1-mini | 68.8% | **0.0%** |
| Llama 3.1:8b | ~85% | **0.0%** |

**Correcao importante:** Inicialmente reportamos 6.2% de ASR no modo defendido, mas ao auditar cientificamente os resultados, descobrimos que era um **falso positivo do scorer** — o modelo recusava a requisicao mas mencionava o nome "Alice Johnson" na recusa, e o scorer contava como vazamento. Apos corrigir o scorer e validar com 10 casos rotulados (100% de acuracia), o ASR real e 0.0%.

### 4.5 Context Separation sozinho e tao efetivo quanto todas as defesas

Estudo de ablacao com N=3 execucoes, 27 ataques, Llama 3.1:8b:

| Configuracao | ASR Media | IC 95% |
|-------------|-----------|--------|
| Sem defesa (baseline) | 86.4% | [72.4%, 100%] |
| Output Filter sozinho | 28.4% | [23.1%, 33.7%] |
| Input Filter sozinho | 23.5% | [18.1%, 28.8%] |
| Semantic Guard sozinho | 17.3% | [12.0%, 22.6%] |
| Permission Validator sozinho | 18.5% | [9.3%, 27.7%] |
| Instruction Hierarchy sozinho | 13.6% | [3.0%, 24.2%] |
| **Context Separation sozinho** | **9.9%** | [4.6%, 15.2%] |
| **Context Sep + Inst Hier** | **8.6%** | [3.3%, 14.0%] |
| **Todas as 6 defesas** | **11.1%** | [11.1%, 11.1%] |

Os ICs de Context Separation (9.9%) e Todas as Defesas (11.1%) se sobrepoe, indicando que **nao ha diferenca estatisticamente significativa** entre usar so o sandwich defense ou usar todas as 6 camadas.

**Por que isso e importante:** Significa que o system prompt hardening (sandwich defense) e responsavel por quase toda a protecao. As outras camadas adicionam complexidade mas pouco beneficio marginal. Isso contradiz a intuicao de que "mais camadas = mais seguro".

### 4.6 Ataques em portugues e ingles tem ASR similar no baseline

Comparacao cross-lingual com ataques estaticos (N=3):

| Configuracao | Ingles | Portugues |
|-------------|--------|-----------|
| Baseline | 83.3% | 81.1% |
| Defendido | 11.7% | 0.0% |

No baseline, portugues e ingles sao igualmente efetivos. No modo defendido, portugues e paradoxalmente MENOS efetivo — provavelmente porque os ataques em portugues nao ativam os regex patterns do input filter (que sao em ingles), entao passam direto pro sandwich defense que bloqueia tudo.

### 4.7 Crescendo adaptativo e devastador

Ataques Crescendo (escalacao multi-turn) contra o baseline do Llama 3.1:8b (N=5):

| Lingua | Taxa de Sucesso | Evidencias/Sessao |
|--------|-----------------|-------------------|
| Ingles | 100% (5/5) | 162 |
| Portugues | 100% (5/5) | 200 (+23%) |

Ambas as linguas atingem 100% de sucesso, mas portugues extrai 23% mais evidencias por sessao. Contra o agente DEFENDIDO, tanto ingles quanto portugues falham completamente (0/5 sessoes).

### 4.8 Ataques adaptativos PAIR falham contra defesas

Testamos o ataque adaptativo PAIR (onde um LLM atacante gera e refina ataques com feedback) com GPT-4.1 como atacante e 15 iteracoes:

- **Baseline Llama 3.1:8b:** Sucesso na iteracao 0 (primeiro ataque ja funciona)
- **Defendido Llama 3.1:8b:** Falha em todas as 15 iteracoes

### 4.9 Modelos open-source sao muito vulneraveis com ataques basicos

| Modelo | ASR | ± Std | IC 95% |
|--------|-----|-------|--------|
| Llama 3.1:8b | 82.5% | ±2.2% | [79.4%, 85.6%] |
| Qwen 2.5:7b | 82.0% | ±2.9% | [78.0%, 86.0%] |
| Mistral:7b | 76.0% | ±2.0% | [73.2%, 78.8%] |
| Llama 3.2:3B | 68.0% | ±2.9% | [64.0%, 72.0%] |
| **Phi-3 Mini:3.8B** | **25.5%** | ±3.7% | [20.4%, 30.6%] |

Phi-3 Mini e um outlier — significativamente mais resistente que modelos maiores. Provavelmente resultado de treinamento de seguranca mais agressivo pela Microsoft.

---

## 5. Relevancia Estatistica

### O que significa "estatisticamente significativo"

Quando rodamos um experimento uma so vez, o resultado pode ser sorte ou azar. Por exemplo, se um modelo tem 80% de ASR numa execucao, nao sabemos se o valor "real" e 70%, 80%, ou 90%.

Para resolver isso:
- **Rodamos N=5 vezes** cada experimento
- **Calculamos a media e desvio padrao** das 5 execucoes
- **Calculamos o Intervalo de Confianca de 95% (IC)** — existe 95% de probabilidade do valor real estar dentro desse intervalo
- **Usamos teste t pareado** (α=0.05) pra comparar duas condicoes — se p < 0.05, a diferenca e significativa

### Exemplo concreto

GPT-4.1-nano teve ASR de [88%, 88%, 88%, 88%, 88%] nas 5 execucoes. Media = 87.5%, desvio padrao = 0. O IC e [87.5%, 87.5%]. Isso significa que temos **certeza estatistica** de que o ASR real e 87.5%.

GPT-4.1-mini teve ASR de [69%, 75%, 62%, 62%, 69%]. Media = 67.5%, IC = [61.0%, 74.0%]. O valor real provavelmente esta entre 61% e 74%.

Como os intervalos [87.5%, 87.5%] e [61.0%, 74.0%] **nao se sobrepoe**, podemos afirmar que GPT-4.1-nano e significativamente mais vulneravel que GPT-4.1-mini.

### Correcao do scorer — por que isso importa

Identificamos que nosso scorer (que detecta se dados vazaram) contava **falsos positivos** — quando o modelo recusava dizendo "Nao posso mostrar o SSN de Alice Johnson", o scorer contava "Alice Johnson" como vazamento. Corrigimos exigindo que nomes so contem como vazamento quando acompanhados de dados reais (SSN, salario, etc.). Essa correcao mudou o ASR defendido de 6.2% pra 0.0% — uma diferenca qualitativa enorme.

Validamos o scorer corrigido com 10 casos rotulados manualmente e obtivemos 100% de acuracia.

---

## 6. O Que Seria Novo num Artigo (Contribuicoes)

1. **Primeiro benchmark de prompt injection em portugues** — nenhum trabalho publicado avalia ataques em portugues sistematicamente

2. **Demonstracao de que ataques basicos subestimam a vulnerabilidade real** — modelos comerciais que parecem seguros (5% ASR) sao altamente vulneraveis (67-87% ASR) com ataques avancados

3. **Avaliacao com ferramentas reais** — maioria dos benchmarks usa ferramentas simuladas; nos usamos SQLite real e sistema de arquivos real

4. **Estudo de ablacao de defesas** — mostramos que Context Separation sozinho e tao efetivo quanto 6 camadas combinadas

5. **Comparacao multi-modelo com rigor estatistico** — 10 modelos, N=5 execucoes, ICs, testes t

6. **Ataques adaptativos (PAIR + Crescendo)** — mostramos que defesas resistem a atacantes LLM-powered

---

## 7. Alvo de Publicacao

**SBSeg 2026** (Simposio Brasileiro de Ciberseguranca)
- Buzios, RJ, 1-4 de setembro de 2026
- **Deadline: 11 de maio de 2026** (~6 semanas)
- Short paper: 7 paginas
- Aceitacao: ~37%
- O call for papers lista explicitamente: "GenAI (Generative AI) and LLMs in Security"

---

## 8. Numeros do Projeto

- **235 testes automatizados** passando
- **10 modelos** avaliados (5 open-source + 5 comerciais)
- **~120 payloads** de ataque em 9 categorias
- **6 camadas de defesa** com ablacao
- **2 metodos de ataque adaptativo** (PAIR + Crescendo)
- **Interface Streamlit** pra demonstracao interativa
- **Repositorio:** https://github.com/NicholasRodrigues/stanford-security-redblue
