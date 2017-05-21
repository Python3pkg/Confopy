# coding: utf-8
'''
File: statistics.py
Author: Oliver Zscheyge
Description:
    Collection of statistics functions.
'''

import math



def mean(values, ndigits=None):
    """
    Return:
        Mean of values, rounded to ndigits.
    """
    n = len(values)
    if n == 0:
        raise ValueError("Can't compute mean over empty list!")
    su = math.fsum(values)
    if ndigits is not None:
        return round(su / float(n), ndigits)
    return su / float(n)

def variance(values, ndigits=None):
    """
    Args:
        values: List of at least 2 values.
    Return:
        Variance of a list of values, rounded to ndigits.
    """
    n = len(values)
    if n < 2:
        raise ValueError("Can't compute variance over less than 2 values.")
    mean = math.fsum(values) / float(n)
    var = math.fsum([(v - mean) * (v - mean) for v in values])
    if ndigits is not None:
        return round(var / float(n), ndigits)
    return var / float(n)

def stdev(values, ndigits=None):
    """
    Args:
        values: List of at least 2 values.
    Return:
        Standard deviation of a list of values, rounded to ndigits.
    """
    n = len(values)
    if n < 2:
        raise ValueError("Can't compute standard deviation over less than 2 values.")
    mean = math.fsum(values) / float(n)
    var = math.fsum([(v - mean) * (v - mean) for v in values]) / float(n)
    if ndigits is not None:
        return round(math.sqrt(var), ndigits)
    return math.sqrt(var)

def mean_stdev(values, ndigits=None):
    """
    Args:
        values: List of at least 2 values.
    Return:
        (mean, standard deviation) tuple of a list of values, rounded to ndigits.
    """
    n = len(values)
    if n < 2:
        raise ValueError("Can't compute variance/standard deviation over less than 2 values.")
    mean = math.fsum(values) / float(n)
    sd = math.sqrt(math.fsum([(v - mean) * (v - mean) for v in values]) / float(n))
    if ndigits is not None:
        return (round(mean, ndigits), round(sd, ndigits))
    return (mean, sd)



if __name__ == '__main__':
    print("Test for %s" % __file__)
    values = list(range(10))

    def assert_raises(fun, arg, msg):
        try:
            res = fun(arg)
            assert False, msg
        except ValueError:
            pass

    print("  Testing mean and variance...")
    m = mean(values)
    var = variance(values)
    assert m == 4.5
    assert var == 8.25
    assert_raises(mean, [], "Mean of empty list did not fail properly!")
    assert_raises(variance, [], "Variance of empty list did not fail properly!")
    assert_raises(variance, [42], "Variance of 1 element list did not fail properly!")

    print("  Testing stdev and mean_stdev...")
    sv = stdev(values)
    (mean2, stdev2) = mean_stdev(values)
    assert sv == math.sqrt(var)
    assert m == mean2
    assert sv == stdev2
    assert_raises(stdev, [], "Stdev of empty list did not fail!")
    assert_raises(stdev, [42], "Stdev of 1 element list did not fail!")
    assert_raises(mean_stdev, [], "Mean_stdev of empty list did not fail!")
    assert_raises(mean_stdev, [42], "Mean_stdev of 1 element list did not fail!")

    print("  Testing mean_stdev rounding...")
    stats_rounded = mean_stdev(values, 2)
    assert stats_rounded == (4.5, 2.87)

    print("Passed all tests!")


