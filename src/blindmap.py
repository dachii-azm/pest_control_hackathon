import argparse
import numpy as np
import json
import os
from matplotlib import pyplot as plt                                                          
from matplotlib.colors import TABLEAU_COLORS as base_col
from matplotlib.colors import CSS4_COLORS as css_col
import matplotlib.patches as patch
from descartes import PolygonPatch

def read_camera_config(filename):
    data = json.load(open(filename))["config"]
    cdata = {}
    for d in data:
        dv_id, R, t, param = get_camera_param(d)
        cdict = {"device_id": dv_id, "R": R, "t": t, "param": param}
        #cdata.append(cdict)
        cdata[dv_id] = cdict
    return cdata

def get_camera_param(data):
    dv_id = data["device_id"]
    t = np.array(data["position"])
    rot = data["rotation"]
    roll = Ru(float(rot["roll"]))
    pitch = Re(float(rot["pitch"]))
    yaw = Rn(float(rot["yaw"]))
    R = yaw.dot(pitch).dot(roll)
    #R = R.dot(Re(-90))

    fov = data["fov"]
    w = data["width"]
    h = data["height"]
    param = (fov, w, h)

    return dv_id, R, t, param

def get_od_results(filedir):
    device2inference = {}
    res_list = os.listdir(filedir)
    for l in res_list:
        res_path = os.path.join(filedir, l)
        data = json.load(open(res_path))
        device_id = data["DeviceID"]
        res = data["Inferences"]
        rect = res["inferenceResults"][0]
        bbox = np.array([[rect["Left"], rect["Top"]], [rect["Right"], rect["Top"]]])
        class_id = rect["C"]
        timestamp = res["T"]
        res_dict = {"class_id": class_id, "bbox": bbox, "T": timestamp}
        device2inference[device_id] = res_dict
    return device2inference

def calc_vector(u, v, **kwargs):
    kw = kwargs["kwargs"]
    K = calc_K(*kw["param"])
    obj_vctr = obj_toward_vector(u, v, kw["R"], kw["t"], K)
    return obj_vctr

def run(cp, od):
    cdata = read_camera_config(cp)
    dvc2inf = get_od_results(od)
    blindmap = {}
    camera_range={}
    for k, v in dvc2inf.items():
        device_cfg = cdata[k]
        device_cfg.update(v)
        obj_range = []
        for pos in device_cfg["bbox"]:
            obj_vctr = calc_vector(pos[0], pos[1], kwargs=device_cfg)
            obj_range.append(obj_vctr)
        blindmap[k] = obj_range

    for k, v in cdata.items():
        range_min = calc_vector(0, 0, kwargs=v)
        range_max = calc_vector(640, 0, kwargs=v)
        camera_range[k] = []
        camera_range[k].append(range_min)
        camera_range[k].append(range_max)

    return cdata, blindmap, camera_range

def obj_toward_vector(u, v, R, t, K=None, z=None):
    obj_pos_in_img = np.array([u, v, 1])
    if z is not None:
        obj_pos_in_img = obj_pos_in_img * z
    if K is not None:
        K_inv = np.linalg.inv(K)
        camera_coord = np.dot(K_inv, obj_pos_in_img)
    else:
        camera_coord = obj_pos_in_img
    obj_vctr = np.dot(R, camera_coord)
    return obj_vctr

def Rn(roll):
    r = np.deg2rad(roll)
    return np.array([   [ np.cos(r), 0,  np.sin(r) ],
                        [ 0,         1,  0         ],
                        [-np.sin(r), 0,  np.cos(r) ] ])

def Re(pitch):
    p = np.deg2rad(pitch)
    return np.array([   [1,  0,           0       ],
                        [0,  np.cos(p), -np.sin(p)],
                        [0,  np.sin(p),  np.cos(p)]  ])

def Ru(yaw):
    g = np.deg2rad(yaw)
    return  np.array([  [ np.cos(g),  np.sin(g), 0],
                        [-np.sin(g),  np.cos(g), 0],
                        [0,          0,         1] ])

def calc_K(fov, w, h):
    cx = w / 2.0
    cy = h / 2.0
    fx = 1.0 / (2.0 * np.tan(np.radians(fov) / 2.0)) * w
    fy = fx
    
    K = np.array([
        [fx, 0, cx],
        [0, fx, cy],
        [0, 0, 1],
    ])
    return K

def map_visualizer(cdata, blindmap, camera_range, scale=10):
        fig, ax = plt.subplots()
        for k, v in cdata.items():
            pos = v["t"]
            plt.plot(pos[0], pos[1], '.', color="black", markersize=10)

        area = {}
        for k, v in blindmap.items():
            cfg = cdata[k]
            pos = cfg["t"]
            
            area_line = []
            for vctr in v:
                vctr *= 20
                plt.plot([pos[0], vctr[2]+pos[0]], [pos[1], vctr[0]+pos[1]], color="green", alpha=0.5)
                area_line.append(np.array([[vctr[2]+pos[0], vctr[0]+pos[1]], [pos[0], pos[1]]]))
            area[k] = area_line

            geo = obj_vctr2polygon(pos, v)
            poly = patch.Polygon(geo[:, :2], fc='g', alpha=0.3)
            ax.add_patch(poly)

        area = list(area.values())
        if len(area) >=2:
            insec = intersection(area[0][0], area[1][0])
            insec1 = intersection(area[0][0], area[1][1])
            insec2 = intersection(area[0][1], area[1][1])
            insec3 = intersection(area[0][1], area[1][0])
            insec_poly = np.array([
                insec, insec1, insec2, insec3, insec])
            insec_poly = patch.Polygon(insec_poly, fc='r', alpha=0.8)
            ax.add_patch(insec_poly)
        #intersection = intersection(area, )

        for k, v in camera_range.items():
            cfg = cdata[k]
            pos = cfg["t"]
            for vctr in v:
                vctr *= 20
                plt.plot([pos[0], vctr[2]+pos[0]], [pos[1], vctr[0]+pos[1]], ":", color="black")

        ax.set_xlim(-3, 13)
        ax.set_ylim(-3, 13)
        ax.set_aspect('equal')
        plt.show()

def obj_vctr2polygon(pos, v):
    arr = [
        [pos[0], pos[1]],
        [v[0][2]+pos[0], v[0][0]+pos[1]],
        [v[1][2]+pos[0], v[1][0]+pos[1]]
    ]
    arr = list(arr)
    arr.append(arr[0])
    return np.array(arr)

def intersection(target, source):
    area = np.concatenate([target, source])
    area = np.array(area)
    if len(area) < 4:
        return None
    a, b, c, d = area
    alpha1 = b[0] - a[0]
    beta1 =  b[1] - a[1]
    alpha2 = d[0] - c[0]
    beta2 = d[1] - c[1]
    
    scalar = (alpha1 * beta2 - alpha2 * beta1)
    if scalar == 0:
        return None
    
    #A1 = np.array([[beta2, -alpha2], [beta1, -alpha1]])
    #A2 = np.array([c[0] - a[0], c[1] - a[1]])

    sn = beta2 * (c[0]-a[0]) - alpha2 * (c[1]-a[1])
    return [a[0] + alpha1*sn/scalar, a[1] + beta1*sn/scalar]

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--camera_pose')
    parser.add_argument('--od_result')
    args = parser.parse_args()
    
    cdata, blindmap, camera_range = run(args.camera_pose, args.od_result)
    map_visualizer(cdata, blindmap, camera_range)