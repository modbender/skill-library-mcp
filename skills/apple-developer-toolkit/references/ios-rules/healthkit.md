---
description: "Implementation rules for healthkit"
---
# Healthkit

HEALTHKIT:
- import HealthKit; HKHealthStore()
- Check availability: HKHealthStore.isHealthDataAvailable()
- Request auth: healthStore.requestAuthorization(toShare:read:)
- Requires NSHealthShareUsageDescription + NSHealthUpdateUsageDescription (add CONFIG_CHANGES)
- Requires com.apple.developer.healthkit entitlement (add CONFIG_CHANGES)
- Query: HKSampleQuery, HKStatisticsQuery for aggregated data
- Common types: HKQuantityType(.stepCount), .heartRate, .activeEnergyBurned
