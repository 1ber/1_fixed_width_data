#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright Humberto Ramos Costa (2024)

from FixedWidthSeries import FixedWidthSeries
import sys, traceback, re, os
import pandas as  pd
import numpy as np

def read_fixed_width_file(fixed_width_series, data_file: str=None , 
    filter: list=None, chunksize: int=1000000)->pd.DataFrame:
    """
    filter --- a field and a value to be preserved, if field is providaded
                all rows that don't match it are deleted.
    """
    colspecs=[(s.start-1,s.end-1) for s in fixed_width_series]

    dataframe=pd.concat(pd.read_fwf(data_file, colspecs=colspecs, names=[s.name 
        for s in fixed_width_series], chunksize=chunksize))

    if(filter is not None):
        print(filter)
        for key, value in filter.items():
            print(key,value)
            dataframe=dataframe[dataframe[key]==value]

    for s in fixed_width_series:
        dataframe[s.name]=s.treat_series(dataframe[s.name])

    return(dataframe)

def create_fixed_width_series(start, meta_data):
    #Extracts and convert the name
    name=meta_data[0].lower().replace('-','_')

    #Set the 'default' values
    data_type = str
    width=0
    decimals = 0

    # The signed fields in Copybooks starts with an S
    if( meta_data[2].startswith( 's' ) ):
        signed=True
        meta_data[2]=meta_data[2][1:]
    else:
        signed=False

    # This split will separate the decimal definition
    # If it exists, decimals are declared like S99V99
    # Two integer places and two decimals in this example
    length_metadata=meta_data[2].split('v')
    if( len( length_metadata )>1 ):
        
        g = re.findall("\((\d+)\)", length_metadata[1] ) 
        if( len( g ) > 0 ):
            decimals=int( g[0] )
        else:
            decimals=len( length_metadata[1] ) -1 

    if( length_metadata[0].startswith('9') ):
        number=True
    else:
        number=False
    
    # We deal with two ways of declaring digits
    # 9(4) or 9999 
    g = re.findall("\((\d+)\)", length_metadata[0] ) 
    if( len( g ) > 0 ):
        width=int( g[0] )
    else:
        width=length_metadata[0].count('9')

    width=width+decimals
        
    if( number ):
        if( decimals > 0 ):
            data_type=float 
        else:
            data_type=int

    return(FixedWidthSeries( name, data_type, start, width, decimals, 
        signed ))


def read_copybook_file(copy_book_file: str = None):
    series=[]
    start=1
    for l in open(copy_book_file):

        if( l.startswith( '*>~' ) ):
            continue

        ## The convention is that the names in copybooks are uppercase
        ## but in python and pandas they are in general lowercase
        ## the conversion also brings all the identifiers to a default case
        meta_data = l.lower().split()
        tmp_panda_colum_definitions={}

        ## The metadata must have at lest 3 fields
        if ( len( meta_data )>2 and 'pic' in meta_data ):
            ## Delete the first fields (line number and level)
            while( meta_data[0].isnumeric() ):
                meta_data=meta_data[1:]

            ## When all the 'informational' fields are removed
            ## The second ([1]) fields should be 'pic'
            ## and the third ([2]) must end with a '.' 
            if( meta_data[1]=='pic' and meta_data[2].endswith('.')):
                fixed_width_series=create_fixed_width_series(start, meta_data)
                series.append(fixed_width_series)
                start=start+fixed_width_series.width
    return(series)
    