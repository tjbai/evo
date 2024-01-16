import random
import numpy as np
from typing import List, Tuple, Optional 
from dataclasses import dataclass
from collections import defaultdict
from abc import abstractmethod
import tkinter as tk


def clamp(n, nmin, nmax):
    return max(nmin, min(n, nmax))

@dataclass
class CanvasMetainfo:
    canvas: tk.Canvas
    dim: int
    partition_size: int
    verbose: True
    show_health: True

class Entity:
    def __init__(self,
                 meta: CanvasMetainfo,
                 x: float=None,
                 y: float=None,
                 rot: float=None) -> None:
        
        self.meta = meta
        self.gaze = True
        self.fill = 'black'
        self.rad = 2
        
        self.x = x if x is not None else random.uniform(0, meta.dim)
        self.y = y if y is not None else random.uniform(0, meta.dim)
        self.rot = rot if rot is not None else random.uniform(0, 360)
        
        self.linear_vel = 0
        self.angular_vel = 0
    
    def _update_pos(self, linear_acc: float, angular_acc: float) -> None:
        dt = 1e-1
        
        self.linear_vel = clamp(
            self.linear_vel + dt * linear_acc,
            0, 15
        )
        
        self.angular_vel = clamp(
            self.angular_vel + dt * angular_acc,
            -20, 20
        )
        
        self.rot += dt * self.angular_vel 
        self.x += dt * self.linear_vel * np.sin(np.radians(self.rot))
        self.y += dt * self.linear_vel * np.cos(np.radians(self.rot))
        
        self.x = clamp(self.x, 0, self.meta.dim)
        self.y = clamp(self.y, 0, self.meta.dim)
        
    def sq_distance(self, other: 'Entity') -> float:
        return (self.x-other.x)**2 + (self.y-other.y)**2
        
    def overlapping(self, other: 'Entity') -> bool:
        return self.sq_distance(other) < (self.rad+other.rad)**2
    
    @abstractmethod 
    def move(self, context: List['Entity']) -> Tuple[float, float]:
        raise NotImplementedError()
    
    @abstractmethod
    def is_alive(self) -> bool:
        raise NotImplementedError()
    
    @abstractmethod
    def reproduce(self) -> Optional['Entity']:
        raise NotImplementedError()
    
    def __repr__(self) -> str:
        return f'{self.__class__}:{self.x:.2f}:{self.y:.2f}:{self.rot:.2f}'

class State:
    def __init__(self, entities: List[Entity], meta: CanvasMetainfo, reproduction_rate: int = 100)-> None:
        self.entities = entities
        self.meta = meta
        self.reproduction_rate = reproduction_rate
        self.partition = defaultdict(list)
        self.tick_count = 1
        
    def show_neighbors(self, entity: Entity) -> None:
        print(self._get_context(self.partition, entity))
    
    def tick(self) -> None:
        self.tick_count += 1
        
        new_partition = defaultdict(list) 
        for entity in self.entities:
            context = self._get_context(partition=self.partition, entity=entity)
            x, y = entity.move(context=context)
            px, py = x//self.meta.partition_size, y//self.meta.partition_size
            new_partition[(px, py)].append(entity)
           
        new_entities = []
        for entity in self.entities:
            match entity.is_alive():
                case False: continue
                case True: new_entities.append(entity)
                
        self.entities = new_entities
        self.partition = new_partition
        
        if self.tick_count % self.reproduction_rate != 0: return
                
        for entity in self.entities:
            match entity.reproduce():
                case None: continue
                case child: self.entities.append(child)
                
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

class NeuralEntity(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rad = 5
        self.pov_angle = 90
    
    # return list of entities in current pov 
    def _observer_env(self, context: List[Entity]) -> List[Entity]:
        return []