#!/usr/bin/env python3
"""
Arccos Golf Analysis Script

Analyzes Arccos Golf performance data including club distances, strokes gained,
scoring patterns, and performance trends. Designed for security compliance
with no subprocess calls or external dependencies.

Author: OpenClaw AI Agent
Version: 1.0.0
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import statistics


class ArccosAnalyzer:
    """Main analyzer for Arccos Golf data."""
    
    def __init__(self, data_file: Path):
        """Initialize analyzer with data file path.
        
        Args:
            data_file: Path to Arccos data JSON file
            
        Raises:
            FileNotFoundError: If data file doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load and validate Arccos data from JSON file.
        
        Returns:
            Dict containing the parsed JSON data
            
        Raises:
            FileNotFoundError: If the specified file doesn't exist
            json.JSONDecodeError: If the JSON file is malformed
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found: {self.data_file}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in {self.data_file}: {e}")
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get overall summary statistics.
        
        Returns:
            Dict containing summary statistics
        """
        return {
            'golfer': self.data.get('golfer', 'Unknown'),
            'last_updated': self.data.get('last_fetched', 'Unknown'),
            'total_shots': self.data.get('total_shots', 0),
            'total_rounds': self.data.get('total_rounds', 0),
            'longest_drive': self.data.get('longest_shot', 0),
            'current_handicap_breakdown': self.data.get('handicap_breakdown', {}),
            'overall_strokes_gained': self.data.get('strokes_gained', {}).get('overall', 0),
        }
    
    def get_strokes_gained_analysis(self) -> Dict[str, Any]:
        """Analyze strokes gained performance across all categories.
        
        Returns:
            Dict with strokes gained analysis and improvement suggestions
        """
        sg_data = self.data.get('strokes_gained', {})
        
        # Categorize performance (positive is good, negative is bad)
        categories = ['driving', 'approach', 'short_game', 'putting']
        analysis = {
            'overall': sg_data.get('overall', 0),
            'by_category': {},
            'strengths': [],
            'weaknesses': [],
            'improvement_priority': []
        }
        
        for category in categories:
            value = sg_data.get(category, 0)
            analysis['by_category'][category] = value
            
            if value > 0:
                analysis['strengths'].append(f"{category.replace('_', ' ').title()}: +{value:.1f}")
            elif value < -1.0:
                analysis['weaknesses'].append(f"{category.replace('_', ' ').title()}: {value:.1f}")
        
        # Sort weaknesses by magnitude for improvement priority
        weakness_values = [(cat, abs(sg_data.get(cat, 0))) for cat in categories if sg_data.get(cat, 0) < -1.0]
        weakness_values.sort(key=lambda x: x[1], reverse=True)
        analysis['improvement_priority'] = [cat.replace('_', ' ').title() for cat, _ in weakness_values]
        
        return analysis
    
    def get_club_distances(self, club_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get club distance analysis.
        
        Args:
            club_filter: Optional filter for specific club type (e.g., 'iron', 'wedge', 'wood')
            
        Returns:
            List of club distance data
        """
        clubs = self.data.get('clubs', [])
        
        if club_filter:
            filter_lower = club_filter.lower()
            clubs = [club for club in clubs if filter_lower in club.get('club', '').lower()]
        
        # Sort by average distance descending
        clubs_with_distance = [club for club in clubs if club.get('avg_distance', 0) > 0]
        clubs_with_distance.sort(key=lambda x: x.get('avg_distance', 0), reverse=True)
        
        return clubs_with_distance
    
    def get_scoring_analysis(self) -> Dict[str, Any]:
        """Analyze scoring patterns and performance.
        
        Returns:
            Dict with scoring analysis
        """
        scoring = self.data.get('scoring', {})
        
        analysis = {
            'scoring_averages': {
                'par_3': scoring.get('par3_avg', 0),
                'par_4': scoring.get('par4_avg', 0), 
                'par_5': scoring.get('par5_avg', 0)
            },
            'score_distribution': {
                'birdies': f"{scoring.get('birdies_pct', 0)}%",
                'pars': f"{scoring.get('pars_pct', 0)}%",
                'bogeys': f"{scoring.get('bogeys_pct', 0)}%",
                'double_plus': f"{scoring.get('double_plus_pct', 0)}%"
            }
        }
        
        # Calculate scoring tendencies
        total_under_par = scoring.get('birdies_pct', 0)
        total_at_par = scoring.get('pars_pct', 0) 
        total_over_par = scoring.get('bogeys_pct', 0) + scoring.get('double_plus_pct', 0)
        
        analysis['tendencies'] = {
            'under_par': f"{total_under_par}%",
            'at_par': f"{total_at_par}%", 
            'over_par': f"{total_over_par}%"
        }
        
        return analysis
    
    def get_putting_analysis(self) -> Dict[str, Any]:
        """Analyze putting performance.
        
        Returns:
            Dict with putting analysis
        """
        putting = self.data.get('putting', {})
        
        return {
            'putts_per_round': putting.get('putts_per_round', 0),
            'putts_per_hole': putting.get('putts_per_hole', 0),
            'putts_per_gir': putting.get('putts_per_gir', 0),
            'distribution': {
                'one_putts': f"{putting.get('one_putt_pct', 0)}%",
                'two_putts': f"{putting.get('two_putt_pct', 0)}%",
                'three_plus_putts': f"{putting.get('three_plus_putt_pct', 0)}%"
            },
            'strokes_gained_by_distance': putting.get('sg_by_distance', {})
        }
    
    def get_recent_rounds(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent round performance.
        
        Args:
            limit: Number of recent rounds to return
            
        Returns:
            List of recent rounds data
        """
        rounds = self.data.get('recent_rounds', [])
        return rounds[:limit]
    
    def get_approach_analysis(self) -> Dict[str, Any]:
        """Analyze approach shot performance.
        
        Returns:
            Dict with approach shot analysis
        """
        approach = self.data.get('approach', {})
        
        return {
            'greens_in_regulation': f"{approach.get('gir_pct', 0)}%",
            'gir_per_round': approach.get('gir_per_round', 0),
            'miss_distribution': approach.get('distribution', {}),
            'strokes_gained_by_distance': approach.get('sg_by_distance', {}),
            'strokes_gained_by_terrain': approach.get('sg_by_terrain', {})
        }
    
    def generate_report(self, format_type: str = 'text') -> Union[str, Dict[str, Any]]:
        """Generate comprehensive analysis report.
        
        Args:
            format_type: Output format ('text' or 'json')
            
        Returns:
            Formatted report as string or dict
        """
        if format_type == 'json':
            return {
                'summary': self.get_summary_stats(),
                'strokes_gained': self.get_strokes_gained_analysis(),
                'clubs': self.get_club_distances(),
                'scoring': self.get_scoring_analysis(),
                'putting': self.get_putting_analysis(),
                'approach': self.get_approach_analysis(),
                'recent_rounds': self.get_recent_rounds()
            }
        
        # Text format
        summary = self.get_summary_stats()
        sg_analysis = self.get_strokes_gained_analysis()
        clubs = self.get_club_distances()
        scoring = self.get_scoring_analysis()
        putting = self.get_putting_analysis()
        approach = self.get_approach_analysis()
        rounds = self.get_recent_rounds()
        
        report_lines = [
            "🏌️ Arccos Golf Performance Report",
            "=" * 40,
            f"Golfer: {summary['golfer']}",
            f"Last Updated: {summary['last_updated']}",
            f"Total Shots Tracked: {summary['total_shots']:,}",
            f"Total Rounds: {summary['total_rounds']}",
            f"Longest Drive: {summary['longest_drive']} yards",
            "",
            "📊 STROKES GAINED ANALYSIS",
            "-" * 30,
            f"Overall: {sg_analysis['overall']:+.1f}",
        ]
        
        for category, value in sg_analysis['by_category'].items():
            report_lines.append(f"{category.replace('_', ' ').title()}: {value:+.1f}")
        
        if sg_analysis['strengths']:
            report_lines.extend(["", "💪 Strengths:"] + [f"  • {s}" for s in sg_analysis['strengths']])
        
        if sg_analysis['weaknesses']:
            report_lines.extend(["", "⚠️ Areas for Improvement:"] + [f"  • {w}" for w in sg_analysis['weaknesses']])
        
        if sg_analysis['improvement_priority']:
            report_lines.extend(["", "🎯 Priority Areas:"] + [f"  {i+1}. {area}" for i, area in enumerate(sg_analysis['improvement_priority'])])
        
        # Club distances
        report_lines.extend([
            "",
            "🏌️ CLUB DISTANCES",
            "-" * 20
        ])
        
        for club in clubs[:10]:  # Top 10 clubs by distance
            if club.get('club') != 'Putter':
                name = club.get('club', 'Unknown')
                avg_dist = club.get('avg_distance', 0)
                shots = club.get('total_shots', 0)
                longest = club.get('longest', 0)
                report_lines.append(f"{name}: {avg_dist} yds avg ({shots} shots, longest: {longest})")
        
        # Scoring
        report_lines.extend([
            "",
            "⛳ SCORING ANALYSIS", 
            "-" * 20,
            f"Par 3 Average: {scoring['scoring_averages']['par_3']:.1f}",
            f"Par 4 Average: {scoring['scoring_averages']['par_4']:.1f}",
            f"Par 5 Average: {scoring['scoring_averages']['par_5']:.1f}",
            "",
            "Score Distribution:",
            f"  Birdies+: {scoring['score_distribution']['birdies']}",
            f"  Pars: {scoring['score_distribution']['pars']}",
            f"  Bogeys: {scoring['score_distribution']['bogeys']}",
            f"  Double+: {scoring['score_distribution']['double_plus']}"
        ])
        
        # Putting
        report_lines.extend([
            "",
            "⛳ PUTTING ANALYSIS",
            "-" * 20,
            f"Putts per Round: {putting['putts_per_round']:.1f}",
            f"GIR Putts: {putting['putts_per_gir']:.1f}",
            f"One-Putts: {putting['distribution']['one_putts']}",
            f"Three-Putts+: {putting['distribution']['three_plus_putts']}"
        ])
        
        # Recent rounds
        if rounds:
            report_lines.extend([
                "",
                "📈 RECENT ROUNDS",
                "-" * 20
            ])
            for round_data in rounds:
                date = round_data.get('date', 'Unknown')
                course = round_data.get('course', 'Unknown')
                score = round_data.get('score', 0)
                over_par = round_data.get('over_par', 0)
                report_lines.append(f"{date}: {score} (+{over_par}) at {course}")
        
        return "\n".join(report_lines)


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Analyze Arccos Golf performance data')
    parser.add_argument('data_file', type=Path, help='Path to Arccos JSON data file')
    parser.add_argument('--format', choices=['text', 'json'], default='text', 
                       help='Output format (default: text)')
    parser.add_argument('--clubs', type=str, help='Filter clubs by type (iron, wedge, wood, etc.)')
    parser.add_argument('--summary', action='store_true', help='Show summary statistics only')
    parser.add_argument('--strokes-gained', action='store_true', help='Show strokes gained analysis only')
    parser.add_argument('--recent-rounds', type=int, default=5, help='Number of recent rounds to show')
    
    args = parser.parse_args()
    
    try:
        analyzer = ArccosAnalyzer(args.data_file)
        
        if args.summary:
            if args.format == 'json':
                print(json.dumps(analyzer.get_summary_stats(), indent=2))
            else:
                summary = analyzer.get_summary_stats()
                print(f"Golfer: {summary['golfer']}")
                print(f"Shots: {summary['total_shots']:,} | Rounds: {summary['total_rounds']}")
                print(f"Overall SG: {summary['overall_strokes_gained']:+.1f}")
        
        elif args.strokes_gained:
            sg_analysis = analyzer.get_strokes_gained_analysis()
            if args.format == 'json':
                print(json.dumps(sg_analysis, indent=2))
            else:
                print(f"Overall: {sg_analysis['overall']:+.1f}")
                for cat, val in sg_analysis['by_category'].items():
                    print(f"{cat.replace('_', ' ').title()}: {val:+.1f}")
        
        elif args.clubs:
            clubs = analyzer.get_club_distances(args.clubs)
            if args.format == 'json':
                print(json.dumps(clubs, indent=2))
            else:
                for club in clubs:
                    name = club.get('club', 'Unknown')
                    avg = club.get('avg_distance', 0)
                    shots = club.get('total_shots', 0)
                    print(f"{name}: {avg} yds ({shots} shots)")
        
        else:
            # Full report
            report = analyzer.generate_report(args.format)
            if args.format == 'json':
                print(json.dumps(report, indent=2))
            else:
                print(report)
                
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()