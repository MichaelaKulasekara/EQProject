import numpy as np
import os

def kmeans(image, k, isVector=False):
    # Flatten the image so that all of the values are in an array
    # If the image is a vector, then do not combine the last dimension
    flattenedImage = image.reshape(-1, image.shape[-1] if isVector else 1)

    centroids, labels, inertia = sklearn.cluster.k_means(flattenedImage, k)
    labelOrder = np.argsort(centroids.sum(axis=1))

    return labelOrder, centroids, labels.reshape(image.shape[:-1] if isVector else image.shape)


def maxargwhere(array, axis=0):
    def func(a):
        x = np.argwhere(a)
        return -1 if len(x) == 0 else x.max()

    return np.apply_along_axis(func, axis, array)


def minargwhere(array, axis=0):
    def func(a):
        x = np.argwhere(a)
        return -1 if len(x) == 0 else x.min()

    return np.apply_along_axis(func, axis, array)


def nearestargwhere(array, index=0, axis=0):
    def func(a):
        x = np.argwhere(a)
        if len(x) == 0:
            return -1

        minIndex = np.abs(x - index).argmin()

        return x[minIndex]

    return np.apply_along_axis(func, axis, array)


def defaultmin(x, default):
    return default if x.size == 0 else x.min()


def cleanPath(path, forwardSlash=True):
    # Replace the path with all forward slashes or back slashes
    # When using os.path.join and other Python utilities, the default os.pathsep is used based on the OS
    # It is very easy to get a mixture of path separators and so this function will fix that and switch forward slash
    # to back slashes or vice versa
    return path.replace('\\', '/') if forwardSlash else path.replace('/', '\\')


def splitext(path):
    # Split a given path into it's basename and file extension
    # This function is similar to os.path.splitext except it resolves issues with multiple periods in the extension.
    # For example, .tar.gz returns the extension as .gz. and not .tar.gz. This function corrects that and will return
    # based on the first period found in the path
    #
    # In addition, if no extension is available in the path, the extension will be returned as an empty string
    # File extensions are case insensitive, so lowercase the extension
    x = path.split(os.extsep, 1)

    return x[0], (os.extsep + x[1].lower()) if len(x) == 2 else (x[0], '')

