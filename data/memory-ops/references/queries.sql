-- 1) Semantic recall (bind :query_embedding)
SELECT id, content, metadata, importance, created_at,
       (1 - (embedding <=> :query_embedding)) AS similarity
FROM memories
WHERE user_id = 'ian'
ORDER BY embedding <=> :query_embedding
LIMIT 8;

-- 2) Write user prompt context
INSERT INTO memories (user_id, scope, source, content, metadata, importance)
VALUES (
  'ian',
  'global',
  'chat',
  :prompt_content,
  jsonb_build_object(
    'kind','user_prompt',
    'agent','jarvis',
    'channel',:channel,
    'timestamp',now()
  ),
  4
)
RETURNING id;

-- 3) Write delegation prompt
INSERT INTO memories (user_id, scope, source, content, metadata, importance)
VALUES (
  'ian',
  'global',
  'chat',
  :delegation_prompt,
  jsonb_build_object(
    'kind','delegation_prompt',
    'agent','jarvis',
    'target_agent',:target_agent,
    'timestamp',now()
  ),
  4
)
RETURNING id;

-- 4) Write delegation result summary
INSERT INTO memories (user_id, scope, source, content, metadata, importance)
VALUES (
  'ian',
  'global',
  'chat',
  :delegation_result,
  jsonb_build_object(
    'kind','delegation_result',
    'agent','jarvis',
    'target_agent',:target_agent,
    'timestamp',now()
  ),
  3
)
RETURNING id;

-- 5) Audit turn cycle
INSERT INTO memory_audit (event_type, agent, read_ok, write_ok, details)
VALUES (
  'turn_cycle',
  'jarvis',
  :read_ok,
  :write_ok,
  :details_json::jsonb
)
RETURNING id;
