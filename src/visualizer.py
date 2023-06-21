from matplotlib import pyplot as plt                                                          
from matplotlib.colors import TABLEAU_COLORS as base_col
from matplotlib.colors import CSS4_COLORS as css_col
import matplotlib.patches as patch
from descartes import PolygonPatch
import numpy as np
import json
import sys

class Visualize:
    
    def read_geojson(filepath):
        with open(filepath) as f:
            src = json.load(f)
            feat = src.get('features')
        return feat
            
    def get_geojson_data(feat):
        prop = feat.get("properties")
        geo = feat.get("geometry")
        return prop, geo
    
    def calc_coordinates_lim(geo):
        coord = np.array(geo["coordinates"][0])
        coord_max = np.max(coord, axis=0)
        coord_min = np.min(coord, axis=0)
        coord_lim = np.array([coord_min, coord_max])
        return coord_lim
    
    def calc_poly_lim(tgt, src):
        if tgt is not None:
            concat = np.concatenate([tgt, src])
            coord_lim = np.array([np.min(concat, axis=0), np.max(concat, axis=0)])
            return coord_lim
        else:
            return src
    
    def visualize_geom(filepath):
        fig, ax = plt.subplots()
        
        feat = Visualize.read_geojson(filepath)
        
        coord_lim = None
        for f in feat:
            prop, geo = Visualize.get_geojson_data(f)
            obj = prop["object"]
            if obj == "camera":
                clim = Visualize.calc_coordinates_lim(geo)
                coord_lim = Visualize.calc_poly_lim(coord_lim, clim)
                poly = PolygonPatch(geo, fill=False, ec='k', alpha=1)
                ax.add_patch(poly)
            if obj == "camera_line":
                lines = geo["coordinates"][0]
                plt.plot([lines[0][0], lines[1][0]], [lines[0][1], lines[1][1]], color="black")
            if obj =="camera_range":
                lines =geo["coordinates"][0]
                plt.plot([lines[0][0], lines[1][0]], [lines[0][1], lines[1][1]], ":", color="black")
                
        ax.set_xlim(coord_lim[0][0], coord_lim[1][0])
        ax.set_ylim(coord_lim[0][1], coord_lim[1][1] + 10)
        ax.set_aspect('equal')
        
        plt.show()
        
if __name__=="__main__":
    Visualize.visualize_geom("/home/dachii/workspace/Project/pest_control_hackathon/camera_dammy.json")
    #Visualize.visualize_geom("/home/dachii/workspace/Project/pest_control_hackathon/tokyo23_.json")