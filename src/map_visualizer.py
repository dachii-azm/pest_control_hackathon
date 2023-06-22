from matplotlib import pyplot as plt                                                          
from matplotlib.colors import TABLEAU_COLORS as base_col
from matplotlib.colors import CSS4_COLORS as css_col
import matplotlib.patches as patch
from descartes import PolygonPatch
import numpy as np
import json
import sys

class MapVisualizer:

    def map_visualizer(cdata, blindmap):
        fig, ax = plt.subplot()
        for k, v in blindmap.items():
            cfg = cdata[k]
            pos = cfg["t"]
            plt.plot(pos[0], pos[1], color="black")
        
        ax.set_xlim(0, 13)
        ax.set_ylim(0, 13)
        ax.set_aspect('equal')
        plt.show()


            


