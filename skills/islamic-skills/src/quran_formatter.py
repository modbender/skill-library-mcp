class QuranFormatter:
    @staticmethod
    def format_ayah(ayah_data):
        """Format a single Ayah for display."""
        if not ayah_data:
            return "Ayah not found."
            
        surah_name = ayah_data['surah']['englishName'] 
        surah_num = ayah_data['surah']['number']
        ayah_num = ayah_data['numberInSurah']
        text_ar = ayah_data['text_ar']
        text_tr = ayah_data['text_tr']
        
        return f"=== {surah_name} ({surah_num}:{ayah_num}) ===\n\n{text_ar}\n\n{text_tr}"

    @staticmethod
    def format_surah(ayahs):
        """Format a full Surah."""
        if not ayahs:
            return "Surah not found."
        
        # ayahs is a list of ayah dicts
        first_ayah = ayahs[0]
        # In get_surah, 'surah' key contains the surah metadata
        surah_meta = first_ayah['surah']
        surah_name = surah_meta.get('englishName', f"Surah {surah_meta.get('number')}")
        surah_num = surah_meta.get('number')
        
        output = [f"=== {surah_name} (Surah {surah_num}) ==="]
        for ayah in ayahs:
            output.append(f"\n[{ayah['numberInSurah']}] {ayah['text_ar']}")
            output.append(f"{ayah['text_tr']}")
            
        return "\n".join(output)

    @staticmethod
    def format_search_results(results, keyword):
        """Format search results."""
        if not results:
            return f"No results found for '{keyword}'."
            
        output = [f"Search results for '{keyword}':\n"]
        for ayah in results:
            output.append(QuranFormatter.format_ayah(ayah))
            output.append("-" * 30)
            
        return "\n".join(output)
