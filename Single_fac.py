from Alpha_func import *

class SingleFactor():
    def __init__(self, data, univ = None, freq = None, ret = None):
        '''
        Configure the research eviroment
        data: the master table (stock_num * date_num) * factor_num
        univ: stock universe
        freq: portfolio rebalancing frequency
        ret:  the forward return of stock you want to predict, 
              could be somthing other than ret, but need to be self defined
        '''
        self.data = data
        
        self.univ = univ if univ is not None else data.index.get_level_values(0)
        
        self.freq = freq if freq is not None else 1
        
        # the column names here is hard coded 
        self.ret = ret if ret is not None else data['adj_close'].groupby('stock').apply(lambda x: DELAY(x,-self.freq)/x-1)
            
    def getFactor(self, facName):        
        return self.data[facName]
    
    

        