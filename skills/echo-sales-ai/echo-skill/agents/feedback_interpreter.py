import openai
import json

class FeedbackInterpreter:
    def __init__(self, api_key):
        openai.api_key = api_key

    def interpret(self, feedback_text):
        """
        Interprets natural language feedback and converts it into structured commands.
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in analyzing feedback for email generation. Your task is to convert natural language feedback into a structured JSON object. The user will provide feedback on an email, and you must extract the key sentiment, the specific aspect being criticized (e.g., tone, length, call-to-action), and a suggested modification. The possible values for 'aspect' are: 'tone', 'length', 'style', 'vocabulary', 'call_to_action', 'greeting', 'closing', 'clarity', 'urgency', 'personalization'. The possible values for 'sentiment' are 'positive', 'negative', 'neutral'. The 'modification' should be a concise instruction for an AI writer. If the feedback is vague, set 'modification' to 'general_improvement'."
                    },
                    {
                        "role": "user",
                        "content": f"The user's feedback is: '{feedback_text}'. Please convert this into a structured JSON object with the keys 'sentiment', 'aspect', and 'modification'."
                    }
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error interpreting feedback: {e}")
            return json.dumps({"sentiment": "neutral", "aspect": "unknown", "modification": "general_improvement"})
