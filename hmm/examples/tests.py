# -*- coding: utf-8 -*-

'''
Created on Nov 13, 2012

@author: GuyZ
'''

import numpy

from hmm.continuous.GMHMM import GMHMM
from hmm.discrete.DiscreteHMM import DiscreteHMM
import os
import sys
from hmm.Parameters import Parameters
from hmm.Path import Path


# file parsing tools as external lib 
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir,os.path.pardir )) 
print parentDir

pathAlignmentDuration = os.path.join(parentDir, 'AlignmentDuration')
if not pathAlignmentDuration in sys.path:
    sys.path.append(pathAlignmentDuration)
    
from Phonetizer import Phonetizer
from MakamScore import loadLyrics
from LyricsWithModels import LyricsWithModels
from Decoder import Decoder
from FeatureExtractor import loadMFCCs


modelDIR = pathAlignmentDuration + '/model/'
HMM_LIST_URI = modelDIR + '/monophones0'
MODEL_URI = modelDIR + '/hmmdefs9gmm9iter'

# parser of htk-build speech model
pathHtkModelParser = os.path.join(parentDir, 'pathHtkModelParser')
sys.path.append(pathHtkModelParser)
from htk_converter import HtkConverter


pathToComposition = '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey/'
# URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/ISTANBUL/safiye/01_Bakmiyor_1_zemin'
URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey/04_Hamiyet_Yuceses_-_Bakmiyor_Cesm-i_Siyah_Feryade/04_Hamiyet_Yuceses_-_Bakmiyor_Cesm-i_Siyah_Feryade'
whichSection = 1

def test_simple():
    n = 2
    m = 2
    d = 2
    pi = numpy.array([0.5, 0.5])
    A = numpy.ones((n,n),dtype=numpy.double)/float(n)
    
    w = numpy.ones((n,m),dtype=numpy.double)
    means = numpy.ones((n,m,d),dtype=numpy.double)
    covars = [[ numpy.matrix(numpy.eye(d,d)) for j in xrange(m)] for i in xrange(n)]
    
    w[0][0] = 0.5
    w[0][1] = 0.5
    w[1][0] = 0.5
    w[1][1] = 0.5    
    means[0][0][0] = 0.5
    means[0][0][1] = 0.5
    means[0][1][0] = 0.5    
    means[0][1][1] = 0.5
    means[1][0][0] = 0.5
    means[1][0][1] = 0.5
    means[1][1][0] = 0.5    
    means[1][1][1] = 0.5    

    gmmhmm = GMHMM(n,m,d,A,means,covars,w,pi,init_type='user',verbose=True)
    
    obs = numpy.array([ [0.3,0.3], [0.1,0.1], [0.2,0.2]])
    
    print "Doing Baum-welch"
    gmmhmm.train(obs,10)
    print
    print "Pi",gmmhmm.pi
    print "A",gmmhmm.A
    print "weights", gmmhmm.w
    print "means", gmmhmm.means
    print "covars", gmmhmm.covars
    
def test_rand():
    gmmhmm,d = makeTestDurationHMM()
    obs = numpy.array((0.6 * numpy.random.random_sample((40,d)) - 0.3), dtype=numpy.double)
    
    print "Doing Baum-welch"
    gmmhmm.train(obs,1000)
    print
    print "Pi",gmmhmm.pi
    print "A",gmmhmm.A
    print "weights", gmmhmm.w
    print "means", gmmhmm.means
    print "covars", gmmhmm.covars
    
def test_discrete():

    ob5 = (3,1,2,1,0,1,2,3,1,2,0,0,0,1,1,2,1,3,0)
    print "Doing Baum-welch"
    
    atmp = numpy.random.random_sample((4, 4))
    row_sums = atmp.sum(axis=1)
    a = atmp / row_sums[:, numpy.newaxis]    

    btmp = numpy.random.random_sample((4, 4))
    row_sums = btmp.sum(axis=1)
    b = btmp / row_sums[:, numpy.newaxis]
    
    pitmp = numpy.random.random_sample((4))
    pi = pitmp / sum(pitmp)
    
    hmm2 = DiscreteHMM(4,4,a,b,pi,init_type='user',precision=numpy.longdouble,verbose=True)
    hmm2.train(numpy.array(ob5*10),100)
    print "Pi",hmm2.pi
    print "A",hmm2.A
    print "B", hmm2.B


def makeTestDurationHMM():
    '''
    generate some random model. 
    '''
    n = 5
    d = 2
    m = 3
    atmp = numpy.random.random_sample((n, n))
    row_sums = atmp.sum(axis=1)
    a = numpy.array(atmp / row_sums[:, numpy.newaxis], dtype=numpy.double)    

    wtmp = numpy.random.random_sample((n, m))
    row_sums = wtmp.sum(axis=1)
    w = numpy.array(wtmp / row_sums[:, numpy.newaxis], dtype=numpy.double)
    
    means = numpy.array((0.6 * numpy.random.random_sample((n, m, d)) - 0.3), dtype=numpy.double)
    covars = numpy.zeros( (n,m,d,d) )
    
    for i in xrange(n):
        for j in xrange(m):
            for k in xrange(d):
                covars[i][j][k][k] = 1    
    
    pitmp = numpy.random.random_sample((n))
    pi = numpy.array(pitmp / sum(pitmp), dtype=numpy.double)

    gmmhmm = GMHMM(n,m,d,a,means,covars,w,pi,init_type='user',verbose=True)
    
    
    return    gmmhmm, d  

def testRand_DurationHMM():
    '''
    test with audio features from real recording, but some random model, not trained model 
    TODO: this might not work. rewrite
    '''
    durGMMhmm,d = makeTestDurationHMM()
    
    durGMMhmm.setALPHA(0.97)
    
    listDurations = [70,30,20,10,20];
    durGMMhmm.setDurForStates(listDurations)
    
    
    observationFeatures = numpy.array((0.6 * numpy.random.random_sample((2,d)) - 0.3), dtype=numpy.double)
#     observationFeatures = loadMFCCs(URIrecordingNoExt)


    durGMMhmm.initDecodingParameters(observationFeatures)
    chiBackPointer, psiBackPointer = durGMMhmm._viterbiForcedDur(observationFeatures)
    
        
#     # test computePhiStar
#     currState = 1
#     currTime = 25
#     phiStar, fromState, maxDurIndex = durGMMhmm.computePhiStar(currTime, currState)
#     print "phiStar={}, maxDurIndex={}".format(phiStar, maxDurIndex)


def loadSmallAudioFragment(lyrics, URIrecordingNoExt, withSynthesis, fromTs=-1, toTs=-1):
    '''
    test duration-explicit HMM with audio features from real recording and htk-loaded model
    asserts it works. no results provided 
    '''
 
     
    htkParser = HtkConverter()
    htkParser.load(MODEL_URI, HMM_LIST_URI)
    lyricsWithModels = LyricsWithModels(lyrics, htkParser, 'False')
     
    observationFeatures = loadMFCCs(URIrecordingNoExt, withSynthesis, fromTs, toTs) #     observationFeatures = observationFeatures[0:1000]
     
    lyricsWithModels.duration2numFrameDuration(observationFeatures, URIrecordingNoExt)
#     lyricsWithModels.printWordsAndStates()
    
    return lyricsWithModels, observationFeatures

def decode(lyricsWithModels, observationFeatures):   
    '''
    same as decoder.decodeAudio() without the parts with WITH_Duration flag.
    '''
    alpha = 0.97
    deviationInSec = 0.1
    ONLY_MIDDLE_STATE=False
    params = Parameters(alpha, ONLY_MIDDLE_STATE, deviationInSec)
    decoder = Decoder(lyricsWithModels, params.ALPHA, params.deviationInSec)
    
    #  decodes
    decoder.hmmNetwork.initDecodingParameters(observationFeatures)
    chiBackPointer, psiBackPointer = decoder.hmmNetwork._viterbiForcedDur(observationFeatures)
    
    # backtrack
    path =  Path(chiBackPointer, psiBackPointer)
    detectedWordList = decoder.path2ResultWordList(path)
         # DEBUG
    
    decoder.lyricsWithModels.printWordsAndStatesAndDurations(decoder.path)
    path.printDurations()
    

    
if __name__ == '__main__':    
    #test_simple()
    # test_rand()
    #test_discrete()
    # testRand_DurationHMM()
    
    withSynthesis = False
    lyrics = loadLyrics(pathToComposition, whichSection, withSynthesis)
    lyricsWithModels, observationFeatures = loadSmallAudioFragment(lyrics,  URIrecordingNoExt, withSynthesis, fromTs=-1, toTs=-1)
    decode(lyricsWithModels, observationFeatures)