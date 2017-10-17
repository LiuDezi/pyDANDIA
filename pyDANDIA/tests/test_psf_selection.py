# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 20:44:24 2017

@author: rstreet
"""

from os import getcwd, path, remove
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../'))
import logs
import psf_selection
import random
import pipeline_setup
import metadata

cwd = getcwd()
TEST_DIR = path.join(cwd,'data','proc','ROME-FIELD-0002_lsc-doma-1m0-05-fl15_ip')

def test_id_mid_range_stars():
    """Function to test the selection of stars in the reference image, excluding
    the brightest and faintest N% of those detected"""
    
    setup = pipeline_setup.pipeline_setup({'red_dir': TEST_DIR})
    
    metadata = 
    
    log = logs.start_stage_log( cwd, 'test_psf_selection' )
    
    # Generating test catalog with columns:
    # idx x  y  ra  dec  inst_mag inst_mag_err J  Jerr  H Herr   K   Kerr
    nstars = 10
    bright = 16.0
    faint = 23.0
    ref_star_catalog = np.array(nstars,13)
    ref_star_catalog[:,0] = range(0,nstars,1)
    ref_star_catalog[:,1] = random.normalvariate(100.0,100.0)
    ref_star_catalog[:,2] = random.normalvariate(100.0,100.0)
    ref_star_catalog[:,3] = random.normalvariate(17.0*15.0,20.0)
    ref_star_catalog[:,4] = random.normalvariate(-27.0,10.0)
    ref_star_catalog[:,5] = np.arange(bright,faint,(faint-bright)/float(nstars))
    ref_star_catalog[:,6] = 0.005 + ref_star_catalog[:,4]*0.05
    
    psf_stars_idx = np.ones(nstars)
    
    psf_range_thresh = metadata.reduction_parameters[0]['psf_range_thresh']
    
    nstar_cut = int(float(len(nstars)) * psf_range_thresh)
    istart = nstar_cut
    iend = len(ref_star_catalog) - nstar_cut
    
    test_psf_stars_idx = np.ones(nstars)
    test_psf_stars_idx[0:nstar_cut] = 0
    test_psf_stars_idx[-1:(-1*nstar_cut)] = 0
    
    psf_stars_idx = psf_selection.id_mid_range_stars(setup,metadata,log,
                                                     ref_star_catalog,
                                                     psf_stars_idx)
    
    assert psf_stars_idx == test_psf_stars_idx
    