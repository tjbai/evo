import random
import numpy as np
from typing import List, Tuple, Literal, Union
from dataclasses import dataclass
from collections import defaultdict
from abc import abstractmethod
import tkinter as tk


# python needs ADTs
type Lifecycle = Union[Tuple[Literal['live'], Entity], Literal['die']]

@dataclass
class CanvasMetainfo:
    canvas: tk.Canvas
    dim: int
    partition_size: int

class Entity:
    def __init__(self,
                 meta: CanvasMetainfo,
                 x: float = None,
                 y: float = None,
                 rot: float = None) -> None:
        
        self.meta = meta
        self.gaze = True
        self.fill = 'black'
        
        self.x = x if x is not None else random.uniform(0, meta.dim)
        self.y = y if y is not None else random.uniform(0, meta.dim)
        self.rot = rot if rot is not None else random.uniform(0, 360)
        
        self.linear_vel = 0
        self.angular_vel = 0
    
    def _update_pos(self, linear_acc: float, angular_acc: float) -> None:
        dt = 1e-1
        
        self.linear_vel = max(0, self.linear_vel + dt * linear_acc)
        self.angular_vel += dt * angular_acc
        
        self.rot += dt * self.angular_vel 
        self.x += dt * self.linear_vel * np.sin(np.radians(self.rot))
        self.y += dt * self.linear_vel * np.cos(np.radians(self.rot))
        
        self.x = max(self.x, 0)
        self.x = min(self.x, self.meta.dim)
        self.y = max(self.y, 0)
        self.y = min(self.y, self.meta.dim)
    
    @abstractmethod 
    def move(self, context: List['Entity']) -> Tuple[float, float]:
        raise NotImplementedError()
    
    @abstractmethod
    def lifecycle(self, context: List['Entity']) -> Lifecycle:
        raise NotImplementedError()
    
    @abstractmethod
    def reproduce(self) -> 'Entity':
        raise NotImplementedError()
    
    def __repr__(self) -> str:
        return f'{self.__class__}:{self.x:.2f}:{self.y:.2f}:{self.rot:.2f}'

class State:
    def __init__(self, entities, meta: CanvasMetainfo)-> None:
        self.entities = entities
        self.meta = meta
        self.partition = defaultdict(list)
        
    def show_neighbors(self, entity: Entity) -> None:
        print(self._get_context(self.partition, entity))
    
    def tick(self) -> None:
        new_partition = defaultdict(list) 
        for entity in self.entities:
            context = self._get_context(partition=self.partition, entity=entity)
            x, y = entity.move(context=context)
            new_partition[(x//self.meta.partition_size, y//self.meta.partition_size)].append(entity)

        new_entities = []
        for entity in self.entities:
            match entity.lifecycle():
                case 'live', child:
                    new_entities.append(entity)
                    if child is not None: new_entities.append(child)
                case 'die':
                    continue
                case _:
                    raise TypeError()
                
        self.entities = new_entities
        self.partition = new_partition
                
    def _get_context(self, partition: dict, entity: Entity) -> List[Entity]:
        rx, ry = entity.x//self.meta.partition_size, entity.y//self.meta.partition_size
        return list(filter(
            lambda e: e is not Entity,
            partition[(rx-1, ry)] +
            partition[(rx+1, ry)] +
            partition[(rx, ry-1)] +
            partition[(rx, ry+1)] +
            partition[(rx-1, ry-1)] +
            partition[(rx+1, ry+1)] +
            partition[(rx-1, ry+1)] +
            partition[(rx+1, ry-1)] 
        ))
    
class Simpleton(Entity):
    def __init__(self, meta, brain = None):
        super().__init__(meta)
        self.brain = brain
        self.health = 100
        self.fill = 'black'
    
    def move(self, context) -> Tuple[float, float]:
        self._update_pos(random.uniform(-10,10), random.uniform(-20,20))
        return self.x, self.y
    
    def lifecycle(self) -> Lifecycle:
        return 'live'
    
    def reproduce(self) -> Entity:
        return Entity(
            dim=self.dim,
            x=self.x,
            y=self.y,
            brain=self.brain
        )
    
class Food(Entity):
    def __init__(self, meta, x, y) -> None:
        super().__init__(meta)
        self.fill = 'green'
        self.gaze = False
        self.health = 1
    
    def move(self) -> Tuple[float, float]:
        return self.x, self.y
    
    def lifecycle(self) -> Lifecycle:
        if self.health <= 0: return 'die'
        return 'live', (None, self.reproduce())[random.uniform(0, 1) < 0.25]
    
    def reproduce(self) -> Entity:
        d = 1
        return Food(meta=self.meta,
                    x=self.x+d*random.uniform(0,10),
                    y=self.x+d*random.uniform(0,10))