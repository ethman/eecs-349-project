import SourceSeparation as nussl


def main():
    # input audio file
    inputName = 'training/hum1__tapping1_0.0.wav'
    signal = nussl.AudioSignal(inputName)

    # Set up and run Repet Original flavor
    repetOrg = nussl.Repet(signal, Type=nussl.RepetType.ORIGINAL)
    repetOrg.Run()

    # Get audio signals and write out to files
    bkgd, fgnd = repetOrg.MakeAudioSignals()
    bkgd.WriteAudioFile('Output/repetOrg_background.wav')
    fgnd.WriteAudioFile('Output/repetOrg_foreground.wav')

    # get beat spectrum
    beatSpec = repetOrg.GetBeatSpectrum()

    # Set up and run Repet Sim
    repetSim = nussl.Repet(signal, Type=nussl.RepetType.SIM)
    repetSim.Run()

    # Get audio signals and write out to files
    bkgd, fgnd = repetSim.MakeAudioSignals()
    bkgd.WriteAudioFile('Output/repetSim_background.wav')
    fgnd.WriteAudioFile('Output/repetSim_foreground.wav')

    # get similarity matrix
    simMat = repetSim.GetSimilarityMatrix()

    # also, FYI this is possible too:
    beatSpec2 = repetSim.GetBeatSpectrum()
    simMat2 = repetOrg.GetSimilarityMatrix()


if __name__ == '__main__':
    main()
