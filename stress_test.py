#!/usr/bin/env python

import os
import sys
import time
from util import load_level


from multiprocessing import Pool, cpu_count


def run_test(path):
    try:
        level = load_level(path)
        return False
    except:
        return True


PREVIEW_COUNT = 100
PREVIEW_THRESHOLD = 1000

if __name__ == "__main__":
    start = time.time()
    with open("test_corpus.txt", "r") as input_file:
        corpus = input_file.readlines()

    paths = []
    for line in corpus:
        path = line.strip()
        if os.path.isdir(path):
            continue
        elif os.path.isfile(path):
            paths.append(path)
        else:
            print "Skipping %s" % path

    pool = Pool(max(cpu_count(), 2))
    if len(paths) > PREVIEW_THRESHOLD:
        sample = paths[:PREVIEW_COUNT]
        remainder = paths[len(sample):]

        est_start = time.time()
        results = pool.map(run_test, sample)
        est_end = time.time()
        per_file = (est_end - est_start)/len(sample)
        estimate = len(remainder) * per_file
        print "Estimated completion time: %s" % time.strftime(
            "%I:%M %p", time.localtime(estimate + time.time()))
        
        results += pool.map(run_test, remainder)
    else:
        results = pool.map(run_test, paths)
        
    end = time.time()
    elapsed = end - start
    print "Took {} seconds to test {} files.".format(elapsed, len(paths))

    failures = []
    for result, path in zip(results, paths):
        if result:
            failures.append(path)

    if failures:
        print " - %s files raised an exception." % len(failures)
        with open("test_failures.txt", "w") as out_file:
            out_file.write("\n".join(failures))
        print " - see test_failures.txt"
