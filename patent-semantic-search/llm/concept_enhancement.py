"""
AI Concept Enhancement engine — Patent Consultancy Recommendation Report.

Expands the user's original invention Title and Description into a professional
engineering assessment:
1. Enhanced Technical Concept (Core principle, key modules table, technical differentiators)
2. Suggested System Architecture (Flow description, architecture table)
3. Recommended Technologies & Tools (Categorized table with fit explanations)
4. Innovation Expansion Opportunities (Actionable cards with technical specs & patent benefits)
5. Future Enhancement Roadmap (Near-term and Long-term roadmap table)
6. Commercialization Potential (Business-oriented assessment table)

Does not repeat the invention title in generated paragraphs. Uses retrieved patents
only as contextual references without dominating the recommendations.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional

TECH_CATEGORIES = [
    "AI Model",
    "Processor",
    "Sensors",
    "Communication",
    "Database",
    "Dashboard",
    "Prototyping",
]


class ConceptEnhancementGenerator:
    """Produces the professional Patent Consultancy Recommendation Report."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()

    def generate(
        self,
        invention_title: str,
        invention_description: str,
        retrieved_patents: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        title = (invention_title or "").strip()
        description = (invention_description or "").strip()
        if not title and not description:
            return self._empty_result()

        patents = retrieved_patents or []
        if self.api_key:
            try:
                result = self._generate_with_gemini(title, description, patents)
                if result:
                    return self._normalize(result, title, description)
            except Exception as e:
                print(f"[ConceptEnhancementGenerator] Gemini API fallback: {e}")

        return self._fallback(title, description, patents)

    def _generate_with_gemini(
        self,
        title: str,
        description: str,
        patents: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prior_art_context = "None retrieved."
        if patents:
            lines = []
            for p in patents[:3]:
                lines.append(
                    f"- Title: {p.get('title', 'N/A')} | Field: {p.get('field_of_invention', 'N/A')} | "
                    f"Context (landscape reference only): {(p.get('search_text') or '')[:300]}"
                )
            prior_art_context = "\n".join(lines)

        prompt = f"""
You are a Senior Patent Engineering Consultant preparing a professional Patent Consultancy Recommendation Report.
Your objective is to help the inventor improve and expand their submitted invention by suggesting practical engineering
components, technologies, implementation modules, and future innovation opportunities while preserving the original invention's purpose.

STRICT RULES & CONSTRAINTS:
1. NEVER repeat, quote, or mention the invention title or description verbatim anywhere in your output paragraphs, section titles, table cells, or bullet points.
   Refer only to "the proposed system", "the device", "the core architecture", or specific engineering components.
   (The title and description are already displayed in dedicated cards elsewhere in the report).
2. DO NOT write academic explanations, literature reviews, textbook definitions, or introductory pleasantries.
3. DO NOT generate generic AI-written essays. Focus strictly on actionable engineering specifications, structured tables, and bullet points.
4. Retrieved patents are for contextual landscape reference only. They MUST NOT dominate the report or dictate the invention.
5. Preserve the invention's core purpose and intent—do not pivot to an unrelated product.

User Invention Baseline:
Title: {title}
Description: {description}

Prior-Art Landscape Reference:
{prior_art_context}

Return STRICT JSON adhering EXACTLY to this schema:
{{
  "section1_technical_concept": {{
    "core_principle": [
      "Paragraph 1: Concise technical statement of the primary operating mechanism (physical/digital input to output transformation).",
      "Paragraph 2: Detailed signal/data flow from sensor acquisition through processing and actuation/reporting.",
      "Paragraph 3: Key engineering considerations for deterministic, real-time, or fail-safe operation."
    ],
    "key_modules": [
      {{"module": "Module Name 1", "purpose": "Concrete engineering function in this system."}},
      {{"module": "Module Name 2", "purpose": "Concrete engineering function in this system."}},
      {{"module": "Module Name 3", "purpose": "Concrete engineering function in this system."}},
      {{"module": "Module Name 4", "purpose": "Concrete engineering function in this system."}}
    ],
    "technical_differentiators": [
      "Differentiator 1: Concrete technical advantage over standard implementations.",
      "Differentiator 2: Specific operational latency, efficiency, or accuracy benefit.",
      "Differentiator 3: Distinct architectural or hardware-software coupling advantage.",
      "Differentiator 4: Robustness or fault-isolation capability."
    ]
  }},
  "section2_system_architecture": {{
    "system_flow": "A concise, professional description of the end-to-end data and control flow across the architecture.",
    "architecture_table": [
      {{"layer": "Sensing", "components": "Specific sensors, transducers, or input devices", "data_flow": "Capture and initial signal conditioning"}},
      {{"layer": "Processing", "components": "Compute units, MCUs, NPUs, or embedded boards", "data_flow": "Feature extraction and real-time decision inference"}},
      {{"layer": "Control", "components": "Actuators, motor drivers, relays, or control interfaces", "data_flow": "Physical execution or state control based on inference"}},
      {{"layer": "Monitoring", "components": "Operator dashboard, local HMI, or telemetry bus", "data_flow": "Telemetry aggregation, event logs, and status display"}}
    ]
  }},
  "section3_recommended_technologies": [
    {{"category": "AI Model", "recommended_technology": "Specific model or algorithm with 1-sentence engineering justification."}},
    {{"category": "Processor", "recommended_technology": "Specific processor/MCU with 1-sentence engineering justification."}},
    {{"category": "Sensors", "recommended_technology": "Specific sensor hardware with 1-sentence engineering justification."}},
    {{"category": "Communication", "recommended_technology": "Specific protocol/transceiver with 1-sentence engineering justification."}},
    {{"category": "Database", "recommended_technology": "Specific storage/database engine with 1-sentence engineering justification."}},
    {{"category": "Dashboard", "recommended_technology": "Specific UI/dashboard framework with 1-sentence engineering justification."}},
    {{"category": "Prototyping", "recommended_technology": "Specific prototyping/simulation tool with 1-sentence engineering justification."}}
  ],
  "section4_innovation_expansion": [
    {{
      "enhancement": "Feature Enhancement Name",
      "technical_implementation": "Actionable technical implementation details explaining how to build this module.",
      "patent_benefit": "How this introduces a new claimable mechanism or strengthens patent defensibility."
    }},
    {{
      "enhancement": "Second Enhancement Name",
      "technical_implementation": "Actionable technical implementation details.",
      "patent_benefit": "Patent strengthening benefit."
    }},
    {{
      "enhancement": "Third Enhancement Name",
      "technical_implementation": "Actionable technical implementation details.",
      "patent_benefit": "Patent strengthening benefit."
    }},
    {{
      "enhancement": "Fourth Enhancement Name",
      "technical_implementation": "Actionable technical implementation details.",
      "patent_benefit": "Patent strengthening benefit."
    }}
  ],
  "section5_enhancement_roadmap": [
    {{"phase": "Near-Term", "enhancement": "Optimization or feature 1", "engineering_impact": "Direct operational impact"}},
    {{"phase": "Near-Term", "enhancement": "Optimization or feature 2", "engineering_impact": "Direct operational impact"}},
    {{"phase": "Long-Term", "enhancement": "Advanced R&D addition 1", "engineering_impact": "Direct operational impact"}},
    {{"phase": "Long-Term", "enhancement": "Advanced R&D addition 2", "engineering_impact": "Direct operational impact"}}
  ],
  "section6_commercialization_potential": [
    {{"item": "Target Market", "assessment": "Specific vertical market segments and deployment facilities."}},
    {{"item": "Deployment", "assessment": "Installation footprint, retrofit viability, and site integration requirements."}},
    {{"item": "Cost Complexity", "assessment": "Low/Medium/High with BOM and component sourcing evaluation."}},
    {{"item": "Scalability", "assessment": "Assessment of scaling from prototype to multi-site deployment."}},
    {{"item": "Regulatory Considerations", "assessment": "Applicable industrial, environmental, or electrical safety standards (e.g. CE, FCC, ISO, BIS)."}}
  ]
}}
"""

        response = model.generate_content(prompt)
        text = (response.text or "").strip()
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if not json_match:
            return None
        return json.loads(json_match.group(0))

    def _clean_title_repetitions(self, text: Any, title: str) -> Any:
        """Removes accidental verbatim title repetitions from generated text."""
        if not isinstance(text, str):
            return text
        if not title:
            return text

        cleaned = text
        # Remove quoted title occurrences
        cleaned = re.sub(re.escape(f'"{title}"'), "the system", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(re.escape(f"'{title}'"), "the system", cleaned, flags=re.IGNORECASE)
        # Remove common introductory title framing
        cleaned = re.sub(
            rf"\bThe proposed invention,?\s+(?:\"{re.escape(title)}\"|'{re.escape(title)}'|{re.escape(title)}),?\s+is\b",
            "The system is",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(
            rf"\bFor\s+(?:\"{re.escape(title)}\"|'{re.escape(title)}'|{re.escape(title)}),?\b",
            "For the proposed architecture,",
            cleaned,
            flags=re.IGNORECASE,
        )
        # Scrub direct raw title match if longer than 10 characters
        if len(title) > 10:
            cleaned = re.sub(re.escape(title), "the proposed system", cleaned, flags=re.IGNORECASE)

        return cleaned

    def _normalize(
        self,
        raw: Dict[str, Any],
        title: str,
        description: str,
    ) -> Dict[str, Any]:
        fallback = self._fallback(title, description, [])

        # Section 1: Technical Concept
        raw_s1 = raw.get("section1_technical_concept") or {}
        core_p = raw_s1.get("core_principle") or fallback["technical_concept"]["core_principle"]
        if isinstance(core_p, str):
            core_p = [p.strip() for p in core_p.split("\n\n") if p.strip()]
        core_p = [self._clean_title_repetitions(p, title) for p in core_p]

        key_mods = raw_s1.get("key_modules") or []
        cleaned_mods = []
        for m in key_mods:
            mod_name = self._clean_title_repetitions(str(m.get("module", "")).strip(), title)
            purpose = self._clean_title_repetitions(str(m.get("purpose", "")).strip(), title)
            if mod_name and purpose:
                cleaned_mods.append({"module": mod_name, "purpose": purpose})
        if len(cleaned_mods) < 3:
            cleaned_mods = fallback["technical_concept"]["key_modules"]

        diffs = raw_s1.get("technical_differentiators") or []
        cleaned_diffs = [self._clean_title_repetitions(str(d).strip(), title) for d in diffs if str(d).strip()]
        if len(cleaned_diffs) < 3:
            cleaned_diffs = fallback["technical_concept"]["technical_differentiators"]

        # Section 2: Architecture
        raw_s2 = raw.get("section2_system_architecture") or {}
        flow = self._clean_title_repetitions(str(raw_s2.get("system_flow") or "").strip(), title)
        if not flow:
            flow = fallback["system_architecture"]["system_flow"]

        arch_table = []
        for row in raw_s2.get("architecture_table") or []:
            layer = self._clean_title_repetitions(str(row.get("layer", "")).strip(), title)
            comps = self._clean_title_repetitions(str(row.get("components", "")).strip(), title)
            dflow = self._clean_title_repetitions(str(row.get("data_flow", "")).strip(), title)
            if layer and comps:
                arch_table.append({"layer": layer, "components": comps, "data_flow": dflow})
        if len(arch_table) < 3:
            arch_table = fallback["system_architecture"]["architecture_table"]

        # Section 3: Recommended Technologies
        raw_s3 = raw.get("section3_recommended_technologies") or []
        tech_rows = []
        for row in raw_s3:
            cat = str(row.get("category", "")).strip()
            rec = self._clean_title_repetitions(str(row.get("recommended_technology", "")).strip(), title)
            if cat and rec:
                tech_rows.append({"category": cat, "recommended_technology": rec})
        if len(tech_rows) < 4:
            tech_rows = fallback["recommended_technologies"]

        # Section 4: Innovation Expansion
        raw_s4 = raw.get("section4_innovation_expansion") or []
        exp_cards = []
        for row in raw_s4:
            enh = self._clean_title_repetitions(str(row.get("enhancement", "")).strip(), title)
            impl = self._clean_title_repetitions(str(row.get("technical_implementation", "")).strip(), title)
            ben = self._clean_title_repetitions(str(row.get("patent_benefit", "")).strip(), title)
            if enh and impl:
                exp_cards.append({
                    "enhancement": enh,
                    "technical_implementation": impl,
                    "patent_benefit": ben or "Strengthens independent patent claim scope.",
                })
        if len(exp_cards) < 3:
            exp_cards = fallback["innovation_expansion"]

        # Section 5: Enhancement Roadmap
        raw_s5 = raw.get("section5_enhancement_roadmap") or []
        roadmap = []
        for row in raw_s5:
            phase = str(row.get("phase", "Near-Term")).strip()
            enh = self._clean_title_repetitions(str(row.get("enhancement", "")).strip(), title)
            impact = self._clean_title_repetitions(str(row.get("engineering_impact", "")).strip(), title)
            if enh:
                roadmap.append({"phase": phase, "enhancement": enh, "engineering_impact": impact})
        if len(roadmap) < 3:
            roadmap = fallback["enhancement_roadmap"]

        # Section 6: Commercialization Potential
        raw_s6 = raw.get("section6_commercialization_potential") or []
        comm = []
        for row in raw_s6:
            item = str(row.get("item", "")).strip()
            assess = self._clean_title_repetitions(str(row.get("assessment", "")).strip(), title)
            if item and assess:
                comm.append({"item": item, "assessment": assess})
        if len(comm) < 4:
            comm = fallback["commercialization_potential"]

        # Build clean unified payload
        payload = {
            "invention_title": title,
            "invention_description": description,
            "technical_concept": {
                "core_principle": core_p,
                "key_modules": cleaned_mods[:6],
                "technical_differentiators": cleaned_diffs[:5],
            },
            "system_architecture": {
                "system_flow": flow,
                "architecture_table": arch_table,
            },
            "recommended_technologies": tech_rows,
            "innovation_expansion": exp_cards[:6],
            "enhancement_roadmap": roadmap[:6],
            "commercialization_potential": comm,
            # Legacy compatibility mappings
            "concept_expansion": "\n\n".join(core_p),
            "suggested_system_architecture": flow,
            "hardware_components": [
                {"component": m["module"], "purpose": m["purpose"]} for m in cleaned_mods
            ],
            "software_stack": [
                {"layer": r["category"], "recommendation": r["recommended_technology"]}
                for r in tech_rows
            ],
            "advanced_enhancement_ideas": [
                {"idea": c["enhancement"], "explanation": f"{c['technical_implementation']} Patent Benefit: {c['patent_benefit']}"}
                for c in exp_cards
            ],
        }
        return payload

    def _fallback(
        self,
        title: str,
        description: str,
        patents: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        idea = f"{title}. {description}".strip().lower()
        domain = self._infer_domain(idea)

        return {
            "invention_title": title,
            "invention_description": description,
            "technical_concept": {
                "core_principle": domain["core_principle"],
                "key_modules": domain["key_modules"],
                "technical_differentiators": domain["technical_differentiators"],
            },
            "system_architecture": {
                "system_flow": domain["system_flow"],
                "architecture_table": domain["architecture_table"],
            },
            "recommended_technologies": domain["recommended_technologies"],
            "innovation_expansion": domain["innovation_expansion"],
            "enhancement_roadmap": domain["enhancement_roadmap"],
            "commercialization_potential": domain["commercialization_potential"],
            # Legacy compatibility mappings
            "concept_expansion": "\n\n".join(domain["core_principle"]),
            "suggested_system_architecture": domain["system_flow"],
            "hardware_components": [
                {"component": m["module"], "purpose": m["purpose"]} for m in domain["key_modules"]
            ],
            "software_stack": [
                {"layer": r["category"], "recommendation": r["recommended_technology"]}
                for r in domain["recommended_technologies"]
            ],
            "advanced_enhancement_ideas": [
                {"idea": c["enhancement"], "explanation": f"{c['technical_implementation']} Patent Benefit: {c['patent_benefit']}"}
                for c in domain["innovation_expansion"]
            ],
        }

    def _infer_domain(self, text: str) -> Dict[str, Any]:
        is_waste = any(k in text for k in ["waste", "recycl", "segregat", "garbage", "trash", "sorting", "bin"])
        is_comm = any(k in text for k in ["communication", "network", "disaster", "mesh", "radio", "lte", "5g", "lora", "wifi"])
        is_med = any(k in text for k in ["health", "patient", "medical", "wearable", "ecg", "glucose", "biomedical", "diagnostic"])
        is_agri = any(k in text for k in ["crop", "soil", "farm", "agriculture", "irrigation", "greenhouse"])
        is_vehicle = any(k in text for k in ["vehicle", "traffic", "autonomous", "drone", "uav", "navigation"])
        is_energy = any(k in text for k in ["solar", "battery", "grid", "energy", "power"])
        is_vision = any(k in text for k in ["image", "camera", "vision", "video", "detect", "surveillance"])

        if is_waste:
            return self._domain_waste()
        if is_med:
            return self._domain_medical()
        if is_agri:
            return self._domain_agriculture()
        if is_vehicle:
            return self._domain_vehicle()
        if is_energy:
            return self._domain_energy()
        if is_comm:
            return self._domain_communication()
        if is_vision:
            return self._domain_vision()
        return self._domain_general()

    def _domain_waste(self) -> Dict[str, Any]:
        return {
            "core_principle": [
                "The system operates through an integrated electro-mechanical pipeline combining multi-spectral visual capture, weight-based volumetric profiling, and automated robotic or pneumatic diversion.",
                "Inbound material enters an isolated inspection bay where high-speed imaging sensors extract surface contour and texture data. On-device edge neural models execute real-time classification across biodegradable, recyclable, and hazardous categories in sub-50ms cycles.",
                "Deterministic control logic coordinates servo-driven deflectors to guide sorted items into designated receptacles, while load transducers monitor bin capacity and trigger compaction or emptying alerts.",
            ],
            "key_modules": [
                {"module": "Computer Vision", "purpose": "Multi-class waste item detection and classification."},
                {"module": "Sensor Fusion", "purpose": "Correlates visual bounding boxes with mass density from load cells."},
                {"module": "Edge AI", "purpose": "Executes quantized neural inference locally without latency."},
                {"module": "Mechanical Sorting", "purpose": "Actuates servo diverters and pneumatic flaps for physical separation."},
                {"module": "Telemetry Node", "purpose": "Tracks fill levels and transmits operational metrics to municipal dashboards."},
            ],
            "technical_differentiators": [
                "Dual-stage classification combining visual geometry with mass-to-volume ratio to resolve ambiguous packaging.",
                "Edge-native inference pipeline delivering consistent sub-50ms mechanical gating independent of cloud backhaul.",
                "Self-clearing anti-jam mechanical diverters equipped with current-sensing stall protection.",
                "Continuous automated calibration compensating for ambient illumination and dust accumulation.",
            ],
            "system_flow": "Material passes through an optical scanning chamber where visual and weight sensors stream data to an edge processor. The processor infers material classification and pulses high-speed servo actuators, while operational metrics sync to an administrative dashboard.",
            "architecture_table": [
                {"layer": "Sensing", "components": "Industrial RGB-D Camera, Strain-Gauge Load Cell, Proximity Sensors", "data_flow": "Captures item imagery, dimensions, and mass upon entry."},
                {"layer": "Processing", "components": "Edge Compute SoC (Jetson/Pi 5), Quantized Neural Engine", "data_flow": "Generates multi-class classification and actuation coordinates."},
                {"layer": "Control", "components": "Brushless Servo Motors, Pneumatic Diverters, MCU Controller", "data_flow": "Executes physical separation into segregated bins."},
                {"layer": "Monitoring", "components": "Cloud Telemetry Gateway, Municipal Web/Mobile Dashboard", "data_flow": "Transmits bin capacity levels, throughput counts, and diagnostic logs."},
            ],
            "recommended_technologies": [
                {"category": "AI Model", "recommended_technology": "YOLOv8-nano — Delivers high-FPS object detection suitable for resource-constrained edge hardware."},
                {"category": "Processor", "recommended_technology": "Raspberry Pi 5 with Hailo-8 NPU / Jetson Orin Nano — Ensures low-latency local inference."},
                {"category": "Sensors", "recommended_technology": "Wide-angle RGB camera with dual IR illuminators & 5kg strain-gauge load cells."},
                {"category": "Communication", "recommended_technology": "Wi-Fi 6 & LoRaWAN — Provides high-bandwidth local telemetry with low-power wide-area fallback."},
                {"category": "Database", "recommended_technology": "PostgreSQL with TimescaleDB — Efficiently indexes timestamped sorting logs and fill-rate metrics."},
                {"category": "Dashboard", "recommended_technology": "Flutter Web Dashboard — Delivers cross-platform visualization of sorting efficiency and bin status."},
                {"category": "Prototyping", "recommended_technology": "Streamlit & ROS 2 — Accelerates sensor-actuator calibration and rapid logic verification."},
            ],
            "innovation_expansion": [
                {
                    "enhancement": "Material Recognition Module",
                    "technical_implementation": "Integrate short-wave infrared (SWIR) or spectroscopy-assisted material identification for mixed polymers.",
                    "patent_benefit": "Introduces a new claimable optical detection mechanism beyond surface-level RGB classification.",
                },
                {
                    "enhancement": "Autonomous Anti-Jam Mechanism",
                    "technical_implementation": "Incorporate motor current monitoring and vibration sensors to detect sorting chutes blockages and execute reverse-cycle clearing.",
                    "patent_benefit": "Defines dependent claims on self-clearing fault tolerance and mechanical reliability.",
                },
                {
                    "enhancement": "Dynamic Fill-Level Compaction",
                    "technical_implementation": "Pair ultrasonic depth arrays with motorized linear compression plates to double bin capacity before service intervals.",
                    "patent_benefit": "Creates novel claims covering closed-loop volumetric volume optimization in smart receptacles.",
                },
                {
                    "enhancement": "Contaminant Gas & Hazardous Vapor Sniffer",
                    "technical_implementation": "Deploy volatile organic compound (VOC) and gas sensor arrays in the collection chamber to flag hazardous chemical or battery off-gassing.",
                    "patent_benefit": "Expands protection into safety and hazardous waste compliance monitoring.",
                },
            ],
            "enhancement_roadmap": [
                {"phase": "Near-Term", "enhancement": "Offline Quantization of Vision Models", "engineering_impact": "Accelerates inference cycle time to under 30ms on low-cost compute."},
                {"phase": "Near-Term", "enhancement": "Adaptive Illumination Chamber", "engineering_impact": "Stabilizes recognition accuracy across varying daylight and outdoor conditions."},
                {"phase": "Long-Term", "enhancement": "Multi-Spectrum Polymer Discrimination", "engineering_impact": "Enables granular sub-classification of PET, HDPE, and polypropylene resins."},
                {"phase": "Long-Term", "enhancement": "Municipal Fleet Route Optimization", "engineering_impact": "Synchronizes real-time fill metrics directly with municipal collection vehicles."},
            ],
            "commercialization_potential": [
                {"item": "Target Market", "assessment": "Smart Cities, municipal recycling centers, commercial campuses, and transport hubs."},
                {"item": "Deployment", "assessment": "Modular drop-in retrofit designed for standard municipal 3-stream and 4-stream bins."},
                {"item": "Cost Complexity", "assessment": "Medium — Uses commercial off-the-shelf camera modules and standard microcontrollers to minimize unit BOM."},
                {"item": "Scalability", "assessment": "High — Standardized mechanical frame and cloud telemetry allow linear expansion across city-scale fleets."},
                {"item": "Regulatory Considerations", "assessment": "Machinery safety compliance (CE/FCC), battery safety directives, and ISO 14001 environmental standards."},
            ],
        }

    def _domain_communication(self) -> Dict[str, Any]:
        return {
            "core_principle": [
                "The system operates as a resilient multi-bearer telemetry and messaging infrastructure designed to maintain operational continuity under degraded network conditions.",
                "Field nodes sample local status, queue packets with cryptographic hashes, and route them through dynamic priority protocols across cellular, LoRa, or peer-to-peer mesh links.",
                "Autonomous link-state supervisors detect network degradation and automatically switch between synchronous transmission and store-and-forward delay-tolerant pipelines.",
            ],
            "key_modules": [
                {"module": "Multi-Bearer Transceiver", "purpose": "Dynamic switching between cellular, LoRa, and Wi-Fi networks."},
                {"module": "Priority Message Queuing", "purpose": "Enforces delay-tolerant store-and-forward caching under backhaul failure."},
                {"module": "Cryptographic Authentication", "purpose": "Hardware-level payload signing and anti-spoofing verification."},
                {"module": "Power Management Unit", "purpose": "Duty-cycles radio hardware based on battery reserve and channel health."},
            ],
            "technical_differentiators": [
                "Deterministic bearer fallback protocol requiring zero operator reconfiguration.",
                "Store-and-forward caching ensuring zero telemetry loss during complete network outages.",
                "Hardware-enforced packet prioritization reserving bandwidth for high-criticality events.",
            ],
            "system_flow": "Telemetry is captured by edge sensor interfaces, serialized into cryptographically signed packets, and routed via the optimal available radio bearer to field terminals or central gateways.",
            "architecture_table": [
                {"layer": "Sensing", "components": "GPS/GNSS, Battery Monitors, Local Input Interfaces", "data_flow": "Captures location, timestamp, and device health parameters."},
                {"layer": "Processing", "components": "Low-Power Dual-Core MCU (ARM Cortex-M33)", "data_flow": "Executes cryptographic signing, packet framing, and routing logic."},
                {"layer": "Control", "components": "Radio Power Switches, RF Multiplexer, Watchdog Co-Processor", "data_flow": "Manages RF power sequencing and hardware recovery states."},
                {"layer": "Monitoring", "components": "Field Mobile Console, Gateway Dispatch Dashboard", "data_flow": "Presents real-time node connectivity map and event log."},
            ],
            "recommended_technologies": [
                {"category": "AI Model", "recommended_technology": "Lightweight RF link-quality classifier — Predicts channel fading to preempt packet drops."},
                {"category": "Processor", "recommended_technology": "Nordic nRF9160 / ESP32-S3 — Provides integrated LTE-M/NB-IoT and Wi-Fi/BLE in a low-power footprint."},
                {"category": "Sensors", "recommended_technology": "Multi-constellation GNSS receiver + environmental telemetry sensors."},
                {"category": "Communication", "recommended_technology": "LoRaWAN Class A/C + Cellular LTE-M — Bridges local mesh nodes with wide-area backhaul."},
                {"category": "Database", "recommended_technology": "SQLite on edge gateway; PostgreSQL with TimescaleDB on central servers."},
                {"category": "Dashboard", "recommended_technology": "Flutter / React Native — Cross-platform tactical UI for field technicians."},
                {"category": "Prototyping", "recommended_technology": "Zephyr RTOS & Saleae Logic — Enables deterministic firmware simulation and bus analysis."},
            ],
            "innovation_expansion": [
                {
                    "enhancement": "Epidemic Routing & Opportunistic Mesh",
                    "technical_implementation": "Deploy peer-to-peer epidemic forwarding where passing field nodes exchange cached emergency packets.",
                    "patent_benefit": "Secures novel claims on autonomous ad-hoc relay mechanisms without centralized infrastructure.",
                },
                {
                    "enhancement": "Adaptive RF Modulation Scaling",
                    "technical_implementation": "Dynamically adjust spreading factor and transmission power according to localized SNR metrics.",
                    "patent_benefit": "Expands patent scope to cover power-conserving modulation adaptation algorithms.",
                },
                {
                    "enhancement": "Tamper & Geofence Heartbeat",
                    "technical_implementation": "Combine accelerometer motion signatures with GPS coordinates to broadcast silent anti-theft distress signals.",
                    "patent_benefit": "Introduces hardware security and chain-of-custody claims for remote assets.",
                },
                {
                    "enhancement": "Zero-Trust Device Identity Engine",
                    "technical_implementation": "Embed secure elements (ATECC608B) generating ephemeral session keys for message attestation.",
                    "patent_benefit": "Strengthens defensive patent posture against packet-injection and replay attacks.",
                },
            ],
            "enhancement_roadmap": [
                {"phase": "Near-Term", "enhancement": "Firmware Compression & Differential OTA", "engineering_impact": "Enables remote updates over narrow-band 2G/LoRa channels."},
                {"phase": "Near-Term", "enhancement": "Energy-Harvesting Power Integration", "engineering_impact": "Extends autonomous field life up to 5 years without battery replacement."},
                {"phase": "Long-Term", "enhancement": "Satellite Direct-to-Device (D2D) Linkage", "engineering_impact": "Provides continuous fail-safe telemetry in oceanic and remote wilderness zones."},
                {"phase": "Long-Term", "enhancement": "Self-Organizing Mesh Cluster Synchronization", "engineering_impact": "Scales network topology automatically to thousands of concurrent nodes."},
            ],
            "commercialization_potential": [
                {"item": "Target Market", "assessment": "Disaster management authorities, remote mining operations, utilities, and emergency logistics."},
                {"item": "Deployment", "assessment": "Ruggedized IP67 weatherproof enclosures with mast or vehicle-mounting brackets."},
                {"item": "Cost Complexity", "assessment": "Low-to-Medium — Highly integrated system-in-package (SiP) modules keep assembly costs modest."},
                {"item": "Scalability", "assessment": "High — Standard ISM-band radios eliminate recurring carrier SIM fees for localized networks."},
                {"item": "Regulatory Considerations", "assessment": "Radio spectrum compliance (WPC India, FCC Part 15, CE RED), IP67 environmental standards."},
            ],
        }

    def _domain_medical(self) -> Dict[str, Any]:
        return {
            "core_principle": [
                "The system provides continuous physiological signal acquisition through low-noise bio-sensing front-ends coupled with deterministic on-body signal conditioning.",
                "Raw electro-potential or optical readings are filtered for baseline wander and motion artifacts before feeding into calibrated feature extractors for anomaly detection.",
                "Verified physiological alerts are communicated via localized haptic/visual interfaces and encrypted near-field telemetry to supervisory clinical consoles.",
            ],
            "key_modules": [
                {"module": "Analog Front-End (AFE)", "purpose": "Low-noise physiological signal amplification and filtering."},
                {"module": "Signal Quality Metric (SQM)", "purpose": "Detects and suppresses motion artifacts before inference."},
                {"module": "Edge Anomaly Detector", "purpose": "Identifies arrhythmia or acute events locally in real-time."},
                {"module": "Encrypted Telemetry Engine", "purpose": "Transmits patient data via BLE using HIPAA-compliant encryption."},
            ],
            "technical_differentiators": [
                "Multi-parameter signal quality gating preventing false-alarm fatigue.",
                "Sub-milliwatt real-time inference operating on an ultra-low-power biomedical MCU.",
                "Deterministic on-device thresholding guaranteeing local alerts even when unpaired from mobile devices.",
            ],
            "system_flow": "Biosensors sample physiological data, the analog front-end digitizes and filters the signal, the on-body processor evaluates clinical patterns, and high-confidence metrics sync via encrypted links to companion apps.",
            "architecture_table": [
                {"layer": "Sensing", "components": "Biocompatible Electrodes, Photoplethysmography (PPG) Sensors, IMU", "data_flow": "Captures raw biopotential and motion acceleration streams."},
                {"layer": "Processing", "components": "Ultra-Low Power Biomedical SoC (ARM Cortex-M4F + AFE)", "data_flow": "Executes digital notch filtering, baseline removal, and peak detection."},
                {"layer": "Control", "components": "Haptic Resonator, Status LED Drivers, Emergency Beeper", "data_flow": "Triggers immediate physical sensory alerts upon critical thresholds."},
                {"layer": "Monitoring", "components": "Clinician Web Console, Patient Mobile Companion App", "data_flow": "Displays historical trend analytics and generates diagnostic summaries."},
            ],
            "recommended_technologies": [
                {"category": "AI Model", "recommended_technology": "Quantized 1D-CNN / Temporal Convolutional Network — Efficient waveform pattern matching."},
                {"category": "Processor", "recommended_technology": "Analog Devices MAX30001 / STM32WB55 — Combines integrated biopotential AFE with BLE 5.3."},
                {"category": "Sensors", "recommended_technology": "Dry-contact silver-silver chloride (Ag/AgCl) electrodes + dual-wavelength optical PPG."},
                {"category": "Communication", "recommended_technology": "Bluetooth Low Energy (BLE 5.3) with AES-128 GCM encryption."},
                {"category": "Database", "recommended_technology": "Encrypted SQLite on mobile client; HL7/FHIR-compliant repository on server."},
                {"category": "Dashboard", "recommended_technology": "React Native Health Dashboard with real-time waveform charting."},
                {"category": "Prototyping", "recommended_technology": "Biomedical evaluation boards (AD8232 / MAX30102) with Python signal toolkits."},
            ],
            "innovation_expansion": [
                {
                    "enhancement": "Self-Calibrating Baseline Drift Compensator",
                    "technical_implementation": "Deploy dynamic Kalman filtering coupled with impedance pneumography to track patient skin contact resistance in real time.",
                    "patent_benefit": "Claims novel adaptive noise-cancellation mechanisms independent of ambient temperature.",
                },
                {
                    "enhancement": "Closed-Loop Emergency Alert Dispatch",
                    "technical_implementation": "Combine acute biomarker threshold crossings with accelerometer fall-impact signatures to trigger automated SOS geolocation broadcasts.",
                    "patent_benefit": "Secures multi-modal diagnostic trigger claims covering combined cardiac and kinetic distress.",
                },
                {
                    "enhancement": "Continuous Energy Harvesting from Body Heat",
                    "technical_implementation": "Incorporate flexible thermoelectric generators (TEG) on the device base to trickle-charge primary cells during wear.",
                    "patent_benefit": "Protects continuous non-invasive energy reclamation techniques for wearable monitors.",
                },
                {
                    "enhancement": "Differential Waveform Explainability Engine",
                    "technical_implementation": "Annotate specific clinical morphological segments (P-Q-R-S-T complexes) directly on device before transmission.",
                    "patent_benefit": "Introduces intellectual property on explainable, clinician-auditable on-edge signal parsing.",
                },
            ],
            "enhancement_roadmap": [
                {"phase": "Near-Term", "enhancement": "Motion Artifact Cancellation Algorithms", "engineering_impact": "Reduces false positive alarms by 85% during ambulatory exercise."},
                {"phase": "Near-Term", "enhancement": "Ultra-Low-Power Sleep Modes", "engineering_impact": "Extends continuous operation to 7 days on a single coin cell."},
                {"phase": "Long-Term", "enhancement": "Non-Invasive Continuous Glucose Co-Estimation", "engineering_impact": "Expands diagnostic capability to metabolic syndrome tracking."},
                {"phase": "Long-Term", "enhancement": "Federated Clinical Model Retraining", "engineering_impact": "Enables distributed cohort improvement without exposing raw patient data."},
            ],
            "commercialization_potential": [
                {"item": "Target Market", "assessment": "Hospitals, remote patient monitoring providers, elderly care homes, and clinical trials."},
                {"item": "Deployment", "assessment": "Non-invasive skin-patch or wrist-strap wearable with hypoallergenic silicone casing."},
                {"item": "Cost Complexity", "assessment": "Medium — Precision analog components and medical-grade certifications dictate moderate unit costs."},
                {"item": "Scalability", "assessment": "High — Digital health subscription models and remote physician review support rapid adoption."},
                {"item": "Regulatory Considerations", "assessment": "Medical device clearance (CDSCO India Class B/C, FDA 510(k), CE MDR), ISO 13485, and HIPAA/DPDP data privacy."},
            ],
        }

    def _domain_agriculture(self) -> Dict[str, Any]:
        return {
            "core_principle": [
                "The system executes precision agronomic monitoring through ruggedized in-situ probe arrays paired with autonomous micro-climate analysis engines.",
                "Multi-depth probes sample moisture, electrical conductivity (EC), and ambient temperature, which are correlated against soil-type calibration matrices on an edge node.",
                "Irrigation or fertigation solenoids are driven through closed-loop duty cycles, minimizing water consumption while maintaining optimal root-zone saturation.",
            ],
            "key_modules": [
                {"module": "Sub-Surface Soil Probe", "purpose": "Multi-depth capacitive volumetric water content and EC measurement."},
                {"module": "Edge Irrigation Optimizer", "purpose": "Calculates evapotranspiration curves and controls valve actuation."},
                {"module": "Solar-Harvesting Power Unit", "purpose": "Ensures continuous field operation through seasons without grid power."},
                {"module": "Long-Range Telemetry Node", "purpose": "Bridges agricultural plot metrics to farm gateways over LoRaWAN."},
            ],
            "technical_differentiators": [
                "Multi-layer capacitive depth profiling preventing over-saturation past active root zones.",
                "Zero-maintenance solar energy harvesting operating reliably under heavy canopy shading.",
                "Offline autonomous actuation schedules executing even during farm connectivity dropouts.",
            ],
            "system_flow": "In-situ soil probes sample parameters at regular intervals, transmitting readings via LoRa to a local gateway. The gateway checks agronomic rules and actuates irrigation relays while syncing telemetry to mobile devices.",
            "architecture_table": [
                {"layer": "Sensing", "components": "Capacitive Soil Moisture Sensors, EC Probes, NPK Transducers, Pyranometer", "data_flow": "Samples sub-surface moisture and nutrient metrics."},
                {"layer": "Processing", "components": "Low-Power Field MCU + Farm Gateway Controller (Linux ARM)", "data_flow": "Computes daily water balance and evapotranspiration models."},
                {"layer": "Control", "components": "Latching Solenoid Valves, Relay Actuators, Drip Emitters", "data_flow": "Pulsed valve opening and closing based on agronomic thresholds."},
                {"layer": "Monitoring", "components": "Farmer Smartphone App (Offline-First), SMS Alert Gateway", "data_flow": "Presents field hydration maps and delivers urgent moisture alerts."},
            ],
            "recommended_technologies": [
                {"category": "AI Model", "recommended_technology": "Evapotranspiration regression model (Penman-Monteith with ML tuning) — Predicts exact crop water deficit."},
                {"category": "Processor", "recommended_technology": "Seeed Studio Xiao ESP32-S3 / STM32L431 — Balances micro-amp sleep currents with math acceleration."},
                {"category": "Sensors", "recommended_technology": "Industrial SDI-12 soil moisture & temperature probe with anti-corrosion stainless electrodes."},
                {"category": "Communication", "recommended_technology": "LoRaWAN (865-867 MHz in India / 915 MHz US) — Provides 10km line-of-sight farm coverage."},
                {"category": "Database", "recommended_technology": "InfluxDB / TimescaleDB — Optimized for multi-sensor temporal agro-climatic logs."},
                {"category": "Dashboard", "recommended_technology": "Progressive Web App with multi-lingual voice/SMS prompts for vernacular accessibility."},
                {"category": "Prototyping", "recommended_technology": "KiCAD for custom field PCB design & FarmOS integration for rapid pilot testing."},
            ],
            "innovation_expansion": [
                {
                    "enhancement": "Dynamic Soil Texture Auto-Calibration",
                    "technical_implementation": "Analyze hydraulic conductivity decay curves during irrigation to automatically classify soil type (sandy vs clay loam).",
                    "patent_benefit": "Protects autonomous soil-type adaptation without requiring laboratory core sampling.",
                },
                {
                    "enhancement": "Acoustic Pest & Root-Borer Detection",
                    "technical_implementation": "Embed acoustic contact microphones in probe stakes to record sub-soil feeding vibrations from larval pests.",
                    "patent_benefit": "Creates novel claims on non-destructive sub-surface bio-acoustic pest surveillance.",
                },
                {
                    "enhancement": "Predictive Weather Frost Prevention Trigger",
                    "technical_implementation": "Combine local dew point telemetry with forecast pressure trends to automate micro-sprinkler misting before frost events.",
                    "patent_benefit": "Strengthens claims on predictive micro-climate crop preservation mechanisms.",
                },
                {
                    "enhancement": "Nutrient Leaching Prevention Controller",
                    "technical_implementation": "Track vertical EC velocity through multi-depth sensors to halt irrigation before nitrogen leaches past root depth.",
                    "patent_benefit": "Secures intellectual property around environmentally sustainable precision fertigation.",
                },
            ],
            "enhancement_roadmap": [
                {"phase": "Near-Term", "enhancement": "Latching Solenoid Driver Circuitry", "engineering_impact": "Reduces valve actuation energy by 90% using millisecond pulse discharge."},
                {"phase": "Near-Term", "enhancement": "Vernacular Voice Interface for Mobile App", "engineering_impact": "Eliminates literacy barriers for rural smallholders."},
                {"phase": "Long-Term", "enhancement": "Drone Multispectral NDVI Telemetry Fusion", "engineering_impact": "Correlates aerial canopy stress with sub-surface probe telemetry."},
                {"phase": "Long-Term", "enhancement": "Autonomous Solar Desalination Coupling", "engineering_impact": "Enables brackish groundwater utilization for arid zone agriculture."},
            ],
            "commercialization_potential": [
                {"item": "Target Market", "assessment": "Commercial plantations, greenhouse operators, government irrigation projects, and smallholder cooperatives."},
                {"item": "Deployment", "assessment": "Direct in-field stake insertion with IP68 potting and UV-stabilized polycarbonate housing."},
                {"item": "Cost Complexity", "assessment": "Low — Modular probe design keeps node cost under target commercial price thresholds."},
                {"item": "Scalability", "assessment": "High — Standard LoRaWAN gateways easily support 500+ probe nodes per installation."},
                {"item": "Regulatory Considerations", "assessment": "BIS / IP68 ingress protection standards, RoHS environmental conformity, and regional agricultural subsidy certifications."},
            ],
        }

    def _domain_vehicle(self) -> Dict[str, Any]:
        return {
            "core_principle": [
                "The system provides autonomous navigation and spatial perception through synchronized multi-modal sensor streams processed on deterministic embedded computing nodes.",
                "High-frequency spatial observations (cameras, radar, or ultrasonic ranging) are fused to build a local probabilistic occupancy grid with obstacle velocity vectors.",
                "A hierarchical motion planner calculates dynamically feasible trajectories, enforcing strict safety margins through dual-redundant hardware interlocks.",
            ],
            "key_modules": [
                {"module": "Perception Engine", "purpose": "Real-time obstacle detection and spatial bounding box estimation."},
                {"module": "Sensor Fusion Filter", "purpose": "Combines visual odometry with IMU/GNSS kinematics."},
                {"module": "Trajectory Planner", "purpose": "Generates collision-free trajectories respecting dynamic vehicle limits."},
                {"module": "Safety Watchdog MCU", "purpose": "Enforces emergency deceleration and fail-safe stop maneuvers."},
            ],
            "technical_differentiators": [
                "Dual-channel safety supervisor capable of overriding AI path planning within 10ms of anomaly detection.",
                "Lightweight occupancy grid computation operating under low electrical power budgets.",
                "Robust feature tracking maintained across severe weather and lens occlusion conditions.",
            ],
            "system_flow": "Perception transducers capture environmental data, an edge accelerator computes 3D obstacle vectors, the path planner calculates steer/throttle commands, and the vehicle drive-by-wire controller actuates mechanical responses.",
            "architecture_table": [
                {"layer": "Sensing", "components": "Automotive Cameras, LiDAR / Radar, High-G IMU, RTK-GNSS", "data_flow": "Streams timestamped point clouds, image frames, and vehicle ego-motion."},
                {"layer": "Processing", "components": "Automotive SoC (NVIDIA Jetson / NXP S32G) + Safety MCU", "data_flow": "Fuses sensor data and executes real-time motion planning algorithms."},
                {"layer": "Control", "components": "CAN-Bus Drive-by-Wire Interface, Steering/Braking Actuators", "data_flow": "Transmits torque and angle setpoints to chassis control units."},
                {"layer": "Monitoring", "components": "In-Cabin HMI, Remote Fleet Telemetry Tele-Operations Bus", "data_flow": "Provides operational status, geofencing coordinates, and fault diagnostics."},
            ],
            "recommended_technologies": [
                {"category": "AI Model", "recommended_technology": "PointPillars / YOLO-World 3D — Real-time 3D bounding box detection on sparse sensor streams."},
                {"category": "Processor", "recommended_technology": "NVIDIA Jetson Orin / Texas Instruments TDA4VM — ASIL-D compliant functional safety computing."},
                {"category": "Sensors", "recommended_technology": "Solid-state automotive LiDAR (905nm) + automotive HDR global-shutter camera modules."},
                {"category": "Communication", "recommended_technology": "Automotive Ethernet (1000BASE-T1) & CAN-FD with 4G/5G Cellular V2X fallback."},
                {"category": "Database", "recommended_technology": "MCAP / ROS 2 Bag format for flight recorder logging; TimescaleDB on cloud servers."},
                {"category": "Dashboard", "recommended_technology": "Qt / QML Embedded Display — Low-latency native in-vehicle situational visualization."},
                {"category": "Prototyping", "recommended_technology": "CARLA Autonomous Driving Simulator & ROS 2 Humble framework."},
            ],
            "innovation_expansion": [
                {
                    "enhancement": "Deterministic Dynamic Safety Envelope",
                    "technical_implementation": "Implement non-linear control barrier functions (CBF) in a secondary safety coprocessor to physically constrain steering angles.",
                    "patent_benefit": "Secures claims on provable mathematical safety envelopes independent of neural net outputs.",
                },
                {
                    "enhancement": "Adverse Weather Sensor Self-Cleaning Module",
                    "technical_implementation": "Deploy piezoelectric ultrasonic transducer rings around camera optics to atomize rain droplets and clear dust.",
                    "patent_benefit": "Protects continuous optical clarity mechanisms for autonomous field perception.",
                },
                {
                    "enhancement": "Cooperative V2X Platooning Mesh",
                    "technical_implementation": "Form ephemeral peer-to-peer 5G sidelink meshes sharing braking intent and perception maps with neighboring vehicles.",
                    "patent_benefit": "Claims collaborative decentralized collision avoidance and drag-reduction architectures.",
                },
                {
                    "enhancement": "Black-Box Cryptographic Incident Recorder",
                    "technical_implementation": "Continuously log signed 10-second rolling sensor buffers into tamper-resistant secure flash memory upon impact threshold.",
                    "patent_benefit": "Expands patent protections into verifiable vehicular forensics and legal compliance.",
                },
            ],
            "enhancement_roadmap": [
                {"phase": "Near-Term", "enhancement": "Hardware-Accelerated Sensor Fusion Pipeline", "engineering_impact": "Cuts end-to-end perception latency from 80ms down to 18ms."},
                {"phase": "Near-Term", "enhancement": "Dynamic Battery Thermal Management Integration", "engineering_impact": "Improves cold-weather range and vehicle runtime by 15%."},
                {"phase": "Long-Term", "enhancement": "Neuromorphic Event-Camera Integration", "engineering_impact": "Enables microsecond obstacle detection under blinding glare."},
                {"phase": "Long-Term", "enhancement": "Fully Infrastructure-Free SLAM Navigation", "engineering_impact": "Permits reliable high-speed operation inside tunnels and GPS-denied environments."},
            ],
            "commercialization_potential": [
                {"item": "Target Market", "assessment": "Autonomous mobile robotics (AMRs), yard tugs, agricultural automation, and defense logistics."},
                {"item": "Deployment", "assessment": "Bolt-on drive-by-wire kit compatible with standard industrial vehicle chassis and CAN architectures."},
                {"item": "Cost Complexity", "assessment": "High — Industrial compute modules and automotive-grade sensors require significant upfront investment."},
                {"item": "Scalability", "assessment": "High — Commercial software licensing and modular hardware kits allow deployment across diverse vehicle formats."},
                {"item": "Regulatory Considerations", "assessment": "ISO 26262 functional safety (ASIL-B/D), ISO 21448 (SOTIF), and regional motor vehicle safety directives."},
            ],
        }

    def _domain_energy(self) -> Dict[str, Any]:
        return {
            "core_principle": [
                "The system optimizes power generation, energy storage, and load distribution through high-speed digital instrumentation coupled with predictive dispatch algorithms.",
                "Electrical parameters (voltage, current, harmonic distortion) are sampled at kilohertz frequencies by dedicated metering ICs to evaluate instantaneous grid power quality.",
                "Edge optimization models balance battery state-of-charge, forecasted ambient conditions, and tariff schedules to drive bidirectional power converters with maximum efficiency.",
            ],
            "key_modules": [
                {"module": "High-Precision Metering Front-End", "purpose": "Sub-cycle voltage, current, and frequency instrumentation."},
                {"module": "Battery Management & Balancing", "purpose": "Cell-level state-of-charge (SoC) and state-of-health (SoH) tracking."},
                {"module": "Predictive Dispatch Controller", "purpose": "Arbitrates energy storage discharge against solar/grid tariff models."},
                {"module": "Hardware Protection Interlock", "purpose": "Fast solid-state galvanic isolation and overcurrent protection."},
            ],
            "technical_differentiators": [
                "Sub-cycle islanding detection and fault disconnect under 8 milliseconds.",
                "Cell-level dynamic balancing extending lithium battery pack cycle longevity by over 25%.",
                "Edge-resident economic dispatch operating autonomously without cloud dependency during blackouts.",
            ],
            "system_flow": "Current and voltage transducers sample bus bars, edge firmware calculates power factors and harmonics, the dispatch algorithm determines optimal inverter setpoints, and solid-state switches manage energy routing.",
            "architecture_table": [
                {"layer": "Sensing", "components": "Hall-Effect Current Transducers, Precision PT/CTs, Thermal Probes", "data_flow": "Streams high-bandwidth waveform metrics and temperature readings."},
                {"layer": "Processing", "components": "Digital Signal Processor (TI C2000) + Edge Linux Controller", "data_flow": "Computes instantaneous power, executes FFT harmonics, and optimizes dispatch."},
                {"layer": "Control", "components": "Bidirectional Inverters, Solid-State Relays, DC/DC Converters", "data_flow": "Modulates pulse-width (PWM) gate drives and isolates circuits."},
                {"layer": "Monitoring", "components": "Industrial Touchscreen HMI, SCADA / Cloud Energy Management System", "data_flow": "Displays generation yields, battery capacity, and grid export revenue."},
            ],
            "recommended_technologies": [
                {"category": "AI Model", "recommended_technology": "Temporal regression / LSTM load forecaster — Predicts 24-hour facility energy consumption patterns."},
                {"category": "Processor", "recommended_technology": "Texas Instruments TMS320F280049C DSP + STM32MP1 MPUs — Combines deterministic PWM with Linux connectivity."},
                {"category": "Sensors", "recommended_technology": "Fluxgate zero-flux current transducers & Class 0.2S multi-function metering ICs."},
                {"category": "Communication", "recommended_technology": "Modbus TCP/IP & CAN 2.0B with IEC 61850 substation automation protocol support."},
                {"category": "Database", "recommended_technology": "TimescaleDB / InfluxDB — High-frequency electrical time-series logging."},
                {"category": "Dashboard", "recommended_technology": "Grafana Industrial UI — Live visualization of phase balance, solar generation, and battery SoH."},
                {"category": "Prototyping", "recommended_technology": "MATLAB / Simulink Simscape Electrical with hardware-in-the-loop (HIL) simulators."},
            ],
            "innovation_expansion": [
                {
                    "enhancement": "Electrochemical Impedance Spectroscopy (EIS) on Edge",
                    "technical_implementation": "Inject high-frequency perturbation currents across battery strings to extract internal resistance and dendrite formation.",
                    "patent_benefit": "Secures high-value claims on non-destructive battery degradation pre-emption.",
                },
                {
                    "enhancement": "Autonomous Microgrid Black-Start Synchronization",
                    "technical_implementation": "Implement droop-control inverter algorithms enabling multiple distributed generators to synchronize voltage without central clocking.",
                    "patent_benefit": "Protects decentralized islanded microgrid recovery architectures.",
                },
                {
                    "enhancement": "AI-Driven Arc-Fault Detection",
                    "technical_implementation": "Execute high-speed wavelets and spectral density analysis on DC buses to identify ionizing arc signatures within 5ms.",
                    "patent_benefit": "Expands patent coverage into critical electrical fire-prevention safety mechanisms.",
                },
                {
                    "enhancement": "Dynamic Grid Synthetic Inertia Emulation",
                    "technical_implementation": "Program converter firmware to inject instantaneous active power proportional to rate-of-change of grid frequency (RoCoF).",
                    "patent_benefit": "Claims grid-forming synthetic inertia algorithms for high-renewable penetration zones.",
                },
            ],
            "enhancement_roadmap": [
                {"phase": "Near-Term", "enhancement": "Wide-Bandgap Silicon Carbide (SiC) MOSFET Upgrades", "engineering_impact": "Elevates inverter efficiency to 98.8% while halving magnetic core size."},
                {"phase": "Near-Term", "enhancement": "Dynamic Peak-Shaving Firmware Profiles", "engineering_impact": "Cuts commercial utility demand charges by up to 35%."},
                {"phase": "Long-Term", "enhancement": "Decentralized Peer-to-Peer Energy Settlement", "engineering_impact": "Permits automated energy trading across adjacent microgrids."},
                {"phase": "Long-Term", "enhancement": "Second-Life EV Battery Pack Integration", "engineering_impact": "Enables mixed-chemistry pack operation without thermal imbalance."},
            ],
            "commercialization_potential": [
                {"item": "Target Market", "assessment": "Commercial solar-plus-storage, industrial manufacturing facilities, telecommunication towers, and microgrid developers."},
                {"item": "Deployment", "assessment": "Standard 19-inch rack-mount or outdoor NEMA 4X / IP65 enclosures with quick-connect DC busbars."},
                {"item": "Cost Complexity", "assessment": "Medium-to-High — Power semiconductor and magnetics dominate the Bill of Materials."},
                {"item": "Scalability", "assessment": "High — Modular inverter blocks allow linear capacity additions from 50kW to multiple megawatts."},
                {"item": "Regulatory Considerations", "assessment": "Grid interconnect standards (IEEE 1547, UL 1741-SA, CEA India), safety certifications (IEC 62109, IEC 62619)."},
            ],
        }

    def _domain_vision(self) -> Dict[str, Any]:
        return {
            "core_principle": [
                "The system provides high-speed optical inspection and spatial classification through calibrated optics, synchronized strobe illumination, and optimized neural edge models.",
                "Incoming frames are preprocessed for exposure stabilization and geometric distortion correction before entering a parallel feature extraction pipeline.",
                "Extracted bounding boxes, semantic masks, or dimensional measurements are evaluated against quality tolerance envelopes to trigger sorting or alarming mechanisms.",
            ],
            "key_modules": [
                {"module": "High-Speed Optical Ingestion", "purpose": "Global-shutter image acquisition synchronized with strobe illumination."},
                {"module": "Pre-Processing & Spatial Warping", "purpose": "Corrects optical distortion and normalizes lighting gradients."},
                {"module": "Neural Inference Core", "purpose": "Performs segmentation, detection, or anomaly classification at high FPS."},
                {"module": "Hardware Trigger & Strobe I/O", "purpose": "Synchronizes camera exposure with workpiece arrival with microsecond accuracy."},
            ],
            "technical_differentiators": [
                "Sub-15ms end-to-end latency from optical exposure to discrete I/O output.",
                "Zero-blur image acquisition on continuous conveyor lines up to 5 meters per second.",
                "Robust feature extraction insensitive to ambient factory lighting variations.",
            ],
            "system_flow": "Sensors detect workpiece presence, pulsing the strobe light and triggering camera exposure; the edge processor classifies defects within 20ms and commands downstream pneumatic rejectors.",
            "architecture_table": [
                {"layer": "Sensing", "components": "Industrial Global-Shutter Camera, Telecentric Lenses, Ring Illuminator", "data_flow": "Captures distortion-free, high-resolution visual frames."},
                {"layer": "Processing", "components": "Edge AI Box (NVIDIA Jetson / Intel Core Ultra), TensorRT Engine", "data_flow": "Executes neural segmentation and sub-pixel defect boundary calculations."},
                {"layer": "Control", "components": "Optocoupled Industrial I/O Module, High-Speed Pneumatic Ejector", "data_flow": "Pulses mechanical rejection within microsecond timing windows."},
                {"layer": "Monitoring", "components": "Operator Touchscreen Console, Defect Heatmap Database", "data_flow": "Visualizes live yield trends, defect Pareto charts, and archived inspection clips."},
            ],
            "recommended_technologies": [
                {"category": "AI Model", "recommended_technology": "YOLOv8-Seg / PatchCore Anomaly Detector — Sub-pixel defect segmentation and zero-shot anomaly detection."},
                {"category": "Processor", "recommended_technology": "NVIDIA Jetson Orin Nano / Advantech Industrial Edge PC — Sustains high tensor throughput."},
                {"category": "Sensors", "recommended_technology": "Basler / FLIR Global-Shutter GigE Vision camera with telecentric optics."},
                {"category": "Communication", "recommended_technology": "GigE Vision (Gigabit Ethernet) & Industrial Optoisolated 24V I/O."},
                {"category": "Database", "recommended_technology": "SQLite for local fast logging; MinIO for defect image storage with PostgreSQL metadata."},
                {"category": "Dashboard", "recommended_technology": "PyQt / Web-based HMI — Real-time display of inspection crops and statistical process control (SPC)."},
                {"category": "Prototyping", "recommended_technology": "OpenCV, GStreamer pipelines, and Roboflow for automated dataset labeling."},
            ],
            "innovation_expansion": [
                {
                    "enhancement": "Multi-Angle Photometric Stereo Defect Extraction",
                    "technical_implementation": "Rapidly cycle 4-quadrant directional strobe illumination to compute 3D surface normal maps, isolating micro-scratches from surface print.",
                    "patent_benefit": "Secures valuable claims on surface-relief defect discrimination independent of background color.",
                },
                {
                    "enhancement": "Few-Shot Unsupervised Anomaly Engine",
                    "technical_implementation": "Train memory-bank feature embeddings exclusively on pristine gold-standard units, flagging any statistical deviation as a defect.",
                    "patent_benefit": "Claims novel unsupervised inspection workflows that eliminate the need to collect rare defect samples.",
                },
                {
                    "enhancement": "Thermal & Optical Dual-Spectrum Registration",
                    "technical_implementation": "Align an uncooled LWIR micro-bolometer with the visual lens to simultaneously detect surface blemishes and internal heating.",
                    "patent_benefit": "Expands patent coverage into combined thermal-structural non-destructive testing.",
                },
                {
                    "enhancement": "Edge Active-Learning Feedback Loop",
                    "technical_implementation": "Automatically route borderline confidence detections to quality inspectors, updating the edge model without re-training.",
                    "patent_benefit": "Protects continuous online learning mechanisms in automated manufacturing environments.",
                },
            ],
            "enhancement_roadmap": [
                {"phase": "Near-Term", "enhancement": "TensorRT Model FP16/INT8 Quantization", "engineering_impact": "Doubles frame processing throughput from 45 FPS to 120 FPS."},
                {"phase": "Near-Term", "enhancement": "Automated Lens Dirt & Focus Calibration Check", "engineering_impact": "Prevents optical degradation from causing false reject spikes."},
                {"phase": "Long-Term", "enhancement": "3D Laser Line Profile Reconstruction", "engineering_impact": "Extends inspection to volumetric height and depth measurements."},
                {"phase": "Long-Term", "enhancement": "Multi-Camera Cross-View Object Association", "engineering_impact": "Enables seamless 360-degree inspection of complex freeform geometries."},
            ],
            "commercialization_potential": [
                {"item": "Target Market", "assessment": "High-volume packaging, automotive component manufacturers, electronics assembly, and pharmaceutical sorting."},
                {"item": "Deployment", "assessment": "Over-conveyor mounting bracket with adjustable C-mount optics and industrial IP65 enclosure."},
                {"item": "Cost Complexity", "assessment": "Medium — Precision industrial cameras and optics dictate professional assembly margins."},
                {"item": "Scalability", "assessment": "High — Software licenses and standardized optical gantries deploy quickly across production lines."},
                {"item": "Regulatory Considerations", "assessment": "CE/FCC Class A industrial emissions, ISO 9001 compliance tracking, and 21 CFR Part 11 audit trails for pharma."},
            ],
        }

    def _domain_general(self) -> Dict[str, Any]:
        return {
            "core_principle": [
                "The system provides structured signal acquisition, transparent edge decision processing, and reliable actuation/telemetry within a unified engineering architecture.",
                "Input sensors sample real-time operational metrics, conditioning raw readings through localized feature filters to eliminate electrical and physical noise.",
                "A modular decision engine matches incoming vectors against calibrated behavioral limits, triggering deterministic local actions while forwarding event states to supervisory interfaces.",
            ],
            "key_modules": [
                {"module": "Transducer Ingestion Unit", "purpose": "Samples primary operational signals with low-noise amplification."},
                {"module": "Feature Filtering & Processing", "purpose": "Applies edge filtering and rule-based or ML inference."},
                {"module": "Actuation & Control Driver", "purpose": "Executes hardware control commands with failsafe verification."},
                {"module": "Telemetry & Supervisory Interface", "purpose": "Presents operational states and logs audit data securely."},
            ],
            "technical_differentiators": [
                "Deterministic modular architecture maintaining fail-safe local function during communications loss.",
                "Sub-millisecond sensor acquisition with integrated fault-isolation watchdogs.",
                "Scalable hardware-software abstraction layer allowing drop-in transducer upgrades.",
            ],
            "system_flow": "Physical inputs are acquired by the sensor layer, digitized and evaluated by the edge processing core, converted into control actions by the actuation plane, and reported via the telemetry dashboard.",
            "architecture_table": [
                {"layer": "Sensing", "components": "Transducers, Conditioning Front-End, Environmental Probes", "data_flow": "Captures raw operational state parameters and analog signals."},
                {"layer": "Processing", "components": "Application Processor / MCU, Local Decision Core", "data_flow": "Executes algorithmic inference, bounds verification, and timing checks."},
                {"layer": "Control", "components": "Power Relays, Actuator Drivers, Local HMI Indicator", "data_flow": "Translates decision logic into physical states or alarms."},
                {"layer": "Monitoring", "components": "Supervisory Web/Mobile Dashboard, Event Log Historian", "data_flow": "Records event logs, displays analytics, and manages configuration."},
            ],
            "recommended_technologies": [
                {"category": "AI Model", "recommended_technology": "Gradient Boosted Trees / Lightweight ONNX Neural Model — Balances explainability with non-linear inference."},
                {"category": "Processor", "recommended_technology": "STM32H7 / ESP32-S3 — High-performance microcontroller with dual-core real-time execution."},
                {"category": "Sensors", "recommended_technology": "Application-specific industrial transducers with calibrated digital I2C/SPI interfaces."},
                {"category": "Communication", "recommended_technology": "Ethernet / Wi-Fi with MQTT over TLS — Robust industrial telemetry protocol."},
                {"category": "Database", "recommended_technology": "PostgreSQL with SQLite local edge buffer for offline resilience."},
                {"category": "Dashboard", "recommended_technology": "Streamlit / React Dashboard — Responsive, clean interface for operator oversight."},
                {"category": "Prototyping", "recommended_technology": "Python SDK, VS Code PlatformIO, and Logic Analyzer tooling."},
            ],
            "innovation_expansion": [
                {
                    "enhancement": "Deterministic Dynamic Safety Interlock",
                    "technical_implementation": "Add an independent analog or hardware-level comparator circuit that forcibly halts actuation if critical bounds are breached.",
                    "patent_benefit": "Establishes independent claims on dual-layer functional safety and fault containment.",
                },
                {
                    "enhancement": "Self-Diagnostic Calibration Loop",
                    "technical_implementation": "Periodically route internal reference voltages or known signals across sensors to calculate and correct drift offsets.",
                    "patent_benefit": "Secures claims on automated in-situ calibration without field technician intervention.",
                },
                {
                    "enhancement": "Secure Cryptographic Event Signing",
                    "technical_implementation": "Incorporate hardware secure elements to append cryptographic signatures to each logged event and action.",
                    "patent_benefit": "Protects audit-trail integrity and tamper-proof verification for regulatory compliance.",
                },
                {
                    "enhancement": "Modular Plug-and-Play Expansion Bus",
                    "technical_implementation": "Define a standardized physical and logical I/O bus enabling hot-swappable sensor and actuator modules.",
                    "patent_benefit": "Broadens claim scope to encompass modular, field-extensible system architectures.",
                },
            ],
            "enhancement_roadmap": [
                {"phase": "Near-Term", "enhancement": "Real-Time OS (FreeRTOS) Migration", "engineering_impact": "Guarantees deterministic task execution with microsecond scheduling accuracy."},
                {"phase": "Near-Term", "enhancement": "Power Optimization & Low-Power Sleep States", "engineering_impact": "Reduces standby power consumption by over 60%."},
                {"phase": "Long-Term", "enhancement": "Distributed Multi-Node Mesh Orchestration", "engineering_impact": "Permits collaborative operation across networked installations."},
                {"phase": "Long-Term", "enhancement": "Autonomous Predictive Maintenance Analytics", "engineering_impact": "Forecasts component wear and schedules service before field failure occurs."},
            ],
            "commercialization_potential": [
                {"item": "Target Market", "assessment": "Industrial automation, smart building infrastructure, OEM equipment manufacturers."},
                {"item": "Deployment", "assessment": "DIN-rail or panel-mounted enclosure designed for standard industrial control cabinets."},
                {"item": "Cost Complexity", "assessment": "Medium — Standard commercial microcontrollers and off-the-shelf components ensure competitive BOM."},
                {"item": "Scalability", "assessment": "High — Modular software firmware and standardized interfaces allow straightforward market expansion."},
                {"item": "Regulatory Considerations", "assessment": "Industrial EMC standards (CE/FCC Class B), electrical safety (IEC 61010), and RoHS compliance."},
            ],
        }

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "invention_title": "",
            "invention_description": "",
            "technical_concept": {
                "core_principle": ["Insufficient title and description were provided to generate the technical concept."],
                "key_modules": [],
                "technical_differentiators": [],
            },
            "system_architecture": {
                "system_flow": "N/A",
                "architecture_table": [],
            },
            "recommended_technologies": [],
            "innovation_expansion": [],
            "enhancement_roadmap": [],
            "commercialization_potential": [],
            "concept_expansion": "N/A",
            "suggested_system_architecture": "N/A",
            "hardware_components": [],
            "software_stack": [],
            "advanced_enhancement_ideas": [],
        }
