---
name: podcastindex
description: "name: podcast-index description: Access and search podcast
  information using the Podcast Index API, including searching for podcasts,
  episodes, and retrieving details. homepage: https://podcastinde..."
---


name: podcast-index description: Access and search podcast information using the Podcast Index API, including searching for podcasts, episodes, and retrieving details. homepage: https://podcastindex.org/api/docs metadata: {“openclaw”:{“requires”:{“env”:[“PODCASTINDEX_API_KEY”,“PODCASTINDEX_API_SECRET”]},“primaryEnv”:“PODCASTINDEX_API_KEY”,“emoji”:“🎙️”}}
This skill allows you to interact with the Podcast Index API to search for podcasts, retrieve podcast and episode details, and more. Use this when the user asks for podcast recommendations, episode information, or searches related to podcasts.
Prerequisites
	•	Ensure PODCASTINDEX_API_KEY and PODCASTINDEX_API_SECRET are set in the environment or config.
	•	All requests must be authenticated with specific headers.
	•	Base URL: https://api.podcastindex.org/api/1.0
Authentication
To authenticate a request:
	1	Get the current Unix timestamp: unixTime = Math.floor(Date.now() / 1000)
	2	Compute the SHA-1 hash: hash = crypto.createHash('sha1').update(PODCASTINDEX_API_KEY + PODCASTINDEX_API_SECRET + unixTime.toString()).digest('hex')
	3	Include these headers in every request:
	◦	User-Agent: OpenClaw/1.0 (or a suitable identifier)
	◦	X-Auth-Key: [PODCASTINDEX_API_KEY]
	◦	X-Auth-Date: [unixTime]
	◦	Authorization: [hash]
Use the built-in HTTP request tool (e.g., fetch or http_get) to send GET requests with these headers. If executing code, use Node.js modules like ‘node-fetch’ and ‘crypto’.
Key Endpoints and Usage
	•	Search Podcasts by Term: Use when searching for podcasts by keywords in title, author, or owner.
	◦	Endpoint: GET /search/byterm?q=[query]&[optional params like max=10, fulltext=true]
	◦	Example: To find podcasts about “AI”, request /search/byterm?q=AI
	•	Search Podcasts by Title: Use for exact title matches.
	◦	Endpoint: GET /search/bytitle?q=[query]
	•	Search Episodes by Person: Use to find episodes featuring a specific person.
	◦	Endpoint: GET /search/byperson?q=[person name]
	•	Get Podcast by Feed ID: Use to retrieve full podcast details by its Podcast Index ID.
	◦	Endpoint: GET /podcasts/byfeedid?id=[feedId]
	•	Get Podcast by Feed URL: Use to retrieve details by RSS feed URL.
	◦	Endpoint: GET /podcasts/byfeedurl?url=[encoded feed URL]
	•	Get Episodes by Feed ID: Use to get a list of episodes for a podcast.
	◦	Endpoint: GET /episodes/byfeedid?id=[feedId]&[max=10]
	•	Get Episode by ID: Use for single episode metadata.
	◦	Endpoint: GET /episodes/byid?id=[episodeId]
	•	Trending Podcasts: Use for popular podcasts.
	◦	Endpoint: GET /podcasts/trending?[cat=technology&max=10]
	•	Recent Episodes: Use for newly released episodes.
	◦	Endpoint: GET /recent/episodes?max=10
Always parse the JSON response and summarize relevant information for the user. If the request fails, check authentication and retry. Add ?pretty to URLs for readable output during testing.
