import numpy as np

def empirical_psf_median(image, psf_size, max_adu):
    """Empirical psf for a given image
    This stage determines an empirical psf based on local maxima found on the
    image. 

    :return: median_psf, median_psf_error
    """

    deltamat = np.zeros(np.shape(image))
    nximg, nyimg = np.shape(image)
    upper = max_adu
    lower = np.median(image) + np.std(image)
    h_kernel_size = int(psf_size / 2)
    stack = []
    for idx in range(psf_size, nximg - psf_size):
        for jdx in range(psf_size, nyimg - psf_size):
            if np.max(image[idx - 1:idx + 2, jdx - 1:jdx + 2]) == image[idx, jdx]:
                if image[idx, jdx] < upper and image[idx, jdx] > lower:
                    stack.append(image[idx - h_kernel_size:idx + h_kernel_size + 1, jdx - h_kernel_size:jdx + h_kernel_size + 1] / np.sum(
                        image[idx - h_kernel_size:idx + h_kernel_size + 1, jdx - h_kernel_size:jdx + h_kernel_size + 1]))
                    deltamat[idx, jdx] = image[idx, jdx]
    # correction for median error:
    scale = 1.253 / float(len(stack))**0.5
    return np.median(stack, axis=0), np.std(stack, axis=0) * scale
