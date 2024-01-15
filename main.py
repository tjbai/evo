#!./venv/bin/python3

import argparse
import tkinter as tk
import numpy as np
from typing import List 

from core import Entity, Simpleton, State, CanvasMetainfo, Food

def draw_objects(meta: CanvasMetainfo, entities: List[Entity]) -> None:
    r = 2
    gaze_length = 10 
    gaze_width = 15
    
    canvas = meta.canvas
    canvas.delete("all")
    
    for i in range(0, meta.dim, meta.partition_size):
        canvas.create_line(i, 0, i, meta.dim, fill='light grey')
        canvas.create_line(0, i, meta.dim, i, fill='light grey')    
    
    for entity in entities:
        x, y, rot = entity.x, entity.y, entity.rot
        
        canvas.create_oval(x-r, y-r, 
                           x+r, y+r, 
                           fill=entity.fill, outline=entity.fill)
        
        canvas.create_text(x+10, y+10, text=f'{x//5}, {y//5}')
        
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dim', type=int, default=800)
    parser.add_argument('-p', '--partition-size', type=int, default=12)
    args = parser.parse_args()
    
    window = tk.Tk()
    canvas = tk.Canvas(window, width=args.dim, height=args.dim)
    canvas.pack()
    
    meta = CanvasMetainfo(canvas=canvas, dim=args.dim, partition_size=args.partition_size)
    
    simpletons = [Simpleton(meta=meta) for _ in range(100)]
    food = [Food(meta=meta) for _ in range(50)]
    state = State(entities=simpletons+food, meta=meta)
    
    def update():
        draw_objects(meta, state.entities)
        state.tick()
        window.after(10, update)
    
    window.after(100, update)
    window.mainloop()

if __name__ == '__main__':
    main()