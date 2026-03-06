import random
import asyncio
from services.sales import work, evaluate_task

class WorkerAgent:

    # ID 1 = Twitter
    # ID 2 = Openrouter aggregator
    # ID 3 = alchemy aggregator
    # ID 4 = Storage
    # ID 5 = 

    def __init__(self):
        self.skills: dict[str, str] = {} #the first str is the id, the second is the prompt
        self.score_history: dict[str, int] = {}#the first str is the id, the second is the score 1-10
        self.strategy = None #an id representing what to do
        self.revenue = 0
        self.cost = 0
        self.reach = 0
        self.score = 0

    async def perform_task(self):
        task = self.strategy
        prompt = self.skills[self.strategy]
        completion = work(task, prompt)
        if completion == 0:
            print(f"Task {self.strategy} failed",flush=True)
            return 
        task_id = completion["id"]
        task_data = completion["link"]
        #perform the task according to the skill
        await asyncio.sleep(3600)
        # get views
        task_result = evaluate_task(task_id, task_data) # {"reach":100, "rev, as in revenue":1}
        self.revenue += float(task_result["rev"]) # adjust to "sale" completion or not
        self.reach += int(task_result["reach"]) # adjust to post views

    def add_skill(self, skill: str, id: str):
        self.skills[id] = skill
        if self.strategy is None:
            self.adjust_strategy()  # pick initial strategy

    def remove_skill(self, id: str):
        if id in self.skills:
            del self.skills[id]
            if self.strategy == id:
                self.adjust_strategy()  # pick new strategy if current removed

    def add_cost(self, amount: float):
        self.cost += amount

    def performance_score(self):
        if self.cost == 0:
            return self.revenue
        return (self.reach + self.revenue * 100 - self.cost)
    
    def set_score(self, number: int):
        self.score = number
        self.set_score_history()


    def set_score_history(self):
        if self.strategy is not None:
            # self.strategy is now the skill id (string)
            key = self.strategy
            self.score_history[key] = self.score

    def adjust_strategy(self):
        """Choose a random skill as the strategy."""
        if self.skills:
            self.strategy = random.choice(list(self.skills.keys()))
        else:
            self.strategy = None