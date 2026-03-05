"""
LLM Processor - Text analysis using OpenAI/Anthropic APIs
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

from models import SummaryStyle


logger = logging.getLogger(__name__)


class LLMProcessor:
    """Process text with LLM using configured prompts."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "./config.json"
        self._config = None

    @property
    def config(self) -> dict:
        """Load config lazily."""
        if self._config is None:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
            else:
                self._config = {}
        return self._config

    @property
    def prompts_dir(self) -> Path:
        """Get prompts directory."""
        return Path(__file__).parent / "prompts"

    def _load_prompt(self, prompt_type: str) -> Optional[str]:
        """Load prompt template."""
        prompt_file = self.prompts_dir / f"{prompt_type}.md"

        if not prompt_file.exists():
            return None

        with open(prompt_file, "r", encoding="utf-8") as f:
            content = f.read().strip()

        # Add placeholder if missing
        if "{transcript_text}" not in content:
            content += "\n\n{transcript_text}"

        return content

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def process(self, text: str, prompt_type: str) -> Optional[str]:
        """
        Process text with LLM.

        Args:
            text: Input text
            prompt_type: evaluation/summary/format

        Returns:
            Processed text from LLM
        """
        prompt_template = self._load_prompt(prompt_type)
        if not prompt_template:
            print(f"⚠️  Prompt not found: {prompt_type}")
            return None

        prompt = prompt_template.format(transcript_text=text)

        # Get LLM config
        llm_config = self.config.get("llm", {})
        provider = llm_config.get("provider", "openai")

        if provider == "openai":
            return self._call_openai(prompt, llm_config)
        elif provider == "anthropic":
            return self._call_anthropic(prompt, llm_config)
        else:
            print(f"⚠️  Unsupported provider: {provider}")
            return None

    def _call_openai(self, prompt: str, config: dict) -> Optional[str]:
        """Call OpenAI API."""
        try:
            from openai import OpenAI
        except ImportError:
            print("❌ OpenAI package not installed")
            return None

        api_key = (
            config.get("api_key")
            or os.getenv("VIDEO_ANALYZER_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        base_url = config.get("base_url", "https://api.openai.com/v1")
        model = config.get("model", "gpt-4o-mini")

        if not api_key:
            raise ValueError("API key not configured in config.json")

        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.get("temperature", 0.3),
                max_tokens=config.get("max_tokens", 4000),
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API call failed: {type(e).__name__}: {e}")
            logger.error(f"API endpoint: {base_url}, Model: {model}")
            raise

    def process_summary(
        self,
        text: str,
        style: SummaryStyle,
        video_title: str = "",
        duration_minutes: float = 0.0,
        **kwargs,
    ) -> Optional[str]:
        """
        Process text with style-specific summary generation.

        Args:
            text: Transcript text to summarize
            style: Summary style (from SummaryStyle enum)
            video_title: Video title for context
            duration_minutes: Video duration in minutes
            **kwargs: Additional context variables

        Returns:
            Generated summary text, or None if processing fails
        """
        # Map style enum to prompt file name
        style_map = {
            SummaryStyle.BRIEF_POINTS: "concise",
            SummaryStyle.DEEP_LONGFORM: "deep",
            SummaryStyle.SOCIAL_MEDIA: "social",
            SummaryStyle.STUDY_NOTES: "study",
        }

        style_name = style_map.get(style)
        if not style_name:
            logger.error(f"Unknown summary style: {style}")
            return None

        # Load style-specific prompt
        prompt_file = self.prompts_dir / "summary_styles" / f"{style_name}.md"
        if not prompt_file.exists():
            logger.error(f"Prompt file not found: {prompt_file}")
            return None

        with open(prompt_file, "r", encoding="utf-8") as f:
            prompt_template = f.read().strip()

        # Format prompt with context
        prompt = prompt_template.format(
            video_title=video_title,
            duration_minutes=duration_minutes,
            transcript=text,
            **kwargs,
        )

        # Get LLM config
        llm_config = self.config.get("llm", {})
        provider = llm_config.get("provider", "openai")

        # Call LLM with retry
        try:
            if provider == "openai":
                return self._call_openai(prompt, llm_config)
            elif provider == "anthropic":
                return self._call_anthropic(prompt, llm_config)
            else:
                logger.error(f"Unsupported provider: {provider}")
                return None
        except Exception as e:
            logger.error(f"Failed to process summary: {e}")
            return None

    def select_key_nodes(
        self,
        timestamped_transcript: List[Dict[str, Any]],
        screenshot_count: int,
        video_title: str = "",
        duration_minutes: float = 0.0,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Select key nodes from timestamped transcript for screenshot extraction.

        Args:
            timestamped_transcript: List of transcript segments with start/end/text
            screenshot_count: Target number of screenshots to extract
            video_title: Video title for context
            duration_minutes: Video duration in minutes
            **kwargs: Additional context variables

        Returns:
            List of key nodes with structure:
            [{timestamp_seconds: float, title: str, importance_score: float}]
            Returns empty list if processing fails
        """
        # Load key node selection prompt
        prompt_file = self.prompts_dir / "key_node_selection.md"
        if not prompt_file.exists():
            logger.error(f"Prompt file not found: {prompt_file}")
            return []

        with open(prompt_file, "r", encoding="utf-8") as f:
            prompt_template = f.read().strip()

        # Format transcript for prompt
        transcript_text = json.dumps(
            timestamped_transcript, ensure_ascii=False, indent=2
        )

        # Format prompt with context
        try:
            prompt = prompt_template.format(
                video_title=video_title,
                duration_minutes=duration_minutes,
                screenshot_count=screenshot_count,
                transcript=transcript_text,
                **kwargs,
            )
        except KeyError as e:
            logger.error(f"Missing placeholder in prompt template: {e}")
            return []

        # Get LLM config
        llm_config = self.config.get("llm", {})
        provider = llm_config.get("provider", "openai")

        # Call LLM with retry
        try:
            if provider == "openai":
                response_text = self._call_openai(prompt, llm_config)
            elif provider == "anthropic":
                response_text = self._call_anthropic(prompt, llm_config)
            else:
                logger.error(f"Unsupported provider: {provider}")
                return []

            if not response_text:
                logger.error("Empty response from LLM")
                return []

            # Parse JSON response with error handling
            return self._parse_key_nodes_json(response_text, screenshot_count)

        except Exception as e:
            logger.error(f"Failed to select key nodes: {e}")
            return []

    def _parse_key_nodes_json(
        self, response_text: str, expected_count: int
    ) -> List[Dict[str, Any]]:
        """
        Parse key nodes JSON from LLM response with error handling.

        Args:
            response_text: LLM response text
            expected_count: Expected number of key nodes

        Returns:
            List of parsed key nodes, or empty list if parsing fails
        """
        # Try to extract JSON from response (handles markdown code blocks)
        json_text = response_text.strip()

        # Remove markdown code block markers if present
        if json_text.startswith("```json"):
            json_text = json_text[7:]  # Remove ```json
        elif json_text.startswith("```"):
            json_text = json_text[3:]  # Remove ```

        if json_text.endswith("```"):
            json_text = json_text[:-3]  # Remove trailing ```

        json_text = json_text.strip()

        # Try to parse JSON
        try:
            parsed = json.loads(json_text)

            # Validate structure
            if not isinstance(parsed, list):
                logger.warning("Response is not a JSON array, wrapping in array")
                parsed = [parsed]

            # Validate each node
            valid_nodes = []
            for node in parsed:
                if not isinstance(node, dict):
                    logger.warning(f"Skipping non-dict node: {node}")
                    continue

                # Required fields
                if "timestamp_seconds" not in node or "title" not in node:
                    logger.warning(f"Skipping node missing required fields: {node}")
                    continue

                # Add default importance_score if missing
                if "importance_score" not in node:
                    node["importance_score"] = 0.5

                # Ensure timestamp is float
                try:
                    node["timestamp_seconds"] = float(node["timestamp_seconds"])
                except (ValueError, TypeError):
                    logger.warning(f"Invalid timestamp in node: {node}")
                    continue

                # Ensure importance_score is float
                try:
                    node["importance_score"] = float(node["importance_score"])
                except (ValueError, TypeError):
                    node["importance_score"] = 0.5

                valid_nodes.append(node)

            # Check count
            if len(valid_nodes) != expected_count:
                logger.warning(
                    f"Expected {expected_count} nodes, got {len(valid_nodes)}"
                )

            # Sort by timestamp
            valid_nodes.sort(key=lambda x: x["timestamp_seconds"])

            return valid_nodes

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response_text[:500]}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error parsing key nodes: {e}")
            return []

    def _call_anthropic(self, prompt: str, config: dict) -> Optional[str]:
        """Call Anthropic API."""
        try:
            from anthropic import Anthropic
        except ImportError:
            print("❌ Anthropic package not installed")
            return None

        api_key = (
            config.get("api_key")
            or os.getenv("VIDEO_ANALYZER_API_KEY")
            or os.getenv("ANTHROPIC_API_KEY")
        )
        model = config.get("model", "claude-3-5-sonnet-20241022")

        if not api_key:
            raise ValueError("API key not configured in config.json")

        client = Anthropic(api_key=api_key)

        try:
            response = client.messages.create(
                model=model,
                max_tokens=config.get("max_tokens", 4000),
                temperature=config.get("temperature", 0.3),
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API call failed: {type(e).__name__}: {e}")
            logger.error(f"Model: {model}")
            raise
