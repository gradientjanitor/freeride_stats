import easyocr
import glob
import copy
import os
import subprocess
import shutil
import sys
import tqdm

from difflib import SequenceMatcher

# use sequencematcher to determine the similarity of two strings
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# given a bounding box returned by easyocr, compute its center of mass
def centroid(b):
    b0 = sum([bb[0] for bb in b]) / 4
    b1 = sum([bb[1] for bb in b]) / 4

    return b0, b1

# compute our keys back into floats for quick dist calc
def key_to_float(key):
    return [float(a) for a in key.split("-")]

# compute a distance between two oints
def dist(x1, x2):
    return (x1[0] - x2[0]) ** 2 + (x1[1] - x2[1]) ** 2

# given the dict of points, find the nearest blob of text and return it.
def find_nearest(points, search_point):
    min_dist = None

    search_coords = key_to_float(search_point)

    for k in points:
        if k == search_point:
            continue

        point = key_to_float(k)

        point_distances = dist(search_coords, point)
        if min_dist is None or point_distances < min_dist:
            min_dist = point_distances
            min_word = points[k]
            min_loc = k

    return min_word, min_loc

# try to cast a value to an int.  return -1 if the cast doesn't work
def try_int_cast(val):
    try:
        return int(val)
    except:
        return -1


def main(video_file):
    try:
        shutil.rmtree("pngs/")
    except:
        print("pngs doesn't exist, how great!")
        
    # make the pngs directory
    os.mkdir("pngs/")

    # run ffmpeg, grabbing 1 frame per second and downsample to 640 x whatever
    subprocess.run(f"ffmpeg -i {video_file} -r 1 -vf scale=640:-1 pngs/out%04d.png".split())

    # instantiate the ocr
    reader = easyocr.Reader(["en"])

    # start writing the csv
    outfile = open(video_file + ".csv", "w")
    outfile.write("frame,output,resistance,cadence\n")
    
    # proceed through the pngs
    i = 0
    for g in tqdm.tqdm(sorted(glob.glob("pngs/*.png"))):
        i += 1
        metrics = {"Output": -1, "Resistance": -1, "Cadence": -1}
    
        # do the ocr
        result = reader.readtext(g)
    
        # parse the points into a dict for quick lookup of positions
        points = dict()
        for r in result:
            bbox, text, confidence = r
            center = centroid(bbox)
            key = "%d-%d" % (center[0], center[1])
            points[key] = text
    
        # search each point to see if we have a match with the stat we want to track
        for k in points:
            for metric in metrics:
                if similar(points[k], metric) > 0.5:
                    possible_metric, location = find_nearest(points, k)
    
                    # if we get a space in the ocr, pull out the int with the max val
                    if " " in possible_metric:
                        possible_metrics = [try_int_cast(p) for p in possible_metric.split()]
                        possible_metric = max(possible_metrics)
                    else:
                        possible_metric = try_int_cast(possible_metric)
    
                    metrics[metric] = possible_metric
    
        # dump out to csv
        outfile.write("%d,%d,%d,%d\n" % (i, metrics["Output"], metrics["Resistance"], metrics["Cadence"]))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: ocr.py (video_file)")
        sys.exit()
    
    main(sys.argv[1])
