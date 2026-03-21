"""
Medical Agent Safety Layer.

This module implements HARD POLICY CONSTRAINTS for the medical agent:
- Emergency keyword detection (triggers immediate escalation)
- Prohibited action enforcement (no diagnosis, no prescriptions)
- Medical disclaimer injection
- PHI sanitization helpers
- Input validation

These constraints are enforced at the code level — they are NOT
simply part of the LLM prompt and cannot be overridden by user input.
"""

from __future__ import annotations

import logging
import re
from typing import List, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# HARD POLICY CONSTRAINTS
# These represent the non-negotiable safety boundaries.
# ---------------------------------------------------------------------------

PROHIBITED_ACTIONS: List[str] = [
    "prescribe medication",
    "diagnose",
    "provide a diagnosis",
    "order lab tests",
    "interpret radiology",
    "recommend surgery",
    "replace a doctor",
    "guarantee a cure",
]

MEDICAL_DISCLAIMER = (
    "⚠️ MEDICAL DISCLAIMER: This assessment is for informational and triage "
    "support purposes only. It does NOT constitute medical advice, a diagnosis, "
    "or a treatment plan. Always consult a licensed healthcare professional. "
    "In an emergency, call 911 or go to the nearest emergency room immediately."
)

# ---------------------------------------------------------------------------
# EMERGENCY KEYWORD DETECTION
# These patterns trigger immediate high-risk escalation regardless of
# the rest of the risk scoring pipeline.
# ---------------------------------------------------------------------------

EMERGENCY_PATTERNS: List[str] = [
    # Cardiac
    r"\bchest\s*pain\b",
    r"\bchest\s*pressure\b",
    r"\bchest\s*tightness\b",
    r"\bheart\s*attack\b",
    r"\bpalpitation",
    r"\birregular\s*heartbeat\b",
    # Neurological
    r"\bstroke\b",
    r"\bseizure\b",
    r"\bunconscious\b",
    r"\bpassed\s*out\b",
    r"\bfainted\b",
    r"\bcan.?t\s*(speak|talk|move)\b",
    r"\bnumbness\b.*\b(face|arm|leg)\b",
    r"\bsudden\s*(headache|vision|weakness)\b",
    r"\bconfusion\b",
    r"\bdisoriented\b",
    # Respiratory
    r"\bcan.?t\s*breathe\b",
    r"\bdifficulty\s*breathing\b",
    r"\bshortness\s*of\s*breath\b",
    r"\bnot\s*breathing\b",
    r"\bblue\s*lips?\b",
    r"\bcyanosis\b",
    # Bleeding / Trauma
    r"\bheavy\s*bleeding\b",
    r"\buncontrolled\s*bleeding\b",
    r"\bsevere\s*bleeding\b",
    r"\bcoughing\s*(up\s*)?blood\b",
    r"\bvomiting\s*blood\b",
    r"\bblood\s*in\s*(stool|urine)\b",
    # Allergic / Toxic
    r"\banaphylaxis\b",
    r"\bsevere\s*allergic\b",
    r"\bthroat\s*swelling\b",
    r"\bpoisoning\b",
    r"\boverdose\b",
    r"\bsuicid",          # suicidal / suicide attempt
    r"\bself.?harm\b",
    # High fever / Sepsis
    r"\bhigh\s*fever\b",
    r"\bsepsis\b",
    r"\btemperature\s*(of\s*)?(40|41|42|43|44)\b",  # ≥40°C
    # Obstetric
    r"\bheavy\s*vaginal\s*bleeding\b",
    r"\bwater\s*(broke|broken)\b",
    r"\bpremature\s*labor\b",
    # General distress
    r"\bcan.?t\s*(move|walk|stand)\b",
    r"\bextreme\s*pain\b",
    r"\bworst\s*(pain|headache)\s*(of\s*my\s*life)?\b",
]

_COMPILED_EMERGENCY = [re.compile(p, re.IGNORECASE) for p in EMERGENCY_PATTERNS]

# HIGH-RISK patterns (not emergency-level but flag for medium-high risk)
HIGH_RISK_PATTERNS: List[str] = [
    r"\bsevere\s*(pain|headache|nausea|vomiting|dizziness)\b",
    r"\bpersistent\s*fever\b",
    r"\bfever\s*(for\s*more\s*than\s*[3-9]|over\s*[3-9])\s*days?\b",
    r"\bblood\s*(in\s*)?(stool|urine|vomit|sputum)\b",
    r"\bsudden\s*(weight\s*loss|fatigue)\b",
    r"\bnight\s*sweats\b",
    r"\bdiabetes\b.*\b(uncontrolled|spike|crash)\b",
    r"\bdehydration\b",
    r"\bjaundice\b",
    r"\byellow\s*(skin|eyes)\b",
]

_COMPILED_HIGH_RISK = [re.compile(p, re.IGNORECASE) for p in HIGH_RISK_PATTERNS]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def detect_emergency_keywords(text: str) -> Tuple[bool, List[str]]:
    """
    Scan patient input for emergency-level keywords.

    Returns:
        (is_emergency, list_of_matched_patterns)

    This function is called BEFORE any LLM processing.
    If is_emergency is True, the agent MUST escalate immediately.
    """
    matched: List[str] = []
    for pattern in _COMPILED_EMERGENCY:
        if pattern.search(text):
            matched.append(pattern.pattern)

    if matched:
        logger.warning(
            "Emergency keywords detected in patient input. Patterns: %s", matched
        )
    return bool(matched), matched


def detect_high_risk_keywords(text: str) -> Tuple[bool, List[str]]:
    """
    Scan patient input for high-risk (non-emergency) keywords.

    Returns:
        (is_high_risk, list_of_matched_patterns)
    """
    matched: List[str] = []
    for pattern in _COMPILED_HIGH_RISK:
        if pattern.search(text):
            matched.append(pattern.pattern)
    return bool(matched), matched


def enforce_prohibited_actions(agent_response: str) -> Tuple[bool, str]:
    """
    Check if an LLM-generated response violates hard medical policies.

    If a violation is detected, the response is blocked and replaced
    with a safe refusal message.

    Returns:
        (violation_found, safe_response)
    """
    lower_response = agent_response.lower()
    for action in PROHIBITED_ACTIONS:
        if action in lower_response:
            logger.error(
                "POLICY VIOLATION: Agent response contained prohibited action: '%s'. "
                "Response blocked.",
                action,
            )
            safe_response = (
                "I'm sorry, I'm not able to provide that type of medical guidance. "
                "Please consult a licensed healthcare professional for diagnosis, "
                "prescriptions, or treatment decisions. "
                f"\n\n{MEDICAL_DISCLAIMER}"
            )
            return True, safe_response
    return False, agent_response


def inject_disclaimer(response: str) -> str:
    """Append the mandatory medical disclaimer to any agent response."""
    if MEDICAL_DISCLAIMER not in response:
        return f"{response}\n\n{MEDICAL_DISCLAIMER}"
    return response


def sanitize_phi(text: str) -> str:
    """
    Basic PHI sanitization — redacts common patterns before logging.
    This is a lightweight helper; full PHI handling requires field-level encryption.
    """
    # Redact SSN
    text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN REDACTED]", text)
    # Redact phone numbers
    text = re.sub(
        r"\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b",
        "[PHONE REDACTED]",
        text,
    )
    # Redact email
    text = re.sub(
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b",
        "[EMAIL REDACTED]",
        text,
    )
    # Redact dates that look like DOB (MM/DD/YYYY or MM-DD-YYYY)
    text = re.sub(
        r"\b(0?[1-9]|1[0-2])[/\-](0?[1-9]|[12]\d|3[01])[/\-](19|20)\d{2}\b",
        "[DOB REDACTED]",
        text,
    )
    return text


def validate_symptom_input(text: str) -> Tuple[bool, str]:
    """
    Basic input validation before passing to the agent.
    Rejects injections, excessively long inputs, and empty strings.

    Returns:
        (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Input cannot be empty."
    if len(text) > 5000:
        return False, "Input exceeds the maximum allowed length (5000 characters)."
    # Block obvious prompt injection attempts
    injection_patterns = [
        r"ignore\s+(previous|all)\s+instructions?",
        r"you\s+are\s+now\s+(a\s+)?different",
        r"pretend\s+(you\s+are|to\s+be)",
        r"disregard\s+(your|all)\s+(rules?|guidelines?|instructions?)",
        r"jailbreak",
        r"DAN\s+mode",
    ]
    for p in injection_patterns:
        if re.search(p, text, re.IGNORECASE):
            logger.warning("Prompt injection attempt detected and blocked.")
            return False, "Invalid input detected. Please describe your symptoms clearly."
    return True, ""
