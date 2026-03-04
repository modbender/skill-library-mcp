#!/usr/bin/env python3
"""
Research AI search prompts for GEO strategy.
"""

import argparse
import json
import sys
from datetime import datetime


class PromptResearcher:
    """Generate and research AI search prompts."""
    
    def __init__(self, brand, category, competitors=None, audience=None):
        self.brand = brand
        self.category = category
        self.competitors = competitors or []
        self.audience = audience or ""
        self.prompts = []
    
    def generate_all_prompts(self):
        """Generate prompts across all types and stages."""
        self._generate_discovery_prompts()
        self._generate_comparison_prompts()
        self._generate_howto_prompts()
        self._generate_definition_prompts()
        self._generate_recommendation_prompts()
        self._generate_problem_aware_prompts()
        return self.prompts
    
    def _generate_discovery_prompts(self):
        """Generate discovery-type prompts."""
        templates = [
            "best {category}",
            "best {category} for {audience}",
            "top {category} tools",
            "top {category} for {audience}",
            "{category} recommendations",
            "{category} recommendations for {audience}",
            "what {category} should I use",
            "what is the best {category}",
        ]
        
        for template in templates:
            prompt = template.format(
                category=self.category,
                audience=self.audience or "teams"
            )
            self.prompts.append({
                "prompt": prompt,
                "type": "discovery",
                "intent": "commercial",
                "priority": "high"
            })
    
    def _generate_comparison_prompts(self):
        """Generate comparison prompts."""
        # Brand vs competitors
        for competitor in self.competitors[:3]:
            self.prompts.append({
                "prompt": f"{self.brand} vs {competitor}",
                "type": "comparison",
                "intent": "commercial",
                "priority": "high"
            })
            self.prompts.append({
                "prompt": f"{competitor} vs {self.brand}",
                "type": "comparison",
                "intent": "commercial",
                "priority": "high"
            })
            self.prompts.append({
                "prompt": f"{self.brand} or {competitor}",
                "type": "comparison",
                "intent": "commercial",
                "priority": "high"
            })
        
        # Competitor vs competitor (gaps)
        for i, comp1 in enumerate(self.competitors[:2]):
            for comp2 in self.competitors[i+1:3]:
                self.prompts.append({
                    "prompt": f"{comp1} vs {comp2}",
                    "type": "comparison",
                    "intent": "commercial",
                    "priority": "high",
                    "note": "Gap: Brand not mentioned"
                })
        
        # Alternative prompts
        for competitor in self.competitors[:2]:
            self.prompts.append({
                "prompt": f"alternative to {competitor}",
                "type": "comparison",
                "intent": "commercial",
                "priority": "high"
            })
            self.prompts.append({
                "prompt": f"cheaper alternative to {competitor}",
                "type": "comparison",
                "intent": "commercial",
                "priority": "medium"
            })
    
    def _generate_howto_prompts(self):
        """Generate how-to prompts."""
        templates = [
            "how to use {brand}",
            "how to get started with {category}",
            "how to choose {category}",
            "how to switch from {competitor} to {brand}",
            "how to implement {category}",
        ]
        
        for template in templates:
            if "{competitor}" in template and self.competitors:
                for comp in self.competitors[:2]:
                    self.prompts.append({
                        "prompt": template.format(brand=self.brand, category=self.category, competitor=comp),
                        "type": "how-to",
                        "intent": "informational",
                        "priority": "medium"
                    })
            else:
                self.prompts.append({
                    "prompt": template.format(brand=self.brand, category=self.category),
                    "type": "how-to",
                    "intent": "informational",
                    "priority": "medium"
                })
    
    def _generate_definition_prompts(self):
        """Generate definition prompts."""
        # Category definitions
        self.prompts.append({
            "prompt": f"what is {self.category}",
            "type": "definition",
            "intent": "informational",
            "priority": "medium"
        })
        
        # Brand definitions (if not well known)
        self.prompts.append({
            "prompt": f"what is {self.brand}",
            "type": "definition",
            "intent": "informational",
            "priority": "low"
        })
    
    def _generate_recommendation_prompts(self):
        """Generate recommendation prompts."""
        templates = [
            "recommend a {category}",
            "recommend {category} for {audience}",
            "suggest a {category}",
            "what {category} should I choose",
            "looking for {category}",
        ]
        
        for template in templates:
            self.prompts.append({
                "prompt": template.format(category=self.category, audience=self.audience or "my team"),
                "type": "recommendation",
                "intent": "commercial",
                "priority": "high"
            })
    
    def _generate_problem_aware_prompts(self):
        """Generate problem-aware prompts."""
        templates = [
            "how to solve [problem]",
            "why is [problem] happening",
            "best way to [achieve outcome]",
        ]
        
        # These are category-specific and would need customization
        # Adding placeholders for user to fill in
        self.prompts.append({
            "prompt": "[CUSTOMIZE: how to solve your audience's main problem]",
            "type": "problem-aware",
            "intent": "informational",
            "priority": "medium",
            "note": "Customize based on your audience's pain points"
        })
    
    def cluster_prompts(self):
        """Group prompts by theme."""
        clusters = {}
        
        for prompt in self.prompts:
            text = prompt["prompt"].lower()
            
            # Simple keyword-based clustering
            if any(word in text for word in ["vs", "compare", "alternative", "or"]):
                cluster = "comparisons"
            elif any(word in text for word in ["how to", "guide", "steps"]):
                cluster = "how-to"
            elif any(word in text for word in ["best", "top", "recommend"]):
                cluster = "discovery"
            elif "what is" in text:
                cluster = "definitions"
            elif "price" in text or "cost" in text or "free" in text:
                cluster = "pricing"
            else:
                cluster = "other"
            
            if cluster not in clusters:
                clusters[cluster] = []
            clusters[cluster].append(prompt)
        
        return clusters
    
    def generate_report(self):
        """Generate markdown report."""
        lines = [
            f"# AI Prompt Research Report\n",
            f"**Brand**: {self.brand}  ",
            f"**Category**: {self.category}  ",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d')}\n",
            f"**Competitors**: {', '.join(self.competitors) if self.competitors else 'None specified'}\n",
            "---\n",
            "## Summary\n",
            f"- **Total prompts**: {len(self.prompts)}\n",
        ]
        
        # Count by priority
        high = sum(1 for p in self.prompts if p.get("priority") == "high")
        medium = sum(1 for p in self.prompts if p.get("priority") == "medium")
        low = sum(1 for p in self.prompts if p.get("priority") == "low")
        
        lines.append(f"- **High priority**: {high}")
        lines.append(f"- **Medium priority**: {medium}")
        lines.append(f"- **Low priority**: {low}\n")
        
        # High priority section
        lines.append("## 🔴 High Priority Prompts\n")
        high_prompts = [p for p in self.prompts if p.get("priority") == "high"]
        for i, prompt in enumerate(high_prompts[:20], 1):
            lines.append(f"{i}. \"{prompt['prompt']}\" — {prompt['type']}")
        if len(high_prompts) > 20:
            lines.append(f"\n... and {len(high_prompts) - 20} more\n")
        
        # Clusters
        lines.append("\n## Topic Clusters\n")
        clusters = self.cluster_prompts()
        for cluster_name, cluster_prompts in clusters.items():
            lines.append(f"### {cluster_name.title()} ({len(cluster_prompts)} prompts)")
            for p in cluster_prompts[:5]:
                lines.append(f"- \"{p['prompt']}\"")
            if len(cluster_prompts) > 5:
                lines.append(f"- ... and {len(cluster_prompts) - 5} more")
            lines.append("")
        
        # Recommendations
        lines.append("## Recommended Actions\n")
        lines.append("1. **Content priority**: Create comparison pages for top competitor pairs")
        lines.append("2. **Quick win**: Optimize existing content for 'best [category]' queries")
        lines.append("3. **Long-term**: Build comprehensive guides for how-to prompts")
        
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description="Research AI search prompts")
    parser.add_argument("--brand", required=True, help="Brand name")
    parser.add_argument("--category", required=True, help="Product category")
    parser.add_argument("--competitors", help="Comma-separated competitor names")
    parser.add_argument("--audience", help="Target audience description")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="Output format")
    
    args = parser.parse_args()
    
    competitors = [c.strip() for c in args.competitors.split(",")] if args.competitors else []
    
    researcher = PromptResearcher(
        brand=args.brand,
        category=args.category,
        competitors=competitors,
        audience=args.audience
    )
    
    researcher.generate_all_prompts()
    
    if args.format == "json":
        output = json.dumps(researcher.prompts, indent=2)
    else:
        output = researcher.generate_report()
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Report saved to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
