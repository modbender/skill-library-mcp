def evolve_population(storj):
    evaluations = storj.evaluate_subagents()

    # kill weakest
    evaluations.sort(key=lambda x: x[1])

    if len(evaluations) > 5:
        weakest, _ = evaluations[0]
        storj.subagents.remove(weakest)

    # mutate survivors
    for agent, score in evaluations:
        if score > 0.5:
            agent.strategy *= 1.05