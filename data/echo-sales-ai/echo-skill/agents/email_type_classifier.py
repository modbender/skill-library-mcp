'''
Email Type Classifier Agent
'''

class EmailTypeClassifier:
    def __init__(self):
        pass

    def classify(self, email_body):
        '''
        Classifies an email as "sales", "marketing", or "other" based on keywords.
        '''
        # Simple keyword-based classification
        body_lower = email_body.lower()
        sales_keywords = ["quote", "proposal", "pricing", "demo", "consultation", "appointment"]
        marketing_keywords = ["newsletter", "promotion", "webinar", "ebook", "discount", "subscribe"]

        if any(keyword in body_lower for keyword in sales_keywords):
            return "sales"
        elif any(keyword in body_lower for keyword in marketing_keywords):
            return "marketing"
        else:
            return "other"
