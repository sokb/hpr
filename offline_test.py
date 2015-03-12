#!/usr/bin/env python
__author__="athanasia sapountzi"

import  warnings, math, pickle, scipy.stats
from gridfit import gridfit
import numpy as np
import scipy.io as sio
import scipy.special
import matplotlib.pyplot as plt
import mytools as mt #DBSCAN function and perquisites are stored here
import sys
import os.path

from os import listdir
from os.path import isfile, join, splitext
from myhog import hog
from scipy.stats.mstats import zscore
from sklearn.decomposition import PCA
from sklearn.naive_bayes import GaussianNB

ccnames =['gray', 'black', 'violet', 'blue', 'cyan', 'rosy', 'orange', 'red', 'green', 'brown', 'yellow', 'gold']
cc  =  ['#808080',  'k',  '#990099', '#0000FF', 'c','#FF9999','#FF6600','r','g','#8B4513','y','#FFD700']
wall_flag = 0
fr_index = 0
z = 0
z_scale= float(5*25) / float(3600)
w_index = 1
counter = 0
limit = 40
slot_count = 0
classification_results = []
annotated_data=[]

data_path = ''
annotation_path = ''
class_path = ''
pca_path = ''

gau_classifier = GaussianNB()
pca_obj = PCA()
plt.ion()
super_hogs=[]

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
        
def RepresentsFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def calc_metrics():
    
    global annotated_data, classification_results
    pos = 1
    true_pos = 0.0
    true_neg = 0.0
    false_pos = 0.0
    false_neg = 0.0
    neg = 0
    
    annotated_data = np.array(annotated_data)
    classification_results = np.array(classification_results)
    print annotated_data
    print classification_results
    key_press = raw_input("Press to continue")
    
    for i in range(len(classification_results)):
        if annotated_data[i]==1:
            if classification_results[i]==1:
                true_pos += 1.0
            else:
                false_neg += 1.0
        else:
            if classification_results[i]==1:
                false_pos += 1.0
            else:
                true_neg += 1.0
    precision = true_pos/(true_pos + false_pos)
    recall = true_pos/(true_pos + false_neg)
    accuracy = (true_pos + true_neg)/(true_pos + false_pos + true_neg + false_neg)
    print "Precision : {0}".format(precision)
    print "Recall : {0}".format(recall)
    print "Accuracy : {0}".format(accuracy)
    input ("Press any key to exit")
    return
def offline_test():

    global wall_flag , wall , fr_index ,  intens ,w_index,phi,sampling
    global phi, z, zscale, gau_classifier,timewindow , wall_cart,ax,fig1, kat
    global data_path, class_path, pca_path, pca_obj
    global classification_results, super_hogs, slot_count, limit, annotated_data
    
    
    print "###################################"
    print "offline_test.py : test classifier from data file"
    print "For non interactive input run as follows : "
    print ">python offline_test.py <data_file_path> <annotation_data> <classifier_path> <pca_object_path> <timewindow> <frames for walls>"
    print "You gave {0} arguments".format(len(sys.argv))
    print "##################################"
    if not (len(sys.argv)==7):
        print 'set timewindow in frames:'
        timewindow=input()
        print 'set max frames for wall settting'
        wall_end=input()
        print 'set maximum range'
        range_limit=input()
        filename=input('Enter data file name: ')
        mat=sio.loadmat(filename)
        pca 
        all_data=mat.get('ranges')
        angle_min=mat.get('angle_min')
        angle_max=mat.get('angle_max')
        angle_increment=mat.get('angle_increment')
        mybuffer=all_data[0]
    #INPUT MANAGEMENT    
    else:
        data_path = sys.argv[1]
        if not os.path.isfile(data_path):
            while True :
                try:
                    data_path=raw_input('Enter data file path: ')
                    if os.path.isfile(data_path):
                        break
                    else:
                        print 'File does not exist! Try again!'
                except SyntaxError:
                    print 'Try again'
        
        annotation_path = sys.argv[2]
        if not os.path.isfile(annotation_path):
            while True :
                try:
                    annotation_path=raw_input('Enter annotation file path: ')
                    if os.path.isfile(annotation_path):
                        break
                    else:
                        print 'File does not exist! Try again!'
                except SyntaxError:
                    print 'Try again'
        
        
        class_path = sys.argv[3]
        if not os.path.isfile(class_path):
            while True :
                try:
                    class_path=raw_input('Enter classifier object file path: ')
                    if os.path.isfile(class_path):
                        break
                    else:
                        print 'File does not exist! Try again!'
                except SyntaxError:
                    print 'Try again'
        
        pca_path = sys.argv[4]
        if not os.path.isfile(pca_path):
            while True :
                try:
                    pca_path=raw_input('Enter pca object object file path: ')
                    if os.path.isfile(pca_path):
                        break
                    else:
                        print 'File does not exist! Try again!'
                except SyntaxError:
                    print 'Try again'
        
        timewindow = sys.argv[5]
        while not RepresentsInt(timewindow):
            timewindow=input('Set timewindow in frames: ')
            if RepresentsInt(timewindow):
                break
            else:
                print 'Try again'
                
        wall_end = float(sys.argv[6])
        while not (RepresentsInt(wall_end) or RepresentsFloat(wall_end)):
            wall_end=input('Set frames for wall: ')
            if RepresentsInt(timewindow):
                break
            else:
                print 'Try again'
    #INPUT MANAGEMENT
    
    print "Data File : {0}".format(data_path)
    print "Annotation File : {0}".format(annotation_path)
    print "PCA File : {0}".format(pca_path)
    print "Classifier File : {0}".format(class_path)
    print "Timewindow : {0}".format(timewindow)
    print "Wall Frames : {0}".format(wall_end)
    
    #LOAD FILE TO BE CLASSIFIED
    test_mat = sio.loadmat(data_path)
    all_data = test_mat.get('ranges')
    angle_min = test_mat.get('angle_min')
    angle_max = test_mat.get('angle_max')
    angle_increment = test_mat.get('angle_increment')
    mybuffer = all_data[0]
    range_limit = np.amax(all_data)
    
    
    #LOAD ANNOTATED FILE
    annotated_data = pickle.load( open( annotation_path, "rb" ) )
    
    sampling = np.arange(0,len(mybuffer),2)#apply sampling e.g every 2 steps
    max_index = len(all_data)
    print "Max Index : {0}".format(max_index)
    key_press = raw_input("Press key to continue ")
    em_index = 0
    
    limit = int((max_index-wall_end-(3*int(timewindow)))/int(timewindow))
    
    #LOAD CLASSIFIER and PCA
    gau_classifier = pickle.load(open( class_path, "rb" ))
    pca_obj = pickle.load(open (pca_path, "rb"))
    
    key_press = raw_input("Press any key to cont.")
    phi = np.arange(angle_min,angle_max,angle_increment)[sampling]
    wall = all_data[0]
    
    for wall_index in range(1,int(wall_end)):

        print 'Wall_index : {0}'.format(wall_index)
        wall = all_data[fr_index]
        filter = np.where(wall>=range_limit)
        wall[filter] = range_limit

        if (wall_index<wall_end):
            mybuffer = np.vstack((mybuffer,wall ))  #  add to buffer with size=(wall_index x 720)

    mybuffer = mybuffer[:,sampling]

    wall = np.min(mybuffer, axis=0)-0.1 #select min of measurements
    print "Wall Index : {0}".format(wall_index)
    print "Wall : {0}".format(wall)
    wall_cart=np.array(pol2cart(wall,phi,0) )[:,0:2] #convert to Cartesian
    kat,ax=initialize_plots(wall_cart)

    print 'Walls set...'

    for outer_index in range(wall_index,max_index):
        
        print 'Outer_index : {0}'.format(outer_index)
        ranges = all_data[outer_index]#[ind]
        ranges = ranges[sampling]
        filter = np.where(ranges <= wall) # remove walls
        ranges = ranges[filter]
        theta = phi[filter]
        
        print "Ranges : {0}".format(len(ranges))
        
        if (len(ranges)<3 ):
            print "Empty Scan"
            em_index = em_index+1
            
        if (len(ranges)>=3): #each scan should consist of at least 3 points to be valid
            print "Valid Scan"
            print "Frame Index"
            
            z = z + z_scale
            fr_index=fr_index+1
            C=np.array(pol2cart(ranges,theta,z) ) #convert to Cartesian
            
            if ((int(fr_index) % int(timewindow)) == 1 or fr_index==1):
                mybuffer = C
                
            if (fr_index>1) :
                mybuffer=np.concatenate((mybuffer,C), axis=0 )
            
            if ((int(fr_index) % int(timewindow)) == 0):

                mybuffer = mybuffer[np.where( mybuffer[:,0] > 0.2),:][0] #mishits safety margin
                mybuffer = mybuffer[np.where( mybuffer[:,0] < 5),:][0]#ignore distant points

                if len(mybuffer>3): #at least 3 points are needed to form a cluster
                    print "Clustering"
                    clustering(mybuffer)
    print "HERE"
    
def pol2cart(r,theta,zed):

    #metatropi kylindrikon syntentagmenon se kartesianes
    x=np.multiply(r,np.cos(theta))
    y=np.multiply(r,np.sin(theta))
    z=np.ones(r.size)*zed
    C=np.array([x,y,z]).T
    return C


def initialize_plots(wall_cart):
    global fig1

    temp=plt.figure()
    plot2d = temp.add_subplot(111)
    plot2d.set_xlabel('Vertical distance')
    plot2d.set_ylabel('Robot is here')
    plot2d.plot(wall_cart[:,0],wall_cart[:,1])

    fig1=plt.figure()
    plot3d= fig1.gca(projection='3d')
    plot3d.set_xlabel('X - Distance')
    plot3d.set_ylabel('Y - Robot')
    plot3d.set_zlabel('Z - time')

    plt.show()
    return plot2d,plot3d

def clustering(clear_data):

    global cc, ccnames, fig1, slot_count
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    hogs=[]
    colors=[]
    vcl=[] #Valid Cluster Labels
    valid_flag=0 #this flag is only set if we have at least one valid cluster
    Eps, cluster_labels= mt.dbscan(clear_data,3) # DB SCAN
    max_label=int(np.amax(cluster_labels))
    [xi,yi,zi] = [clear_data[:,0] , clear_data[:,1] , clear_data[:,2]]
    fig1.clear()

    #scatter_all(xi,yi,zi,cluster_labels)#optional 3d scatter plot of all clusters

    for k in range(1,max_label+1) :
        filter=np.where(cluster_labels==k)
        if len(filter[0])>40 :
            #ax.scatter(xi[filter],yi[filter], zi[filter], 'z', 30, cc[k%12]) #this can be commented out
            valid_flag=1
            #print 'extracting surface for ',ccnames[k-1],' cluster'
            vcl.append(k)
            colors.append(ccnames[k%12])
            grid=gridfit(yi[filter], zi[filter], xi[filter], 16, 16) #extract surface
            grid=grid-np.amin(grid)
            hogs.append(hog(grid))  #extract hog features
    
    print"Found {0} clusters".format(len(hogs))
    
    if len(hogs)!=0:
        print'len(hogs)!=0'
        slot_count=slot_count+1
        #print 'File : {0}'.format(filename)
        print 'slot count : {0} || limit :{1}'.format(slot_count, limit)
        ha=np.array(slot_count*np.ones(len(clear_data))) #data point -> slot_number
        update_plots(valid_flag,hogs,xi,yi,zi,cluster_labels,vcl)
        fig1.show()
        if slot_count==limit-1 :
            #build_classifier(np.array(all_hogs),np.array(annotations))
            #save_data()
            calc_metrics()
            exit()
        if slot_count>limit:
            calc_metrics()
            print 'EXITING'
            exit()
    print "Slot Count : {0}".format(slot_count)
    print "Limit : {0}".format(limit)                    
    
    
    return valid_flag,hogs,xi,yi,zi,cluster_labels,vcl

def scatter_all(xi,yi,zi,cluster_labels):

    global cc
    fig2 = plt.figure()
    ax2 = fig2.gca(projection='3d')
    ax2.set_xlabel('X - Distance')
    ax2.set_ylabel('Y - Robot')
    ax2.set_zlabel('Z - time')

    max_label=int(np.amax(cluster_labels))

    for k in range(1,max_label+1) :
        filter=np.where(cluster_labels==k)
        if len(filter[0])>40 :
            ax2.scatter(xi[filter],yi[filter], zi[filter], 'z', 30, cc[k%12])

    fig2.pause(0.00001)

def update_plots(flag,hogs,xi,yi,zi,cluster_labels,vcl):

    global kat, fig1, ax, wall_cart, gau_classifier, counter, pca_obj, classification_results
    
    temp=[]
    temp2=np.empty(36)
    
    if flag==1:
        kat.clear()
        kat.plot(wall_cart[:,0],wall_cart[:,1])
        if np.array(hogs).shape==(1,36):
            #BEFORE
            temp = zscore(np.array(hogs)[0])
            #AFTER
            temp2 = np.array(hogs)[0]
        else:
            #BEFORE
            for i in range(0,len(hogs)):
                temp.append(zscore(np.array(hogs[i])))
            #AFTER
            temp2 = np.array(hogs)
            print temp2.shape
            
        #AFTER, zscore the array of size <# of clusters> x <#number of features>
        #temp2_zscore = zscore(temp2)
        temp2_zscore = zscore(temp)
        temp2_zscore = pca_obj.transform(temp2_zscore)
        
        results = gau_classifier.predict(temp2_zscore)
        print results
        cnt=0
        for k in vcl:

            filter=np.where(cluster_labels==k)

            [x,y,zed] = [xi[filter] , yi[filter] , zi[filter]]

            if results[cnt]==1:
                kat.scatter(x,y,s=20, c='r')
                ax.scatter(x,y, zed, 'z', 30, c='r') #human
                fig1.add_axes(ax)
                classification_results.append(1)
                
            else:
                kat.scatter(x,y,s=20, c='b')
                ax.scatter(x,y, zed, 'z', 30, c='b') #object
                fig1.add_axes(ax)
                classification_results.append(0)
            cnt=cnt+1
        plt.pause(0.0001)
        key_press = raw_input("Press a key to continue")
        counter=counter+cnt


if __name__ == '__main__':
    offline_test()
