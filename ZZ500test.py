# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 15:04:25 2016

ONLY LONG POSITION

@author: zzw
"""
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
import numpy as np
import pandas as pd
from math import *
from functions import *
from DataImport import *
from getcalendar import calendarSig
from today import sbegin_date

    

'''行业分类'''
indlist={}
industry500listcsv=pd.read_csv('industry500list.csv')
for indid in indcount500.index:
     indlist[indid]=industry500listcsv[industry500listcsv.industryID1==indid].index
#industrytest1listcsv=pd.read_csv('C:\Users\et_test\Desktop\ZZ500 DATA\industrytest1list.csv')
#for indid in indcounttest1.index:
#    indlist[indid]=industrytest1listcsv[industrytest1listcsv.industryID1==indid].index

'''股票池'''
ZZ500=list((pd.read_excel('ZZ500.xlsx'))['secID'])
RidList=list((pd.read_excel('ZZ500.xlsx'))['secID'])


'''
industrytest1list=np.zeros(len(RidList))
for i in range(len(RidList)):
    if RidList[i] in list(industrytest1listcsv['secID']):
        industrytest1list[i]=industrytest1listcsv[industrytest1listcsv.secID==RidList[i]]['industryID1']
'''       
'''对A-ST-CAP500一级行业rank'''
'''
def grouprank(factor):
    factor=pd.Series(np.nan_to_num(factor))
    for indid in indcounttest1.index:
        #print(industrytest1listcsv.industryID1==indid)
        ranked=rank(factor[industrytest1list==indid])
        factor[industrytest1list==indid]=ranked
    return(np.array(factor))
'''
    
'''初始条件'''
booklimit=100000000.0 #总体仓位
refresh_rate=10
Icindexcsv=pd.read_csv('Icindex.csv')
Indreturn=Icindexcsv['0'].pct_change() #指数的收益
Indreturn[0]=0.0

'''产生信号'''  

Volume[Volume==0]=nan
NMIbig=((NMIM+NMIL+NMIXl)/Volume) 
RelativeR=pd.DataFrame(columns=RidList)
rNMIbig=pd.DataFrame(columns=RidList)
mNMIbig=NMIbig.mean(axis=1)

for col in RidList:
    RelativeR[col]=ReturnDf[col]-np.array(Indreturn)
    rNMIbig[col]=NMIbig[col]-mNMIbig

class Sigclass():
    def __init__(self,date):
        cal=calendarSig[calendarSig.calendarDate==date]
        idx=list(cal.index)[0]#得到当日在整个calendar的排次
        
        #self.mom_sig=growthscore(ETA,date) #单因子纵向    
        #self.mom_sig=crossscore1(-KDJ_K+KDJ_J,date) #单因子横向
        '''#换手率-KDJ死叉
        cumturn=(turn)[idx-refresh_rate:idx+1].sum(axis=0)
        for i in range(len(cumturn)):
            if cumturn[i]==0:
                cumturn[i]=nan
        sig=rank(-cumturn)
        #sig1=np.zeros(len(sig))
        t=np.array(KDJ_J.loc[date]<KDJ_K.loc[date]) & np.array(KDJ_J.iloc[idx-1]>KDJ_K.iloc[idx-1])
        sig[t]=np.zeros(len(sig[t]))
        sig=rank(sig)        
        sig[sig<0.9]=np.zeros(len(sig[sig<0.9]))
        self.mom_sig=sig
        '''
        
        
        
        #基本面+换手率
        sig1=standardize(rank(ORGR.loc[date]))+standardize(rank(NPGR.loc[date]))+standardize(rank(ETA.loc[date]))+standardize(ts_rank(ROA,date,252))+standardize(ts_rank(EPS,date,252))+standardize(ts_rank(-PE,date,252))++standardize(ts_rank(-PB,date,252))
        sig1=rank(sig1)
        sig1[rank(sig1)<0.5]=np.zeros(len(sig1[rank(sig1)<0.5]))#剔除基本面得分后50%股票
        
        
        ma=PriceDf[idx-250:idx+1].mean(axis=0)
        cumturn=(turn)[idx-refresh_rate:idx+1].sum(axis=0)
        for i in range(len(cumturn)):
            if cumturn[i]==0:
                cumturn[i]=nan
        sig=rank(-cumturn)
        #temp=(rNMIbig[idx-refresh_rate:idx+1]>0)
        #count=temp.sum(axis=0)
        #cumreturn=RelativeR[idx-refresh_rate/2:idx+1].sum(axis=0)
        #stdreturn=RelativeR[idx-refresh_rate:idx+1].std(axis=0)
        NMIbigdate=NMIbig[idx-refresh_rate:idx+1].sum(axis=0)
        
        tf=NMIbigdate<0 | (PriceDf.loc[date]<ma) | (PriceDf.iloc[idx]<PriceDf.iloc[idx-250])
        tf=np.array(tf)
        sig[tf]=np.zeros(len(sig[tf]))
 
        sig=rank(sig*sig1)#sig1做一次筛选
        sig[sig<0.9]=np.zeros(len(sig[sig<0.9]))#只取前10%股票
        if idx>10:
            self.mom_sig=sig
        else:
            self.mom_sig=sig1
        
        
def getSignal(date):
    sig=Sigclass(date)
    return sig

'''回测'''
class Port():
    def __init__(self,benchmark):
        self.Simu(benchmark)
        if benchmark==False:
            self.summary()
            
    def summary(self):
        '''Long Only Performance'''
        self.annret=(np.nansum(self.PnlVec)/booklimit)*(252.0/len(self.PnlVec))  #annual return..
        self.annrisk=(np.nanstd(self.PnlVec)*np.sqrt(252))/np.mean(self.BookVec)  # annual risk…
        self.SR=self.annret/self.annrisk  # annual sharpe ratio…
        self.annbps=(np.nansum(self.PnlVec)/np.nansum(self.TrdValVec))*(10**4)
        self.maxdrawdown=0
        for i in range(len(self.CumPnlVec)):
            currentdd=(max(self.CumPnlVec[:i+1])-self.CumPnlVec[i])/booklimit
            if currentdd>self.maxdrawdown:
                self.maxdrawdown=currentdd
        print ('summary:')
        print ('risk: '+ str(self.annrisk))
        print ('ret: '+ str(self.annret))
        print ('Sharpe: '+ str(self.SR))
        print ('MaxDrawdown: '+ str(self.maxdrawdown))
        print ('Return/DD: '+str(self.annret/self.maxdrawdown))
        print ('bps: '+str(self.annbps)+'\n')
        
        '''Hedged Performance'''
        self.hannret=(np.nansum(self.HedgedPnlVec)/booklimit)*(252.0/len(self.HedgedPnlVec)) #annual return..
        self.hannrisk=(np.nanstd(self.HedgedPnlVec)*np.sqrt(252))/np.nanmean(self.BookVec)      # annual risk…
        self.hSR=self.hannret/self.hannrisk                    # annual sharpe ratio…
        self.hannbps=(np.nansum(self.HedgedPnlVec)/np.nansum(self.TrdValVec))*(10**4)
        self.hmaxdrawdown=0
        for i in range(len(self.CumPnlVec)):
            currentdd=(max(np.array(self.CumPnlVec[:i+1])-np.array(self.IndCumPnlVec[:i+1]))-(np.array(self.CumPnlVec[i])-np.array(self.IndCumPnlVec[i])))/booklimit
            if currentdd>self.hmaxdrawdown:
                self.hmaxdrawdown=currentdd
        print ('hedged summary(index):')
        print ('risk: '+ str(self.hannrisk))
        print ('ret: '+ str(self.hannret))
        print ('Sharpe: '+ str(self.hSR))
        print ('MaxDrawdown: '+ str(self.hmaxdrawdown))
        print ('Return/DD: '+str(self.hannret/self.hmaxdrawdown))
        print ('bps: '+str(self.hannbps)+'\n')
        
    def Simu(self,benchmark):
        self.start_Pos=np.array([0 for i in range(len(RidList))])
        self.Pnl=np.array([0 for i in range(len(RidList))])
        self.Port_Value=np.array([0 for i in range(len(RidList))])
        self.Trd=np.array([0 for i in range(len(RidList))])
        self.Cumpnl=0.0
        self.IndCumPnl=0.0
        self.PnlVec=[]
        self.HedgedPnlVec=[]
        self.RetVec=[]
        self.BookVec=[]
        self.TrdValVec=[]
        self.CumPnlVec=[]
        self.IndCumPnlVec=[]
        self.secpos={} #每日持仓
        
        mom_sig=np.zeros(len(RidList))
        for i in range(len(RidList)):
            if RidList[i] in ZZ500:
                mom_sig[i]=1
        
        for idx in calendarSig.index:
            date=calendarSig['calendarDate'][idx]
            if idx-1>=0:
                yesday=calendarSig['calendarDate'][idx-1]
            #print(np.nansum(self.Port_Value))
            self.Pnl=self.Port_Value*np.array(ReturnDf.loc[date]) #按照昨天的仓位回测
            self.book=np.nansum(np.abs(self.Port_Value)) #每天开始的booksize
            dailypnl=np.nansum(self.Pnl) #今天的pnl
            inddailypnl=booklimit*np.array(Indreturn)[idx]  ##指数的PNL
            
            self.todayPrc=np.array(PriceDf.loc[date])
            if idx>refresh_rate:
                self.Port_Value=self.tgt_Pos*self.todayPrc#算完pnl后更新净值
            
            self.ret=0.0
            if self.book>0:
                self.ret=dailypnl/self.book
            self.RetVec.append(self.ret)
            self.BookVec.append(self.book)
            self.PnlVec.append(dailypnl)
            self.HedgedPnlVec.append(dailypnl-inddailypnl) #对冲后的每日收益向量
            
            self.IndCumPnl=self.IndCumPnl+inddailypnl
            self.Cumpnl+=dailypnl
            self.IndCumPnlVec.append(self.IndCumPnl) #指数累计收益向量
            self.CumPnlVec.append(self.Cumpnl) #alpha累计收益向量
                        
            '''Dailiy Performance'''
            #print(date)
            #print( 'cumpnl: '+str(self.Cumpnl))
            #print('daily PNL: '+str(dailypnl))
            #print('bookvalue: '+str(self.book))
            #print ('ret:' + str(self.ret)+'\n')
                
            if idx % refresh_rate==0: #N个交易日调仓
                if benchmark==False:
                    if idx-1>=0:
                        sigclass=getSignal(yesday)  ## import sig…..收盘调仓 delay1
                    else:
                        sigclass=getSignal(date)  ## import sig…..收盘调仓
                    mom_sig=np.array(sigclass.mom_sig)
                    #mom_sig=Indneutralize(mom_sig,indlist) #行业中性化
                    
                mom_sig=mom_sig/np.nansum(np.abs(mom_sig)) #权重归一化,zh
                self.Port_Value=booklimit*mom_sig
                self.tgt_Size=self.Port_Value #策略生成信号中每个股票的金额向量
              
                for i in range(len(self.tgt_Size)):
                    self.tgt_Size[i]=min(self.tgt_Size[i],booklimit/10) #最大权重10%
                self.tgt_Pos=np.round((self.tgt_Size/self.todayPrc)/100)*100 #每个股票的股票数向量
                #print(((tgt_Size/self.todayPrc)/100))
                
                '''Adjust the start_pos and volume'''
                #self.start_Pos=(self.start_Pos*np.array(AdjustDf[yesday]))/np.array(AdjustDf[date])         
                #cidx=list(VolumeDf.columns).index(date)
                #self.Volume_rd=np.array(VolumeDf.ix[:,cidx-10:cidx+1])*np.array(AdjustDf.ix[:,cidx-10:cidx+1])
                #self.Volume_rd=self.Volume_rd/np.array(AdjustDf.ix[:,cidx:cidx+1])                        
                #self.tgt_Pos=np.nan_to_num(np.array(self.tgt_Pos))
                self.start_Pos=np.nan_to_num(self.start_Pos)            
                self.Trd=self.tgt_Pos-self.start_Pos            
                #liquidity=np.multiply(np.nanmean(self.Volume_rd,axis=1),0.05)
                #self.Trd=np.array([max(-liquidity[i],min(liquidity[i],self.Trd[i])) for i in range(len(liquidity))])
                self.Trd=np.nan_to_num(self.Trd)
                '''处理停牌'''
                TrdList=isOpen.loc[date]
                TrdList=TrdList[TrdList==1]
                TrdList=list(TrdList.index) 
                for i in range(len(mom_sig)):
                    if RidList[i] not in TrdList:
                        self.tgt_Pos[i]=self.start_Pos[i] #停牌，保持上期持仓
                        
                self.Trd_Val=self.Trd*self.todayPrc #换手交易量
                self.Port_Value=self.tgt_Pos*self.todayPrc
                self.Port_Value=booklimit/np.nansum(self.Port_Value)*self.Port_Value #停牌了权重分配不到位，其他整体放大（还有点偏差，暂时不管）
                dailytrd=np.nansum(np.abs(self.Trd_Val))
                #print ('bps: '+str(dailypnl/dailytrd)+'\n')#margin
                self.TrdValVec.append(dailytrd)
                self.start_Pos=self.tgt_Pos
                mark=self.start_Pos>0
                self.secpos[date]=pd.Series(RidList)[mark]
            
if __name__=="__main__":
    port=Port(False)
    a=port.PnlVec    
    benchmark=Port(True)
    #Volume_rd=port.Volume_rd    
    #Hedged Summary(EqualWeight)
    '''对冲等权'''
    PnlVechedged=np.array(port.PnlVec)-np.array(benchmark.PnlVec)
    b=PnlVechedged
    annret=np.nansum(PnlVechedged/booklimit)*(252.0/len(port.PnlVec))  #annual return..
    annrisk=(np.nanstd(PnlVechedged)*np.sqrt(252))/booklimit  # annual risk…
    SR=annret/annrisk  # annual sharpe ratio…
    maxdrawdown=0#下面算最大回撤
    for i in range(len(port.CumPnlVec)):
        currentdd=(max(np.array(port.CumPnlVec[:i+1])-np.array(benchmark.CumPnlVec[:i+1]))-(np.array(port.CumPnlVec[i])-np.array(benchmark.CumPnlVec[i])))/booklimit
        if currentdd>maxdrawdown:
            maxdrawdown=currentdd
    #annbps=(np.nansum(self.PnlVec)/np.nansum(self.TrdValVec))*(10**4)
    print ('hedged summary(equal weight):')
    print ('risk: '+ str(annrisk))
    print ('ret: '+ str(annret))
    print ('Sharpe: '+ str(SR))
    print ('MaxDrawdown: '+str(maxdrawdown))
    print ('Return/DD: '+str(annret/maxdrawdown)+'\n')
    #print ('bps: '+str(self.annbps)+'\n')
    
    '''模拟盘'''
    cal=calendarSig[calendarSig.calendarDate==sbegin_date]
    idx=list(cal.index)[0]#得到当日在整个calendar的排次
    
    sannret=(np.nansum(port.PnlVec[idx+1:])/booklimit)*(252.0/len(port.PnlVec[idx+1:]))  #annual return..
    sannrisk=(np.nanstd(port.PnlVec[idx+1:])*np.sqrt(252))/np.mean(port.BookVec[idx+1:])  # annual risk…
    sSR=sannret/sannrisk  # annual sharpe ratio…
    #sannbps=(np.nansum(port.PnlVec[idx+1:])/np.nansum(port.TrdValVec[idx+1:]))*(10**4)
    smaxdrawdown=0#下面算最大回撤
    for i in range(idx,len(port.CumPnlVec)):
        currentdd=(max(port.CumPnlVec[idx:i+1])-(port.CumPnlVec[i]))/booklimit
        if currentdd>smaxdrawdown:
            smaxdrawdown=currentdd
    print ('emulation summary:')
    print ('risk: '+ str(sannrisk))
    print ('ret: '+ str(sannret))
    print ('Sharpe: '+ str(sSR))
    print ('MaxDrawdown: '+ str(smaxdrawdown))
    print ('Return/DD: '+str(sannret/smaxdrawdown)+'\n')
    #print ('bps: '+str(sannbps)+'\n')
    
    '''Hedged Performance'''
    shannret=(np.nansum(port.HedgedPnlVec[idx+1:])/booklimit)*(252.0/len(port.HedgedPnlVec[idx+1:])) #annual return..
    shannrisk=(np.nanstd(port.HedgedPnlVec[idx+1:])*np.sqrt(252))/np.nanmean(port.BookVec[idx+1:])      # annual risk…
    shSR=shannret/shannrisk                    # annual sharpe ratio…
    #shannbps=(np.nansum(port.HedgedPnlVec[idx+1:])/np.nansum(port.TrdValVec[idx+1:]))*(10**4)
    shmaxdrawdown=0 #下面算最大回撤
    for i in range(idx,len(port.CumPnlVec)):
        currentdd=(max(np.array(port.CumPnlVec[idx:i+1])-np.array(port.IndCumPnlVec[idx:i+1]))-(np.array(port.CumPnlVec[i])-np.array(port.IndCumPnlVec[i])))/booklimit
        if currentdd>shmaxdrawdown:
            shmaxdrawdown=currentdd
    print ('emulation hedged summary(index):')
    print ('risk: '+ str(shannrisk))
    print ('ret: '+ str(shannret))
    print ('Sharpe: '+ str(shSR))
    print ('MaxDrawdown: '+ str(shmaxdrawdown))
    print ('Return/DD: '+str(shannret/shmaxdrawdown)+'\n')
    #print ('bps: '+str(shannbps)+'\n')
        
    '''plot part'''
    fig=plt.figure()
    fig.set_tight_layout(True)
    graph=fig.add_subplot(211)
    graph.plot(np.array(port.CumPnlVec)/booklimit,color='red',label='Alpha')   
    graph.plot(np.array(port.IndCumPnlVec)/booklimit,color='blue',label='HS300index')
    graph.plot(np.array(benchmark.CumPnlVec)/booklimit,color='green',label='EqualWeight')
    graph.legend(loc=0)
    graph.grid()
    graphHedge=fig.add_subplot(212)
    t1=np.array(port.CumPnlVec)/booklimit-np.array(port.IndCumPnlVec)/booklimit
    t1=pd.Series(t1,index=calendarSig['calendarDate'])
    t1.plot(color='red',label='Alpha-HS300index')
    t2=np.array(port.CumPnlVec)/booklimit-np.array(benchmark.CumPnlVec)/booklimit
    t2=pd.Series(t2,index=calendarSig['calendarDate'])
    t2.plot(color='green',label='Alpha-EqualWeight')
    graphHedge.legend(loc=0)
    graphHedge.grid()
    