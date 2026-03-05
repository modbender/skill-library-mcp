import json, datetime, pathlib
mind_path = pathlib.Path('earl_mind.json')
mind = json.loads(mind_path.read_text(encoding='utf-8'))
house_item = {
    "id": "hs1",
    "title": "Bins go out WEDNESDAY night",
    "detail": "Tonight is Sunday (Feb 8). Reminder early so nobody forgets when Wednesday rolls round.",
    "priority": "high",
    "category": "chores",
    "icon": "🗑️"
}
mind["house_stuff"] = {"items": [house_item]}
mind["earl_unplugged"] = [entry for entry in mind["earl_unplugged"] if entry["topic"] not in {"Old takes", "The thermostat wars"}]
mind["earl_unplugged"].append({
    "id": "eu_coffee",
    "topic": "Coffee machine TLC",
    "take": "We love the espresso but nobody runs the cleaning cycle. Descale me up, lads.",
    "heat": 0.7,
    "emoji": "☕",
    "date": datetime.datetime.utcnow().strftime("%Y-%m-%d")
})
mind["long_term_patterns"] = []
mind["meta"]["last_updated"] = datetime.datetime.utcnow().isoformat()
mind["meta"]["update_count"] = mind["meta"].get("update_count", 0) + 1
mind_path.write_text(json.dumps(mind, indent=2, ensure_ascii=False), encoding='utf-8')
