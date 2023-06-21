import argparse
import numpy as np
import json

def get_camera_config(filename):
    data = json.load(open(filename))
    camera_id = data["camera_id"]
    t = np.array(data["position"]).reshape(3, 1)
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
    return R, t, param

def get_od_results(filename):
    data = json.load(open(filename))
    res = data["results"][0]
    class_id = res["class_id"]
    bbox = np.array(res["bbox"])
    return class_id, bbox
    
def run(cp, od):
    R, t, param = get_camera_config(cp)
    K = calc_K(*param)
    _, bbox = get_od_results(od)
    u, v = bbox[:2]
    obj_vctr = obj_toward_vector(u, v, R, t, K)
    return obj_vctr, t
    
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

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--camera_pose')
    parser.add_argument('--od_result')
    args = parser.parse_args()
    
    vctr, t = run(args.camera_pose, args.od_result)
    print(vctr)