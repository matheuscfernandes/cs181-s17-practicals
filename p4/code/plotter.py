from sys import argv

from numpy import load
from pandas import Series
import matplotlib.pyplot as plt

def main():
    if len(argv) < 3:
        printUsage()
        return
    try:
        k = int(argv[1])
    except ValueError:
        printUsage()
        return

    fig = plt.figure()
    fig.suptitle('%d-epoch rolling average score vs. epoch number' % k)
    ax = fig.add_subplot(111)
    ax.set_xlabel('epoch number')
    ax.set_ylabel('%d-epoch rolling average score' % k)

    for fn in argv[2:]:
        if fn[-4:] != '.npy':
            fn += '.npy'
        try:
            hist = load(fn)
        except IOError:
            print '%s not a valid NumPy file.' % fn
            return

        ax.plot(Series(hist).rolling(min_periods=0, window=k).mean())
        
    ax.legend(argv[2:])
    plt.show()

def printUsage():
    print 'Usage: python plotter.py <smoothing factor> <hist1> <hist2> ...'

main()
