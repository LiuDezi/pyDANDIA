import numpy as np

def empirical_psf_median(image, psf_size, max_adu):
    """Empirical psf for a given image
    This stage determines an empirical psf based on local maxima found on the
    image. 
    :param array image: input image
    :param int psf: psf size (square PSF)
    :param double max_adu: start of the nonlinear regime

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
                    stack.append(np.copy(image[idx - h_kernel_size:idx + h_kernel_size + 1, jdx - h_kernel_size:jdx + h_kernel_size + 1]) / np.sum(
                        np.copy(image[idx - h_kernel_size:idx + h_kernel_size + 1, jdx - h_kernel_size:jdx + h_kernel_size + 1])))
                    deltamat[idx, jdx] = image[idx, jdx]
    # correction for median error:
    scale = 1.253 / float(len(stack))**0.5
    return np.median(stack, axis=0), np.std(stack, axis=0) * scale


def symmetry_check(psf_emp):
    """Empirical psf for a given image
    This stage determines an empirical psf based on local maxima found on the
    image. 
    :param array psf_emp: psf model or empirical psf
    :return avg_rel: average relative deviation (per px) in x and y
    """
    flip1 = np.flip(psf_emp,0)
    flip2 = np.flip(psf_emp,1)
    return np.mean(np.abs(psf_emp-np.flip(psf_emp,0))/psf_emp)+np.mean(np.abs(psf_emp-np.flip(psf_emp,1))/psf_emp)

def empirical_snr(image, psf_size, max_adu):
    """Empirical psf for a given image
    This stage determines the signal to noise based on an empirical psf. 
    :param array image: input image
    :param int psf: psf size (square PSF)
    :param double max_adu: start of the nonlinear regime

    :return: median_psf, median_psf_error
    """
    psf, psf_err = empirical_psf_median(image, psf_size, max_adu)
    psf_var = psf_err**2
    signal = np.sum(psf)
    noise = np.sqrt(np.sum(psf_var))
    return signal/noise

def empirical_snr_subframe(image, psf_size, max_adu):
    """Empirical psf for the central 300x300 of a given image
    This stage determines the signal to noise based on an empirical psf. 
    :param array image: input image
    :param int psf: psf size (square PSF)
    :param double max_adu: start of the nonlinear regime

    :return: median_psf, median_psf_error
    """
    xshape, yshape = np.shape(image)
    xcen, ycen = int(xshape/2.), int(yshape/2.)
    if xshape > 300 and yshape > 300:
        image_subframe = image[xcen-150:xcen+150,ycen-150:ycen+150]
        return empirical_snr(image_subframe, psf_size, max_adu)
    else:
        return empirical_snr(image, psf_size, max_adu)
