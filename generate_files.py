__author__ = 'ethanmanilow'

import scipy.io.wavfile as wav
import numpy as np
import random
import os
from os.path import join, isfile


def main():
    outputFolder = 'Output/'
    inputFolder = 'Input/'
    maxFileLength = 10.0  # in seconds

    for f in [f for f in os.listdir(inputFolder) if isfile(join(inputFolder, f))]:
        inputPath = join(inputFolder, f)
        sample_rate, data = wav.read(inputPath)

        out = None

        # This doesn't yield the best results, make this better.
        for fudge in np.arange(0.1, 1.0, 0.1):
            while True:
                length = int(random.random() * fudge * len(data))

                if out is None:
                    out = np.array(data[0:length])
                else:
                    out = np.concatenate((out, data[0:length]))

                if len(out) >= sample_rate * maxFileLength:
                    break

            outName = f.split('.')[0] + str(fudge) + '.wav'
            outPath = join(outputFolder, outName)
            if out is not None:
                wav.write(outPath, sample_rate, out)


if __name__ == '__main__':
    main()
