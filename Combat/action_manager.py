class Action:
    def __init__(self, action_type, actor, target, position):
        self.action_type = action_type  # e.g., "move", "attack", "heal"
        self.actor = actor              # Character performing the action
        self.target = target            # Target character (if applicable)
        self.position = position        # Target position (if applicable)

class ActionManger:
    def __init__(self):
        pass

    def validate_action(self, action, actor):
        if action.action_type == "attack":
            actor.do_attack(action.target, action)
