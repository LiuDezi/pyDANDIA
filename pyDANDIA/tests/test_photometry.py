# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 14:07:33 2017

@author: rstreet
"""

import os
import sys
cwd = os.getcwd()
sys.path.append(os.path.join(cwd,'../'))
import numpy as np
import logs
import pipeline_setup
import metadata
import photometry
import catalog_utils
import psf
from astropy.table import Table


TEST_DATA = os.path.join(cwd,'data')
TEST_DIR = os.path.join(cwd,'data','proc',
                        'ROME-FIELD-0002_lsc-doma-1m0-05-fl15_ip')

def test_run_psf_photometry():
    """Function to test the PSF-fitting photometry module for a single image"""
    
    setup = pipeline_setup.pipeline_setup({'red_dir': TEST_DIR})
    
    log = logs.start_stage_log( cwd, 'test_photometry' )
    
    reduction_metadata = metadata.MetaData()
    reduction_metadata.load_a_layer_from_file( setup.red_dir, 
                                              'pyDANDIA_metadata.fits', 
                                              'reduction_parameters' )
    reduction_metadata.load_a_layer_from_file( setup.red_dir, 
                                              'pyDANDIA_metadata.fits', 
                                              'images_stats' )

    log.info('Read metadata')
    
    # NOTE: Once stage 2 is complete, the reference image path should be
    # extracted directly from the metadata.
    reduction_metadata.reference_image_path = os.path.join(TEST_DATA, 
                            'lsc1m005-fl15-20170701-0144-e91_cropped.fits')
                            
    image_path = reduction_metadata.reference_image_path
    
    star_catalog_file = os.path.join(TEST_DATA,'star_catalog.fits')
                            
    ref_star_catalog = catalog_utils.read_ref_star_catalog_file(star_catalog_file)
    
    psf_model = psf.get_psf_object('Moffat2D')
    
    xstar = 194.654006958
    ystar = 180.184967041
    psf_size = 8.0
    x_cen = psf_size + (xstar-int(xstar))
    y_cen = psf_size + (ystar-int(ystar))
    psf_params = [ 5807.59961215, x_cen, y_cen, 7.02930822229, 11.4997891585 ]
    
    psf_model.update_psf_parameters(psf_params)

    sky_model = psf.ConstantBackground()
    sky_model.background_parameters.constant = 1345.0

    log.info('Performing PSF fitting photometry on '+os.path.basename(image_path))

    ref_star_catalog = photometry.run_psf_photometry(setup,reduction_metadata,
                                                     log,ref_star_catalog,
                                                     image_path,
                                                     psf_model,sky_model,
                                                     centroiding=True)
    
    assert ref_star_catalog[:,5].max() > 0.0
    assert ref_star_catalog[:,6].max() > 0.0
    assert ref_star_catalog[:,5].max() <= 25.0
    assert ref_star_catalog[:,6].max() <= 10.0
    
    logs.close_log(log)

def test_plot_ref_mag_errors():
    """Function to test the plotting function"""
    
    setup = pipeline_setup.pipeline_setup({'red_dir': TEST_DIR})
    
    reduction_metadata = metadata.MetaData()
    reduction_metadata.load_a_layer_from_file( setup.red_dir, 
                                              'pyDANDIA_metadata.fits', 
                                              'star_catalog' )
   
    idx = reduction_metadata.star_catalog[1]['star_index'].data
    x = reduction_metadata.star_catalog[1]['x_pixel'].data
    y = reduction_metadata.star_catalog[1]['y_pixel'].data
    ra = reduction_metadata.star_catalog[1]['RA_J2000'].data
    dec = reduction_metadata.star_catalog[1]['DEC_J2000'].data
    mag = reduction_metadata.star_catalog[1]['Instr_mag'].data
    merr = reduction_metadata.star_catalog[1]['Instr_mag_err'].data


    ref_star_catalog = []
    
    for i in range(0,len(idx),1):

        ref_star_catalog.append( [idx[i], x[i], y[i], ra[i], dec[i], mag[i], merr[i]] )
        
    ref_star_catalog = np.array(ref_star_catalog)
    
    photometry.plot_ref_mag_errors(setup,ref_star_catalog)
    
    plot_file = os.path.join(setup.red_dir,'ref','ref_image_phot_errors.png')
    
    assert os.path.isfile(plot_file)

if __name__ == '__main__':
    
    test_run_psf_photometry()
    test_plot_ref_mag_errors()