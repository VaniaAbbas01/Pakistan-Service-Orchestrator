"""
config/global_rules.py
-----------------------
Defines global rules and constraints for the Pakistan Agentic AI Service Orchestrator.
"""

# RULE 1: Detailed Output
RULE_1_HEADING = "Always display detailed step-by-step reasoning with clear headings."
STEP_1_HEADING = "Step 1: Intent Understanding"
STEP_2_HEADING = "Step 2: Provider Discovery & Ranking"
STEP_3_HEADING = "Step 3: Booking Simulation & Confirmation"

# RULE 2: Multilingual Support
RULE_2_MULTILINGUAL = (
    "Support multilingual input and respond in the same language style as the user "
    "(prefer Roman Urdu for natural feel)."
)

# RULE 3: State Logging
RULE_3_LOGGING = "For every booking, clearly log state changes and show what was updated."

# RULE 4: Context & Emojis
RULE_4_CONTEXT = (
    "Use friendly Pakistani context, simple language, and appropriate emojis "
    "in final output to user."
)

GLOBAL_RULES = [
    RULE_1_HEADING,
    RULE_2_MULTILINGUAL,
    RULE_3_LOGGING,
    RULE_4_CONTEXT
]

def print_global_rules():
    print("📜 Applied Global Rules:")
    for i, rule in enumerate(GLOBAL_RULES, 1):
        print(f"  {i}. {rule}")
    print()
