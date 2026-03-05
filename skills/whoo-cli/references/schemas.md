# whoo CLI — JSON Output Schemas

Reference for `--json` flag output. All duration fields are in milliseconds — divide by
`3_600_000` for hours or `60_000` for minutes.

---

## `whoo recovery --json`

```
{
  recoveries: [
    {
      start: string,                    // ISO timestamp
      end: string,                      // ISO timestamp
      timezone_offset: string,          // e.g. "+05:30"
      score_state: "SCORED" | "PENDING_MANUAL" | "UNSCORABLE",
      score: {
        recovery_score: number,         // 0–100 (%)
        hrv_rmssd_milli: number,        // ms
        resting_heart_rate: number,     // bpm
        spo2_percentage: number,        // %
        skin_temp_celsius: number,      // deviation from personal baseline (°C)
        user_calibrating: boolean
      }
    }
  ]
}
```

---

## `whoo sleep --json`

```
{
  sleeps: [
    {
      start: string,                                // ISO timestamp
      end: string,                                  // ISO timestamp
      timezone_offset: string,
      nap: boolean,
      score_state: "SCORED" | "PENDING_MANUAL" | "UNSCORABLE",
      score: {
        stage_summary: {
          total_in_bed_time_milli: number,
          total_awake_time_milli: number,
          total_no_data_time_milli: number,
          total_light_sleep_time_milli: number,
          total_slow_wave_sleep_time_milli: number, // deep/SWS
          total_rem_sleep_time_milli: number,
          sleep_cycle_count: number,
          disturbance_count: number
        },
        sleep_needed: {
          baseline_milli: number,
          need_from_sleep_debt_milli: number,
          need_from_recent_strain_milli: number,
          need_from_recent_nap_milli: number        // negative when nap reduces need
        },
        respiratory_rate: number,                   // breaths/min
        sleep_performance_percentage: number,       // actual vs needed (%)
        sleep_consistency_percentage: number,       // vs prior 28-day pattern (%)
        sleep_efficiency_percentage: number         // time asleep / time in bed (%)
      }
    }
  ]
}
```

---

## `whoo overview --json`

```
{
  profile: {
    first_name: string,
    last_name: string,
    email: string
  },
  cycles: [
    {
      cycle: {
        start: string,                 // ISO timestamp
        end: string | null,            // null = cycle still in progress
        timezone_offset: string,
        score_state: "SCORED" | "PENDING_MANUAL" | "UNSCORABLE",
        score: {
          strain: number,              // 0–21 (day strain)
          kilojoule: number,           // energy expenditure (kJ)
          average_heart_rate: number,  // bpm
          max_heart_rate: number       // bpm
        }
      },
      recovery: { /* same shape as recoveries[n] */ } | null,
      sleep:    { /* same shape as sleeps[n] */ }    | null
    }
  ]
}
```

---

## `whoo user --json`

```
{
  profile: {
    first_name: string,
    last_name: string,
    email: string
  },
  bodyMeasurement: {
    max_heart_rate: number   // bpm
  } | null
}
```
