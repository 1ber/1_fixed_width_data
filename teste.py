
from FixedWidthDataFrame import *

def main()->None:
    series=read_copybook_file('series2.cob')
    series.pop(1)
    df=read_fixed_width_file(series, 'teste.txt', ['tpreg',1])
    


if __name__ == '__main__':
    main()