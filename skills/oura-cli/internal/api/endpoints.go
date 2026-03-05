package api

import (
	"net/url"
)

// --- Types ---

type PersonalInfo struct {
	ID     string  `json:"id"`
	Age    int     `json:"age"`
	Weight float64 `json:"weight"`
	Height float64 `json:"height"`
	Gender string  `json:"gender"`
	Email  string  `json:"email"`
}

type DailySleep struct {
	ID        string `json:"id"`
	Day       string `json:"day"`
	Score     int    `json:"score"`
	Timestamp string `json:"timestamp"`
	// Add more fields as needed per docs, keeping it minimal for CLI summary for now
}

type DailySleepResponse struct {
	Data      []DailySleep `json:"data"`
	NextToken string       `json:"next_token"`
}

type DailyActivity struct {
	ID    string `json:"id"`
	Day   string `json:"day"`
	Score int    `json:"score"`
	Steps int    `json:"steps"`
	// ...
}

type DailyActivityResponse struct {
	Data      []DailyActivity `json:"data"`
	NextToken string          `json:"next_token"`
}

type DailyReadiness struct {
	ID    string `json:"id"`
	Day   string `json:"day"`
	Score int    `json:"score"`
	// ...
}

type DailyReadinessResponse struct {
	Data      []DailyReadiness `json:"data"`
	NextToken string           `json:"next_token"`
}

type HeartRate struct {
	ID        string `json:"id"`
	BPM       int    `json:"bpm"`
	Source    string `json:"source"`
	Timestamp string `json:"timestamp"`
}

type HeartRateResponse struct {
	Data      []HeartRate `json:"data"`
	NextToken string      `json:"next_token"`
}

type Workout struct {
	ID            string  `json:"id"`
	Activity      string  `json:"activity"`
	Calories      float64 `json:"calories"`
	Day           string  `json:"day"`
	Distance      float64 `json:"distance"`
	EndDatetime   string  `json:"end_datetime"`
	StartDatetime string  `json:"start_datetime"`
	Label         string  `json:"label"`
}

type WorkoutResponse struct {
	Data      []Workout `json:"data"`
	NextToken string    `json:"next_token"`
}

type SpO2 struct {
	ID             string `json:"id"`
	Day            string `json:"day"`
	SpO2Percentage struct {
		Average float64 `json:"average"`
	} `json:"spo2_percentage"`
}

type SpO2Response struct {
	Data      []SpO2 `json:"data"`
	NextToken string `json:"next_token"`
}

type Sleep struct {
	ID            string `json:"id"`
	Day           string `json:"day"`
	Score         int    `json:"score"`
	Efficiency    int    `json:"efficiency"`
	Type          string `json:"type"`
	BedtimeStart  string `json:"bedtime_start"`
	BedtimeEnd    string `json:"bedtime_end"`
	Hypnogram5Min string `json:"hypnogram_5min"`
}

type SleepResponse struct {
	Data      []Sleep `json:"data"`
	NextToken string  `json:"next_token"`
}

type Session struct {
	ID            string `json:"id"`
	Day           string `json:"day"`
	StartDatetime string `json:"start_datetime"`
	EndDatetime   string `json:"end_datetime"`
	Type          string `json:"type"`
	Status        string `json:"status"`
	MotionCount   int    `json:"motion_count"`
}

type SessionResponse struct {
	Data      []Session `json:"data"`
	NextToken string    `json:"next_token"`
}

type SleepTime struct {
	ID             string `json:"id"`
	Day            string `json:"day"`
	OptimalBedtime struct {
		DayTZ       int    `json:"day_tz"`
		EndOffset   int    `json:"end_offset"`
		StartOffset int    `json:"start_offset"`
		Status      string `json:"status"`
	} `json:"optimal_bedtime"`
	Recommendation string `json:"recommendation"`
}

type SleepTimeResponse struct {
	Data      []SleepTime `json:"data"`
	NextToken string      `json:"next_token"`
}

type EnhancedTag struct {
	ID          string `json:"id"`
	TagTypeCode string `json:"tag_type_code"`
	StartTime   string `json:"start_time"`
	EndTime     string `json:"end_time"`
	Comment     string `json:"comment"`
}

type EnhancedTagResponse struct {
	Data      []EnhancedTag `json:"data"`
	NextToken string        `json:"next_token"`
}

type DailyStress struct {
	ID           string `json:"id"`
	Day          string `json:"day"`
	StressHigh   int    `json:"stress_high"`
	RecoveryHigh int    `json:"recovery_high"`
	DaySummary   string `json:"day_summary"`
}

type DailyStressResponse struct {
	Data      []DailyStress `json:"data"`
	NextToken string        `json:"next_token"`
}

type DailyResilience struct {
	ID           string `json:"id"`
	Day          string `json:"day"`
	Level        string `json:"level"`
	Contributors struct {
		SleepRecovery   float64 `json:"sleep_recovery"`
		DaytimeRecovery float64 `json:"daytime_recovery"`
		Stress          float64 `json:"stress"`
	} `json:"contributors"`
}

type DailyResilienceResponse struct {
	Data      []DailyResilience `json:"data"`
	NextToken string            `json:"next_token"`
}

type DailyCardiovascularAge struct {
	ID               string `json:"id"`
	Day              string `json:"day"`
	VascularAgeRange int    `json:"vascular_age_range"`
}

type DailyCardiovascularAgeResponse struct {
	Data      []DailyCardiovascularAge `json:"data"`
	NextToken string                   `json:"next_token"`
}

type VO2Max struct {
	ID     string  `json:"id"`
	Day    string  `json:"day"`
	VO2Max float64 `json:"vo2_max"`
}

type VO2MaxResponse struct {
	Data      []VO2Max `json:"data"`
	NextToken string   `json:"next_token"`
}

type RingConfiguration struct {
	ID              string `json:"id"`
	Color           string `json:"color"`
	Design          string `json:"design"`
	FirmwareVersion string `json:"firmware_version"`
	HardwareType    string `json:"hardware_type"`
	Size            int    `json:"size"`
}

type RingConfigurationResponse struct {
	Data      []RingConfiguration `json:"data"`
	NextToken string              `json:"next_token"`
}

type RestModePeriod struct {
	ID        string `json:"id"`
	Day       string `json:"day"`
	EndDay    string `json:"end_day"`
	StartDay  string `json:"start_day"`
	StartTime string `json:"start_time"`
	EndTime   string `json:"end_time"`
}

type RestModePeriodResponse struct {
	Data      []RestModePeriod `json:"data"`
	NextToken string           `json:"next_token"`
}

// --- Methods ---

func (c *Client) GetPersonalInfo() (*PersonalInfo, error) {
	var p PersonalInfo
	err := c.get("personal_info", nil, &p)
	return &p, err
}

func (c *Client) GetDailySleep(start, end string) (*DailySleepResponse, error) {
	params := url.Values{}
	if start != "" {
		params.Set("start_date", start)
	}
	if end != "" {
		params.Set("end_date", end)
	}

	var res DailySleepResponse
	err := c.get("daily_sleep", params, &res)
	return &res, err
}

func (c *Client) GetDailyActivity(start, end string) (*DailyActivityResponse, error) {
	params := url.Values{}
	if start != "" {
		params.Set("start_date", start)
	}
	if end != "" {
		params.Set("end_date", end)
	}

	var res DailyActivityResponse
	err := c.get("daily_activity", params, &res)
	return &res, err
}

func (c *Client) GetDailyReadiness(start, end string) (*DailyReadinessResponse, error) {
	params := url.Values{}
	if start != "" {
		params.Set("start_date", start)
	}
	if end != "" {
		params.Set("end_date", end)
	}

	var res DailyReadinessResponse
	err := c.get("daily_readiness", params, &res)
	return &res, err
}

func (c *Client) GetHeartRate(start, end string) (*HeartRateResponse, error) {
	params := url.Values{}
	if start != "" {
		params.Set("start_datetime", start)
	}
	if end != "" {
		params.Set("end_datetime", end)
	}

	var res HeartRateResponse
	err := c.get("heartrate", params, &res)
	return &res, err
}

func (c *Client) GetWorkouts(start, end string) (*WorkoutResponse, error) {
	params := url.Values{}
	if start != "" {
		params.Set("start_date", start)
	}
	if end != "" {
		params.Set("end_date", end)
	}

	var res WorkoutResponse
	err := c.get("workout", params, &res)
	return &res, err
}

func (c *Client) GetSpO2(start, end string) (*SpO2Response, error) {
	params := url.Values{}
	if start != "" {
		params.Set("start_date", start)
	}
	if end != "" {
		params.Set("end_date", end)
	}

	var res SpO2Response
	err := c.get("daily_spo2", params, &res)
	return &res, err
}

func (c *Client) GetSleep(start, end string) (*SleepResponse, error) {
	params := url.Values{}
	if start != "" {
		params.Set("start_date", start)
	}
	if end != "" {
		params.Set("end_date", end)
	}

	var res SleepResponse
	err := c.get("sleep", params, &res)
	return &res, err
}

func (c *Client) GetSessions(start, end string) (*SessionResponse, error) {
	params := url.Values{}
	if start != "" {
		params.Set("start_date", start)
	}
	if end != "" {
		params.Set("end_date", end)
	}

	var res SessionResponse
	err := c.get("session", params, &res)
	return &res, err
}

func (c *Client) GetSleepTimes(start, end string) (*SleepTimeResponse, error) {
	params := url.Values{}
	if start != "" {
		params.Set("start_date", start)
	}
	if end != "" {
		params.Set("end_date", end)
	}

	var res SleepTimeResponse
	err := c.get("sleep_time", params, &res)
	return &res, err
}

func (c *Client) GetEnhancedTags(start, end string) (*EnhancedTagResponse, error) {
	params := url.Values{}
	if start != "" {
		params.Set("start_date", start)
	}
	if end != "" {
		params.Set("end_date", end)
	}
	var res EnhancedTagResponse
	err := c.get("enhanced_tag", params, &res)
	return &res, err
}

func (c *Client) GetDailyStress(start, end string) (*DailyStressResponse, error) {
	params := url.Values{}
	if start != "" {
		params.Set("start_date", start)
	}
	if end != "" {
		params.Set("end_date", end)
	}
	var res DailyStressResponse
	err := c.get("daily_stress", params, &res)
	return &res, err
}

func (c *Client) GetDailyResilience(start, end string) (*DailyResilienceResponse, error) {
	params := url.Values{}
	if start != "" {
		params.Set("start_date", start)
	}
	if end != "" {
		params.Set("end_date", end)
	}
	var res DailyResilienceResponse
	err := c.get("daily_resilience", params, &res)
	return &res, err
}

func (c *Client) GetCVAge(start, end string) (*DailyCardiovascularAgeResponse, error) {
	params := url.Values{}
	if start != "" {
		params.Set("start_date", start)
	}
	if end != "" {
		params.Set("end_date", end)
	}
	var res DailyCardiovascularAgeResponse
	err := c.get("daily_cardiovascular_age", params, &res)
	return &res, err
}

func (c *Client) GetVO2Max(start, end string) (*VO2MaxResponse, error) {
	params := url.Values{}
	if start != "" {
		params.Set("start_date", start)
	}
	if end != "" {
		params.Set("end_date", end)
	}
	var res VO2MaxResponse
	err := c.get("vO2_max", params, &res)
	return &res, err
}

func (c *Client) GetRingConfiguration(start, end string) (*RingConfigurationResponse, error) {
	params := url.Values{}
	if start != "" {
		params.Set("start_date", start)
	}
	if end != "" {
		params.Set("end_date", end)
	}
	var res RingConfigurationResponse
	err := c.get("ring_configuration", params, &res)
	return &res, err
}

func (c *Client) GetRestModePeriod(start, end string) (*RestModePeriodResponse, error) {
	params := url.Values{}
	if start != "" {
		params.Set("start_date", start)
	}
	if end != "" {
		params.Set("end_date", end)
	}
	var res RestModePeriodResponse
	err := c.get("rest_mode_period", params, &res)
	return &res, err
}
