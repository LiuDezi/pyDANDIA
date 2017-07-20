# -*- coding: utf-8 -*-
"""
Created on Sat Jul 15 14:08:54 2017

@author: rstreet
"""
from os import path
from astropy.io import fits
from astropy.table import Table
from astropy.table import Column

import numpy as np
import collections

def update_a_dictionnary(dictionnary, new_key, new_value):

	new_keys = dictionnary._fields + (new_key,)
	new_dictionnary = collections.namedtuple(dictionnary.__name__, new_keys)
	


	for index,key in enumerate(dictionnary._fields):

		value = getattr(dictionnary, key)
			
		setattr(new_dictionnary, key, value)

	
	setattr(new_dictionnary, new_key, new_value)	
	
	return new_dictionnary



class MetaData:
    """Class defining the data structure produced by the pyDANDIA pipeline
    to hold metadata regarding the reduction of a single dataset, including
    reduction configuration parameters, the data inventory and key measured
    parameters from each stage. 
    """
    
    def __init__(self):
       
	# attributes = [astropy.header,astropy.Table]
			
        self.data_architecture = [None,None]
        self.reduction_parameters = [None,None]
        self.headers_summary = [None,None]
        self.data_inventory = [None,None]


    
	
    def create_metadata_file(self, metadata_directory, metadata_name):
	
        metadata = fits.HDUList()

	data_architecture_header = fits.Header()
	data_architecture_header.update({'NAME':'DATA_ARCHITECTURE'})

	

	metadata_informations = ['output_directory', 'name']
	metadata_values = [metadata_directory, metadata_name]

	names = fits.Column(name = 'keys', format = '20A', array=metadata_informations)
	values = fits.Column(name = 'values', format = '20A', array=metadata_values)	
	
	data_architecture_columns = fits.ColDefs([names, values])
	tbhdu = fits.BinTableHDU.from_columns(data_architecture_columns, header = data_architecture_header )
	


	tbhdu.name = 'DATA_ARCHITECTURE'

	metadata.append(tbhdu)

        metadata.writeto(metadata_directory+metadata_name, overwrite=True)

   	
	
    def load_a_layer_from_file(self, metadata_directory, metadata_name, key_layer):
	
        metadata = fits.open(metadata_directory + metadata_name, mmap=True)

        layer = metadata[key_layer]
	
	header = layer.header
	table = Table(layer.data)
	
        setattr(self, key_layer, [header, table])

    def save_a_layer_to_file(self, metadata_directory, metadata_name, key_layer):

	layer = getattr(self, key_layer)

	update_layer = fits.BinTableHDU(layer[1], header = layer[0] )
	
        metadata = fits.open(metadata_directory + metadata_name, mmap=True)	

	metadata[key_layer] = update_layer

	metadata.writeto(metadata_directory+metadata_name, overwrite=True)
    
    def transform_2D_table_to_dictionary(self, key_layer):
	
	layer = getattr(self, key_layer)

	column_names = layer[1].keys()

	keys = column_names[0]
		
	
	dictionary = collections.namedtuple(key_layer+'_dictionnary', layer[1][keys].data.tolist())
	
	for index,key in enumerate(dictionary._fields):

		setattr(dictionary, key, layer[1][index][1])
		
	return dictionary


    def update_2D_table_with_dictionary(self, key_layer, dictionary):

	layer = getattr(self, key_layer)

	column_names = layer[1].keys()
	keys = column_names[0]

	existing_rows = layer[1][keys].data.tolist()

	for index,key in enumerate(dictionary._fields):
	
		value = getattr(dictionary, key)

		if key in existing_rows:
			
			layer[1][index][1] = value

		else :

			
			layer[1].add_row([key,value])
	
	
    	
    def add_row_to_layer(self, key_layer, new_row):

	layer = getattr(self, key_layer)
	layer[1].add_row(new_row)

    

    def add_column_to_layer(self, key_layer, new_column_name, new_column_data, new_column_format):
	
	layer = getattr(self, key_layer)
	new_column = Column(new_column_data, name = new_column_name, dtype = new_column_format)
	layer[1].add_column(new_column)

	

    def set_pars(self,par_dict):
        
        for key, value in par_dict.items():
            setattr(self,key,value)
    
    def set_reduction_paths(self,red_dir):
        """Method to establish the reduction directory path.  The directory
        basename will also be taken to be the reduction code 
        e.g. ROME-FIELD-01_lsc_doma-1m0-05-fl15_ip
        and this will be used to set the path to the metadata file,
        e.g. ROME-FIELD-01_lsc_doma-1m0-05-fl15_ip_meta.fits
        """
        
        self.red_dir = red_dir
        self.red_code = path.basename(self.red_dir)
        self.metadata_file = path.join(self.red_dir,self.red_code+'_meta.fits')
    
    def write(self):
        """Method to output the reduction metadata in the pyDANDIA
        pipeline-standard multi-extension FITS binary table format. 
        """
        
        hdulist = fits.HDUList()

        level0 = self.get_level0()
        hdulist.append(level0)
        
        level1 = self.get_level1()
        hdulist.append(level1)
        
        level2 = self.get_level2()
        hdulist.append(level2)
        
        level3 = self.get_level3()
        hdulist.append(level3)
        
        level4 = self.get_level4()
        hdulist.append(level4)
        
        hdulist.writeto(self.metadata_file,clobber=True)
        print('Output metadata to '+self.metadata_file)

    def build_hdu(self, data):
        """Method to construct a Primary Header Data Unit from a list of 
        entries of the format:
        list [ self.attribute, keyword, format, comment_string]
        """
        
        hdu = fits.PrimaryHDU()
        for attr, key, keytype, comment in data:
            value = getattr(self,attr)
            if keytype == 'string':
                value = str(value)
            elif keytype == 'int':
                value = int(value)
            elif keytype == 'float':
                value = float(value)
            hdu.header[key] = (value, comment)

        return hdu


    def get_level0(self):
        """Method that defines the FITS header keywords and comments for 
        Level 0 of the pyDANDIA metadata file:
        Dataset description parameters
        """
        
        data = [['field','FIELD', 'string', 'Name of target field'],
                  ['site', 'SITE', '5A', 'Site code'],
                    ['enclosure','DOME', '10A', 'Dome code'],
                    ['telescope','TEL', '20A', 'Telescope'],
                    ['instrument','CAMERA', '20A', 'Instrument'],
                    ['filter','FILTER', '20A', 'Filter'],
                    ['binx','BINX', 'I5', 'Instrument binning factor in x-axis [pix]'],
                    ['biny','BINY', 'I5', 'Instrument binning factor in y-axis [pix]'],
                    ['pixel_scale','PIXSCALE', 'E', 'Pixel scale of instrument [arcsec/pix]'],
                    ]
        
        hdu = self.build_hdu(data)

        return hdu


    def get_level1(self):
        """Method that defines the FITS header keywords and comments for 
        Level 1 of the pyDANDIA metadata file:
        Reduction configuration parameters
        """
        
        data = [[ 'year', 'YEAR', 'int', 'Year of observations'],
                [ 'back_var', 'BACKVAR', 'int', 'Switch for a spatially variable differential background'],
                [ 'coeff2', 'COEFF2', 'float', '' ],
                [ 'coeff3', 'COEFF3', 'float', '' ],
                [ 'datekey', 'DATE-KEY', 'string', 'Name of date keyword in image headers'],
                [ 'deckey', 'DEC-KEY', 'string', 'Name of Declination keyword in image headers'],
                [ 'det_thresh', 'DETTHRS', 'float', 'Detection threshold [image sky sigma]'],
                [ 'diffpro', 'DIFFPRO', 'int', 'Switch for the method of difference image creation'],
                [ 'expfrac', 'EXPFRAC', 'float', 'Fraction of the exposure time to be added to the UTC'],
                [ 'expkey', 'EXP-KEY', 'string', 'Name of exposure time keyword in image header'],
                [ 'filtkey', 'FILT-KEY', 'string', 'Name of filter keyword in image header'],
                [ 'growsatx', 'GROWSATX', 'float', 'Half saturated pixel box size in the x direction [pix]'],
                [ 'growsaty', 'GROWSATY', 'float', 'Half saturated pixel box size in the y direction [pix]'],
                [ 'imagedx', 'IMAGE-DX', 'float', 'Width of image subframe [pix]'],
                [ 'imagedy', 'IMAGE-DY', 'float', 'Height of image subframe [pix]'],
                [ 'imagex1', 'IMAGEX1', 'int', 'Subframe starting pixel in x-axis [pix]'],
                [ 'imagex2', 'IMAGEX2', 'int', 'Subframe end pixel in x-axis [pix]'],
                [ 'imagexmax', 'IMGXMAX', 'int', 'Last pixel of image area in x-axis [pix]'],
                [ 'imagexmin', 'IMGXMIN', 'int', 'First pixel of image area in x-axis [pix]'],
                [ 'imagey1', 'IMAGEY1', 'int', 'Subframe starting pixel in y-axis [pix]'],
                [ 'imagey2', 'IMAGEY2', 'int', 'Subframe end pixel in y-axis [pix]'],
                [ 'imageymax', 'IMGYMAX', 'int', 'Last pixel of image area in y-axis [pix]'],
                [ 'imageymin', 'IMGYMIN', 'int', 'First pixel of image area in y-axis [pix]'],
                [ 'ker_rad', 'KERRAD', 'float', 'Radius of the kernel pixel array [FWHM]'],
                [ 'max_nim', 'MAX-NIM', 'int', 'Maximum number of images to combine for the reference image'],
                [ 'max_sky', 'MAX-SKY', 'float', 'Maximum allowed sky background [counts] for reference image'],
                [ 'min_ell', 'MIN-ELL', 'float', 'Minimum allowed ellipticity for reference image'],
                [ 'obskey', 'OBSTKEY', 'string', 'Name of data type keywork in image header'],
                [ 'obskeyb', 'OBSTBIAS', 'string', 'Obstype entry if image is a bias'],
                [ 'obskeyd', 'OBSTDARK', 'string', 'Obstype entry if image is a dark'],
                [ 'obskeyf', 'OBSTFLAT', 'string', 'Obstype entry if image is a flat'],
                [ 'obskeys', 'OBSTSCI', 'string', 'Obstype entry if image is a science image'],
                [ 'oscanx1', 'OSCANX1', 'int', 'Starting pixel of overscan region in x [pix]'],
                [ 'oscanx2', 'OSCANX2', 'int', 'End pixel of overscan region in x [pix]'],
                [ 'oscany1', 'OSCANY1', 'int', 'Starting pixel of overscan region in y [pix]'],
                [ 'oscany2', 'OSCANY2', 'int', 'End pixel of overscan region in y[pix]'],
                [ 'psf_comp_dist', 'PSFDIST', 'float', 'Minimum separation of PSF neighbour stars [PSF FWHM]'],
                [ 'psf_comp_flux', 'PSFCFLUX', 'float', 'Maximum flux ratio of PSF neighbour stars'],
                [ 'rakey', 'RA-KEY', 'string', 'Name of RA keyword in image header'],
                [ 'subframes_x', 'SUBREGX', 'int', 'Number of image subregions in x-axis'],
                [ 'subframes_y', 'SUBREGY', 'int', 'Number of image subregions in y-axis'],
                [ 'timekey', 'TIME-KEY', 'string', 'Name of exposure timestamp keyword in image header'],
                ]
        
        hdu = self.build_hdu(data)

        return hdu


    def get_level2(self):
        """Method that defines the FITS header keywords and comments for 
        Level 2 of the pyDANDIA metadata file
        Data inventory
        """
        
        level2 = [[0,'IMAGE', '100A', ''],
                  [1, 'FIELD', '100A', ''],
                    [2, 'DATE', '10A', 'UTC'],
                    [3,'TIME', '12A', 'UTC'],
                    [4,'PROCSTAT', '1A', ''],
                    ]
        
        data = np.array(self.inventory)
        table = []
        for col, key, fstr, unit in level2:
            table.append( fits.Column(name=key, format=fstr, 
                                         array=data[:,col], 
                                            unit=unit) )
        
        tbhdu = fits.BinTableHDU.from_columns(table)

        return tbhdu

    def get_level3(self):
        """Method that defines the FITS header keywords and comments for 
        Level 2 of the pyDANDIA metadata file
        Image data parameters (~old trendlog.imred)
        """
        
        level3 = [['image','IMAGE', '100A', ''],
                  [0, 'HJD', 'E', ''],
                    [1, 'EXPTIME', 'E', 's'],
                    [2, 'SKYBKGD', 'E', 'counts'],
                    [3, 'SKYSIG', 'E', 'counts'],
                    [4, 'FWHM', 'E', 'pix'],
                    [5, 'NSTARS', 'I', ''],
                    [None, 'AIRMASS', 'E', ''],
                    [None, 'MOONSEP', 'E', 'degrees'],
                    [None, 'MOONFRAC', 'E', '%'],
                    ]
        image_list = list(self.imred.keys())
        image_list.sort
        data = []
        for image in image_list:
            data.append( self.imred[image] )
        data = np.array(data)
        table = []
        for col, key, fstr, unit in level3:
            if col == 'image':
                table.append( fits.Column(name=key, format=fstr, 
                                         array=np.array(image_list),
                                            unit=unit) )
            elif col != None and col > 0:
                table.append( fits.Column(name=key, format=fstr, 
                                         array=data[:,col],
                                            unit=unit) )
            else:
                table.append( fits.Column(name=key, format=fstr, 
                                         array=np.zeros(len(data[:,0])),
                                            unit=unit) )
        tbhdu = fits.BinTableHDU.from_columns(table)

        return tbhdu
        
    def get_level4(self):
        """Method that defines the FITS header keywords and comments for 
        Level 2 of the pyDANDIA metadata file
        Geometric alignment parameters (~trendlog.gimred)
        """
        
        level1 = [['image','IMAGE', '100A', ''],
                  [0, 'A0', 'E', ''],
                    [1, 'A1', 'E', 's'],
                    [2, 'A2', 'E', 'counts'],
                    [3, 'A3', 'E', 'counts'],
                    [4, 'A4', 'E', 'pix'],
                    [5, 'A5', 'E', ''],
                    [6, 'A6', 'E', ''],
                    [7, 'NSMATCH', 'I', 'degrees'],
                    [8, 'RMSX', 'E', '%'],
                    [9, 'RMSY', 'E', '%'],
                    ]
        
        image_list = list(self.gimred.keys())
        image_list.sort
        data = []
        for image in image_list:
            data.append( self.gimred[image] )
        data = np.array(data)
        table = []
        for col, key, fstr, unit in level1:
            if col == 'image':
                table.append( fits.Column(name=key, format=fstr, 
                                         array=np.array(image_list),
                                            unit=unit) )
            elif col != None and col > 0:
                table.append( fits.Column(name=key, format=fstr, 
                                         array=data[:,col],
                                            unit=unit) )
            else:
                table.append( fits.Column(name=key, format=fstr, 
                                         array=np.zeros(len(data[:,0])),
                                            unit=unit) )
        tbhdu = fits.BinTableHDU.from_columns(table)

        return tbhdu

    
	