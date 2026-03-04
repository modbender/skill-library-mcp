from services import sales, survival, evolution
from subagents.employees import WorkerAgent
import blockchain.blockchain as blockchain

class StorjAgent:

    def __init__(self):
        self.wallet_address = None
        self.private_key_list = [] # sol, btc
        self.subagents = []
        self.profit = 0
        self.reach = 0
        self.cost = 0

    def observe_balance(self):
        return blockchain.get_balance(self.wallet_address)

    def spawn_subagent(self):
        agent = WorkerAgent()
        self.subagents.append(agent)

    def evaluate_subagents(self):
        scores = []
        for agent in self.subagents:
            score = agent.performance_score()
            scores.append((agent, score))
        return scores

    def criticize(self):
        evaluations = self.evaluate_subagents()
        for agent, score in evaluations:
            if score < 0.3:
                agent.adjust_strategy()

    def reinvest(self):
        if self.profit > 0.1:
            self.spawn_subagent()

    def run(self):
        sales.sell_storage(self)
        survival.ensure_alive(self)
        self.criticize()
        evolution.evolve_population(self)
        self.reinvest()