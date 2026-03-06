import sys
import json
import os
import datetime
from utils.phi_lite import PHILite

class AgentMonitor:
    """
    Agent Behavior Monitor
    [PATENT_CLAIM_1: Prosodic Signal Vectorization]
    [PATENT_CLAIM_8: Zero Trust Gateway Interceptor]
    """
    def __init__(self, input_source=None):
        self.phi = PHILite()
        self.input_source = input_source or sys.stdin

    def monitor(self):
        # Determine if we're reading from a file or stdin
        if isinstance(self.input_source, str):
            if os.path.exists(self.input_source):
                with open(self.input_source, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = self.input_source # Treat as raw text
        else:
            content = self.input_source.read()

        if not content.strip():
            return {"error": "No input content detected", "threat_level": "UNKNOWN"}

        analysis = self.phi.analyze(content)
        
        now = datetime.datetime.now(datetime.timezone.utc)
        event_data = {
            "timestamp": now.isoformat().split('.')[0] + "Z",
            "event_type": "BEHAVIOR_MONITOR",
            "input_preview": content[:100] + "..." if len(content) > 100 else content,
            "phi_scores": {
                dim: results["score"] 
                for dim, results in analysis["dimensions"].items()
            },
            "overall_score": analysis["overall_score"],
            "threat_level": analysis["threat_label"],
            "findings": [
                {
                    "dimension": dim,
                    "severity": "HIGH" if res["score"] > 0.7 else "MEDIUM" if res["score"] > 0.4 else "LOW",
                    "evidence": res["matches"]
                } for dim, res in analysis["dimensions"].items() if res["matches"]
            ]
        }
        
        return event_data

if __name__ == "__main__":
    # Support both piped input and command line argument
    source = sys.argv[1] if len(sys.argv) > 1 else sys.stdin
    monitor = AgentMonitor(source)
    result = monitor.monitor()
    
    # Clean output for piping
    print(json.dumps(result, indent=2))
