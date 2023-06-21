import numpy as np
import pandas as pd
import streamlit as st
#from pathlib import Path
from datetime import datetime
import plotly.express as px

from PIL import Image
#import plotly.graph_objects as go
#import plotly.io as pio


realBonds = ['R197', 'I2025', 'R210', 'I2029', 'I2031', 'I2033', 'R202', 'I2038', 'I2046', 'I2050']

nomBonds = ['R186', 'R2030', 'R213', 'R2032', 'R2035', 'R209', 'R2037', 'R2040', 'R214', 'R2044', 'R2048', 'R2053']



#file = "BondDetails.csv"
file = "BondDetailsv1.csv"
fileprev = 'BondDetailsv0.csv'

@st.cache_data
def data(file):
    #df = pd.read_csv(file, delimiter=";", index_col="Date", parse_dates=True, infer_datetime_format=True)
    #df = pd.read_csv(file, delimiter=";")
    df = pd.read_csv(file, delimiter=",")
    return df

df = data(file)
dfprev =data(fileprev)

#bondData = df[['Bond Code', 'Date', 'ISSUER', 'ISSUER_INDUSTRY', 'PAYMENT_RANK', 'Coupon', 'Companion Bond',
#               'BP Spread', 'MTM', 'Last MTM Change Date', 'DAYS_TO_NEXT_COUPON', 'NXT_CPN_DT', 'Modified Duration']]

bondData = df[['Bond Code', 'Maturity', 'ISSUER', 'ISSUER_INDUSTRY', 'PAYMENT_RANK', 'Coupon', 'Companion Bond',
               'BP Spread', 'MTM', 'Last MTM Change Date', 'DAYS_TO_NEXT_COUPON', 'NXT_CPN_DT', 'Modified Duration']]


change0 = df[['Bond Code', 'ISSUER', 'ISSUER_INDUSTRY', 'PAYMENT_RANK', 'Companion Bond', 'BP Spread']]
change1 = dfprev[['Bond Code', 'ISSUER', 'ISSUER_INDUSTRY', 'PAYMENT_RANK', 'Companion Bond', 'BP Spread']]

#change0['BP Spread'] = change0['BP Spread'].astype(float)
#change1['BP Spread'] = change1['BP Spread'].astype(float)

change = pd.merge(change0, change1, on='Bond Code', how='left')

change = change.drop(['ISSUER_y'], axis=1)
change = change.drop(['ISSUER_INDUSTRY_y'], axis=1)
change = change.drop(['PAYMENT_RANK_y'], axis=1)
change = change.drop(['Companion Bond_y'], axis=1)

#change0['BP Spread'] = change0['BP Spread'].astype(float)
#change1['BP Spread'] = change1['BP Spread'].astype(float)

change['Move'] = change['BP Spread_x'] - change['BP Spread_y']

change = change.dropna()

change = change[(change['Move'] != 0)]

change = change.rename({'ISSUER_x': 'Issuer',
                        'ISSUER_INDUSTRY_x': 'Industry',
                        'PAYMENT_RANK_x': 'Rank',
                        'Companion Bond_x': 'Companion',
                        'BP Spread_x': 'Spread(t)',
                        'BP Spread_y': 'Spread(t-1)',
            }, axis=1)


#st.dataframe(change)

#st.dataframe(bondData)

#bondData = bondData.dropna()
#bondaData = bondData.dropna(subset = ['DAYS_TO_NEXT_COUPON'])
#bondaData = bondaData.loc[bondaData['DAYS_TO_NEXT_COUPON'] != ' #N/A N/A ']

#st.dataframe(bondData)
##bondaData['DAYS_TO_NEXT_COUPON'] = bondaData['DAYS_TO_NEXT_COUPON'].replace(' -  ', 0)
#bondaData = bondData.dropna(subset = ['Date'])

#bondaData = bondData.dropna(subset = ['NXT_CPN_DT'])
#bondaData = bondData.dropna(subset = ['DAYS_TO_NEXT_COUPON'])


today = datetime.today().date()

#bondData['Maturity'] = bondData.apply(lambda x: datetime.strptime(x['Date'], "%Y/%m/%d").date(), axis=1)
bondData['Maturity'] = bondData.apply(lambda x: datetime.strptime(x['Maturity'], "%d-%b-%y").date(), axis=1)
bondData['Last_MTM_Change'] = bondData.apply(lambda x: datetime.strptime(x['Last MTM Change Date'], "%d-%b-%y").date(), axis=1)

#bondData['NXT_CPN_DT'] = bondData.apply(lambda x: datetime.strptime(x['NXT_CPN_DT'], "%Y/%m/%d").date(), axis=1)

bondData['Term'] = bondData.apply(lambda x: ((x['Maturity'] - today).days)/365, axis=1)


#bondData['MD'] = bondData.apply(lambda x: ((x['DAYS_TO_NEXT_COUPON'] - today).days)/365, axis=1)
bondData['MD'] = bondData.apply(lambda x: (float(x['DAYS_TO_NEXT_COUPON']))/365 if (x['Companion Bond'] == 'JIBAR') else x['Modified Duration'] , axis=1)


#bondData = bondData.drop(['Date'], axis=1)
bondData = bondData.drop(['Last MTM Change Date'], axis=1)

bondData = bondData.sort_values(by='Maturity')

issuerData = bondData['ISSUER'].unique()

industryData = bondData['ISSUER_INDUSTRY'].unique()

rankData = bondData['PAYMENT_RANK'].unique()

benchmarkData = bondData['Companion Bond'].unique()

codes = bondData['Bond Code'].unique()

options = ['Issuer', 'Industry', 'Rank']

issuers = sorted(issuerData)

industry = sorted(industryData)

rank = sorted(rankData)

benchmark = benchmarkData


####benchmark = sorted(benchmarkData)#####


@st.cache_data
def MTMRegression(data):

    fig = px.scatter(data, x='Term', y='Companion_Spread', text='Bond Code', trendline='ols', trendline_color_override='red')

    fig.update_traces(textposition='top center')

    results = px.get_trendline_results(fig)
    results0 = results.iloc[0]["px_fit_results"].summary()
    results1 = results.iloc[0]["px_fit_results"].params

    return fig, results0, results1



@st.cache_data
def MTMRegressionJIBAR(data):

    fig = px.scatter(data, x='Term', y='JIBAR_Spread', text='Bond Code', trendline='ols', trendline_color_override='red')

    fig.update_traces(textposition='top center')

    results = px.get_trendline_results(fig)
    results0 = results.iloc[0]["px_fit_results"].summary()
    results1 = results.iloc[0]["px_fit_results"].params

    return fig, results0, results1



@st.cache_data
def MTMHistogram(data, metric, attribute):

    fig = px.histogram(data, x=metric, color=attribute, text_auto = True)


    fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=-0.3,
    xanchor="left",
    x=0.0
))


    return fig
    

#st.markdown("<h3 style='text-align: left; color: purple; padding-left: 0px; font-size: 40px'><b>Credit Analysis<b></h3>", unsafe_allow_html=True)

st.header('Credit Analysis')

st.markdown(" ")
banner2 = Image.open('background1.jpg')
st.image(banner2)
st.markdown(" ")


#st.header('Spread Moves')

#st.dataframe(change)


st.sidebar.header('Pricing Inputs')

st.markdown(" ")
banner1 = Image.open('sidebarBackground2.jpg')
st.sidebar.image(banner1)
st.markdown(" ")


refRate = st.sidebar.number_input('3M JIBAR', value=8.492)

inflation = st.sidebar.number_input('12M Expected Inflation', value=6.800)

####Need to fix this, include or incorporate inflation#############
####Also need to think about spread - it should be spread over Companion not JIBAR?########

#bondData['YTM'] = bondData.apply(lambda x: 200*((1+((refRate + (x['BP Spread'])/100))/400)**(2)-1) if (x['Companion Bond'] == 'JIBAR') else x['MTM'], axis =1) 

#bondData['Spread'] = bondData.apply(lambda x: round(100*((400*(((1+((x['YTM'])/200))**(0.5))-1))-refRate),2), axis =1) 

@st.cache_data
def ytm(data):

    lenth = data.shape[0]

    yieldToMaturity = []

    for i in range(0,lenth):

        #if (data['Companion Bond'].iloc[i].isin(realBonds)):
        if(data['Companion Bond'].iloc[i] == 'R197'):
            ytm =  data['MTM'].iloc[i] + (inflation)
            yieldToMaturity.append(ytm)

        elif(data['Companion Bond'].iloc[i] == 'I2025'):
            ytm =  data['MTM'].iloc[i] + (inflation)
            yieldToMaturity.append(ytm)


        elif(data['Companion Bond'].iloc[i] == 'R210'):
            ytm =  data['MTM'].iloc[i] + (inflation)
            yieldToMaturity.append(ytm)

        elif(data['Companion Bond'].iloc[i] == 'I2029'):
            ytm =  data['MTM'].iloc[i] + (inflation)
            yieldToMaturity.append(ytm)

        elif(data['Companion Bond'].iloc[i] == 'I2029'):
            ytm =  data['MTM'].iloc[i] + (inflation)
            yieldToMaturity.append(ytm)


        elif(data['Companion Bond'].iloc[i] == 'R2031'):
            ytm =  data['MTM'].iloc[i] + (inflation)
            yieldToMaturity.append(ytm)

        elif(data['Companion Bond'].iloc[i] == 'R2033'):
            ytm =  data['MTM'].iloc[i] + (inflation)
            yieldToMaturity.append(ytm)


        elif(data['Companion Bond'].iloc[i] == 'R202'):
            ytm =  data['MTM'].iloc[i] + (inflation)
            yieldToMaturity.append(ytm)

        elif(data['Companion Bond'].iloc[i] == 'I2038'):
            ytm =  data['MTM'].iloc[i] + (inflation)
            yieldToMaturity.append(ytm)


        elif(data['Companion Bond'].iloc[i] == 'I2046'):
            ytm =  data['MTM'].iloc[i] + (inflation)
            yieldToMaturity.append(ytm)

        elif(data['Companion Bond'].iloc[i] == 'I2050'):
            ytm =  data['MTM'].iloc[i] + (inflation)
            yieldToMaturity.append(ytm)


        elif(data['Companion Bond'].iloc[i] == 'JIBAR'):
            ytm = (data['BP Spread'].iloc[i]/100) + refRate
            yieldToMaturity.append(ytm)

        else:
            ytm = data['MTM'].iloc[i]

            yieldToMaturity.append(ytm)
        
    return yieldToMaturity


@st.cache_data
def jibarSpread(data):

    lenth = data.shape[0]

    jibarSpread = []

    for i in range(0,lenth):

        if(data['Companion Bond'].iloc[i] == 'JIBAR'):
            spread = round((data['YTM'].iloc[i] - refRate)*100,2)
            jibarSpread.append(spread)

        else:
            spread = round((((((1+((data['YTM'].iloc[i])/200))**(2/4)) - 1)*400) - refRate)*100,2)
            jibarSpread.append(spread)
    
    return jibarSpread

        
#bondData['Spread'] = bondData['BP Spread']

#bondData['YTM'] = bondData.apply(lambda x: x['MTM'] if (x['MTM'] > 0) else ((x['Spread']/100) + refRate), axis=1)

bondData['YTM'] = ytm(bondData)

bondData['Companion_Spread'] = bondData['BP Spread']

#bondData['JIBAR_Spread'] = (bondData['YTM'] - refRate)*100

bondData['JIBAR_Spread'] = jibarSpread(bondData)

#########
#########

#bondData['MD'] = bondData.apply(lambda x: (float(x['DAYS_TO_NEXT_COUPON'])/365) if (x['Companion Bond'] == 'JIBAR') else x['Modified Duration'], axis =1)



bondData = bondData.drop(['BP Spread'], axis=1)
bondData = bondData.drop(['MTM'], axis=1)
bondData = bondData.drop(['DAYS_TO_NEXT_COUPON'], axis=1)
bondData = bondData.drop(['NXT_CPN_DT'], axis=1)
bondData = bondData.drop(['Modified Duration'], axis=1)


st.header('BESA MTM')


st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: left;} </style>', unsafe_allow_html=True)
                 
showDF = st.radio("Details",("Spread Change", "All Bonds"))

if (showDF == 'Spread Change'):
    st.dataframe(change)
else:
    st.dataframe(bondData)


selection = st.sidebar.selectbox('Criteria', options, index=0)


###################################################################################################################################################
################################### Code within if statements based on selection ##################################################################

st.markdown(" ")
st.markdown(" ")
st.header('Filtered Bond')

if (selection == 'Issuer'):

    issuer1 = st.multiselect('Issuers', issuers, default = 'ABSA BANK LTD')

    emptyDf = []

    for issuer in issuer1:
        container = bondData.loc[(bondData['ISSUER'] == issuer)]
        emptyDf.append(container)

    issuerFilter = pd.concat(emptyDf)


    issuerIndustry = st.sidebar.checkbox("Industry")
    if issuerIndustry:
        industryIssuer = st.sidebar.selectbox('Industry', industry, index=0)
        issuerFilter = issuerFilter.loc[(issuerFilter['ISSUER_INDUSTRY'] == industryIssuer)]


    issuerRank = st.sidebar.checkbox("Rank")
    if issuerRank:
        rankIssuer = st.sidebar.selectbox('Rank', rank, index=0)
        issuerFilter = issuerFilter.loc[(issuerFilter['PAYMENT_RANK'] == rankIssuer)] 



    issuerBenchmark = st.sidebar.checkbox("Benchmark")
    if issuerBenchmark:
        benchmarkIssuer = st.sidebar.selectbox('Rank', benchmark, index=0)
        issuerFilter = issuerFilter.loc[(issuerFilter['Companion Bond'] == benchmarkIssuer)] 

    issuerDate = st.sidebar.checkbox("Date")
    if issuerDate:
        dateIssuer1 = st.sidebar.date_input("Start Date")
        dateIssuer2 = st.sidebar.date_input("End Date")

        issuerFilter = issuerFilter.loc[(issuerFilter['Maturity'] >= dateIssuer1) & (issuerFilter['Maturity'] <= dateIssuer2)]
    
    
    bondCode = st.checkbox("Filter on Bond Code")

    if bondCode:

        identifier = issuerFilter['Bond Code'].unique()

        codeBonds = st.multiselect('Bond Codes', identifier)

        issuerFilter = issuerFilter[issuerFilter['Bond Code'].isin(codeBonds)]
    


    #st.header('Filtered Bond')
    st.dataframe(issuerFilter, use_container_width=True)


#############
    #showMoves = st.checkbox("Show Spread Changes")

    #if showMoves:
    #    st.header('Spread Moves')

    #    st.dataframe(change)


#############
    showStats = st.checkbox("Show Statistics")

    if showStats:

        #descriptiveDF = issuerFilter[['Spread', 'Term']]
        descriptiveDF = issuerFilter[['Companion_Spread', 'JIBAR_Spread']]

        df1, df2, df3= st.columns([0.6,1,1])

        df1.header('Statistics')
        df1.markdown(' ')
        df1.markdown(' ')
        df1.markdown(' ')
        df1.markdown(' ')
        df1.dataframe(descriptiveDF.describe())

        histSpOJ = MTMHistogram(issuerFilter, 'Companion_Spread', 'ISSUER')
        df2.header('Companion_Spread Histogram')
        df2.plotly_chart(histSpOJ, use_container_width=True)

        #histTerm = MTMHistogram(issuerFilter, 'Term', 'ISSUER')
        #df3.header('Term Histogram')
        #df3.plotly_chart(histTerm, use_container_width=True)

        histJIBARSpread = MTMHistogram(issuerFilter, 'JIBAR_Spread', 'ISSUER')
        df3.header('JIBAR_Spread Histogram')
        df3.plotly_chart(histJIBARSpread, use_container_width=True)



    showGraph = st.checkbox("Spread Over Companion Bond Regression")

    if showGraph:


        yieldGraph, summary, param = MTMRegression(issuerFilter)
        
        
        graphCol, summaryCol = st.columns([1.1,0.9])

        graphCol.header('OLS Comapanion Bond Spread')

        graphCol.plotly_chart(yieldGraph)
         

        summaryCol.header('Companion Bond Model Based Spread')

        constant = round(param[0],5)
        gradient = round(param[1],5)

        summaryCol.markdown(' ')
        summaryCol.markdown(' ')
        summaryCol.markdown(' ')
        summaryCol.markdown(' ')

        summaryCol.markdown('Spread over Companion Bond= '+str(round(param[0],2))+' + ' + str(round(param[1],2)) + ' x Term')

        inputTerm = summaryCol.number_input('Term', value=1.00)

        Spread = round(constant + gradient*inputTerm,2)

        averageCompanionYield = round(issuerFilter['YTM'].mean() - (issuerFilter['Companion_Spread'].mean())/100,2)
        
        YTM = round(averageCompanionYield + (Spread/100), 2)

        YTMQuarterly = round(400*(((1+(YTM/200))**(2/4))-1),2)

        
        #YTM = round(((200*(((1+(((Spread/100)+refRate)/400))**(2))-1))),2)

        summaryCol.markdown('Ref: Average Companion Bond Yield = '+str(averageCompanionYield))

        summaryCol.markdown('Spread over Companion Bond = '+str(Spread))
        summaryCol.markdown('Quarterly YTM = ' + str(YTMQuarterly))
        summaryCol.markdown('Semi-Annual YTM = ' + str(YTM))
        

        showSummary= st.checkbox("Companion Bond Regression Results")
        if showSummary:

            st.header('OLS Results Summary')

            summary




    showGraph = st.checkbox("Spread Over JIBAR Regression")

    if showGraph:


        yieldGraph, summary, param = MTMRegressionJIBAR(issuerFilter)
        
        
        graphCol, summaryCol = st.columns([1.1,0.9])

        graphCol.header('OLS JIBAR Spread')

        graphCol.plotly_chart(yieldGraph)
         

        summaryCol.header('JIBAR Model Based Spread')

        constant = round(param[0],5)
        gradient = round(param[1],5)

        summaryCol.markdown(' ')
        summaryCol.markdown(' ')
        summaryCol.markdown(' ')
        summaryCol.markdown(' ')

        summaryCol.markdown('Spread Over 3M JIBAR = '+str(round(param[0],2))+' + ' + str(round(param[1],2)) + ' x Term')

        inputTerm = summaryCol.number_input('Tenor', value=1.00)

        Spread = round(constant + gradient*inputTerm,2)

        #YTM = round(((200*(((1+(((Spread/100)+refRate)/400))**(2))-1))),2)

        YTM = round((Spread/100) + refRate,2)

        YTMSemi = round(200*(((1+(YTM/400))**(2))-1),2)


        summaryCol.markdown('Ref: 3M JIBAR = '+str(refRate))

        summaryCol.markdown('Spread over 3M JIBAR = '+str(Spread))
        summaryCol.markdown('Quarterly YTM = ' + str(YTM))
        summaryCol.markdown('Semi-Annual YTM = ' + str(YTMSemi))

        showSummary= st.checkbox("JIBAR Spread Regression Results")
        if showSummary:

            st.header('OLS Results Summary')

            summary
######


elif(selection == 'Industry'):

    industry1 = st.multiselect('Industries', industry, default = 'BANK')

    emptyDf = []

    for industry in industry1:
        container = bondData.loc[(bondData['ISSUER_INDUSTRY'] == industry)]
        emptyDf.append(container)

    industryFilter = pd.concat(emptyDf)


    industryIssuer = st.sidebar.checkbox("Issuer")
    if industryIssuer:
        issuerIndustry = st.sidebar.selectbox('Issuer', issuers, index=0)
        industryFilter = industryFilter.loc[(industryFilter['ISSUER'] == issuerIndustry)]


    rankIndustry = st.sidebar.checkbox("Rank")
    if rankIndustry:
        industryRank = st.sidebar.selectbox('Rank', rank, index=0)
        industryFilter = industryFilter.loc[(industryFilter['PAYMENT_RANK'] == industryRank)] 


    industryBenchmark = st.sidebar.checkbox("Benchmark")
    if industryBenchmark:
        benchmarkIndustry = st.sidebar.selectbox('Rank', benchmark, index=0)
        industryFilter = industryFilter.loc[(industryFilter['Companion Bond'] == benchmarkIndustry)] 



    industryDate = st.sidebar.checkbox("Date")
    if industryDate:
        dateIssuer1 = st.sidebar.date_input("Start Date")
        dateIssuer2 = st.sidebar.date_input("End Date")

        industryFilter = industryFilter.loc[(industryFilter['Maturity'] >= dateIssuer1) & (industryFilter['Maturity'] <= dateIssuer2)]

    bondCode = st.checkbox("Filter on Bond Code")

    if bondCode:

        identifier = industryFilter['Bond Code'].unique()

        codeBonds = st.multiselect('Bond Codes', identifier)

        industryFilter = industryFilter[industryFilter['Bond Code'].isin(codeBonds)]

    st.dataframe(industryFilter)


#############
    showStats = st.checkbox("Show Statistics")

    if showStats:

        #descriptiveDF = industryFilter[['Spread', 'Term']]
        descriptiveDF = industryFilter[['Companion_Spread', 'JIBAR_Spread']]

        df1, df2, df3= st.columns([0.6,1,1])

        df1.header('Statistics')
        df1.markdown(' ')
        df1.markdown(' ')
        df1.markdown(' ')
        df1.markdown(' ')
        df1.dataframe(descriptiveDF.describe())

        histSpOJ = MTMHistogram(industryFilter, 'Companion_Spread', 'ISSUER')
        df2.header('Companion_Spread Histogram')
        df2.plotly_chart(histSpOJ, use_container_width=True)

        #histTerm = MTMHistogram(industryFilter, 'Term', 'ISSUER')
        #df3.header('Term Histogram')
        #df3.plotly_chart(histTerm, use_container_width=True)


        histJIBARSpread = MTMHistogram(industryFilter, 'JIBAR_Spread', 'ISSUER')
        df3.header('JIBAR_Spread Histogram')
        df3.plotly_chart(histJIBARSpread, use_container_width=True)




    showGraph = st.checkbox("Spread Over Companion Bond Regression")

    if showGraph:


        yieldGraph, summary, param = MTMRegression(industryFilter)
        
        
        graphCol, summaryCol = st.columns([1.1,0.9])

        graphCol.header('OLS Comapanion Bond Spread')

        graphCol.plotly_chart(yieldGraph)
         

        summaryCol.header('Companion Bond Model Based Spread')

        constant = round(param[0],5)
        gradient = round(param[1],5)

        summaryCol.markdown(' ')
        summaryCol.markdown(' ')
        summaryCol.markdown(' ')
        summaryCol.markdown(' ')

        summaryCol.markdown('Spread over Companion Bond= '+str(round(param[0],2))+' + ' + str(round(param[1],2)) + ' x Term')

        inputTerm = summaryCol.number_input('Term', value=1.00)

        Spread = round(constant + gradient*inputTerm,2)

        averageCompanionYield = round(industryFilter['YTM'].mean() - (industryFilter['Companion_Spread'].mean())/100,2)
        
        YTM = round(averageCompanionYield + (Spread/100), 2)

        YTMQuarterly = round(400*(((1+(YTM/200))**(2/4))-1),2)

        
        #YTM = round(((200*(((1+(((Spread/100)+refRate)/400))**(2))-1))),2)

        summaryCol.markdown('Ref: Average Companion Bond Yield = '+str(averageCompanionYield))

        summaryCol.markdown('Spread over Companion Bond = '+str(Spread))
        summaryCol.markdown('Quarterly YTM = ' + str(YTMQuarterly))
        summaryCol.markdown('Semi-Annual YTM = ' + str(YTM))
        

        showSummary= st.checkbox("Companion Bond Regression Results")
        if showSummary:

            st.header('OLS Results Summary')

            summary




    showGraph = st.checkbox("Spread Over JIBAR Regression")

    if showGraph:


        yieldGraph, summary, param = MTMRegressionJIBAR(industryFilter)
        
        
        graphCol, summaryCol = st.columns([1.1,0.9])

        graphCol.header('OLS JIBAR Spread')

        graphCol.plotly_chart(yieldGraph)
         

        summaryCol.header('JIBAR Model Based Spread')

        constant = round(param[0],5)
        gradient = round(param[1],5)

        summaryCol.markdown(' ')
        summaryCol.markdown(' ')
        summaryCol.markdown(' ')
        summaryCol.markdown(' ')

        summaryCol.markdown('Spread Over 3M JIBAR = '+str(round(param[0],2))+' + ' + str(round(param[1],2)) + ' x Term')

        inputTerm = summaryCol.number_input('Tenor', value=1.00)

        Spread = round(constant + gradient*inputTerm,2)

        #YTM = round(((200*(((1+(((Spread/100)+refRate)/400))**(2))-1))),2)

        YTM = round((Spread/100) + refRate,2)

        YTMSemi = round(200*(((1+(YTM/400))**(2))-1),2)


        summaryCol.markdown('Ref: 3M JIBAR = '+str(refRate))

        summaryCol.markdown('Spread over 3M JIBAR = '+str(Spread))
        summaryCol.markdown('Quarterly YTM = ' + str(YTM))
        summaryCol.markdown('Semi-Annual YTM = ' + str(YTMSemi))

        showSummary= st.checkbox("JIBAR Spread Regression Results")
        if showSummary:

            st.header('OLS Results Summary')

            summary
######





elif (selection == 'Rank'):   
    
    rank1 = st.multiselect('Rank', rank, default = 'Sr Unsecured')

    emptyDf = []

    for rank in rank1:
        container = bondData.loc[(bondData['PAYMENT_RANK'] == rank)]
        emptyDf.append(container)

    rankFilter = pd.concat(emptyDf)  

    rankIssuer = st.sidebar.checkbox("Issuer")
    if rankIssuer:
        issuerRank = st.sidebar.selectbox('Issuer', issuers, index=0)
        rankFilter = rankFilter.loc[(rankFilter['ISSUER'] == issuerRank)]


    rankIndustry = st.sidebar.checkbox("Industry")
    if rankIndustry:
        industryRank = st.sidebar.selectbox('Industry', industry, index=0)
        rankFilter = rankFilter.loc[(rankFilter['ISSUER_INDUSTRY'] == industryRank)] 


    rankBenchmark = st.sidebar.checkbox("Benchmark")
    if rankBenchmark:
        benchmarkRank = st.sidebar.selectbox('Rank', benchmark, index=0)
        rankFilter = rankFilter.loc[(rankFilter['Companion Bond'] == benchmarkRank)] 


    industryDate = st.sidebar.checkbox("Date")
    if industryDate:
        dateIssuer1 = st.sidebar.date_input("Start Date")
        dateIssuer2 = st.sidebar.date_input("End Date")

        rankFilter = rankFilter.loc[(rankFilter['Maturity'] >= dateIssuer1) & (rankFilter['Maturity'] <= dateIssuer2)]
    


    bondCode = st.checkbox("Filter on Bond Code")

    if bondCode:

        identifier = rankFilter['Bond Code'].unique()

        codeBonds = st.multiselect('Bond Codes', identifier)

        rankFilter = rankFilter[rankFilter['Bond Code'].isin(codeBonds)]

    
    st.dataframe(rankFilter)



#############
    showStats = st.checkbox("Show Statistics")

    if showStats:

        #descriptiveDF = rankFilter[['Spread', 'Term']]
        descriptiveDF = rankFilter[['Companion_Spread', 'JIBAR_Spread']]

        df1, df2, df3= st.columns([0.6,1,1])

        df1.header('Statistics')
        df1.markdown(' ')
        df1.markdown(' ')
        df1.markdown(' ')
        df1.markdown(' ')
        df1.dataframe(descriptiveDF.describe())

        histSpOJ = MTMHistogram(rankFilter, 'Companion_Spread', 'ISSUER')
        df2.header('Companion_Spread Histogram')
        df2.plotly_chart(histSpOJ, use_container_width=True)

        #histTerm = MTMHistogram(rankFilter, 'Term', 'ISSUER')
        #df3.header('Term Histogram')
        #df3.plotly_chart(histTerm, use_container_width=True)


        histJIBARSpread = MTMHistogram(rankFilter, 'JIBAR_Spread', 'ISSUER')
        df3.header('JIBAR_Spread Histogram')
        df3.plotly_chart(histJIBARSpread, use_container_width=True)


    showGraph = st.checkbox("Spread Over Companion Bond Regression")

    if showGraph:


        yieldGraph, summary, param = MTMRegression(rankFilter)
        
        
        graphCol, summaryCol = st.columns([1.1,0.9])

        graphCol.header('OLS Comapanion Bond Spread')

        graphCol.plotly_chart(yieldGraph)
         

        summaryCol.header('Companion Bond Model Based Spread')

        constant = round(param[0],5)
        gradient = round(param[1],5)

        summaryCol.markdown(' ')
        summaryCol.markdown(' ')
        summaryCol.markdown(' ')
        summaryCol.markdown(' ')

        summaryCol.markdown('Spread over Companion Bond= '+str(round(param[0],2))+' + ' + str(round(param[1],2)) + ' x Term')

        inputTerm = summaryCol.number_input('Term', value=1.00)

        Spread = round(constant + gradient*inputTerm,2)

        averageCompanionYield = round(rankFilter['YTM'].mean() - (rankFilter['Companion_Spread'].mean())/100,2)
        
        YTM = round(averageCompanionYield + (Spread/100), 2)

        YTMQuarterly = round(400*(((1+(YTM/200))**(2/4))-1),2)

        
        #YTM = round(((200*(((1+(((Spread/100)+refRate)/400))**(2))-1))),2)

        summaryCol.markdown('Ref: Average Companion Bond Yield = '+str(averageCompanionYield))

        summaryCol.markdown('Spread over Companion Bond = '+str(Spread))
        summaryCol.markdown('Quarterly YTM = ' + str(YTMQuarterly))
        summaryCol.markdown('Semi-Annual YTM = ' + str(YTM))
        

        showSummary= st.checkbox("Companion Bond Regression Results")
        if showSummary:

            st.header('OLS Results Summary')

            summary


    showGraph = st.checkbox("Spread Over JIBAR Regression")

    if showGraph:


        yieldGraph, summary, param = MTMRegressionJIBAR(rankFilter)
        
        
        graphCol, summaryCol = st.columns([1.1,0.9])

        graphCol.header('OLS JIBAR Spread')

        graphCol.plotly_chart(yieldGraph)
         

        summaryCol.header('JIBAR Model Based Spread')

        constant = round(param[0],5)
        gradient = round(param[1],5)

        summaryCol.markdown(' ')
        summaryCol.markdown(' ')
        summaryCol.markdown(' ')
        summaryCol.markdown(' ')

        summaryCol.markdown('Spread Over 3M JIBAR = '+str(round(param[0],2))+' + ' + str(round(param[1],2)) + ' x Term')

        inputTerm = summaryCol.number_input('Tenor', value=1.00)

        Spread = round(constant + gradient*inputTerm,2)

        #YTM = round(((200*(((1+(((Spread/100)+refRate)/400))**(2))-1))),2)

        YTM = round((Spread/100) + refRate,2)

        YTMSemi = round(200*(((1+(YTM/400))**(2))-1),2)


        summaryCol.markdown('Ref: 3M JIBAR = '+str(refRate))

        summaryCol.markdown('Spread over 3M JIBAR = '+str(Spread))
        summaryCol.markdown('Quarterly YTM = ' + str(YTM))
        summaryCol.markdown('Semi-Annual YTM = ' + str(YTMSemi))

        showSummary= st.checkbox("JIBAR Spread Regression Results")
        if showSummary:

            st.header('OLS Results Summary')

            summary

################################################################################
################################################################################












