# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 11:43:07 2017

@author: rstreet
"""

from os import getcwd, path
from sys import path as systempath
cwd = getcwd()
systempath.append(path.join(cwd,'../'))
import starfind
import metadata
import stage3
import logs
from astropy.io import fits

cwd = getcwd()
TEST_DATA = path.join(cwd,'data')

def test_star_finder(output=False):
    """Function to test the performance of the starfind function"""
    
    meta = stage3.TmpMeta(TEST_DATA)
    
    log = logs.start_stage_log(meta.log_dir, 'test_star_find')
    
    scidata = fits.getdata(meta.reference_image_path)
    
    sources = starfind.detect_sources(meta,scidata,log)
    
    assert len(sources) == 990
    
    if output == True:
        catalog_file = str(meta.reference_image_path).replace('.fits','_sources.txt')
        sources.write(catalog_file, format='ascii')
        log.info('Output source catalog to '+catalog_file)
        
    logs.close_stage_log(log)
    
if __name__ == '__main__':
    test_star_finder(output=True)