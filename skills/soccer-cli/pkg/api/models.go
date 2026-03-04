package api

// --- Team Search ---
type TeamResponse struct {
	Team Team `json:"team"`
}

type Team struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
}

// --- Fixture (Game) ---
type FixtureResponse struct {
	Fixture  Fixture   `json:"fixture"`
	League   League    `json:"league"`
	Teams    Teams     `json:"teams"`
	Goals    Goals     `json:"goals"`
	Events   []Event   `json:"events"`
	Lineups  []Lineup  `json:"lineups"`
	Players  []PlayerInfo `json:"players"`
}

type Fixture struct {
	ID        int    `json:"id"`
	Date      string `json:"date"`
	Timestamp int    `json:"timestamp"`
	Status    Status `json:"status"`
}

type Status struct {
	Long    string `json:"long"`
	Short   string `json:"short"`
	Elapsed int    `json:"elapsed"`
}

type League struct {
	Name    string `json:"name"`
	Round   string `json:"round"`
}

type Teams struct {
	Home Team `json:"home"`
	Away Team `json:"away"`
}

type Goals struct {
	Home int `json:"home"`
	Away int `json:"away"`
}

// --- Events ---
type Event struct {
	Time   Time   `json:"time"`
	Team   Team   `json:"team"`
	Player Player `json:"player"`
	Assist Player `json:"assist"`
	Type   string `json:"type"` // Goal, Card
	Detail string `json:"detail"` // e.g., "Normal Goal", "Yellow Card", "Red Card"
}

type Time struct {
	Elapsed int `json:"elapsed"`
}

type Player struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
}

// --- Lineups/Squads ---
type Lineup struct {
	Team    Team     `json:"team"`
	Coach   Player   `json:"coach"`
	Formation string `json:"formation"`
	StartXI   []PlayerInfo `json:"startXI"`
	Substitutes []PlayerInfo `json:"substitutes"`
}

type PlayerInfo struct {
	Player Player `json:"player"`
}

// --- Player Stats ---
// This is a separate response structure for the /fixtures/players endpoint
type PlayerStatsParent struct {
	Team    Team     `json:"team"`
	Players []PlayerStatistics `json:"players"`
}

type PlayerStatistics struct {
	Player     Player      `json:"player"`
	Statistics []Statistic `json:"statistics"`
}

type Statistic struct {
	Games  Games  `json:"games"`
}

type Games struct {
	Minutes  int    `json:"minutes"`
	Position string `json:"position"`
	Rating   string `json:"rating"`
}


// --- Generic API Response Wrappers ---
type APIResponse struct {
	Get        string        `json:"get"`
	Parameters interface{}   `json:"parameters"`
	Errors     []interface{} `json:"errors"`
	Results    int           `json:"results"`
	Paging     Paging        `json:"paging"`
	Response   interface{}   `json:"response"`
}
