# Evaluation Methodology

## 1. Experimental Setup

All experiments are conducted with N=5 independent trials using different random seeds to ensure statistical robustness. Results are reported as mean ± standard deviation across trials. Statistical significance of comparisons is determined using paired t-tests with significance level α=0.05.

For each experiment, we record:
- Model name and version string
- Temperature parameter
- Random seed
- All other relevant hyperparameters
- Timestamp of execution

This ensures full reproducibility and enables post-hoc analysis of parameter sensitivity.

## 2. Attack Suite

The attack suite comprises 8 categories covering distinct prompt injection vectors:

1. **Instruction Override** - Direct attempts to replace the original task with adversarial instructions
2. **Persona Switching** - Attacks that request the model adopt alternative personas or roles with modified behavior
3. **Encoding Attacks** - Base64, ROT13, hexadecimal, and other encoding schemes to obfuscate malicious payloads
4. **Context Manipulation** - Fake tool outputs, fabricated documents, and contextual contradictions
5. **Multi-turn** - Sequential interactions designed to gradually manipulate behavior across conversation history
6. **Indirect Injection** - Prompts embedded in tool inputs (database queries, file contents) that execute indirectly
7. **Side-channel** - Timing attacks, resource exhaustion, and information leakage exploits
8. **Portuguese** - Portuguese-language attacks testing cross-lingual vulnerability and defense transfer

Each category employs parameterized attack templates, allowing systematic variation of key elements (instruction length, obfuscation level, context depth). In total, the suite contains approximately 100+ distinct attack payloads, which are tested both individually and in combination to measure interaction effects.

## 3. Defense Evaluation

Defense mechanisms are evaluated through a complete ablation study:

- **Baseline (No Defense)** - Unmodified system with no protective measures
- **Individual Defenses** - Each defense layer tested independently
- **Minimal Viable Set** - Smallest combination of defenses providing meaningful protection
- **Full Stack** - All available defenses applied together

For each configuration, we measure:
- **Attack Success Rate (ASR) reduction** - Percentage point decrease in successful attacks
- **False Positive Rate (FPR) increase** - Impact on legitimate task performance
- **Pareto frontier analysis** - Identifying configurations that optimize ASR reduction per unit FPR cost

This approach enables identification of practical defense combinations suitable for deployment constraints.

## 4. Scoring Methodology

We employ dual scoring mechanisms to ensure robustness:

### Primary Scoring: Regex-Based Detection
Evidence of successful prompt injection is identified through deterministic, reproducible regex patterns applied to model outputs. This method provides:
- Consistency across runs
- Reproducibility without external dependencies
- Clear audit trail of detection logic

### Secondary Scoring: LLM-as-Judge
To validate regex-based results and detect sophisticated attacks, we employ GPT-4.1 as an independent judge. For each test case:
- Three independent judge calls are executed
- Majority voting determines final judgment
- All judge calls use identical prompting and temperature settings

### Inter-method Agreement
We report Cohen's kappa coefficient measuring agreement between regex-based and LLM-as-judge scoring methods. High agreement validates detection methodology; divergence indicates cases requiring manual inspection.

## 5. Models Under Test

### Small/Open-Source Models
- **Llama 3.2 (3B)** - Meta's latest compact model
- **Llama 3.1 (8B)** - Meta's 8B baseline
- **Phi-3-mini (3.8B)** - Microsoft's efficient model
- **Qwen 2.5 (7B)** - Alibaba's multilingual model
- **Mistral (7B)** - Mistral AI's 7B model

### Commercial Models
- **GPT-4.1-nano** - OpenAI's lightweight commercial offering
- **GPT-4.1-mini** - OpenAI's mid-range commercial model
- **Claude Haiku 4.5** - Anthropic's compact model

All models are tested with:
- Identical system prompts specifying agent behavior
- Identical tool configurations (SQLite database and filesystem access)
- Temperature=0 where supported for deterministic outputs
- Standardized input/output interfaces

## 6. Research Questions

**RQ1: Commercial vs. Open-Source Vulnerability**
How do small open-source LLMs (3B-8B parameters) compare to commercial models in susceptibility to prompt injection attacks when deployed as tool-augmented agents?

**RQ2: Attack Effectiveness**
Which attack categories are most effective against agents with access to persistent tools and real data stores?

**RQ3: Defense-in-Depth Optimization**
How effective is layered defense composition? Which defense combinations provide optimal attack success rate reduction while minimizing false positive rate impact?

**RQ4: Cross-Lingual Defense Transfer**
Do defenses designed for English-language attacks effectively mitigate Portuguese-language prompt injection attempts?

## 7. Reproducibility

All code, data, attack payloads, and experimental configurations are published on GitHub with open-source licensing. Each experiment is associated with:
- Exact model version strings (including commit hashes for local models)
- Seed specifications enabling deterministic re-execution
- Complete tool configuration snapshots
- Environment specifications (runtime versions, library versions)

Fixed temperature=0 is used for all deterministic model variants, enabling bit-for-bit result reproduction across multiple executions. For models not supporting zero temperature, we use the lowest available temperature setting with explicit documentation of this constraint.

This comprehensive logging enables independent verification, meta-analysis across studies, and extension by the research community.
