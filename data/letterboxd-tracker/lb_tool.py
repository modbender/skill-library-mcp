import sys
import json
from letterboxdpy import user, movie

def get_user_info(username):
    """Fetches user profile stats and favorites."""
    try:
        lb_user = user.User(username)
        stats = lb_user.get_stats()
        favorites = lb_user.get_favorites()
        
        return json.dumps({
            "username": username,
            "display_name": lb_user.get_display_name(),
            "watched_count": stats.get("films", 0),
            "reviews_count": stats.get("reviews", 0),
            "lists_count": stats.get("lists", 0),
            "favorites": favorites.get("films", [])[:5] if favorites else []
        }, indent=2)
    except Exception as e:
        return f"Error fetching user {username}: {str(e)}"

def get_user_diary(username, limit=10):
    """Fetches recent movies from user's diary."""
    try:
        lb_user = user.User(username)
        diary = lb_user.get_diary_recent()
        
        if not diary or not diary.get("months"):
            return f"No recent diary entries for {username}"
        
        results = []
        months = diary.get("months", {})
        
        # Iterate through months (newest first)
        for month, days in sorted(months.items(), reverse=True):
            for day, films in sorted(days.items(), reverse=True):
                for film in films:
                    results.append({
                        "date": f"2026-{month}-{day}",
                        "name": film.get("name", ""),
                        "slug": film.get("slug", "")
                    })
                    if len(results) >= limit:
                        break
                if len(results) >= limit:
                    break
            if len(results) >= limit:
                break
        
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error fetching diary for {username}: {str(e)}"

def get_user_watchlist(username, limit=10):
    """Fetches user's watchlist."""
    try:
        lb_user = user.User(username)
        watchlist = lb_user.get_watchlist_movies()
        
        if not watchlist:
            return f"No watchlist for {username}"
        
        results = []
        count = 0
        for film_id, film_data in watchlist.items():
            if count >= limit:
                break
            results.append({
                "name": film_data.get("name", ""),
                "year": film_data.get("year", ""),
                "slug": film_data.get("slug", "")
            })
            count += 1
        
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error fetching watchlist for {username}: {str(e)}"

def get_movie_details(movie_slug):
    """Fetches details for a specific movie."""
    try:
        lb_movie = movie.Movie(movie_slug)
        crew = lb_movie.get_crew()
        
        directors = []
        if crew:
            directors = [c.get("name") for c in crew.get("directors", [])]
        
        return json.dumps({
            "title": lb_movie.title,
            "year": lb_movie.year,
            "rating": lb_movie.rating,
            "description": lb_movie.description,
            "directors": directors,
            "genres": lb_movie.genres,
            "runtime": lb_movie.runtime,
            "url": lb_movie.url
        }, indent=2)
    except Exception as e:
        return f"Error fetching movie '{movie_slug}': {str(e)}"

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    target = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if command == "user":
        print(get_user_info(target))
    elif command == "diary":
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        print(get_user_diary(target, limit))
    elif command == "watchlist":
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        print(get_user_watchlist(target, limit))
    elif command == "movie":
        print(get_movie_details(target))
    else:
        print("Commands: user <username>, diary <username> [limit], watchlist <username> [limit], movie <slug>")
