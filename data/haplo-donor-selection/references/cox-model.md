# Cox Model Coefficients

Source: Fuchs et al., Blood 2022;139:1452-1468, Table 3.
Baseline S₀(3yr) = 0.413

## B-Leader (P = .01)
| Status | HR | ln(HR) |
|---|---|---|
| matched | 1.00 | 0.0 (ref) |
| mismatched | 1.20 | 0.1823 |

## DRB1/DQB1 (P = .003)
| Combination | HR | ln(HR) |
|---|---|---|
| mismatch/mismatch | 1.00 | 0.0 (ref) |
| mismatch/match | 0.80 | -0.2231 |
| match/mismatch | 1.30 | 0.2624 |
| match/match | 1.32 | 0.2776 |

## DPB1 TCE (P = .04)
| Status | HR | ln(HR) |
|---|---|---|
| matched_or_permissive | 1.00 | 0.0 (ref) |
| nonpermissive | 0.72 | -0.3285 |
| missing | 0.97 | -0.0305 |

## CMV (P = .005)
| Pat/Don | HR | ln(HR) |
|---|---|---|
| pos/pos | 1.00 | 0.0 (ref) |
| pos/neg | 1.00 | 0.0 |
| neg/pos | 1.10 | 0.0953 |
| neg/neg | 0.79 | -0.2357 |
| missing | 1.30 | 0.2624 |

## HCT-CI (P < .0001)
| Score | HR | ln(HR) |
|---|---|---|
| 0 | 1.00 | 0.0 (ref) |
| 1 | 1.21 | 0.1906 |
| 2 | 1.24 | 0.2151 |
| ≥3 | 1.54 | 0.4318 |

## Patient Age (P = .0001)
| Group | HR | ln(HR) |
|---|---|---|
| 0-18 | 1.00 | 0.0 (ref) |
| 19-29 | 1.03 | 0.0296 |
| 30-39 | 0.99 | -0.0101 |
| 40-49 | 0.90 | -0.1054 |
| 50-59 | 1.07 | 0.0677 |
| ≥60 | 1.41 | 0.3436 |

## Disease/Stage
| Code | HR | ln(HR) |
|---|---|---|
| AML/CR1 | 1.00 | 0.0 (ref) |
| AML/CR2_CR3 | 1.10 | 0.0953 |
| AML/Advanced | 2.10 | 0.7419 |
| ALL/CR1 | 0.56 | -0.5798 |
| ALL/CR2 | 1.59 | 0.4637 |
| ALL/CR3+ | 2.51 | 0.9203 |
| MDS/Early | 1.22 | 0.1989 |
| MDS/Advanced | 1.33 | 0.2852 |

## Formula
```
xβ = Σ(coefficient for each factor)
DFS(3yr) = S₀(3yr)^exp(xβ) = 0.413^exp(xβ)
```
