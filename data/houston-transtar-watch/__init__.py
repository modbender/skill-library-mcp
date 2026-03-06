from .main import RunExternalScript

def setup(bot):
    # This registers the skill instance with the OpenClaw bot
    bot.add_skill(RunExternalScript())

# This makes the class visible to the OpenClaw skill loader
__all__ = ["RunExternalScript", "setup"]
