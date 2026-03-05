import requests
import logging

class QuranAPI:
    BASE_URL = "http://api.alquran.cloud/v1"
    
    # Mapping for language codes to editions
    EDITIONS = {
        'id': 'id.indonesian',
        'en': 'en.sahih',
        'ar': 'quran-uthmani'
    }

    def __init__(self, language="id"):
        self.language = language
        self.translation_edition = self.EDITIONS.get(language, 'en.sahih')
        self.arabic_edition = 'quran-uthmani'
        self.logger = logging.getLogger(__name__)

    def get_ayah(self, surah, ayah):
        """Fetch a specific ayah (Arabic + Translation)."""
        try:
            # Fetch Arabic
            ar_resp = requests.get(f"{self.BASE_URL}/ayah/{surah}:{ayah}/{self.arabic_edition}", timeout=10)
            ar_resp.raise_for_status()
            ar_data = ar_resp.json().get('data')

            # Fetch Translation
            tr_resp = requests.get(f"{self.BASE_URL}/ayah/{surah}:{ayah}/{self.translation_edition}", timeout=10)
            tr_resp.raise_for_status()
            tr_data = tr_resp.json().get('data')

            if not ar_data or not tr_data:
                return None

            return {
                'surah': ar_data['surah'],
                'numberInSurah': ar_data['numberInSurah'],
                'text_ar': ar_data['text'],
                'text_tr': tr_data['text']
            }
        except Exception as e:
            self.logger.error(f"Error fetching ayah {surah}:{ayah}: {e}")
            return None

    def get_surah(self, surah_number):
        """Fetch a full Surah (Arabic + Translation)."""
        try:
            # Fetch Arabic
            ar_resp = requests.get(f"{self.BASE_URL}/surah/{surah_number}/{self.arabic_edition}", timeout=10)
            ar_resp.raise_for_status()
            ar_data = ar_resp.json().get('data')

            # Fetch Translation
            tr_resp = requests.get(f"{self.BASE_URL}/surah/{surah_number}/{self.translation_edition}", timeout=10)
            tr_resp.raise_for_status()
            tr_data = tr_resp.json().get('data')

            if not ar_data or not tr_data:
                return None

            # Combine them
            ayahs = []
            surah_meta = {k: v for k, v in ar_data.items() if k != 'ayahs'} # Extract metadata

            for i, ar_ayah in enumerate(ar_data['ayahs']):
                tr_ayah = tr_data['ayahs'][i]
                ayahs.append({
                    'surah': surah_meta, 
                    'numberInSurah': ar_ayah['numberInSurah'],
                    'text_ar': ar_ayah['text'],
                    'text_tr': tr_ayah['text']
                })
            
            return ayahs

        except Exception as e:
            self.logger.error(f"Error fetching surah {surah_number}: {e}")
            return None

    def search(self, keyword):
        """Search for keyword in translation."""
        try:
            # The search endpoint: /search/{keyword}/{scope}/{edition}
            url = f"{self.BASE_URL}/search/{keyword}/all/{self.translation_edition}"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json().get('data')
            return data
            
        except Exception as e:
            self.logger.error(f"Error searching for '{keyword}': {e}")
            return None
