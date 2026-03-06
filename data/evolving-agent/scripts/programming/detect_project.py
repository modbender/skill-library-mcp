#!/usr/bin/env python3
"""
Project Detector

Detect project type and tech stack from project files.
Supports: package.json, go.mod, pom.xml, requirements.txt, Cargo.toml, etc.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Optional, Dict, List, Any, Union
import xml.etree.ElementTree as ET


# Tech stack detection rules
DETECTION_RULES = {
    # JavaScript/TypeScript ecosystem
    'package.json': {
        'parser': 'json',
        'detect': [
            {'field': 'dependencies.react', 'tech': 'react'},
            {'field': 'dependencies.vue', 'tech': 'vue'},
            {'field': 'dependencies.angular', 'tech': 'angular'},
            {'field': 'dependencies.next', 'tech': 'nextjs'},
            {'field': 'dependencies.nuxt', 'tech': 'nuxt'},
            {'field': 'dependencies.express', 'tech': 'express'},
            {'field': 'dependencies.fastify', 'tech': 'fastify'},
            {'field': 'dependencies.nestjs', 'tech': 'nestjs'},
            {'field': 'devDependencies.typescript', 'tech': 'typescript'},
            {'field': 'devDependencies.vitest', 'tech': 'vitest'},
            {'field': 'devDependencies.jest', 'tech': 'jest'},
            {'field': 'devDependencies.vite', 'tech': 'vite'},
            {'field': 'devDependencies.webpack', 'tech': 'webpack'},
        ],
        'base_tech': 'javascript'
    },
    
    # Go ecosystem
    'go.mod': {
        'parser': 'gomod',
        'detect': [
            {'pattern': r'github\.com/gin-gonic/gin', 'tech': 'gin'},
            {'pattern': r'github\.com/gofiber/fiber', 'tech': 'fiber'},
            {'pattern': r'github\.com/labstack/echo', 'tech': 'echo'},
            {'pattern': r'github\.com/gorilla/mux', 'tech': 'gorilla'},
            {'pattern': r'gorm\.io/gorm', 'tech': 'gorm'},
            {'pattern': r'github\.com/go-redis/redis', 'tech': 'redis'},
            {'pattern': r'github\.com/stretchr/testify', 'tech': 'testify'},
            {'pattern': r'google\.golang\.org/grpc', 'tech': 'grpc'},
            {'pattern': r'github\.com/spf13/cobra', 'tech': 'cobra'},
            {'pattern': r'github\.com/spf13/viper', 'tech': 'viper'},
        ],
        'base_tech': 'go'
    },
    
    # Java/Maven ecosystem
    'pom.xml': {
        'parser': 'pom',
        'detect': [
            {'groupId': 'org.springframework.boot', 'tech': 'spring-boot'},
            {'groupId': 'org.springframework', 'tech': 'spring'},
            {'groupId': 'io.quarkus', 'tech': 'quarkus'},
            {'groupId': 'io.micronaut', 'tech': 'micronaut'},
            {'groupId': 'org.mybatis', 'tech': 'mybatis'},
            {'groupId': 'org.hibernate', 'tech': 'hibernate'},
            {'groupId': 'junit', 'tech': 'junit'},
            {'groupId': 'org.junit.jupiter', 'tech': 'junit5'},
            {'groupId': 'org.mockito', 'tech': 'mockito'},
            {'groupId': 'io.grpc', 'tech': 'grpc-java'},
            {'groupId': 'org.apache.kafka', 'tech': 'kafka'},
            {'groupId': 'redis.clients', 'tech': 'jedis'},
        ],
        'base_tech': 'java'
    },
    
    # Python ecosystem
    'requirements.txt': {
        'parser': 'requirements',
        'detect': [
            {'pattern': r'^django[=<>]?', 'tech': 'django'},
            {'pattern': r'^flask[=<>]?', 'tech': 'flask'},
            {'pattern': r'^fastapi[=<>]?', 'tech': 'fastapi'},
            {'pattern': r'^pytest[=<>]?', 'tech': 'pytest'},
            {'pattern': r'^sqlalchemy[=<>]?', 'tech': 'sqlalchemy'},
            {'pattern': r'^celery[=<>]?', 'tech': 'celery'},
            {'pattern': r'^redis[=<>]?', 'tech': 'redis-py'},
            {'pattern': r'^pandas[=<>]?', 'tech': 'pandas'},
            {'pattern': r'^numpy[=<>]?', 'tech': 'numpy'},
            {'pattern': r'^tensorflow[=<>]?', 'tech': 'tensorflow'},
            {'pattern': r'^torch[=<>]?', 'tech': 'pytorch'},
        ],
        'base_tech': 'python'
    },
    
    # Python pyproject.toml
    'pyproject.toml': {
        'parser': 'toml_simple',
        'detect': [
            {'pattern': r'django', 'tech': 'django'},
            {'pattern': r'flask', 'tech': 'flask'},
            {'pattern': r'fastapi', 'tech': 'fastapi'},
            {'pattern': r'pytest', 'tech': 'pytest'},
        ],
        'base_tech': 'python'
    },
    
    # Rust ecosystem
    'Cargo.toml': {
        'parser': 'toml_simple',
        'detect': [
            {'pattern': r'actix-web', 'tech': 'actix'},
            {'pattern': r'axum', 'tech': 'axum'},
            {'pattern': r'tokio', 'tech': 'tokio'},
            {'pattern': r'serde', 'tech': 'serde'},
            {'pattern': r'diesel', 'tech': 'diesel'},
        ],
        'base_tech': 'rust'
    },
    
    # Gradle (Java/Kotlin)
    'build.gradle': {
        'parser': 'gradle',
        'detect': [
            {'pattern': r'org\.springframework\.boot', 'tech': 'spring-boot'},
            {'pattern': r'org\.jetbrains\.kotlin', 'tech': 'kotlin'},
            {'pattern': r'io\.ktor', 'tech': 'ktor'},
        ],
        'base_tech': 'java'
    },
    'build.gradle.kts': {
        'parser': 'gradle',
        'detect': [
            {'pattern': r'org\.springframework\.boot', 'tech': 'spring-boot'},
            {'pattern': r'org\.jetbrains\.kotlin', 'tech': 'kotlin'},
            {'pattern': r'io\.ktor', 'tech': 'ktor'},
        ],
        'base_tech': 'kotlin'
    },
}


def get_nested_field(data: Dict[str, Any], field_path: str) -> Any:
    """Get nested field from dict using dot notation."""
    keys = field_path.split('.')
    current: Any = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current


def parse_json_file(file_path: Path) -> dict:
    """Parse JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def parse_gomod_file(file_path: Path) -> str:
    """Parse go.mod file and return content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""


def parse_pom_file(file_path: Path) -> list:
    """Parse pom.xml and return list of groupIds."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Handle Maven namespace
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
        
        group_ids = []
        
        # Try with namespace
        for dep in root.findall('.//m:dependency', ns):
            group_id = dep.find('m:groupId', ns)
            if group_id is not None and group_id.text:
                group_ids.append(group_id.text)
        
        # Try without namespace (some pom.xml don't have namespace)
        if not group_ids:
            for dep in root.findall('.//dependency'):
                group_id = dep.find('groupId')
                if group_id is not None and group_id.text:
                    group_ids.append(group_id.text)
        
        # Also check parent
        parent = root.find('m:parent/m:groupId', ns) or root.find('parent/groupId')
        if parent is not None and parent.text:
            group_ids.append(parent.text)
        
        return group_ids
    except Exception:
        return []


def parse_requirements_file(file_path: Path) -> str:
    """Parse requirements.txt and return content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().lower()
    except Exception:
        return ""


def parse_toml_simple(file_path: Path) -> str:
    """Simple TOML parsing - just return content for regex matching."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().lower()
    except Exception:
        return ""


def parse_gradle_file(file_path: Path) -> str:
    """Parse Gradle file and return content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""


def detect_tech_from_file(file_path: Path, rules: dict) -> list:
    """Detect tech stack from a single file."""
    detected = []
    parser = rules.get('parser')
    
    # Add base tech
    if rules.get('base_tech'):
        detected.append(rules['base_tech'])
    
    if parser == 'json':
        data = parse_json_file(file_path)
        for rule in rules.get('detect', []):
            field = rule.get('field')
            if field and get_nested_field(data, field) is not None:
                detected.append(rule['tech'])
    
    elif parser == 'gomod':
        content = parse_gomod_file(file_path)
        for rule in rules.get('detect', []):
            pattern = rule.get('pattern')
            if pattern and re.search(pattern, content):
                detected.append(rule['tech'])
    
    elif parser == 'pom':
        group_ids = parse_pom_file(file_path)
        for rule in rules.get('detect', []):
            group_id = rule.get('groupId')
            if group_id:
                for gid in group_ids:
                    if gid.startswith(group_id):
                        detected.append(rule['tech'])
                        break
    
    elif parser == 'requirements':
        content = parse_requirements_file(file_path)
        for rule in rules.get('detect', []):
            pattern = rule.get('pattern')
            if pattern and re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                detected.append(rule['tech'])
    
    elif parser == 'toml_simple':
        content = parse_toml_simple(file_path)
        for rule in rules.get('detect', []):
            pattern = rule.get('pattern')
            if pattern and pattern.lower() in content:
                detected.append(rule['tech'])
    
    elif parser == 'gradle':
        content = parse_gradle_file(file_path)
        for rule in rules.get('detect', []):
            pattern = rule.get('pattern')
            if pattern and re.search(pattern, content):
                detected.append(rule['tech'])
    
    return list(set(detected))


def detect_project(project_dir: str) -> dict:
    """
    Detect project type and tech stack from project directory.
    
    Returns:
        dict with keys:
        - base_tech: Primary language/platform (javascript, python, go, java, etc.)
        - frameworks: List of detected frameworks
        - tools: List of detected tools/libraries
        - files_found: List of config files found
    """
    project_path = Path(project_dir)
    
    if not project_path.exists():
        return {'error': f'Directory not found: {project_dir}'}
    
    result = {
        'base_tech': [],
        'frameworks': [],
        'tools': [],
        'files_found': []
    }
    
    for config_file, rules in DETECTION_RULES.items():
        file_path = project_path / config_file
        if file_path.exists():
            result['files_found'].append(config_file)
            detected = detect_tech_from_file(file_path, rules)
            
            for tech in detected:
                if tech in ['javascript', 'python', 'go', 'java', 'kotlin', 'rust']:
                    if tech not in result['base_tech']:
                        result['base_tech'].append(tech)
                elif tech in ['react', 'vue', 'angular', 'nextjs', 'nuxt', 'django', 'flask', 
                             'fastapi', 'spring-boot', 'spring', 'quarkus', 'gin', 'fiber', 
                             'echo', 'actix', 'axum', 'express', 'fastify', 'nestjs', 'ktor']:
                    if tech not in result['frameworks']:
                        result['frameworks'].append(tech)
                else:
                    if tech not in result['tools']:
                        result['tools'].append(tech)
    
    return result


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Detect project type and tech stack',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python detect_project.py /path/to/project
  python detect_project.py . --format json
  python detect_project.py . --format markdown
        """
    )
    
    parser.add_argument(
        'project_dir',
        nargs='?',
        default='.',
        help='Project directory path (default: current directory)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'markdown', 'simple'],
        default='json',
        help='Output format'
    )
    
    args = parser.parse_args()
    result = detect_project(args.project_dir)
    
    if 'error' in result:
        print(result['error'], file=sys.stderr)
        sys.exit(1)
    
    if args.format == 'json':
        print(json.dumps(result, indent=2))
    elif args.format == 'markdown':
        print(f"## Project Detection Result\n")
        print(f"**Base Tech**: {', '.join(result['base_tech']) or 'Unknown'}")
        print(f"**Frameworks**: {', '.join(result['frameworks']) or 'None detected'}")
        print(f"**Tools**: {', '.join(result['tools']) or 'None detected'}")
        print(f"**Config Files**: {', '.join(result['files_found']) or 'None found'}")
    elif args.format == 'simple':
        all_tech = result['base_tech'] + result['frameworks'] + result['tools']
        print(','.join(all_tech) if all_tech else 'unknown')


if __name__ == '__main__':
    main()
