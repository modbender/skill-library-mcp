from quran_api import QuranAPI

class QuranSearch:
    def __init__(self, language="id"):
        self.api = QuranAPI(language)

    def search_keyword(self, keyword):
        """Search for keyword and return a list of full ayah details."""
        # Perform search
        results = self.api.search(keyword)
        
        if not results or 'matches' not in results:
            return []

        # Limit to top 3 matches to avoid excessive API calls
        matches = results['matches'][:3]
        
        formatted_results = []
        for match in matches:
            surah_num = match['surah']['number']
            ayah_num = match['numberInSurah']
            
            # Fetch full ayah details (Arabic + Translation)
            full_ayah = self.api.get_ayah(surah_num, ayah_num)
            if full_ayah:
                formatted_results.append(full_ayah)
                
        return formatted_results
