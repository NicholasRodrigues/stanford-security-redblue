"""Security concept mapping — links attacks/defenses to course topics."""

ATTACK_CONCEPTS = {
    "instruction_override": {
        "titulo": "Instruction Override",
        "icone": "\u2694\ufe0f",
        "analogia_curso": "Escalacao de Privilegios (Pentesting)",
        "explicacao": (
            "Assim como um atacante tenta escalar privilegios apos ganhar acesso inicial "
            "durante um pentest, o instruction override tenta substituir as regras do sistema "
            "para obter acesso nao autorizado a dados privados. Mapeia para a fase de "
            "exploracao do pentesting."
        ),
        "conceitos": ["Pentesting: exploitation", "Privilege escalation"],
    },
    "persona_switching": {
        "titulo": "Persona Switching / DAN",
        "icone": "\U0001f3ad",
        "analogia_curso": "Engenharia Social + Cavalo de Troia",
        "explicacao": (
            "Como um cavalo de troia que se disfarca de software legitimo, o DAN jailbreak "
            "tenta fazer o modelo assumir uma persona falsa sem restricoes. Tambem e uma forma "
            "de engenharia social — manipular o 'comportamento' do sistema para contornar "
            "controles de seguranca."
        ),
        "conceitos": ["Malware: Trojans", "Social Engineering: pretexting"],
    },
    "encoding_attacks": {
        "titulo": "Encoding Attacks",
        "icone": "\U0001f510",
        "analogia_curso": "Ofuscacao de Payloads (Malware)",
        "explicacao": (
            "Similar a como malware usa ofuscacao (polimorfismo, packing, encoding) para evadir "
            "deteccao por antivirus e IDS, ataques de encoding codificam instrucoes maliciosas "
            "em Base64, ROT13 ou hexadecimal para burlar filtros de entrada. "
            "Tecnica classica de evasao."
        ),
        "conceitos": ["Malware: payload obfuscation", "Evasion techniques", "Polymorphism"],
    },
    "context_manipulation": {
        "titulo": "Context Manipulation",
        "icone": "\U0001f500",
        "analogia_curso": "Spoofing + Violacao de DMZ",
        "explicacao": (
            "Assim como ataques de spoofing falsificam a origem de pacotes de rede para "
            "atravessar firewalls, a manipulacao de contexto injeta delimitadores falsos e "
            "mensagens de sistema falsas para confundir os limites de confianca do modelo. "
            "E como violar os limites de uma DMZ."
        ),
        "conceitos": ["Spoofing", "DMZ boundary violations", "Delimiter injection"],
    },
    "multi_turn": {
        "titulo": "Multi-Turn Escalation",
        "icone": "\U0001f4c8",
        "analogia_curso": "Ciclo de Pentesting (Recon \u2192 Exfiltracao)",
        "explicacao": (
            "Segue o modelo classico de pentesting: reconhecimento (mapear tabelas e schema), "
            "enumeracao (identificar dados sensiveis), e exfiltracao (extrair os dados). "
            "Simula as fases de um APT (Advanced Persistent Threat) real."
        ),
        "conceitos": ["Pentesting lifecycle", "APT", "Recon \u2192 Exploitation \u2192 Exfiltration"],
    },
    "indirect_injection": {
        "titulo": "Indirect Injection",
        "icone": "\U0001f489",
        "analogia_curso": "Worms + Supply Chain Attack",
        "explicacao": (
            "Como um worm que se auto-propaga pela rede, a injecao indireta planta instrucoes "
            "maliciosas nos dados que o agente processa. O agente 'se infecta' ao ler dados "
            "envenenados — similar a um supply chain attack ou watering hole attack "
            "onde a fonte confiavel e comprometida."
        ),
        "conceitos": ["Malware: worms", "Supply chain attacks", "Data poisoning"],
    },
    "side_channel": {
        "titulo": "Side-Channel / Exfiltracao Lateral",
        "icone": "\U0001f441\ufe0f",
        "analogia_curso": "Reconhecimento Passivo (Pentesting)",
        "explicacao": (
            "Na fase passiva do pentesting, o atacante coleta informacoes sem interagir "
            "diretamente com o alvo — nomes de tabelas, schemas, contagens de registros. "
            "Ataques de canal lateral extraem metadados que revelam a estrutura do sistema "
            "e facilitam ataques subsequentes."
        ),
        "conceitos": ["Pentesting: passive recon", "Information disclosure", "Fingerprinting"],
    },
}

DEFENSE_CONCEPTS = {
    "input_filter": {
        "titulo": "Input Filter",
        "icone": "\U0001f6e1\ufe0f",
        "analogia_curso": "Firewall de Filtragem de Pacotes (Gen 1)",
        "explicacao": (
            "Funciona como um firewall de primeira geracao: examina cada entrada contra "
            "regras pre-definidas (regex patterns) e bloqueia mensagens que correspondem "
            "a padroes de ataque conhecidos. Rapido e eficiente, mas pode ser evadido "
            "por tecnicas de ofuscacao — assim como packet filtering e vulneravel a spoofing."
        ),
        "conceitos": ["Firewall: packet filtering", "Signature-based detection"],
    },
    "semantic_guard": {
        "titulo": "Semantic Guard",
        "icone": "\U0001f9e0",
        "analogia_curso": "NGFW com Deep Packet Inspection (Gen 3)",
        "explicacao": (
            "Como um Next-Generation Firewall que faz Deep Packet Inspection (DPI), "
            "o semantic guard analisa a intencao semantica da mensagem, nao apenas padroes "
            "superficiais. Classifica a intencao como benigna, injecao, escalacao ou "
            "exfiltracao — similar a um IDS/IPS inteligente."
        ),
        "conceitos": ["NGFW", "Deep Packet Inspection", "IDS/IPS"],
    },
    "context_separation": {
        "titulo": "Sandwich Defense",
        "icone": "\U0001f9f1",
        "analogia_curso": "DMZ (Zona Desmilitarizada)",
        "explicacao": (
            "Assim como uma DMZ isola servicos publicos (Web, FTP) da rede interna "
            "corporativa, o sandwich defense coloca a entrada do usuario entre duas camadas "
            "de instrucoes do sistema, criando uma zona de separacao de contexto que "
            "impede que instrucoes do usuario sobrescrevam regras do sistema."
        ),
        "conceitos": ["DMZ", "Network segmentation", "Defense in depth"],
    },
    "instruction_hierarchy": {
        "titulo": "Instruction Hierarchy",
        "icone": "\U0001f3d7\ufe0f",
        "analogia_curso": "Defense in Depth (Niveis de Confianca)",
        "explicacao": (
            "Implementa niveis de confianca hierarquicos (System > Developer > User > External), "
            "similar ao principio de defense in depth onde cada camada tem um nivel de "
            "privilegio diferente. Instrucoes de menor confianca nao podem sobrescrever as de maior."
        ),
        "conceitos": ["Defense in depth", "Trust levels", "Least privilege"],
    },
    "permission_validator": {
        "titulo": "Permission Validator (RBAC)",
        "icone": "\U0001f511",
        "analogia_curso": "Controle de Acesso + IDS",
        "explicacao": (
            "Combina RBAC (Role-Based Access Control) com deteccao de anomalias. "
            "Como um sistema IDS que monitora padroes de acesso suspeitos, detecta "
            "tentativas de escalacao subita de privilegios — um usuario publico "
            "tentando acessar recursos de admin."
        ),
        "conceitos": ["RBAC", "IDS: anomaly detection", "Access control"],
    },
    "output_filter": {
        "titulo": "Output Filter",
        "icone": "\U0001f50d",
        "analogia_curso": "DLP (Data Loss Prevention)",
        "explicacao": (
            "Funciona como um sistema DLP que monitora dados saindo da rede. "
            "Escaneia respostas do agente procurando dados sensiveis (SSNs, nomes, "
            "salarios) e os redacta antes de chegar ao usuario — a ultima linha "
            "de defesa contra exfiltracao de dados."
        ),
        "conceitos": ["DLP", "Egress filtering", "Data sanitization"],
    },
}
