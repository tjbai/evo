import random
from typing import Tuple, Optional

from .models import Entity, NeuralEntity

 
class Simpleton(Entity):
    def __init__(self, meta, brain=None) -> None:
        super().__init__(meta)
        self.brain = brain
        self.health = 500
        self.fill = 'black'
        self.rad = 5
    
    def move(self, context) -> Tuple[float, float]:
        self.health -= 1
        
        for entity in context:
            if isinstance(entity, Simpleton): continue
            if self.overlapping(entity): self.health += 500
        
        linear_acc, angular_acc = random.uniform(-10, 10), random.uniform(-20, 20)
        self._update_pos(linear_acc, angular_acc)
        
        return self.x, self.y
    
    def is_alive(self) -> bool:
        return self.health > 0
    
    def reproduce(self) -> Optional[Entity]:
        return None
    
class Food(Entity):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.fill = 'green'
        self.gaze = False
        self.health = 1
    
    def move(self, context) -> Tuple[float, float]:
        for entity in context:
            if isinstance(entity, Food): continue
            if self.overlapping(entity):
                self.health -= 1
                break
                
        return self.x, self.y
    
    def is_alive(self) -> bool:
        return self.health > 0

    def reproduce(self) -> Optional[Entity]:
        if random.uniform(0, 1) < 0.1:
            return Food(meta=self.meta)
    
class NeuralPrey(NeuralEntity):
    pass

class NeuralPredator(NeuralEntity):
    pass