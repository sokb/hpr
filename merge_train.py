#!/usr/bin/env python

import  pickle
import os.path
import sys
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import time
from os import listdir
from os.path import isfile, join, splitext
from scipy.stats.mstats import zscore
from sklearn.decomposition import PCA
np.set_printoptions(threshold='nan')


#pre-made classifiers
from sklearn import cross_validation
from sklearn.naive_bayes import GaussianNB

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def DisplayClassifier():
    t_files_set = False
    path=''
    if (len(sys.argv)==2):
        path = sys.argv[1]
    try:
        os.remove(path+"traindata_merged.p")
    except OSError:
        pass
    try:
        os.remove(path+"annotations_merged.p")
    except OSError:
        pass
    try:
        os.remove(path+"Gaussian_NB_classifier_merged.p")
    except OSError:
        pass
    onlyfiles = [ f for f in listdir(path) if isfile(join(path,f)) ]
    onlyfiles.sort()
    #print onlyfiles
    ann_files = []
    t_files = []
    for file_ in onlyfiles:
        ext = os.path.splitext(file_)
        if ext[1] == '.p' and (ext[0].find('annotations')!=-1):
            ann_files += list(pickle.load( open( path+file_, "rb" ) ))
        elif ext[1] == '.p' and (ext[0].find('traindata')!=-1):
            if t_files_set :
                t_files = np.vstack((t_files, pickle.load( open( path+file_, "rb" ) )))
            else:
                t_files_set = True
                t_files = pickle.load( open( path+file_, "rb" ) )
    pickle.dump(t_files, open(path+"traindata_merged.p","wb+"))
    pickle.dump(ann_files, open(path+"annotations_merged.p","wb+"))
    temp=zscore(t_files)
    gaussian_nb=GaussianNB()
    pca = PCA()
    pca.fit(temp)
    gaussian_nb.fit(temp,ann_files)
    #gaussian_nb.fit(t_files,ann_files)
    pickle.dump( gaussian_nb, open(path+"Gaussian_NB_classifier_merged.p", "wb+" ) )
    print gaussian_nb.class_prior_
    raw_input("Press any key to exit")


if __name__ == '__main__':
    DisplayClassifier()
