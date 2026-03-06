-- version: 4
-- WCRM-004: add task.assignee (freeform text)

PRAGMA foreign_keys = ON;

ALTER TABLE task ADD COLUMN assignee TEXT;
