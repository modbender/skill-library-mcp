# Model Selection Matrix

## Target Distribution

| Model | Usage % |
|-------|---------|
| Composer 1.5 | 60% |
| Sonnet 4.6 | 30% |
| Opus 4.6 | 10% |

Maintain this distribution across all tasks.

## Planning Complexity

| Level | Characteristics | Model |
|-------|-----------------|-------|
| Very Hard | Major architectural changes, multiple integrated features, complex business logic, high risk | Opus 4.6 |
| Medium | Multiple related features, moderate complexity, several files affected | Sonnet 4.6 |
| Low-Medium | Single feature with dependencies, relatively straightforward, limited scope | Composer 1.5 |

## Implementation Complexity

| Level | Characteristics | Model |
|-------|-----------------|-------|
| Very Hard | Complex algorithms, critical system components, high technical difficulty | Opus 4.6 |
| Medium | Standard features, moderate technical challenges, well-defined patterns | Sonnet 4.6 |
| Low-Medium | Straightforward coding, established patterns, low technical complexity | Composer 1.5 |

## Scenario Summary

| Scenario | Complexity | Model |
|----------|-----------|-------|
| Direct simple changes | Very Low | None (Self) |
| Planning - Easy | Low | Composer 1.5 |
| Planning - Medium | Medium | Sonnet 4.6 |
| Planning - Hard | High | Opus 4.6 |
| Implementation - Easy | Low | Composer 1.5 |
| Implementation - Medium | Medium | Sonnet 4.6 |
| Implementation - Hard | High | Opus 4.6 |
