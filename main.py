#!/usr/local/bin/python3

import os
import logging
import argparse
import tkinter as tk
import numpy as np
from typing import List 

from evo import *


logger = logging.getLogger(__name__)

if 'LEVEL' in os.environ:
    logger.setLevel(level=os.environ['LEVEL'])

def draw_objects(meta: CanvasMetainfo, entities: List[Entity]) -> None:
    gaze_length = 10 
    gaze_width = 15
    
    canvas = meta.canvas
    canvas.delete("all")
    
    for i in range(0, meta.dim, meta.partition_size):
        canvas.create_line(i, 0, i, meta.dim, fill='light grey')
        canvas.create_line(0, i, meta.dim, i, fill='light grey')    
    
    for entity in entities:
        x, y, rot, r = entity.x, entity.y, entity.rot, entity.rad
        
        canvas.create_oval(x-r, y-r, 
                           x+r, y+r, 
                           fill=entity.fill, outline=entity.fill)
        
        if meta.verbose:
            canvas.create_text(x+10, y+10, text=f'{x//5}, {y//5}')
            
        if meta.show_health:
            canvas.create_text(x+10, y+10, text=f'H: {entity.health}')
        
        if entity.gaze:
            canvas.create_line(x, y, 
                            x+np.sin(np.radians(rot))*gaze_length, 
                            y+np.cos(np.radians(rot))*gaze_length, 
                            fill=entity.fill)
            
            canvas.create_line(x, y, 
                            x+np.sin(np.radians(rot-gaze_width))*gaze_length, 
                            y+np.cos(np.radians(rot-gaze_width))*gaze_length, 
                            fill=entity.fill)
        
            canvas.create_line(x, y, 
                            x+np.sin(np.radians(rot+gaze_width))*gaze_length, 
                            y+np.cos(np.radians(rot+gaze_width))*gaze_length, 
                            fill=entity.fill)
            
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    
    # entities
    parser.add_argument('--entities', type=list, nargs='+', default=[])
    parser.add_argument('--counts', type=list, nargs='+', default=[])
    
    # meta 
    parser.add_argument('-d', '--dim', type=int, default=800)
    parser.add_argument('-p', '--partition-size', type=int, default=20)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-sh', '--show-health', action='store_true')
    
    args = parser.parse_args()
    assert len(args.counts) == len(args.entities), 'entity <-> count mismatch'
    
    return args

entity_types = {
    'simpleton': Simpleton,
    'food': Food,
    'predator': NeuralPredator,
    'prey': NeuralPrey
}

def main():
    args = parse_args()

    # init tk 
    window = tk.Tk()
    canvas = tk.Canvas(window, width=args.dim, height=args.dim)
    canvas.pack() 
    
    meta = CanvasMetainfo(
        canvas=canvas,
        dim=args.dim,
        partition_size=args.partition_size,
        verbose=args.verbose,
        show_health=args.show_health
    ) 

    entities = []
    for type, _count in zip(args.entities, args.counts):
        count = int(_count)
        assert type in entity_types, f'unsupported entity type: {type}'
        entities.extend([entity_types.get(type) for _ in range(count)])
        logger.debug(f'initialized {count} {type}')
    
    state = State(entities=entities, meta=meta)
    
    # main event loop
    def update():
        draw_objects(meta, state.entities)
        state.tick()
        window.after(10, update)
    
    window.after(10, update)
    window.mainloop()

if __name__ == '__main__':
    main()