# VitaVault Data Types (Schema v2.0)

48 health metrics exported from Apple Health via VitaVault.

## Activity
| Type | Display Name | Unit |
|------|-------------|------|
| stepCount | Step Count | count |
| distanceWalkingRunning | Walking + Running Distance | mi |
| distanceCycling | Cycling Distance | mi |
| distanceSwimming | Swimming Distance | yd |
| activeEnergyBurned | Active Energy | kcal |
| basalEnergyBurned | Resting Energy (BMR) | kcal |
| appleExerciseTime | Exercise Minutes | min |
| appleStandTime | Stand Hours | hr |
| flightsClimbed | Flights Climbed | count |
| vo2Max | VO2 Max | mL/kg/min |

## Body
| Type | Display Name | Unit |
|------|-------------|------|
| bodyMass | Weight | lb |
| bodyMassIndex | BMI | count |
| height | Height | in |
| bodyFatPercentage | Body Fat | % |
| leanBodyMass | Lean Body Mass | lb |
| waistCircumference | Waist Circumference | in |

## Vitals
| Type | Display Name | Unit |
|------|-------------|------|
| heartRate | Heart Rate | bpm |
| restingHeartRate | Resting Heart Rate | bpm |
| walkingHeartRateAverage | Walking Heart Rate | bpm |
| heartRateVariabilitySDNN | HRV (SDNN) | ms |
| oxygenSaturation | Blood Oxygen (SpO2) | % |
| bloodPressureSystolic | Systolic BP | mmHg |
| bloodPressureDiastolic | Diastolic BP | mmHg |
| respiratoryRate | Respiratory Rate | breaths/min |
| bodyTemperature | Body Temperature | °F |
| bloodGlucose | Blood Glucose | mg/dL |
| electrodermalActivity | Electrodermal Activity | μS |

## Sleep
| Type | Display Name | Unit |
|------|-------------|------|
| sleepAnalysis | Sleep Analysis | category |

Sleep records include category values: InBed, Asleep, AsleepCore, AsleepDeep, AsleepREM, Awake.

## Nutrition
| Type | Display Name | Unit |
|------|-------------|------|
| dietaryEnergyConsumed | Calories | kcal |
| dietaryProtein | Protein | g |
| dietaryCarbohydrates | Carbs | g |
| dietaryFatTotal | Total Fat | g |
| dietaryFatSaturated | Saturated Fat | g |
| dietaryFiber | Fiber | g |
| dietarySugar | Sugar | g |
| dietarySodium | Sodium | mg |
| dietaryCholesterol | Cholesterol | mg |
| dietaryCaffeine | Caffeine | mg |
| dietaryWater | Water | fl_oz |
| dietaryPotassium | Potassium | mg |
| dietaryCalcium | Calcium | mg |
| dietaryIron | Iron | mg |
| dietaryVitaminC | Vitamin C | mg |
| dietaryVitaminD | Vitamin D | IU |

## Mindfulness
| Type | Display Name | Unit |
|------|-------------|------|
| mindfulSession | Mindful Minutes | min |
