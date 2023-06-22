import argparse
import os
import shutil

def run(img_dir):
    imgs = os.listdir(img_dir)
    for i, img in enumerate(imgs):
        img_path = os.path.join(img_dir, img)
        shutil.move(img_path, os.path.join(img_dir, "{}.jpg".format(str(i))))

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_dir')
    args = parser.parse_args()

    run(args.img_dir)