from quran_api import QuranAPI

class QuranRetrieval:
    def __init__(self, language="id"):
        self.api = QuranAPI(language)

    def get_ayah(self, surah, ayah):
        """Fetch a specific ayah."""
        if not surah or not ayah:
            return None
        return self.api.get_ayah(surah, ayah)

    def get_surah(self, surah_number):
        """Fetch a full surah."""
        if not surah_number:
            return None
        return self.api.get_surah(surah_number)
