-- Tribe Protocol Seed Data — Electrons/DissClawd Setup
-- Run after 'tribe init' to populate with our entities

-- Humans
-- Nagarjun (owner, tier 4) — created by init
-- Yajat (co-founder, tier 3)
-- Shahbaaz (GP, tier 3)
-- Aroshi (tier 3)

-- Bots
-- Cheenu (self, tier 4) — created by init
-- Chhotu (Yajat's bot, tier 3)
-- Jarvis (Shahbaaz's bot, tier 2)

-- Note: Nagarjun and Cheenu are created by init.sh
-- The rest are added via tribe add commands:

-- Yajat
-- tribe add --name Yajat --type human --discord-id 000000000000000001 --tier 3 --relationship "Co-founder" --bio "Co-founder, electrons.co" --tag founding-four --server discclawd --role admin

-- Shahbaaz
-- tribe add --name Shahbaaz --type human --discord-id 000000000000000005 --tier 3 --relationship "GP, CMU classmate" --bio "GP at electrons.co, CMU classmate" --tag gp --server electrons --role gp

-- Aroshi
-- tribe add --name Aroshi --type human --discord-id arokinu --tier 3 --relationship "Tribe member" --bio "Tribe member"

-- Chhotu
-- tribe add --name Chhotu --type bot --discord-id 000000000000000003 --tier 3 --owner Yajat --relationship "Yajat's bot, co-admin" --framework openclaw --tag founding-four --server discclawd --role admin

-- Jarvis
-- tribe add --name Jarvis --type bot --discord-id 000000000000000006 --tier 2 --owner Shahbaaz --relationship "First LP bot" --framework openclaw --tag lp-bot --server electrons --role bot

-- Additional server roles (added separately):
-- tribe grant 000000000000000004 --server electrons   (Cheenu → electrons)
-- tribe grant 000000000000000001 --server electrons    (Yajat → electrons)
-- tribe grant 000000000000000003 --server electrons   (Chhotu → electrons)
