"""
Technical Domain Detection Engine for Patent Novelty Assessment.

Maps proposed invention titles, descriptions, and queries to specific, professional
technical domains (e.g., 'Smart Waste Management', 'Computer Vision', 'IoT Automation',
'Biomedical Devices', 'Renewable Energy') rather than generic labels.
"""

import re
from typing import List, Tuple, Any, Optional

# Targeted technical domain definitions ordered by specificity
DOMAIN_RULES: List[Tuple[str, List[str], List[str]]] = [
    # 1. Smart Water Pipeline Monitoring & Leak Detection
    (
        "Smart Water Pipeline Monitoring",
        [
            "water pipeline", "pipeline leak", "leak detection", "water monitoring", "acoustic leak",
            "pipe leak", "water distribution", "pipe pressure", "water network", "pipeline monitoring",
            "leakage detection", "pipeline inspection", "acoustic sensor", "pipe burst", "flow monitoring"
        ],
        ["smart", "monitoring", "leak", "pipeline", "acoustic", "sensor", "detection", "pressure"]
    ),

    # 2. Smart Waste Management & Environmental Automation
    (
        "Intelligent Waste Management Systems",
        ["waste", "garbage", "trash", "recycle", "recycling", "segregation", "bin", "litter", "landfill"],
        ["intelligent", "smart", "system", "automated", "ai", "vision", "sensor", "iot"]
    ),
    (
        "Smart Waste Management",
        ["waste", "garbage", "trash", "recycle", "recycling", "segregation", "bin", "litter", "landfill"],
        ["smart", "iot", "automated", "automation", "sorter", "sorting", "classification"]
    ),
    (
        "Waste Management & Recycling",
        ["waste", "garbage", "trash", "recycle", "recycling", "segregation", "solid waste", "refuse", "compost"],
        []
    ),

    # 3. Computer Vision & Visual AI
    (
        "Computer Vision Classification",
        [
            "computer vision", "object detection", "image classification", "visual recognition",
            "yolo", "cnn", "convolutional neural", "image segmentation", "facial recognition",
            "optical inspection", "camera-based", "visual inspection", "pattern recognition",
            "image processing", "video surveillance", "feature extraction"
        ],
        []
    ),

    # 4. Medical Diagnostic Devices & Biosensors
    (
        "Medical Diagnostic Devices",
        [
            "biosensor", "biomedical", "medical device", "patient monitoring", "vital signs",
            "health monitor", "wearable sensor", "ecg", "eeg", "emg", "microfluidic",
            "diagnostic device", "cardiac", "glucose monitor", "pulse oximeter", "prosthetic",
            "implant", "catheter", "therapeutic device", "surgical robot", "telemedicine",
            "sweat sensor", "electrolyte", "clinical diagnosis"
        ],
        []
    ),

    # 5. Renewable Energy Systems
    (
        "Renewable Energy Systems",
        [
            "solar", "photovoltaic", "solar cell", "solar panel", "wind turbine",
            "renewable energy", "clean energy", "energy harvesting", "fuel cell",
            "geothermal", "hydroelectric", "biomass energy", "ocean energy", "tidal power"
        ],
        []
    ),

    # 6. IoT & Smart Automation
    (
        "IoT Automation",
        [
            "iot", "internet of things", "smart sensor", "wireless sensor network",
            "connected device", "telemetry", "home automation", "building automation",
            "mqtt", "zigbee", "lora", "smart home", "ambient intelligence", "smart appliance"
        ],
        []
    ),

    # 7. Robotics & Autonomous Systems
    (
        "Robotics & Autonomous Systems",
        [
            "robot", "robotic", "autonomous vehicle", "self-driving", "drone", "uav",
            "unmanned aerial", "agv", "quadcopter", "robotic arm", "manipulator",
            "actuator", "kinematics", "slam", "path planning", "exoskeleton"
        ],
        []
    ),

    # 7. Electric Vehicles & Powertrain
    (
        "Electric Vehicles & Powertrain",
        [
            "electric vehicle", "ev", "powertrain", "electric motor", "regenerative braking",
            "charging station", "bms", "battery management system", "inverter drive", "hybrid vehicle"
        ],
        []
    ),

    # 8. Natural Language Processing & Generative AI
    (
        "Natural Language Processing",
        [
            "nlp", "natural language", "llm", "large language model", "speech recognition",
            "text processing", "sentiment analysis", "machine translation", "conversational ai",
            "transformer", "semantic search", "chatbot", "text generation"
        ],
        []
    ),

    # 9. Cybersecurity & Cryptography
    (
        "Cybersecurity & Cryptography",
        [
            "cybersecurity", "cryptography", "encryption", "blockchain", "malware",
            "intrusion detection", "authentication", "zero trust", "network security",
            "smart contract", "cryptographic", "data security"
        ],
        []
    ),

    # 10. Agricultural Automation & Agri-Tech
    (
        "Agricultural Automation",
        [
            "precision agriculture", "smart farming", "crop monitoring", "irrigation",
            "soil moisture", "greenhouse", "farm automation", "harvesting robot",
            "agricultural", "fertilizer application", "plant disease detection"
        ],
        []
    ),

    # 11. Industrial Automation & Smart Manufacturing
    (
        "Industrial Automation",
        [
            "scada", "plc", "industrial automation", "predictive maintenance",
            "smart manufacturing", "industry 4.0", "assembly line", "quality control",
            "pneumatic control", "factory automation", "cnc", "process automation"
        ],
        []
    ),

    # 12. Telecommunications & Networking
    (
        "Telecommunications & Networking",
        [
            "telecommunication", "5g", "6g", "antenna", "cellular network", "mimo",
            "rf transceiver", "beamforming", "satellite communication", "wireless network",
            "optical network", "mesh network", "modulation"
        ],
        []
    ),

    # 13. Energy Storage & Battery Systems
    (
        "Energy Storage & Battery Systems",
        [
            "lithium-ion", "battery pack", "solid-state battery", "supercapacitor",
            "energy storage", "anode", "cathode", "electrolyte", "battery cell"
        ],
        []
    ),

    # 14. Environmental Engineering & Water Technology
    (
        "Environmental Engineering",
        [
            "water purification", "air quality", "pollution control", "water treatment",
            "effluent treatment", "desalination", "carbon capture", "sewage treatment",
            "filtration membrane", "particulate matter"
        ],
        []
    ),

    # 15. Microelectronics & Embedded Systems
    (
        "Microelectronics & Embedded Systems",
        [
            "semiconductor", "vlsi", "microcontroller", "fpga", "integrated circuit",
            "embedded system", "asic", "pcb", "mems", "system on chip", "soc"
        ],
        []
    ),

    # 16. Advanced Materials & Metallurgy
    (
        "Advanced Materials Engineering",
        [
            "nanomaterials", "graphene", "composite material", "alloy", "metallurgy",
            "superalloy", "polymer composite", "nanocomposite", "smart material", "aerogel"
        ],
        []
    ),

    # 17. Biotechnology & Life Sciences
    (
        "Biotechnology & Life Sciences",
        [
            "biotechnology", "dna", "gene", "protein", "enzyme", "crispr", "genomic",
            "microbial", "fermentation", "cellular", "tissue engineering", "vaccine"
        ],
        []
    ),

    # 18. Aerospace & Avionics
    (
        "Aerospace Engineering",
        [
            "aerospace", "aircraft", "avionics", "spacecraft", "propulsion", "aerodynamic",
            "satellite", "flight control", "rocket", "altitude control"
        ],
        []
    )
]


def detect_technical_domain(
    query_text: str = "",
    title: str = "",
    description: str = "",
    patent_context: Any = None
) -> str:
    """
    Infers a precise, professional technical domain for the given invention.
    Evaluates:
    1. Invention Title
    2. Invention Description
    3. Retrieved Patent Context
    Never returns generic placeholders like 'General Engineering'.
    """
    clean_title = (title or "").strip()
    clean_desc = (description or "").strip()
    clean_query = (query_text or "").strip()

    # Extract title and description from user_query if passed as combined format
    if not clean_title and "Title:" in clean_query:
        t_match = re.search(r"Title:\s*(.+?)(?:\n|Description:)", clean_query, re.IGNORECASE)
        if t_match:
            clean_title = t_match.group(1).strip()
    if not clean_desc and "Description:" in clean_query:
        d_match = re.search(r"Description:\s*(.*)", clean_query, re.IGNORECASE | re.DOTALL)
        if d_match:
            clean_desc = d_match.group(1).strip()

    # Contextual patent text
    p_text = ""
    if patent_context:
        if isinstance(patent_context, list):
            p_text = " ".join([
                f"{p.get('title', '')} {p.get('field_of_invention', '')} {p.get('search_text', '')[:200]}"
                for p in patent_context[:3] if isinstance(p, dict)
            ])
        elif isinstance(patent_context, str):
            p_text = patent_context

    full_text = f"{clean_title} {clean_title} {clean_desc} {clean_query} {p_text}".lower()

    # Priority 1: Check direct exact domain naming in Title (e.g. "Smart Waste Management", "Computer Vision")
    title_lower = clean_title.lower()
    for domain_name, primary_kws, secondary_kws in DOMAIN_RULES:
        if domain_name.lower() in title_lower:
            return domain_name

    # Priority 2: Score against domain rules with high weighting for title matches
    best_domain = None
    highest_score = 0

    for domain_name, primary_kws, secondary_kws in DOMAIN_RULES:
        score = 0
        
        # Check primary keywords
        for pkw in primary_kws:
            pkw_lower = pkw.lower()
            if pkw_lower in title_lower:
                score += 5  # High priority for title match
            elif pkw_lower in full_text:
                score += 2

        # If primary keywords matched and secondary keywords exist, check them
        if score > 0 and secondary_kws:
            for skw in secondary_kws:
                skw_lower = skw.lower()
                if skw_lower in title_lower:
                    score += 3
                elif skw_lower in full_text:
                    score += 1
        elif score > 0 and not secondary_kws:
            # Domain has no required secondary kws, slightly boost
            score += 1

        if score > highest_score:
            highest_score = score
            best_domain = domain_name

    if best_domain and highest_score >= 2:
        return best_domain

    # Priority 3: Extract from invention title if available and meaningful
    if clean_title:
        # Strip common stopwords and generic words from title
        clean_name = re.sub(
            r"\b(a|an|the|system|device|apparatus|method|novel|new|and|for|using|with|based)\b",
            "",
            clean_title,
            flags=re.IGNORECASE
        ).strip()
        words = clean_name.split()
        if len(words) >= 2:
            extracted = " ".join(words[:3]).title()
            return f"{extracted} Systems"

    # Priority 4: Intelligent non-generic fallback based on common technical terms
    if any(k in full_text for k in ["mechanical", "gear", "engine", "motor", "chassis"]):
        return "Mechanical Automation Systems"
    if any(k in full_text for k in ["circuit", "voltage", "current", "power", "grid"]):
        return "Electrical Power & Control Systems"
    if any(k in full_text for k in ["chemical", "compound", "reaction", "synthesis"]):
        return "Chemical Process Engineering"
    if any(k in full_text for k in ["software", "data", "algorithm", "cloud", "platform"]):
        return "Intelligent Software Systems"

    return "Applied Engineering & Automation"
