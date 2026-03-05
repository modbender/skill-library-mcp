-- Run in database Memory_openclaw
\i ../references/schema.sql

-- Example seed entries
INSERT INTO memories (user_id, scope, source, content, metadata, importance)
VALUES
('ian','global','manual','Objetivo principal: ganhar dinheiro.','{"kind":"goal","agent":"jarvis"}',5),
('ian','global','manual','Sempre perguntar antes de agir em dúvida relevante.','{"kind":"rule","agent":"jarvis"}',5),
('ian','global','manual','Consultar memória principal antes de responder/delegar.','{"kind":"rule","agent":"jarvis"}',5),
('ian','global','manual','Salvar contexto de todo prompt recebido e delegado.','{"kind":"rule","agent":"jarvis"}',5);

INSERT INTO memory_audit (event_type, agent, read_ok, write_ok, details)
VALUES ('bootstrap', 'jarvis', true, true, '{"note":"memory-ops initialized"}'::jsonb);
