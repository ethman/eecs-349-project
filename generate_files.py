import numpy as np
import random
import os
from os.path import join, isfile, splitext
from SourceSeparation import AudioSignal, Constants


def generate_random_files_spectral_swap():
    seedInputFolder = 'seed/'
    bkgndOutputFolder = 'background/'

    foregroundInputFolder = 'foreground/'
    mixtureOutputFolder = 'training/'

    maxFileLength = 10.0  # in seconds

    # make backgrounds
    for file in [f for f in os.listdir(seedInputFolder) if isfile(join(seedInputFolder, f))]:
        if splitext(file)[1] == '.wav':
            try:
                seed = AudioSignal(join(seedInputFolder, file))
                print('Read {}!'.format(file))
            except:
                print('Couldn\'t read {}'.format(file))
                continue

            if seed.SampleRate != Constants.DEFAULT_SAMPLE_RATE:
                print('Skipping {0} because its sample rate isn\'t {1}'.format(
                    seed.FileName, Constants.DEFAULT_SAMPLE_RATE))
                continue

            audioSig = create_looped_file(seed, maxFileLength, file, bkgndOutputFolder)
            swap_stft_values(audioSig, bkgndOutputFolder)

    # add backgrounds and foregrounds
    for fgndFile in [f for f in os.listdir(foregroundInputFolder) if isfile(join(foregroundInputFolder, f))]:
        try:
            fgnd = AudioSignal(join(foregroundInputFolder, fgndFile))
            print('Read {}!'.format(fgndFile))
        except:
            print('Couldn\'t read {}'.format(fgndFile))
            continue

        if fgnd.SampleRate != Constants.DEFAULT_SAMPLE_RATE:
            print('Skipping {0} because its sample rate isn\'t {1}'.format(
                fgnd.FileName, Constants.DEFAULT_SAMPLE_RATE))
            continue

        if len(fgnd) > int(maxFileLength * fgnd.SampleRate):
            fgnd.setLength(int(maxFileLength * fgnd.SampleRate))

        if len(fgnd) < int(maxFileLength * fgnd.SampleRate):
            z = np.zeros((int(maxFileLength * fgnd.SampleRate) - len(fgnd)))
            z = z[:, np.newaxis]
            fgnd.AudioData = np.concatenate((fgnd.AudioData, z))
            fgnd.SignalLength = int(maxFileLength * fgnd.SampleRate)
            fgnd.WriteAudioFile(join(foregroundInputFolder, fgndFile), verbose=True)

        for bkgdFile in next(os.walk(bkgndOutputFolder))[2]:
            combFileName = splitext(fgndFile)[0] + '__' + bkgdFile
            combPath = join(mixtureOutputFolder, combFileName)

            if os.path.exists(combPath):
                print 'Skipping {0} & {1} because they\'re already combined :)'.format(fgndFile, bkgdFile)
                continue

            path = join(bkgndOutputFolder, bkgdFile)
            try:
                bkgd = AudioSignal(path)
                combined = bkgd + fgnd
            except:
                print('Couldn\'t read {}'.format(path))
                continue

            combined.WriteAudioFile(combPath, sampleRate=Constants.DEFAULT_SAMPLE_RATE, verbose=True)

    test_folder = 'mixture_test/'
    percent = 0.1
    all_examples = [f for f in os.listdir(mixtureOutputFolder) if isfile(join(mixtureOutputFolder, f))]
    indices = random.sample(range(len(all_examples)), int(len(all_examples) * percent))
    for i in indices:
        cur = join(mixtureOutputFolder, all_examples[i])
        dest = join(test_folder, all_examples[i])
        os.rename(cur, dest)


def create_looped_file(audioSignal, maxFileLength, fileName, outputFolder):
    maxSamples = int(maxFileLength * audioSignal.SampleRate)

    while len(audioSignal) < maxSamples:
        audioSignal.concat(audioSignal)

    audioSignal.setLength(maxSamples)

    newPath = join(outputFolder, splitext(fileName)[0] + '_0.0' + splitext(fileName)[1])
    audioSignal.WriteAudioFile(newPath)

    return audioSignal


def swap_stft_values(audioSig, outputFolder):
    if audioSig.nChannels != 1:
        raise Exception('File {} not mono!'.format(audioSig.FileName))

    min = 0.025
    max = 0.25
    step = 0.025

    audioSig.STFT()

    path = splitext(audioSig.FileName.split(os.sep)[-1])

    I, J = audioSig.ComplexSpectrogramData.shape
    for num in np.arange(min, max, step):
        fileName = path[0] + '_' + str(num) + path[1]
        outputPath = join(outputFolder, fileName)

        if os.path.exists(outputPath):
            print 'Skipping {} because it exists :)'.format(fileName)
            continue

        for n in range(int(audioSig.ComplexSpectrogramData.size * num)):
            i1 = random.randint(0, I - 1)
            j1 = random.randint(0, J - 1)
            i2 = random.randint(0, I - 1)
            j2 = random.randint(0, J - 1)
            audioSig.ComplexSpectrogramData[i1, j1], audioSig.ComplexSpectrogramData[i2, j2] = \
                audioSig.ComplexSpectrogramData[i2, j2], audioSig.ComplexSpectrogramData[i1, j1]

        audioSig.iSTFT()
        audioSig.WriteAudioFile(outputPath, verbose=True)


        # FftUtils needs debugging!!!
        # win = WindowAttributes(audioSig.SampleRate)
        # imageName = path[0] + '_' + str(num) + '.png'
        # outputPath = join(outputFolder, imageName)
        # FftUtils.PlotStft(audioSig, outputPath, windowAttributes=win, sampleRate=audioSig.SampleRate)


if __name__ == '__main__':
    generate_random_files_spectral_swap()
