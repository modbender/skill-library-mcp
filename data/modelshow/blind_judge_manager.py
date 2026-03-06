import json
import re
import random
import string
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class BlindJudgeManager:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.mapping = {}        # placeholder → model_name  (used for deanonymization)
        self.reverse_mapping = {}  # model_name → placeholder  (used for anonymization)

    def generate_mapping(self, model_names: list, label_style: str = "alphabetic", shuffle: bool = True) -> tuple[dict, dict]:
        """
        Shuffles models and assigns placeholders.
        Returns (anonymization_map, reverse_map).
          anonymization_map: placeholder → model_name  (e.g. {"Response A": "deepseek"})
          reverse_map:       model_name → placeholder  (e.g. {"deepseek": "Response A"})
        """
        if shuffle:
            shuffled_models = random.sample(model_names, len(model_names))
        else:
            shuffled_models = list(model_names)

        self.mapping = {}
        self.reverse_mapping = {}

        for i, model in enumerate(shuffled_models):
            if label_style == "alphabetic":
                placeholder = f"Response {string.ascii_uppercase[i]}"
            elif label_style == "numeric":
                placeholder = f"Candidate {i + 1}"
            elif label_style == "neutral":
                placeholder = f"Output {string.ascii_uppercase[i % 26]}"
            else:
                placeholder = f"Response {string.ascii_uppercase[i]}"

            self.mapping[placeholder] = model
            self.reverse_mapping[model] = placeholder

        logging.info(f"Generated blind judging mapping: {self.mapping}")
        return self.mapping, self.reverse_mapping

    def get_blind_responses_for_judge(self, responses_by_model: dict) -> dict:
        """
        Takes model_name → response_text and returns placeholder → response_text.
        """
        blind_responses = {}
        for model_name, response_text in responses_by_model.items():
            placeholder = self.reverse_mapping.get(model_name)
            if placeholder:
                blind_responses[placeholder] = response_text
            else:
                logging.warning(f"Model '{model_name}' not found in reverse mapping. Skipping.")
        return blind_responses

    def deanonymize_judge_output(self, judge_output: str) -> str:
        """
        Translates the judge's output back to real model names using self.mapping
        (which must map placeholder → model_name, e.g. {"Response A": "deepseek"}).
        """
        deanonymized_text = judge_output

        sorted_placeholders = sorted(self.mapping.keys(), reverse=True)

        for placeholder in sorted_placeholders:
            real_model = self.mapping[placeholder]
            escaped = re.escape(placeholder)
            pattern = re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)
            deanonymized_text = pattern.sub(f"**{real_model}**", deanonymized_text)

        hallucination_patterns = [
            r"(?<!\w)Response [A-Z](?!\w)",
            r"(?<!\w)Candidate \d+(?!\w)",
            r"(?<!\w)Output [A-Z](?!\w)",
        ]
        for pattern_str in hallucination_patterns:
            remaining_candidates = re.findall(pattern_str, deanonymized_text)
            if remaining_candidates:
                logging.warning(
                    f"Edge Case Detected: Judge hallucinated or misused placeholders: "
                    f"{set(remaining_candidates)}. Leaving intact."
                )

        return deanonymized_text

    def extract_ranked_models(self, judge_output: str) -> list:
        """
        Extracts ranked list from judge output and de-anonymizes placeholders.
        self.mapping must be set (placeholder → model_name) before calling this.
        """
        ranked_list = []

        rank_pattern = re.compile(
            r"(?:^|\n)\s*"
            r"(?:###\s*(?:🥇|🥈|🥉|🏆)?\s*)?(?:\d+(?:st|nd|rd|th)?[.:]?\s+)"
            r"(?:Place[:\s]+|Rank[:\s]+)?"
            r"((?:Response|Candidate|Output)\s+[A-Z0-9]+)"
            r".*?(?:Score[:\s]+|—\s*|:\s*)"
            r"(\d+\.?\d*)\s*/\s*10",
            re.MULTILINE | re.IGNORECASE | re.DOTALL
        )

        seen_placeholders = set()
        for match in rank_pattern.finditer(judge_output):
            placeholder = match.group(1).strip()
            placeholder_normalised = next(
                (k for k in self.mapping if k.lower() == placeholder.lower()),
                placeholder
            )
            if placeholder_normalised in seen_placeholders:
                continue
            seen_placeholders.add(placeholder_normalised)

            score = float(match.group(2))
            model_name = self.mapping.get(placeholder_normalised)
            if model_name:
                ranked_list.append({
                    "placeholder": placeholder_normalised,
                    "model": model_name,
                    "score": score
                })
            else:
                logging.warning(
                    f"Placeholder '{placeholder_normalised}' from judge output not found in mapping. Skipping."
                )

        ranked_list.sort(key=lambda x: x["score"], reverse=True)
        for i, item in enumerate(ranked_list):
            item["rank"] = i + 1

        return ranked_list


def main():
    import sys
    data = json.loads(sys.stdin.read())
    manager = BlindJudgeManager(run_id="modelshow2_run")

    action = data.get("action")

    if action == "anonymize":
        responses_by_model = data["responses"]
        model_names = list(responses_by_model.keys())
        label_style = data.get("label_style", "alphabetic")
        shuffle = data.get("shuffle", True)

        anonymization_map, reverse_map = manager.generate_mapping(model_names, label_style, shuffle)
        blind_responses_for_judge = manager.get_blind_responses_for_judge(responses_by_model)

        print(json.dumps({
            "anonymization_map": anonymization_map,
            "reverse_map": reverse_map,
            "blind_responses_for_judge": blind_responses_for_judge
        }))

    elif action == "deanonymize":
        judge_output = data["judge_output"]

        if "anonymization_map" in data:
            manager.mapping = data["anonymization_map"]
        elif "reverse_map" in data:
            candidate_map = data["reverse_map"]
            sample_key = next(iter(candidate_map), "")
            if re.match(r"(?:Response|Candidate|Output)\s+[A-Z0-9]+", sample_key, re.IGNORECASE):
                manager.mapping = candidate_map
            else:
                manager.mapping = {v: k for k, v in candidate_map.items()}
        else:
            print(json.dumps({"error": "deanonymize action requires 'anonymization_map' or 'reverse_map' key"}))
            return

        manager.reverse_mapping = {v: k for k, v in manager.mapping.items()}

        deanonymized_judge_output = manager.deanonymize_judge_output(judge_output)
        ranked_models_deanonymized = manager.extract_ranked_models(judge_output)

        print(json.dumps({
            "deanonymized_judge_output": deanonymized_judge_output,
            "ranked_models_deanonymized": ranked_models_deanonymized
        }))

    else:
        print(json.dumps({"error": f"Invalid action '{action}'. Expected 'anonymize' or 'deanonymize'."}))


if __name__ == "__main__":
    main()
