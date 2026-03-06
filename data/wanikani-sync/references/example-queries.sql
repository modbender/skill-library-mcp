-- WaniKani Example Queries
-- Run these in your SQLite client after syncing data

-- ============================================
-- BASIC LOOKUPS
-- ============================================

-- Find a specific kanji by character
SELECT s.characters, s.level, json_extract(s.meanings, '$[0]'), json_extract(s.readings, '$[0]')
FROM subjects s
WHERE s.object = 'kanji' AND s.characters = '来';

-- Look up all kanji in a specific level
SELECT characters, json_extract(meanings, '$[0]') as meaning, json_extract(readings, '$[0]') as reading
FROM subjects
WHERE object = 'kanji' AND level = 5
ORDER BY characters;

-- ============================================
-- PROGRESS STATISTICS
-- ============================================

-- SRS stage distribution with percentages
SELECT 
    srs_stage,
    CASE srs_stage
        WHEN 0 THEN 'Locked'
        WHEN 1 THEN 'Apprentice I'
        WHEN 2 THEN 'Apprentice II'
        WHEN 3 THEN 'Apprentice III'
        WHEN 4 THEN 'Apprentice IV'
        WHEN 5 THEN 'Guru I'
        WHEN 6 THEN 'Guru II'
        WHEN 7 THEN 'Master'
        WHEN 8 THEN 'Enlightened'
        WHEN 9 THEN 'Burned'
    END as stage_name,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM assignments), 1) as percentage
FROM assignments
GROUP BY srs_stage
ORDER BY srs_stage;

-- Burned items by level
SELECT 
    s.level,
    COUNT(*) as burned_count
FROM assignments a
JOIN subjects s ON a.subject_id = s.id
WHERE a.burned_at IS NOT NULL
GROUP BY s.level
ORDER BY s.level;

-- Items available for review now (or in next 24 hours)
SELECT s.characters, s.level, a.available_at
FROM assignments a
JOIN subjects s ON a.subject_id = s.id
WHERE a.available_at <= datetime('now', '+1 day')
  AND a.burned_at IS NULL
  AND a.srs_stage > 0
ORDER BY a.available_at
LIMIT 20;

-- ============================================
-- LEECHES & PROBLEMATIC ITEMS
-- ============================================

-- Basic leech detection: items with <75% accuracy
SELECT 
    s.characters,
    s.object as type,
    json_extract(s.meanings, '$[0]') as meaning,
    json_extract(s.readings, '$[0]') as reading,
    rs.percentage_correct as accuracy,
    rs.meaning_incorrect + rs.reading_incorrect as total_fails
FROM review_statistics rs
JOIN subjects s ON rs.subject_id = s.id
WHERE rs.percentage_correct < 75
ORDER BY rs.percentage_correct ASC, total_fails DESC
LIMIT 20;

-- Current leeches: Apprentice stage with high failure count
SELECT 
    s.characters,
    json_extract(s.meanings, '$[0]') as meaning,
    json_extract(s.readings, '$[0]') as reading,
    a.srs_stage,
    rs.meaning_incorrect + rs.reading_incorrect as fails,
    rs.percentage_correct as accuracy
FROM review_statistics rs
JOIN assignments a ON rs.subject_id = a.subject_id
JOIN subjects s ON rs.subject_id = s.id
WHERE a.srs_stage BETWEEN 1 AND 4  -- Apprentice
  AND (rs.meaning_incorrect + rs.reading_incorrect) >= 5
ORDER BY fails DESC, accuracy ASC
LIMIT 15;

-- Items with weak reading streaks (about to drop)
SELECT 
    s.characters,
    json_extract(s.meanings, '$[0]') as meaning,
    json_extract(s.readings, '$[0]') as reading,
    a.srs_stage,
    rs.reading_current_streak,
    rs.reading_max_streak,
    rs.percentage_correct
FROM review_statistics rs
JOIN assignments a ON rs.subject_id = a.subject_id
JOIN subjects s ON rs.subject_id = s.id
WHERE s.object IN ('kanji', 'vocabulary')
  AND rs.reading_current_streak <= 2
  AND a.srs_stage > 2
ORDER BY a.srs_stage DESC, rs.percentage_correct ASC
LIMIT 15;

-- Critical items: High SRS stage but weak streaks (risk of falling back)
SELECT 
    s.characters,
    json_extract(s.meanings, '$[0]') as meaning,
    CASE a.srs_stage
        WHEN 5 THEN 'Guru I'
        WHEN 6 THEN 'Guru II'
        WHEN 7 THEN 'Master'
        WHEN 8 THEN 'Enlightened'
    END as stage,
    rs.reading_current_streak,
    rs.meaning_current_streak,
    rs.percentage_correct,
    a.available_at
FROM review_statistics rs
JOIN assignments a ON rs.subject_id = a.subject_id
JOIN subjects s ON rs.subject_id = s.id
WHERE a.srs_stage BETWEEN 5 AND 8
  AND (rs.reading_current_streak <= 2 OR rs.meaning_current_streak <= 2)
ORDER BY a.srs_stage DESC, rs.percentage_correct ASC;

-- ============================================
-- ACCURACY ANALYSIS
-- ============================================

-- Accuracy by subject type
SELECT 
    subject_type,
    COUNT(*) as count,
    ROUND(AVG(percentage_correct), 1) as avg_accuracy,
    ROUND(MIN(percentage_correct), 1) as worst_accuracy,
    ROUND(MAX(percentage_correct), 1) as best_accuracy
FROM review_statistics
GROUP BY subject_type;

-- Accuracy by WaniKani level
SELECT 
    s.level,
    COUNT(*) as items,
    ROUND(AVG(rs.percentage_correct), 1) as avg_accuracy,
    ROUND(MIN(rs.percentage_correct), 1) as min_accuracy
FROM review_statistics rs
JOIN subjects s ON rs.subject_id = s.id
GROUP BY s.level
ORDER BY s.level;

-- Kanji vs Vocabulary accuracy comparison for same level
SELECT 
    s.level,
    ROUND(AVG(CASE WHEN s.object = 'kanji' THEN rs.percentage_correct END), 1) as kanji_acc,
    ROUND(AVG(CASE WHEN s.object = 'vocabulary' THEN rs.percentage_correct END), 1) as vocab_acc,
    COUNT(CASE WHEN s.object = 'kanji' THEN 1 END) as kanji_count,
    COUNT(CASE WHEN s.object = 'vocabulary' THEN 1 END) as vocab_count
FROM review_statistics rs
JOIN subjects s ON rs.subject_id = s.id
WHERE s.object IN ('kanji', 'vocabulary')
GROUP BY s.level
ORDER BY s.level;

-- ============================================
-- LEVEL PROGRESSION
-- ============================================

-- Time spent at each level
SELECT 
    level,
    unlocked_at,
    started_at,
    passed_at,
    CASE 
        WHEN started_at IS NULL THEN 'Not started'
        WHEN passed_at IS NULL THEN 'In progress'
        ELSE CAST(ROUND(julianday(passed_at) - julianday(started_at)) AS INTEGER) || ' days'
    END as time_to_pass,
    CASE 
        WHEN abandoned_at IS NOT NULL THEN '⚠️ RESET'
        WHEN completed_at IS NOT NULL THEN '✓ Complete'
        WHEN passed_at IS NOT NULL THEN '✓ Passed'
        WHEN started_at IS NOT NULL THEN '⋯ In Progress'
        ELSE '○ Unlocked'
    END as status
FROM level_progressions
ORDER BY level;

-- Average time to pass per level
SELECT 
    level,
    CAST(ROUND(julianday(passed_at) - julianday(started_at)) AS INTEGER) as days_to_pass
FROM level_progressions
WHERE started_at IS NOT NULL AND passed_at IS NOT NULL
ORDER BY days_to_pass DESC;

-- ============================================
-- SUBJECT RELATIONSHIPS
-- ============================================

-- What radicals compose a kanji?
-- (requires subjects.component_subject_ids JSON)
SELECT 
    s.characters as kanji,
    json_extract(s.meanings, '$[0]') as meaning,
    s.component_subject_ids as components
FROM subjects s
WHERE s.object = 'kanji' AND s.characters = '来';

-- What vocabulary uses a specific kanji?
-- (requires subjects.vocabulary_ids JSON)
SELECT 
    s.characters as kanji,
    json_extract(s.meanings, '$[0]') as kanji_meaning,
    s.vocabulary_ids
FROM subjects s
WHERE s.object = 'kanji' AND s.characters = '来';

-- Find all vocabulary for kanji in level 5
SELECT 
    s.characters as kanji,
    json_extract(s.meanings, '$[0]') as kanji_meaning,
    v.characters as vocab,
    json_extract(v.meanings, '$[0]') as vocab_meaning
FROM subjects s
JOIN subjects v ON json_extract(s.vocabulary_ids, '$') LIKE '%' || v.id || '%'
WHERE s.object = 'kanji' AND s.level = 5
  AND v.object = 'vocabulary'
LIMIT 10;

-- ============================================
-- REVIEW PATTERNS (if reviews table populated)
-- ============================================

-- Reviews per day (last 30 days) - requires reviews table
SELECT 
    DATE(created_at) as day,
    COUNT(*) as review_count,
    SUM(incorrect_meaning_answers + incorrect_reading_answers) as total_wrong,
    ROUND(100.0 * (1.0 - CAST(SUM(incorrect_meaning_answers + incorrect_reading_answers) AS FLOAT) / 
          (COUNT(*) * 2)), 1) as accuracy
FROM reviews
WHERE created_at > datetime('now', '-30 days')
GROUP BY DATE(created_at)
ORDER BY day DESC;

-- Most common mistake combinations
SELECT 
    incorrect_meaning_answers as meaning_wrong,
    incorrect_reading_answers as reading_wrong,
    COUNT(*) as frequency
FROM reviews
GROUP BY incorrect_meaning_answers, incorrect_reading_answers
ORDER BY frequency DESC
LIMIT 10;
