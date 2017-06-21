"""Convert from .npy to .js dictionaries.

Usage:
    convert.py <input_path> [options]
    convert.py <input_path> <label_path> [options]
    convert.py dir <raw_dir> <label_dir> [options]

Options:
    --transform     Whether or not
    --out=<out>     Directory for output [default: ./data/js]
    --variable=<v>  Name of variable to assign all data [default: data]
"""

import docopt
import glob
import os
import os.path
import numpy as np


def main():
    arguments = docopt.docopt(__doc__)
    input_path = arguments['<input_path>']
    out_dir = arguments['--out']
    variable = arguments['--variable']
    label_path = arguments['<label_path>']

    if arguments['dir']:
        write_clusters_to_js(
            arguments['<raw_dir>'],
            arguments['<label_dir>'],
            arguments['--out'],
            variable)
    else:
        out_path = os.path.join(out_dir, 'output.js')
        write_cluster_to_js(input_path, label_path, out_path, variable)


def write_clusters_to_js(raw_dir: str, label_dir: str, out_dir: str, variable: str):
    """Write all clouds contained in subdirectories from cloud_dir/.

    Hardcoded to use the directory structure generated by label.py

    raw_dir/<drive>/<cloud>/*.npy
    """
    for raw, label in zip(os.listdir(raw_dir), os.listdir(label_dir)):
        drive_dir_raw = os.path.join(raw_dir, raw)
        drive_dir_label = os.path.join(label_dir, label)
        for subdirectory in os.listdir(drive_dir_raw):
            raw_path = os.path.join(drive_dir_raw, subdirectory, '*.npy')
            label_path = os.path.join(drive_dir_label, subdirectory, 'labels.npy')
            if not os.path.exists(label_path):
                continue
            out_path = os.path.join(out_dir, raw, subdirectory, 'output.js')
            write_cluster_to_js(raw_path, label_path, out_path, variable)


def write_cluster_to_js(raw_path: str, label_path: str, out_path: str, variable: str):
    """Write all clusters to js files. Each cloud has its own js file."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    data = {}
    pcs = [np.load(path) for path in sorted(glob.iglob(raw_path))]
    paths, i = list(glob.iglob(raw_path)), 0
    labels = np.load(label_path) if label_path is not None else paths

    if not len(paths):
        print('No files found at %s' % raw_path)

    for path, pc, label in zip(paths, pcs, labels):
        obj_name = os.path.basename(path).replace('.npy', '').replace('.stl', '')
        if label_path is not None:
            M = np.ones((4, pc.shape[0]))
            M[:3, :] = pc.T
            T = label[2: 18].reshape((4, 4))
            s = label[18]
            pc = T.dot(M)[:3, :].T * s
        data[obj_name] = {
            'vertices': [{'x': x, 'y': y, 'z': z} for x, y, z in pc]}
        if label_path is not None:
            data[obj_name]['label'] = int(label[0])

    with open(out_path, 'w') as f:
        f.write('var %s = %s' % (variable, str(data)))
    print(' * [INFO] Finished processing timestep. (saved to ', out_path, ')')


if __name__ == '__main__':
    main()