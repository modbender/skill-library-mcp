package client

import "time"

type CreateResearchRequest struct {
	Query              string   `json:"query"`
	BrainstormSessionID string  `json:"brainstorm_session_id,omitempty"`
	Answers            []Answer `json:"answers,omitempty"`
	Files              []string `json:"files,omitempty"`
	CollectionIDs      []string `json:"collection_ids,omitempty"`
	ReasoningLoops     int      `json:"reasoning_loops,omitempty"`
	SourceTimeout      int      `json:"source_timeout,omitempty"`
	ReasoningMode      bool     `json:"reasoning_mode,omitempty"`
	AllowEarlyExit     bool     `json:"allow_early_exit,omitempty"`
	ExcludeSocial      bool     `json:"exclude_social,omitempty"`
	ExcludedDomains    []string `json:"excluded_domains,omitempty"`
	Auto               bool     `json:"auto,omitempty"`
	SystemPrompt       string   `json:"system_prompt,omitempty"`
	Model              string   `json:"model,omitempty"`
}

type Answer struct {
	QuestionID string `json:"question_id"`
	Answer     string `json:"answer"`
}

type CreateResearchResponse struct {
	ID     string `json:"id"`
	Status string `json:"status"`
}

type ResearchObject struct {
	ID                     string          `json:"id"`
	CreatedAt              time.Time       `json:"created_at"`
	Status                 string          `json:"status"`
	Query                  string          `json:"query"`
	Content                *string         `json:"content"`
	TransformedContent     *string         `json:"transformed_content"`
	ReasoningLoopsConsumed int             `json:"reasoning_loops_consumed"`
	RunningTime            int             `json:"running_time"`
	Results                []ResearchResult `json:"results"`
}

type ResearchResult struct {
	ID            string `json:"id"`
	Title         string `json:"title"`
	URL           string `json:"url"`
	CitationIndex int    `json:"citation_index"`
}

type ResearchEvent struct {
	Message   string    `json:"message"`
	CreatedAt time.Time `json:"created_at"`
}

type ResultContent struct {
	Content string `json:"content"`
}

type BrainstormSession struct {
	ID        string             `json:"id"`
	Query     string             `json:"query"`
	Questions []BrainstormQuestion `json:"questions"`
	Status    string             `json:"status"`
	CreatedAt time.Time          `json:"created_at"`
}

type BrainstormQuestion struct {
	ID       string            `json:"id"`
	Question string            `json:"question"`
	Options  map[string]string `json:"options"`
}

type ChatMessage struct {
	ID      string           `json:"id"`
	Status  string           `json:"status,omitempty"`
	Content string           `json:"content,omitempty"`
	Results []ResearchResult `json:"results,omitempty"`
}

type Collection struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}
