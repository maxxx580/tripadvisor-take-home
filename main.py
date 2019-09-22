#!/usr/bin/python3

""" 
Author: Zixiang Ma
Email: ericma0824@gmail.com
Time created: Sept 20 2019

ReadMe

1. Throught Process

This script contains two phases. Phase 1 is meant for data manipulation where files are parsed 
and converted into tuples or dictionary. In phase 2, the script counts the mathching tuple by first 
generating all possible synonyms tuples using DFS and compare to the other list of tuples. 

2. General Assumption

This script assumes that files are resonably large and can be read into an single process application. 

3. Error

The application exit with code 1 on argument parsing error and exit with code 2 on file parsing error. 

4. Dependency

This script is developed using Python 3.7.4

5. How to execute

To run this script, execute command: python3 syns.txt file1.txt file2.txt 
To specify tuple size, execute command python3 syns.txt file1.txt file2.txt 5

"""

import sys, re, argparse
from collections import deque

def build_synonyms_dictionary(path):
    """ This function build a dictionary of synonmys mapping. a line of "jog run sprint" 
    will be converted into three key-value pairs: "jog"->["run", "sprint"], "run"->["jog", "sprint"], 
    and "sprint"->["jog", "run"]
    
    Assumptions are listed below
    1. every line represetns a synonyms group
    2. each word are separated by space
    
    Arguments:
        path {string} -- path of the text file
    
    Returns:
        [dictionary] -- a dictionary containing the synonmys mappings.
    """
    dictionary = {}
    file = open(path, 'r')
    for line in file:
        values = line.lower().replace('\n', '').split(' ')
        for i in range(len(values)):
            dictionary[values[i]] = values[:i] + values[i+1:]        
    file.close()
    return dictionary

def build_tuples_from_file(path, tuple_size):
    """ this function build n size tuples from a file.
    Only alphanumeric are kept from the text file.  
    
    Arguments:
        path {string} -- path to text file
        tuple_size {integer} -- size of the tuples
    
    Returns:
        [list] -- list of tuples built from file
    """
    with open(path, 'r') as file:
        text = file.read().lower()
    cleaned_text_arr = re.sub(r'([^\s\w]|_)+', '', text).split()
    running_queue = deque(cleaned_text_arr[:tuple_size])
    res = [tuple(running_queue)]
    for i in range(tuple_size, len(cleaned_text_arr)):
        running_queue.popleft()
        running_queue.append(cleaned_text_arr[i])
        res.append(tuple(running_queue))
    return res

def generate_synonmys_tuples_recusively(res, path, words, index):
    """ this function generate all possible synonmys tuple using depth first search approach. 
    
    Arguments:
        res {list} -- a list of tuples generated so far.
        path {tuple} -- a tuple being built in progress.
        words {list} -- a list of synonmys group used to build synonmys tuple
        index {integer} -- an index pointing at the location to search for synonmys
    """
    if index == len(words):
        res.append(tuple(path))
        return
    for w in words[index]:
        generate_synonmys_tuples_recusively(res, path + [w], words, index+1)
    return

def build_synonyms_tuples(word_tuples, dictionary):
    """ This function build a list of synonmys tuples
    
    Arguments:
        word_tuples {tuple} -- the original word tuple. 
        dictionary {dictionary} -- dictionary with synonyms mapping.
    
    Returns:
        [list] -- a list of synonmys tuples.
    """
    res, words = [], []
    for word_tuple in word_tuples:
        if word_tuple in dictionary:
            words.append(dictionary[word_tuple] + [word_tuple])
        else:
            words.append([word_tuple])
    generate_synonmys_tuples_recusively(res, [], words, 0)
    return res

def count_mathcing_tuples(plagiarized, source, synonyms):
    """ this function count the matching synonyms tuples between plagiarized and source document. 

    Arguments:
        plagiarized {list} -- a list of tuples representing the document examined for plagiarism. 
        source {list} -- a list of tuples representing the possible plagiarism source
        synonyms {dictionary} -- a dictionary containing sysnonmys mappings

    Returns:
        [integer] -- the number of synonyms tuples of plagiarized found in source
    """
    tuple_match_count = 0
    for tup in plagiarized:
        synonyms_tuples = build_synonyms_tuples(tup, synonyms)
        for synonyms_tuple in synonyms_tuples:
            if synonyms_tuple in source:
                tuple_match_count += 1
    return tuple_match_count

if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('synonyms', type=str,
                        help='path to synonmys text file')
    parser.add_argument('file_plagiarized', type=str,
                        help='path to the file examined for plagiarism')
    parser.add_argument('file_source', type=str,
                        help='path to file of possible plagiarism sources')
    parser.add_argument('tuple_size', type=int, default=3, nargs='?',
                        help='size of tuples used for matching, optional, default to 3.')
    try:
        options = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(1)

    try:
        dictionary = build_synonyms_dictionary(options.synonyms)
        tuple_plagiarized = build_tuples_from_file(options.file_plagiarized, options.tuple_size)
        tuple_source = build_tuples_from_file(options.file_source, options.tuple_size)
    except Exception as e:
        print(e)
        sys.exit(2)

    tuple_match_count = count_mathcing_tuples(tuple_plagiarized, tuple_source, dictionary)
    print("%f%%" % (100 * (tuple_match_count)/float(len(tuple_plagiarized))))