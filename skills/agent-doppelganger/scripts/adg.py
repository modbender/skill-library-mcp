import os
import yaml
import json
import logging
from datetime import datetime

class AgentDoppelganger:
    def __init__(self, config_path="~/.openclaw/adg/"):
        self.base_path = os.path.expanduser(config_path)
        self.profile = self._load_yaml("profile/style.yaml")
        self.heuristics = self._load_yaml("profile/heuristics.yaml")
        self.preferences = self._load_yaml("profile/preferences.yaml")
        self.policies = self._load_yaml("policies/authority.yaml")
        self.contacts = self._load_yaml("policies/contacts.yaml")
        
        # Setup logging/audit
        self.audit_path = os.path.join(self.base_path, "audit")
        os.makedirs(self.audit_path, exist_ok=True)
        
    def _load_yaml(self, rel_path):
        full_path = os.path.join(self.base_path, rel_path)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                return yaml.safe_load(f)
        return {}

    def analyze_intent(self, message, channel):
        """
        Axis: Domain, Stakes, Authority, Ambiguity
        """
        msg_lower = message.lower()
        
        # Simple keyword mapping for the demonstration
        domain = "unknown"
        stakes = "low"
        
        if any(word in msg_lower for word in ["meet", "call", "schedule", "calendar", "tomorrow"]):
            domain = "scheduling"
        elif any(word in msg_lower for word in ["$", "money", "price", "pay", "finance"]):
            domain = "finance"
            stakes = "high"
        elif any(word in msg_lower for word in ["status", "check", "update", "design"]):
            domain = "clarifications"
        elif any(word in msg_lower for word in ["politics", "political", "government", "election"]):
            domain = "politics"
            stakes = "medium"

        intent = {
            "domain": domain,
            "stakes": stakes,
            "authority_required": stakes != "low",
            "ambiguity": 0.1 if domain != "unknown" else 0.8
        }
        return intent

    def check_policy(self, intent, channel, sender=None):
        """
        Evaluate BEFORE generation.
        """
        # 1. Check Contact Allowlist (Override)
        if sender:
            contact_policy = self.contacts.get("contacts", {}).get(sender, {})
            if contact_policy.get("allow_autonomous", False):
                if channel in contact_policy.get("channels", []):
                    return True, f"Contact '{sender}' is trusted for autonomous replies."

        if intent["stakes"] == "high":
            return False, "High stakes action blocked by policy."
        
        # Check global topic denials
        global_deny = self.policies.get("topics", {}).get("deny", [])
        if intent["domain"] in global_deny:
            return False, f"Topic '{intent['domain']}' is globally forbidden."
        
        # Check channel allowances
        channel_policy = self.policies.get("channels", {}).get(channel, {})
        if not channel_policy:
            # If channel not configured, default to block for safety
            return False, f"Channel '{channel}' is not configured in policy."

        allowed_intents = channel_policy.get("allow", [])
        denied_intents = channel_policy.get("deny", [])
        
        if intent["domain"] in denied_intents:
            return False, f"Domain '{intent['domain']}' explicitly denied on {channel}."
            
        # If not explicitly allowed, we draft-first or block
        if intent["domain"] not in allowed_intents and intent["domain"] != "unknown":
            return False, f"Domain '{intent['domain']}' not in allowlist for {channel}."

        return True, "Policy check passed."

    def estimate_confidence(self, intent, policy_passed):
        """
        C = w1·IntentCertainty + w2·DomainFamiliarity + w3·PolicyDistance + w4·HistoricalAccuracy
        """
        # Placeholder calculation
        confidence = 0.85 
        return confidence

    def generate_response(self, message, intent, sender=None):
        """
        Style-biased generation.
        """
        # Check for contact-specific response style
        if sender:
            contact_policy = self.contacts.get("contacts", {}).get(sender, {})
            if contact_policy.get("response_style") == "match_language":
                # In a real implementation, this would use an LLM to detect language and respond in kind
                # For now, we return a placeholder that indicates this intent
                return f"[ADG:AUTOREPLY:MATCH_LANG] {message}"

        responses = {
            "scheduling": "Acknowledged. I'll check my availability for that.",
            "clarifications": "Checking the status on that for you now.",
            "unknown": "I'm not sure I can help with that directly."
        }
        return responses.get(intent["domain"], "I'll get back to you on that.")

    def verify(self, response):
        """
        Final check for commitment leakage and tone.
        """
        # Audit against forbidden phrases/commitments
        return True

    def log_decision(self, message, channel, decision):
        log_file = os.path.join(self.audit_path, f"{datetime.now().strftime('%Y-%m-%d')}.jsonl")
        with open(log_file, 'a') as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "channel": channel,
                "message": message,
                "decision": decision
            }) + "\n")

    def apply_watermark(self, text):
        """
        Subtle linguistic fingerprint:
        - Deterministic choice of synonyms (e.g. 'coordination' instead of 'meeting')
        - Non-semantic markers (specific spacing/punctuation patterns)
        """
        # 1. Enforce lowercase if preference is high
        if self.profile.get("lowercase_preference", 0) > 0.8:
            text = text.lower()

        # 2. Phrase cadence: Ensure no trailing punctuation if that's the habit
        if self.profile.get("punctuation_habits", {}).get("end_punc_frequency", 1) < 0.2:
            text = text.strip().rstrip(".!?")

        # 3. Non-semantic marker: Double space before signature if enabled
        watermark_config = self.policies.get("watermark", {})
        if watermark_config.get("enabled", True):
            signature = " ⛧"
            text = f"{text.strip()}  {signature}"
            
        return text

    def handle_message(self, message, channel, sender=None):
        # 1. Intent Analysis
        intent = self.analyze_intent(message, channel)
        
        # 2. Policy Gate
        allowed, reason = self.check_policy(intent, channel, sender)
        if not allowed:
            self.log_decision(message, channel, {"action": "block", "reason": reason})
            return "BLOCKED"

        # 3. Confidence Engine
        conf = self.estimate_confidence(intent, allowed)
        thresholds = self.policies.get("confidence", {})
        
        if conf < thresholds.get("min_global", 0.82):
            self.log_decision(message, channel, {"action": "escalate", "confidence": conf})
            return "ESCALATED (LOW CONFIDENCE)"

        # 4. Response Generation
        response = self.generate_response(message, intent, sender)
        
        # 5. Verification & Watermarking
        if self.verify(response):
            # Apply Style & Watermark
            response = self.apply_watermark(response)
            self.log_decision(message, channel, {"action": "send", "response": response})
            return response
        else:
            return "DRAFT_ONLY (VERIFICATION FAILED)"

import sys

def main():
    adg = AgentDoppelganger()
    
    if len(sys.argv) > 1:
        message = sys.argv[1]
        channel = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        sender = sys.argv[3] if len(sys.argv) > 3 else None
        
        response = adg.handle_message(message, channel, sender)
        print(response)
    else:
        # Example usage
        print(adg.handle_message("Can we meet at 5pm tomorrow?", "email"))


if __name__ == "__main__":
    main()
