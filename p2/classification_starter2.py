## This file provides starter code for extracting features from the xml files and
## for doing some learning.
##
## The basic set-up: 
## ----------------
## main() will run code to extract features, learn, and make predictions.
## 
## extract_feats() is called by main(), and it will iterate through the 
## train/test directories and parse each xml file into an xml.etree.ElementTree, 
## which is a standard python object used to represent an xml file in memory.
## (More information about xml.etree.ElementTree objects can be found here:
## http://docs.python.org/2/library/xml.etree.elementtree.html
## and here: http://eli.thegreenplace.net/2012/03/15/processing-xml-in-python-with-elementtree/)
## It will then use a series of "feature-functions" that you will write/modify
## in order to extract dictionaries of features from each ElementTree object.
## Finally, it will produce an N x D sparse design matrix containing the union
## of the features contained in the dictionaries produced by your "feature-functions."
## This matrix can then be plugged into your learning algorithm.
##
## The learning and prediction parts of main() are largely left to you, though
## it does contain code that randomly picks class-specific weights and predicts
## the class with the weights that give the highest score. If your prediction
## algorithm involves class-specific weights, you should, of course, learn 
## these class-specific weights in a more intelligent way.
##
## Feature-functions:
## --------------------
## "feature-functions" are functions that take an ElementTree object representing
## an xml file (which contains, among other things, the sequence of system calls a
## piece of potential malware has made), and returns a dictionary mapping feature names to 
## their respective numeric values. 
## For instance, a simple feature-function might map a system call history to the
## dictionary {'first_call-load_image': 1}. This is a boolean feature indicating
## whether the first system call made by the executable was 'load_image'. 
## Real-valued or count-based features can of course also be defined in this way. 
## Because this feature-function will be run over ElementTree objects for each 
## software execution history instance, we will have the (different)
## feature values of this feature for each history, and these values will make up 
## one of the columns in our final design matrix.
## Of course, multiple features can be defined within a single dictionary, and in
## the end all the dictionaries returned by feature functions (for a particular
## training example) will be unioned, so we can collect all the feature values 
## associated with that particular instance.
##
## Two example feature-functions, first_last_system_call_feats() and 
## system_call_count_feats(), are defined below.
## The first of these functions indicates what the first and last system-calls 
## made by an executable are, and the second records the total number of system
## calls made by an executable.
##
## What you need to do:
## --------------------
## 1. Write new feature-functions (or modify the example feature-functions) to
## extract useful features for this prediction task.
## 2. Implement an algorithm to learn from the design matrix produced, and to
## make predictions on unseen data. Naive code for these two steps is provided
## below, and marked by TODOs.
##
## Computational Caveat
## --------------------
## Because the biggest of any of the xml files is only around 35MB, the code below 
## will parse an entire xml file and store it in memory, compute features, and
## then get rid of it before parsing the next one. Storing the biggest of the files 
## in memory should require at most 200MB or so, which should be no problem for
## reasonably modern laptops. If this is too much, however, you can lower the
## memory requirement by using ElementTree.iterparse(), which does parsing in
## a streaming way. See http://eli.thegreenplace.net/2012/03/15/processing-xml-in-python-with-elementtree/
## for an example. 

import os
from collections import Counter
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import numpy as np
from scipy import sparse

import util


def extract_feats(ffs, direc="train", global_feat_dict=None):
    """
    arguments:
      ffs are a list of feature-functions.
      direc is a directory containing xml files (expected to be train or test).
      global_feat_dict is a dictionary mapping feature_names to column-numbers; it
      should only be provided when extracting features from test data, so that 
      the columns of the test matrix align correctly.

    returns: 
      a sparse design matrix, a dict mapping features to column-numbers,
      a vector of target classes, and a list of system-call-history ids in order 
      of their rows in the design matrix.
      
      Note: the vector of target classes returned will contain the true indices of the
      target classes on the training data, but will contain only -1's on the test
      data
    """
    fds = [] # list of feature dicts
    classes = []
    ids = [] 
    for datafile in os.listdir(direc):
        # extract id and true class (if available) from filename
        id_str,clazz = datafile.split('.')[:2]
        ids.append(id_str)
        # add target class if this is training data
        try:
            classes.append(util.malware_classes.index(clazz))
        except ValueError:
            # we should only fail to find the label in our list of malware classes
            # if this is test data, which always has an "X" label
            assert clazz == "X"
            classes.append(-1)
        rowfd = {}
        # parse file as an xml document
        tree = ET.parse(os.path.join(direc,datafile))
        # accumulate features
        [rowfd.update(ff(tree)) for ff in ffs]
        fds.append(rowfd)
        
    X,feat_dict = make_design_mat(fds,global_feat_dict)
    return X, feat_dict, np.array(classes), ids


def make_design_mat(fds, global_feat_dict=None):
    """
    arguments:
      fds is a list of feature dicts (one for each row).
      global_feat_dict is a dictionary mapping feature_names to column-numbers; it
      should only be provided when extracting features from test data, so that 
      the columns of the test matrix align correctly.
       
    returns: 
        a sparse NxD design matrix, where N == len(fds) and D is the number of
        the union of features defined in any of the fds 
    """
    if global_feat_dict is None:
        all_feats = set()
        [all_feats.update(fd.keys()) for fd in fds]
        feat_dict = dict([(feat, i) for i, feat in enumerate(sorted(all_feats))])
    else:
        feat_dict = global_feat_dict
        
    cols = []
    rows = []
    data = []        
    for i in xrange(len(fds)):
        temp_cols = []
        temp_data = []
        for feat,val in fds[i].iteritems():
            try:
                # update temp_cols iff update temp_data
                temp_cols.append(feat_dict[feat])
                temp_data.append(val)
            except KeyError as ex:
                if global_feat_dict is not None:
                    pass  # new feature in test data; nbd
                else:
                    raise ex

        # all fd's features in the same row
        k = len(temp_cols)
        cols.extend(temp_cols)
        data.extend(temp_data)
        rows.extend([i]*k)

    assert len(cols) == len(rows) and len(rows) == len(data)
   

    X = sparse.csr_matrix((np.array(data),
                   (np.array(rows), np.array(cols))),
                   shape=(len(fds), len(feat_dict)))
    return X, feat_dict
    

## Here are two example feature-functions. They each take an xml.etree.ElementTree object, 
# (i.e., the result of parsing an xml file) and returns a dictionary mapping 
# feature-names to numeric values.
## TODO: modify these functions, and/or add new ones.
def first_last_system_call_feats(tree):
    """
    arguments:
      tree is an xml.etree.ElementTree object
    returns:
      a dictionary mapping 'first_call-x' to 1 if x was the first system call
      made, and 'last_call-y' to 1 if y was the last system call made. 
      (in other words, it returns a dictionary indicating what the first and 
      last system calls made by an executable were.)
    """
    c = Counter()
    in_all_section = False
    first = True # is this the first system call
    last_call = None # keep track of last call we've seen
    for el in tree.iter():
        # ignore everything outside the "all_section" element
        if el.tag == "all_section" and not in_all_section:
            in_all_section = True
        elif el.tag == "all_section" and in_all_section:
            in_all_section = False
        elif in_all_section:
            if first:
                c["first_call-"+el.tag] = 1
                first = False
            last_call = el.tag  # update last call seen
            
    # finally, mark last call seen
    c["last_call-"+last_call] = 1
    return c

def level_1(tree):
    #all tags
    """
    arguments:
      tree is an xml.etree.ElementTree object
    returns:
      a dictionary mapping 'num_system_calls' to the number of system_calls
      made by an executable (summed over all processes)
    """
    c = Counter()
    in_all_section = False
    for el in tree.iter():
        # ignore everything outside the "all_section" element
        if el.tag == "all_section" and not in_all_section:
            in_all_section = True
        elif el.tag == "all_section" and in_all_section:
            in_all_section = False
        elif in_all_section:
            c['num_system_calls'] += 1
            c[el.tag] += 1
    return c

def level_2(tree):
    #all tags + load_dll attributes
    """
    arguments:
      tree is an xml.etree.ElementTree object
    returns:
      a dictionary mapping 'num_system_calls' to the number of system_calls
      made by an executable (summed over all processes)
    """
    c = Counter()
    in_all_section = False
    for el in tree.iter():
        if el.tag == "all_section" and not in_all_section:
            in_all_section = True
        elif el.tag == "all_section" and in_all_section:
            in_all_section = False
        elif in_all_section:
            c['num_system_calls'] += 1
            if el.tag=="load_dll":
                c['load_dll'] += 1
                for att in el.attrib:
                    c['load_dll'+att+el.attrib[att]]+=1
            else:
                c[el.tag] += 1
    return c

def level_3(tree):
    #all features + 6 attributes
    """
    arguments:
      tree is an xml.etree.ElementTree object
    returns:
      a dictionary mapping 'num_system_calls' to the number of system_calls
      made by an executable (summed over all processes)
    """
    subFeatureTags={"load_dll":1,"vm_protect":5,"vm_write":5,"load_image":100,
        "load_driver":100,"unload_driver":100}
    c = Counter()
    in_all_section = False
    for el in tree.iter():
        if el.tag == "all_section" and not in_all_section:
            in_all_section = True
        elif el.tag == "all_section" and in_all_section:
            in_all_section = False
        elif in_all_section:
            c['num_system_calls'] += 1
            c[el.tag] += 1
            if el.tag in subFeatureTags:
                for att in el.attrib:
                    c[el.tag+att+el.attrib[att]]+=subFeatureTags[el.tag]        
    return c

def level_4(tree):
    #all features + 14 attributes
    """
    arguments:
      tree is an xml.etree.ElementTree object
    returns:
      a dictionary mapping 'num_system_calls' to the number of system_calls
      made by an executable (summed over all processes)
    """
    subFeatureTags={"load_dll":1,"vm_protect":5,"vm_write":5,"load_image":1000,
        "load_driver":1000,"unload_driver":1000,"download_file":10000,"download_file_to_cache":1000,
        "copy_file":1000,"kill_process":1000,"destroy_window":100,"move_file":10000,"start_service":1000,
        "message":100000}
    c = Counter()
    in_all_section = False
    for el in tree.iter():
        if el.tag == "all_section" and not in_all_section:
            in_all_section = True
        elif el.tag == "all_section" and in_all_section:
            in_all_section = False
        elif in_all_section:
            c['num_system_calls'] += 1
            c[el.tag] += 1
            if el.tag in subFeatureTags:
                for att in el.attrib:
                    c[el.tag+att+el.attrib[att]]+=subFeatureTags[el.tag]        
    return c

def feat_counts(tree):
    """
    arguments:
      tree is an xml.etree.ElementTree object
    returns:
      a dictionary mapping 'num_system_calls' to the number of system_calls
      made by an executable (summed over all processes)
    """
    c = Counter()
    in_all_section = False
    for el in tree.iter():
        # ignore everything outside the "all_section" element
        if el.tag == "all_section" and not in_all_section:
            in_all_section = True
        elif el.tag == "all_section" and in_all_section:
            in_all_section = False
        elif in_all_section:
            c['num_system_calls'] += 1
            if el.tag=="load_image":
                c['load_image'] += 1
            elif el.tag=="create_open_file":
                c['create_open_file'] += 1
            elif el.tag=="open_file":
                c['open_file'] += 1
            elif el.tag=="vm_write":
                c['vm_write'] += 1
            elif el.tag=="vm_allocate":
                c['vm_allocate'] += 1
            elif el.tag=="vm_protect":
                c['vm_protect'] += 1
            elif el.tag=="kill_process":
                c['kill_process'] += 1
            elif el.tag=="load_dll":
                c['load_dll'] += 1
            elif el.tag=="create_mutex":
                c['create_mutex'] += 1
            elif el.tag=="set_windows_hook":
                c['set_windows_hook'] += 1
            elif el.tag=="check_for_debugger":
                c['check_for_debugger'] += 1
            elif el.tag=="create_file":
                c['create_file'] += 1
            elif el.tag=="set_file_time":
                c['set_file_time'] += 1
            elif el.tag=="create_window":
                c['create_window'] += 1
            elif el.tag=="destroy_window":
                c['destroy_window'] += 1
            elif el.tag=="enum_window":
                c['enum_window'] += 1
            elif el.tag=="create_process":
                c['create_process'] += 1
            elif el.tag=="open_key":
                c['open_key'] += 1
            elif el.tag=="query_value":
                c['query_value'] += 1
            elif el.tag=="get_system_directory":
                c['create_window'] += 1
            elif el.tag=="find_window":
                c['find_window'] += 1
            elif el.tag=="show_window":
                c['show_window'] += 1
            elif el.tag=="get_file_attributes":
                c['get_file_attributes'] += 1
            elif el.tag=="com_create_instance":
                c['com_create_instance'] += 1
            elif el.tag=="get_username":
                c['get_username'] += 1
            elif el.tag=="set_file_attributes":
                c['set_file_attributes'] += 1
            elif el.tag=="copy_file":
                c['copy_file'] += 1
            elif el.tag=="delete_file":
                c['delete_file'] += 1
            elif el.tag=="open_process":
                c['open_process'] += 1
            elif el.tag=="create_thread_remote":
                c['create_thread_remote'] += 1
            elif el.tag=="sleep":
                c['sleep'] += 1
            elif el.tag=="open_mutex":
                c['open_mutex'] += 1
            elif el.tag=="get_computer_name":
                c['get_computer_name'] += 1
            elif el.tag=="open_scmanager":
                c['open_scmanager'] += 1
            elif el.tag=="create_thread":
                c['create_thread'] += 1
            elif el.tag=="get_host_by_name":
                c['get_host_by_name'] += 1
            elif el.tag=="connect":
                c['connect'] += 1
            elif el.tag=="create_thread_remote":
                c['create_thread_remote'] += 1
            elif el.tag=="create_socket":
                c['create_socket'] += 1
            elif el.tag=="open_url":
                c['open_url'] += 1
            elif el.tag=="enum_processes":
                c['enum_processes'] += 1
    return c


## The following function does the feature extraction, learning, and prediction
def main():
    train_dir = "train"
    test_dir = "test"
    outputfile = "mypredictions.csv"  # feel free to change this or take it as an argument
    
    # TODO put the names of the feature functions you've defined above in this list
    ffs = [first_last_system_call_feats, level_4]
    
    # extract features
    print "extracting training features..."
    X_train,global_feat_dict,t_train,train_ids = extract_feats(ffs, train_dir)
    print "done extracting training features"
    print
    
    # TODO train here, and learn your classification parameters
    print "learning..."
    learned_W = np.random.random((len(global_feat_dict),len(util.malware_classes)))
    print "done learning"
    print
    
    # get rid of training data and load test data
    del X_train
    del t_train
    del train_ids
    print "extracting test features..."
    X_test,_,t_ignore,test_ids = extract_feats(ffs, test_dir, global_feat_dict=global_feat_dict)
    print "done extracting test features"
    print
    
    # TODO make predictions on text data and write them out
    print "making predictions..."
    preds = np.argmax(X_test.dot(learned_W),axis=1)
    print "done making predictions"
    print
    
    print "writing predictions..."
    util.write_predictions(preds, test_ids, outputfile)
    print "done!"

if __name__ == "__main__":
    main()
    