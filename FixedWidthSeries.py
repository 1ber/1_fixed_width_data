#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright Humberto Ramos Costa (2024)

import sys, traceback, re, os, itertools
import pandas as  pd
import numpy as np

# TODO - In field signal (None, beggining, end or EBCDIC)

# TODO - Permitir a criação do layout via parâmetros, strings e arquivos

# TODO - Extender as classes do pandera
# TODO - Separar a parte de layout (Cobol) das definições do Pandas

# TODO - Criar automaticamente os parâmetros para read_fwf

# TODO - Multilevel fields

class FixedWidthSeries():

    id_iter=itertools.count()
    ## Absolute, negative, positive
    conversion_digits=  [
          ['0', '}', '{'] 
        , ['1', 'J', 'A'] 
        , ['2', 'K', 'B'] 
        , ['3', 'L', 'C'] 
        , ['4', 'M', 'D'] 
        , ['5', 'N', 'E'] 
        , ['6', 'O', 'F'] 
        , ['7', 'P', 'G'] 
        , ['8', 'Q', 'H'] 
        , ['9', 'R', 'I'] 
    ]

    def __init__(self,
        name: str = None,
        type: type = str,
        start: int = 0,
        width: int = 0,
        decimals: int=0,
        signed: bool=False,
        raw_data: list = None
        ):
        """
        start  -- 1 based (instead of 0), because of Copybook style
                  but 1 will be subtracted when extracting data.
        width -- Include the decimals, so a number in format IIIDD have
                  width=5
        """

        if(name is None):
            self.name='Column_'+str(next(FixedWidthSeries.id_iter))

        else:
            self.name=name
        self.type=type
        self.start=start
        self.width=width
        self.decimals=decimals
        self.signed=signed

        # When i used [] on the headear all the instances
        # point to one list only, so i have to do this
        if(raw_data is None):
            self.raw_data=[]
        else:
            self.raw_data=raw_data

    @property
    def end(self):
        """
        As self.start it's 1 based, but 1 will be subtracted when needed
        """
        return(self.start+self.width)

    def append_raw_data(self, row: str = ''):
        raw_value=row[self.start-1:self.end-1]
        #print(raw_value)
        self.raw_data.append(raw_value)

    def named_values(self, names:list)->str:
        l=[]
        for n in names:
            n=n.lower()
            if( n in list(self.__dict__.keys())):
                l.append(n+' : '+str(self.__dict__[n]) )
            else:
                l.append(n+' : '+str(getattr(self,n)))

        s=', '.join(l)
        return( s )


    def __repr__(self):
        return (__name__+'{'+self.named_values(['Name', 'Type', 'Start','width',
            'End', 'Decimals','Signed'])+'}')

    def replace_decimal_chars(self, series: pd.Series)->pd.Series:
        
        for chars in FixedWidthSeries.conversion_digits:
            if(series.endswith(chars[1])):
                series=series.replace(chars[1],chars[0])
                series='-'+series
            elif(series.endswith(chars[2])):
                series=series.replace(chars[2],chars[0])

        return(series)

    def treat_series(self, series: pd.Series )->pd.Series:
        if(self.type==str):
            if(series.dtype!=str):
                series=series.astype(str)
            series=series.str.strip()

        else:
            
            ## The signed fields use the last char to indicate negative
            ## or positive numbers, - or + signal will generate an wrong
            ## value. maybe a TODO to detect this and turn them into nan
            if(self.signed and series.map(type).eq(str).all()):
                series=series.map(self.replace_decimal_chars)

            series=series.astype(self.type)
            if(self.decimals>0):
                series=series.div(10**self.decimals)
        return(series)