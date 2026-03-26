# Placeholder for sabotage skill logic
# To be implemented in later phases

class Skill:
    def __init__(self, name):
        self.name = name
        self.cooldown = 0

    def activate(self, target):
        pass

class FreezeSkill(Skill):
    def __init__(self):
        super().__init__('Freeze')

class BlindSkill(Skill):
    def __init__(self):
        super().__init__('Blind')

class ExtraHintSkill(Skill):
    def __init__(self):
        super().__init__('Extra Hint')
