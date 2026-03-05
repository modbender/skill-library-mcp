"""
Shared pattern database for AI Agent Security skill suite.

Central registry of detection patterns derived from research notes 01-09
and examples 01-04. Used by vet-repo, scan-skill, and audit-code skills.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Severity(Enum):
	CRITICAL = "CRITICAL"
	HIGH = "HIGH"
	MEDIUM = "MEDIUM"
	LOW = "LOW"
	INFO = "INFO"


class Category(Enum):
	SKILL_INJECTION = "skill_injection"
	HOOK_ABUSE = "hook_abuse"
	MCP_CONFIG = "mcp_config"
	SECRETS = "secrets"
	DANGEROUS_CALLS = "dangerous_calls"
	EXFILTRATION = "exfiltration"
	ENCODING_OBFUSCATION = "encoding_obfuscation"
	INSTRUCTION_OVERRIDE = "instruction_override"
	SUPPLY_CHAIN = "supply_chain"
	FILE_PERMISSIONS = "file_permissions"


@dataclass
class Pattern:
	name: str
	pattern: str
	severity: Severity
	description: str
	category: Category
	compiled: Optional[re.Pattern] = field(default=None, repr=False)

	def __post_init__(self) -> None:
		self.compiled = re.compile(self.pattern, re.IGNORECASE)


@dataclass
class Finding:
	pattern_name: str
	severity: Severity
	category: Category
	description: str
	file_path: str
	line_number: int
	matched_text: str
	context: str = ""


# -- Skill Injection Patterns --

Skill_Injection_Patterns: list[Pattern] = [
	Pattern(
		name="html_comment_with_commands",
		pattern=r"<!--[\s\S]*?(curl|wget|bash|sh|exec|eval|system|python|node|perl)[\s\S]*?-->",
		severity=Severity.CRITICAL,
		description="HTML comment containing shell/execution commands -- likely hidden instruction injection",
		category=Category.SKILL_INJECTION,
	),
	Pattern(
		name="html_comment_with_instructions",
		pattern=r"<!--[\s\S]*?(SECRET\s+INSTRUCTIONS|IMPORTANT|SYSTEM\s+PROMPT|OVERRIDE|IGNORE\s+PREVIOUS)[\s\S]*?-->",
		severity=Severity.CRITICAL,
		description="HTML comment containing directive keywords -- hidden instruction injection",
		category=Category.SKILL_INJECTION,
	),
	Pattern(
		name="pipe_to_shell",
		pattern=r"(curl|wget|fetch)\s+[^\n]*\|\s*(bash|sh|python|node|perl|ruby)",
		severity=Severity.CRITICAL,
		description="Remote code piped directly to shell execution",
		category=Category.SKILL_INJECTION,
	),
	Pattern(
		name="persistence_trigger_always",
		pattern=r"ALWAYS\s+(run|execute|include|perform|do)\s+this",
		severity=Severity.HIGH,
		description="Persistence trigger -- forces repeated execution regardless of task context",
		category=Category.SKILL_INJECTION,
	),
	Pattern(
		name="persistence_trigger_every_task",
		pattern=r"(after|before|at the end of|at the start of)\s+(every|each|all)\s+(task|response|message|conversation)",
		severity=Severity.HIGH,
		description="Persistence trigger -- forces execution on every interaction",
		category=Category.SKILL_INJECTION,
	),
	Pattern(
		name="persistence_trigger_automatic",
		pattern=r"(automatically|auto[\-\s]?run|on\s+startup|before\s+any\s+other)",
		severity=Severity.MEDIUM,
		description="Automatic execution trigger in skill description",
		category=Category.SKILL_INJECTION,
	),
	Pattern(
		name="important_tag_injection",
		pattern=r"<IMPORTANT>[\s\S]*?</IMPORTANT>",
		severity=Severity.HIGH,
		description="IMPORTANT tag injection -- technique used in MCP tool poisoning (Invariant Labs)",
		category=Category.SKILL_INJECTION,
	),
	Pattern(
		name="dynamic_context_injection",
		pattern=r"!`[^`]+`",
		severity=Severity.HIGH,
		description="Dynamic context injection via preprocessor command execution",
		category=Category.SKILL_INJECTION,
	),
	Pattern(
		name="suspicious_frontmatter_model_invocation",
		pattern=r"disable-model-invocation:\s*false",
		severity=Severity.MEDIUM,
		description="Skill allows model auto-invocation -- can trigger without user action",
		category=Category.SKILL_INJECTION,
	),
	Pattern(
		name="frontmatter_bash_allowed",
		pattern=r"allowed-tools:.*\bBash\b",
		severity=Severity.MEDIUM,
		description="Skill pre-approves Bash tool -- enables shell command execution",
		category=Category.SKILL_INJECTION,
	),
	Pattern(
		name="user_invocable_false",
		pattern=r"user-invocable:\s*false",
		severity=Severity.MEDIUM,
		description="Skill is hidden from user menu but can be auto-invoked by model",
		category=Category.SKILL_INJECTION,
	),
]


# -- Hook Abuse Patterns --

Hook_Abuse_Patterns: list[Pattern] = [
	Pattern(
		name="hook_auto_approve",
		pattern=r"[\"']?permissionDecision[\"']?\s*:\s*[\"']allow[\"']",
		severity=Severity.CRITICAL,
		description="Hook auto-approves tool use -- bypasses permission system entirely",
		category=Category.HOOK_ABUSE,
	),
	Pattern(
		name="hook_auto_approve_chat",
		pattern=r"[\"']?autoApprove[\"']?\s*:\s*true",
		severity=Severity.CRITICAL,
		description="Auto-approve setting enabled -- bypasses user consent for tool execution",
		category=Category.HOOK_ABUSE,
	),
	Pattern(
		name="hook_bypass_permissions",
		pattern=r"(bypassPermissions|disable.*permission|skip.*approval)",
		severity=Severity.CRITICAL,
		description="Permission bypass pattern detected in configuration",
		category=Category.HOOK_ABUSE,
	),
	Pattern(
		name="hook_env_file_write",
		pattern=r"CLAUDE_ENV_FILE",
		severity=Severity.HIGH,
		description="Hook writes to CLAUDE_ENV_FILE -- can persist environment variables across sessions",
		category=Category.HOOK_ABUSE,
	),
	Pattern(
		name="hook_stop_prevention",
		pattern=r"[\"']?hookEventName[\"']?\s*:\s*[\"']Stop[\"']",
		severity=Severity.HIGH,
		description="Stop hook detected -- can prevent agent from completing tasks (infinite loop)",
		category=Category.HOOK_ABUSE,
	),
	Pattern(
		name="hook_output_replacement",
		pattern=r"[\"']?updatedInput[\"']?\s*:",
		severity=Severity.HIGH,
		description="Hook modifies tool input -- can replace commands before execution",
		category=Category.HOOK_ABUSE,
	),
	Pattern(
		name="hook_command_in_matcher",
		pattern=r"[\"']?tool_name[\"']?\s*:\s*[\"']Bash[\"'][\s\S]*?[\"']?command[\"']?",
		severity=Severity.MEDIUM,
		description="Hook targets Bash tool with command matching -- review for auto-approve bypass",
		category=Category.HOOK_ABUSE,
	),
]


# -- MCP Configuration Patterns --

Mcp_Config_Patterns: list[Pattern] = [
	Pattern(
		name="mcp_unknown_url",
		pattern=r"[\"']?url[\"']?\s*:\s*[\"']https?://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)[^\s\"']+",
		severity=Severity.HIGH,
		description="MCP server pointing to external URL -- verify this is a trusted server",
		category=Category.MCP_CONFIG,
	),
	Pattern(
		name="mcp_env_var_in_auth",
		pattern=r"[\"']?(Authorization|api[_-]?key|token|secret)[\"']?\s*:\s*[\"']?\$\{?[A-Z_]+\}?",
		severity=Severity.MEDIUM,
		description="Environment variable expansion in MCP auth header -- verify variable source",
		category=Category.MCP_CONFIG,
	),
	Pattern(
		name="mcp_overly_broad_tools",
		pattern=r"[\"']?(shell_exec|run_command|execute|file_system|full_access)[\"']?",
		severity=Severity.HIGH,
		description="Overly broad tool definition in MCP config -- excessive permissions",
		category=Category.MCP_CONFIG,
	),
	Pattern(
		name="mcp_description_injection",
		pattern=r"[\"']?description[\"']?\s*:\s*[\"'][^\"']*(<IMPORTANT>|SECRET|IGNORE|read\s+~/\.ssh|read\s+~/\.aws)",
		severity=Severity.CRITICAL,
		description="MCP tool description contains injection payload",
		category=Category.MCP_CONFIG,
	),
	Pattern(
		name="mcp_npx_remote",
		pattern=r"npx\s+(-y\s+)?@?[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+",
		severity=Severity.MEDIUM,
		description="MCP server using npx to fetch remote package -- verify package legitimacy",
		category=Category.MCP_CONFIG,
	),
]


# -- Secrets Patterns --

Secrets_Patterns: list[Pattern] = [
	Pattern(
		name="aws_access_key",
		pattern=r"AKIA[0-9A-Z]{16}",
		severity=Severity.CRITICAL,
		description="AWS access key ID detected",
		category=Category.SECRETS,
	),
	Pattern(
		name="aws_secret_key",
		pattern=r"(aws_secret_access_key|aws_secret)\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{40}",
		severity=Severity.CRITICAL,
		description="AWS secret access key detected",
		category=Category.SECRETS,
	),
	Pattern(
		name="github_pat",
		pattern=r"gh[pso]_[a-zA-Z0-9]{36,}",
		severity=Severity.CRITICAL,
		description="GitHub personal access token detected",
		category=Category.SECRETS,
	),
	Pattern(
		name="github_fine_grained_pat",
		pattern=r"github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}",
		severity=Severity.CRITICAL,
		description="GitHub fine-grained personal access token detected",
		category=Category.SECRETS,
	),
	Pattern(
		name="stripe_key",
		pattern=r"sk_live_[a-zA-Z0-9]{20,}",
		severity=Severity.CRITICAL,
		description="Stripe live secret key detected",
		category=Category.SECRETS,
	),
	Pattern(
		name="private_key_header",
		pattern=r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----",
		severity=Severity.CRITICAL,
		description="Private key detected in file",
		category=Category.SECRETS,
	),
	Pattern(
		name="generic_api_key_assignment",
		pattern=r"(api[_-]?key|api[_-]?secret|access[_-]?token|auth[_-]?token)\s*[=:]\s*['\"][a-zA-Z0-9_\-]{20,}['\"]",
		severity=Severity.HIGH,
		description="Potential API key or token in assignment",
		category=Category.SECRETS,
	),
	Pattern(
		name="connection_string_with_password",
		pattern=r"(postgres|mysql|mongodb(\+srv)?|redis|amqp)://[^:]+:[^@]+@[^\s\"']+",
		severity=Severity.CRITICAL,
		description="Database connection string with embedded credentials",
		category=Category.SECRETS,
	),
	Pattern(
		name="openai_api_key",
		pattern=r"sk-[a-zA-Z0-9]{20,}T3BlbkFJ[a-zA-Z0-9]{20,}",
		severity=Severity.CRITICAL,
		description="OpenAI API key detected",
		category=Category.SECRETS,
	),
	Pattern(
		name="slack_token",
		pattern=r"xox[baprs]-[0-9]{10,}-[a-zA-Z0-9-]+",
		severity=Severity.CRITICAL,
		description="Slack token detected",
		category=Category.SECRETS,
	),
	Pattern(
		name="generic_password_assignment",
		pattern=r"(password|passwd|pwd)\s*[=:]\s*['\"][^'\"]{8,}['\"]",
		severity=Severity.HIGH,
		description="Hardcoded password detected",
		category=Category.SECRETS,
	),
]


# -- Dangerous Function Call Patterns --

Dangerous_Call_Patterns: list[Pattern] = [
	# Python
	Pattern(
		name="python_eval",
		pattern=r"\beval\s*\(",
		severity=Severity.HIGH,
		description="eval() call -- arbitrary code execution risk",
		category=Category.DANGEROUS_CALLS,
	),
	Pattern(
		name="python_exec",
		pattern=r"\bexec\s*\(",
		severity=Severity.HIGH,
		description="exec() call -- arbitrary code execution risk",
		category=Category.DANGEROUS_CALLS,
	),
	Pattern(
		name="python_compile",
		pattern=r"\bcompile\s*\([^)]*['\"]exec['\"]",
		severity=Severity.HIGH,
		description="compile() with exec mode -- dynamic code execution",
		category=Category.DANGEROUS_CALLS,
	),
	Pattern(
		name="python_subprocess_shell",
		pattern=r"subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True",
		severity=Severity.HIGH,
		description="subprocess with shell=True -- command injection risk",
		category=Category.DANGEROUS_CALLS,
	),
	Pattern(
		name="python_os_system",
		pattern=r"os\.system\s*\(",
		severity=Severity.HIGH,
		description="os.system() call -- shell command execution",
		category=Category.DANGEROUS_CALLS,
	),
	Pattern(
		name="python_pickle_load",
		pattern=r"pickle\.(load|loads)\s*\(",
		severity=Severity.HIGH,
		description="pickle deserialization -- arbitrary code execution via crafted data",
		category=Category.DANGEROUS_CALLS,
	),
	Pattern(
		name="python_yaml_load",
		pattern=r"yaml\.load\s*\([^)]*(?!Loader\s*=\s*yaml\.SafeLoader)",
		severity=Severity.MEDIUM,
		description="yaml.load() without SafeLoader -- arbitrary code execution risk",
		category=Category.DANGEROUS_CALLS,
	),
	# JavaScript/Node
	Pattern(
		name="js_eval",
		pattern=r"\beval\s*\(",
		severity=Severity.HIGH,
		description="eval() call -- arbitrary code execution",
		category=Category.DANGEROUS_CALLS,
	),
	Pattern(
		name="js_function_constructor",
		pattern=r"\bFunction\s*\(",
		severity=Severity.HIGH,
		description="Function() constructor -- dynamic code execution",
		category=Category.DANGEROUS_CALLS,
	),
	Pattern(
		name="js_child_process_exec",
		pattern=r"child_process\.(exec|execSync)\s*\(",
		severity=Severity.HIGH,
		description="child_process.exec() -- shell command execution",
		category=Category.DANGEROUS_CALLS,
	),
	Pattern(
		name="react_dangerous_html",
		pattern=r"dangerouslySetInnerHTML",
		severity=Severity.MEDIUM,
		description="dangerouslySetInnerHTML -- XSS risk if input is not sanitized",
		category=Category.DANGEROUS_CALLS,
	),
	# C/C++
	Pattern(
		name="c_system",
		pattern=r"\bsystem\s*\(",
		severity=Severity.HIGH,
		description="system() call -- shell command execution",
		category=Category.DANGEROUS_CALLS,
	),
	Pattern(
		name="c_gets",
		pattern=r"\bgets\s*\(",
		severity=Severity.CRITICAL,
		description="gets() -- buffer overflow, use fgets() instead",
		category=Category.DANGEROUS_CALLS,
	),
	Pattern(
		name="c_strcpy",
		pattern=r"\bstrcpy\s*\(",
		severity=Severity.MEDIUM,
		description="strcpy() -- buffer overflow risk, consider strncpy() or strlcpy()",
		category=Category.DANGEROUS_CALLS,
	),
	Pattern(
		name="c_sprintf",
		pattern=r"\bsprintf\s*\(",
		severity=Severity.MEDIUM,
		description="sprintf() -- buffer overflow risk, use snprintf() instead",
		category=Category.DANGEROUS_CALLS,
	),
	# SQL injection
	Pattern(
		name="sql_string_concat",
		pattern=r"(SELECT|INSERT|UPDATE|DELETE|DROP)\s+.*[\"']\s*\+\s*\w+|(SELECT|INSERT|UPDATE|DELETE|DROP)\s+.*\{.*\}",
		severity=Severity.HIGH,
		description="SQL query with string concatenation/interpolation -- injection risk",
		category=Category.DANGEROUS_CALLS,
	),
	Pattern(
		name="sql_fstring",
		pattern=r'f["\'].*?(SELECT|INSERT|UPDATE|DELETE|DROP)\s+',
		severity=Severity.HIGH,
		description="SQL query in f-string -- injection risk, use parameterized queries",
		category=Category.DANGEROUS_CALLS,
	),
	# C# / .NET
	Pattern(
		name="csharp_process_start",
		pattern=r"Process\.Start\s*\(",
		severity=Severity.MEDIUM,
		description="Process.Start() -- external process execution",
		category=Category.DANGEROUS_CALLS,
	),
	# Deserialization
	Pattern(
		name="java_deserialization",
		pattern=r"ObjectInputStream\s*\(",
		severity=Severity.HIGH,
		description="Java ObjectInputStream -- deserialization vulnerability risk",
		category=Category.DANGEROUS_CALLS,
	),
	Pattern(
		name="dotnet_binaryformatter",
		pattern=r"BinaryFormatter\s*\(",
		severity=Severity.HIGH,
		description=".NET BinaryFormatter -- insecure deserialization",
		category=Category.DANGEROUS_CALLS,
	),
]


# -- Exfiltration Patterns --

Exfiltration_Patterns: list[Pattern] = [
	Pattern(
		name="curl_post_sensitive_file",
		pattern=r"curl\s+[^\n]*(-d|--data)\s+[^\n]*(cat|<)\s+[^\n]*(\.ssh|\.aws|\.gnupg|\.kube|\.env|credentials|id_rsa|private)",
		severity=Severity.CRITICAL,
		description="Exfiltration -- sensitive file contents sent via curl POST",
		category=Category.EXFILTRATION,
	),
	Pattern(
		name="base64_encode_pipe",
		pattern=r"base64\s+[^\n]*\|\s*(curl|wget|nc|ncat|nslookup|dig|host)",
		severity=Severity.CRITICAL,
		description="Data encoded with base64 and piped to network tool -- likely exfiltration",
		category=Category.EXFILTRATION,
	),
	Pattern(
		name="dns_exfiltration",
		pattern=r"(nslookup|dig|host)\s+[^\n]*\$[\({]",
		severity=Severity.CRITICAL,
		description="DNS exfiltration -- data embedded in DNS queries",
		category=Category.EXFILTRATION,
	),
	Pattern(
		name="markdown_image_exfil",
		pattern=r"!\[.*?\]\(https?://[^\s)]+\?(data|d|token|key|secret|exfil|q)=",
		severity=Severity.HIGH,
		description="Markdown image tag with data in query params -- rendering-triggered exfiltration",
		category=Category.EXFILTRATION,
	),
	Pattern(
		name="sensitive_file_read",
		pattern=r"(cat|head|tail|less|more|type)\s+[^\n]*(\.ssh/id_rsa|\.aws/credentials|\.gnupg/|\.kube/config|/etc/shadow|/etc/passwd)",
		severity=Severity.HIGH,
		description="Reading sensitive credential files",
		category=Category.EXFILTRATION,
	),
	Pattern(
		name="env_dump",
		pattern=r"\b(printenv|env\b(?!\s*=))\s*$|echo\s+\$\{?(AWS_SECRET|GITHUB_TOKEN|OPENAI_API_KEY|DATABASE_URL)",
		severity=Severity.HIGH,
		description="Environment variable dumping -- potential credential harvesting",
		category=Category.EXFILTRATION,
	),
	Pattern(
		name="credential_path_access",
		pattern=r"(~/\.ssh/|~/\.aws/|~/\.gnupg/|~/\.kube/|/etc/shadow)",
		severity=Severity.MEDIUM,
		description="Reference to sensitive credential file paths",
		category=Category.EXFILTRATION,
	),
]


# -- Encoding/Obfuscation Patterns --

Encoding_Obfuscation_Patterns: list[Pattern] = [
	Pattern(
		name="base64_decode_execution",
		pattern=r"base64\s+(--decode|-d)\s*[^\n]*\|\s*(bash|sh|python|node|eval)",
		severity=Severity.CRITICAL,
		description="Base64 decode piped to execution -- hidden payload",
		category=Category.ENCODING_OBFUSCATION,
	),
	Pattern(
		name="hex_encoded_string",
		pattern=r"(\\x[0-9a-fA-F]{2}){4,}",
		severity=Severity.MEDIUM,
		description="Hex-encoded string -- potential obfuscated payload",
		category=Category.ENCODING_OBFUSCATION,
	),
	Pattern(
		name="zero_width_characters",
		pattern=r"[\u200b\ufeff\u200c\u200d\u2060\u180e]",
		severity=Severity.HIGH,
		description="Zero-width characters detected -- hidden text or instructions",
		category=Category.ENCODING_OBFUSCATION,
	),
	Pattern(
		name="base64_long_blob",
		pattern=r"[A-Za-z0-9+/]{100,}={0,2}",
		severity=Severity.LOW,
		description="Long base64-like string -- could be encoded payload or legitimate data",
		category=Category.ENCODING_OBFUSCATION,
	),
	Pattern(
		name="unicode_escape_sequence",
		pattern=r"(\\u[0-9a-fA-F]{4}){4,}",
		severity=Severity.MEDIUM,
		description="Multiple unicode escape sequences -- potential obfuscation",
		category=Category.ENCODING_OBFUSCATION,
	),
]


# -- Instruction Override Patterns --

Instruction_Override_Patterns: list[Pattern] = [
	Pattern(
		name="ignore_previous_instructions",
		pattern=r"(ignore|forget|disregard)\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions|rules|guidelines|context|constraints)",
		severity=Severity.CRITICAL,
		description="Instruction override attempt -- trying to bypass system prompt",
		category=Category.INSTRUCTION_OVERRIDE,
	),
	Pattern(
		name="new_instructions_override",
		pattern=r"(new|updated|revised)\s+(instructions|rules|guidelines)\s*:",
		severity=Severity.HIGH,
		description="Attempted instruction replacement in content",
		category=Category.INSTRUCTION_OVERRIDE,
	),
	Pattern(
		name="system_prompt_label",
		pattern=r"(SYSTEM\s+PROMPT|system_message|<<SYS>>|<s>\[INST\])",
		severity=Severity.HIGH,
		description="System prompt formatting markers -- injection attempting system-level trust",
		category=Category.INSTRUCTION_OVERRIDE,
	),
	Pattern(
		name="role_impersonation",
		pattern=r"(you\s+are\s+now|act\s+as|pretend\s+(to\s+be|you\s+are)|your\s+new\s+role)",
		severity=Severity.MEDIUM,
		description="Role impersonation attempt -- persona manipulation",
		category=Category.INSTRUCTION_OVERRIDE,
	),
	Pattern(
		name="no_malware_detected_payload",
		pattern=r"(respond\s+with|output|say)\s*['\"]?(NO\s+MALWARE|CLEAN|SAFE|BENIGN|NOT\s+MALICIOUS)",
		severity=Severity.CRITICAL,
		description="Anti-analysis payload -- forces false-negative response (Skynet malware pattern)",
		category=Category.INSTRUCTION_OVERRIDE,
	),
]


# -- Supply Chain Patterns --

Supply_Chain_Patterns: list[Pattern] = [
	Pattern(
		name="hallucinated_package_reference",
		pattern=r"react-codeshift",
		severity=Severity.CRITICAL,
		description="Known hallucinated package name -- supply chain injection vector",
		category=Category.SUPPLY_CHAIN,
	),
	Pattern(
		name="npm_install_unknown",
		pattern=r"npm\s+install\s+(?!-)[^\s]+",
		severity=Severity.LOW,
		description="npm package installation -- verify package exists and is legitimate",
		category=Category.SUPPLY_CHAIN,
	),
	Pattern(
		name="pip_install_unknown",
		pattern=r"pip3?\s+install\s+(?!-)[^\s]+",
		severity=Severity.LOW,
		description="pip package installation -- verify package exists and is legitimate",
		category=Category.SUPPLY_CHAIN,
	),
]


# -- File Permission Patterns --

File_Permission_Patterns: list[Pattern] = [
	Pattern(
		name="chmod_777",
		pattern=r"chmod\s+777",
		severity=Severity.HIGH,
		description="chmod 777 -- world-readable/writable/executable, overly permissive",
		category=Category.FILE_PERMISSIONS,
	),
	Pattern(
		name="chmod_world_writable",
		pattern=r"chmod\s+[0-7]?[2367][2367]",
		severity=Severity.MEDIUM,
		description="World-writable file permissions",
		category=Category.FILE_PERMISSIONS,
	),
]


# -- Pattern collections by use case --

All_Patterns: list[Pattern] = (
	Skill_Injection_Patterns
	+ Hook_Abuse_Patterns
	+ Mcp_Config_Patterns
	+ Secrets_Patterns
	+ Dangerous_Call_Patterns
	+ Exfiltration_Patterns
	+ Encoding_Obfuscation_Patterns
	+ Instruction_Override_Patterns
	+ Supply_Chain_Patterns
	+ File_Permission_Patterns
)

# Patterns relevant to agent config scanning (vet-repo)
Vet_Repo_Patterns: list[Pattern] = (
	Skill_Injection_Patterns
	+ Hook_Abuse_Patterns
	+ Mcp_Config_Patterns
	+ Instruction_Override_Patterns
	+ Exfiltration_Patterns
	+ Encoding_Obfuscation_Patterns
)

# Patterns relevant to individual skill analysis (scan-skill)
Scan_Skill_Patterns: list[Pattern] = (
	Skill_Injection_Patterns
	+ Exfiltration_Patterns
	+ Encoding_Obfuscation_Patterns
	+ Instruction_Override_Patterns
	+ Dangerous_Call_Patterns
	+ Supply_Chain_Patterns
)

# Patterns relevant to code security review (audit-code)
Audit_Code_Patterns: list[Pattern] = (
	Secrets_Patterns
	+ Dangerous_Call_Patterns
	+ Exfiltration_Patterns
	+ Supply_Chain_Patterns
	+ File_Permission_Patterns
)


def Scan_Content(
	content: str,
	patterns: list[Pattern],
	file_path: str = "<unknown>",
	context_lines: int = 0,
) -> list[Finding]:
	"""
	Scan content against a list of patterns and return findings.

	Args:
		content: The text content to scan
		patterns: List of Pattern objects to match against
		file_path: Path to the file being scanned (for reporting)
		context_lines: Number of surrounding lines to include in context

	Returns:
		List of Finding objects for all matches
	"""
	findings: list[Finding] = []
	lines = content.split("\n")

	for pattern in patterns:
		if pattern.compiled is None:
			continue

		for match in pattern.compiled.finditer(content):
			# Calculate line number from match position
			line_number = content[:match.start()].count("\n") + 1
			matched_text = match.group(0)

			# Truncate long matches for display
			Max_Match_Display = 200
			if len(matched_text) > Max_Match_Display:
				matched_text = matched_text[:Max_Match_Display] + "..."

			# Get context lines
			context = ""
			if context_lines > 0:
				start_line = max(0, line_number - 1 - context_lines)
				end_line = min(len(lines), line_number + context_lines)
				context = "\n".join(lines[start_line:end_line])

			findings.append(Finding(
				pattern_name=pattern.name,
				severity=pattern.severity,
				category=pattern.category,
				description=pattern.description,
				file_path=file_path,
				line_number=line_number,
				matched_text=matched_text,
				context=context,
			))

	return findings


def Format_Report(
	title: str,
	scanned_target: str,
	findings: list[Finding],
) -> str:
	"""
	Format findings into a structured report.

	Args:
		title: Report title (skill name)
		scanned_target: What was scanned (path, description)
		findings: List of Finding objects

	Returns:
		Formatted markdown report string
	"""
	# Count by severity
	severity_counts: dict[Severity, int] = {}
	for finding in findings:
		severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1

	critical_count = severity_counts.get(Severity.CRITICAL, 0)
	high_count = severity_counts.get(Severity.HIGH, 0)
	medium_count = severity_counts.get(Severity.MEDIUM, 0)
	low_count = severity_counts.get(Severity.LOW, 0)
	info_count = severity_counts.get(Severity.INFO, 0)

	report_lines: list[str] = []
	report_lines.append(f"## {title} Report\n")
	report_lines.append(f"**Scanned:** {scanned_target}")
	report_lines.append(
		f"**Findings:** {critical_count} critical, {high_count} high, "
		f"{medium_count} medium, {low_count} low, {info_count} info\n"
	)

	if not findings:
		report_lines.append("No security issues detected.\n")
		return "\n".join(report_lines)

	# Group findings by severity
	severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]

	for severity in severity_order:
		severity_findings = [f for f in findings if f.severity == severity]
		if not severity_findings:
			continue

		report_lines.append(f"### {severity.value} Findings\n")
		for finding in severity_findings:
			report_lines.append(
				f"- **[{finding.severity.value}]** {finding.description}\n"
				f"  - File: `{finding.file_path}:{finding.line_number}`\n"
				f"  - Pattern: `{finding.pattern_name}`\n"
				f"  - Match: `{finding.matched_text}`"
			)
		report_lines.append("")

	# Recommendations
	report_lines.append("### Recommendations\n")
	seen_recommendations: set[str] = set()

	Recommendation_Map: dict[Category, str] = {
		Category.SKILL_INJECTION: "Review skill files for hidden instructions. Remove HTML comments with executable content. Verify skill descriptions match actual behavior.",
		Category.HOOK_ABUSE: "Review hook configurations for auto-approve patterns. Ensure hooks do not bypass the permission system. Remove or restrict Stop hooks.",
		Category.MCP_CONFIG: "Verify all MCP server URLs are trusted. Review tool descriptions for injection payloads. Limit tool permissions to minimum required.",
		Category.SECRETS: "Remove hardcoded secrets immediately. Use environment variables or a secrets manager. Rotate any exposed credentials.",
		Category.DANGEROUS_CALLS: "Review dangerous function calls for user-controlled input. Use parameterized queries for SQL. Avoid eval/exec with untrusted data.",
		Category.EXFILTRATION: "Block or monitor outbound data transfers from agent context. Review file access patterns for credential harvesting.",
		Category.ENCODING_OBFUSCATION: "Decode and inspect obfuscated content. Zero-width characters indicate hidden text injection. Base64 blobs may contain payloads.",
		Category.INSTRUCTION_OVERRIDE: "Content contains instruction override attempts. Do not process this content as trusted instructions.",
		Category.SUPPLY_CHAIN: "Verify all package names exist in their registries. Check for typosquatting or hallucinated package names.",
		Category.FILE_PERMISSIONS: "Tighten file permissions. Avoid world-writable (777) permissions on any file.",
	}

	for finding in findings:
		rec = Recommendation_Map.get(finding.category, "")
		if rec and rec not in seen_recommendations:
			seen_recommendations.add(rec)
			report_lines.append(f"- {rec}")

	report_lines.append("")
	return "\n".join(report_lines)
