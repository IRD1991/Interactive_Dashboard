#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Dec 14 2023 14:33

@author: Isobel Dixon
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import int_dash_data_functions as funcs
import datetime

from streamlit_autorefresh import st_autorefresh

#####PAGE SETTING DEFAULTS

st.set_page_config(
    page_title="Property Price Dashboard", #title shown in browser tab
    #page_icon="✅", #emoji as string or in shortcode or pass URL/np array of image
    layout="wide", #use entire screen
)

st_autorefresh(interval=36000000)

#####LOAD DATA

cpi_df = funcs.format_cpi_data(funcs.get_cpi_data())
gdp_df = funcs.format_gdp_data(funcs.get_gdp_data())
mortgage_df = funcs.format_mortgage_data(funcs.get_mortgage_data())
interest_df = funcs.format_interest_data(funcs.get_interest_data())
ukhpi_df = funcs.format_ukhpi_data(funcs.get_ukhpi_data())
avg_price_df = funcs.format_avg_price_data(funcs.get_avg_price_data())

all_dfs = [cpi_df, gdp_df, mortgage_df, interest_df, ukhpi_df, avg_price_df]
df = funcs.stitch_all_data(all_dfs)

#####PAGE TITLE

st.markdown("<h1 style='text-align: center;'>Property Price Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Explore the effects of inflation, GDP, mortgages and interest rates on UK property prices.</h4>", unsafe_allow_html=True)
st.markdown("<h6 style='text-align: center;'>Data sourced from: HM Land Registry, Bank of England, and Office for National Statistics. All data used is available in the public domain.</h6>", unsafe_allow_html=True)


#####ESTABLISHING STRUCTURE

st.markdown("<h3>Most Recent KPIs</h3>", unsafe_allow_html=True)
kpi_left, kpi_middle, kpi_right = st.columns(3)
with kpi_left.container():
    kpi_cpi = st.empty()
    kpi_gdp = st.empty()
with kpi_middle.container():
    kpi_hpi = st.empty()
    kpi_avg_price = st.empty()
with kpi_right.container():
    kpi_mortgages = st.empty()
    kpi_interest = st.empty()

st.markdown("<h3>Compare over time</h3>", unsafe_allow_html=True)
option_left, option_right = st.columns(2)
graphic_ukhpi = st.empty()
graphic_variable = st.empty()
graphic_avg_price = st.empty()

df_left, df_right = st.columns(2)


#####KPI METRICS SECTION

with kpi_cpi.container():
    curr_cpi = cpi_df['Overall Index'].iloc[-1]
    cpi_change = cpi_df['Overall Index'].iloc[-1] - cpi_df['Overall Index'].iloc[-2]
    st.metric(
        label='Overall Consumer Price Index',
        value=float("{:.2f}".format(curr_cpi)),
        delta=float("{:.2f}".format(cpi_change)),
        # delta_color='off'
    )

with kpi_gdp.container():
    curr_gdp = gdp_df['Monthly GDP'].iloc[-1]
    gdp_change = gdp_df['Monthly GDP'].iloc[-1] - gdp_df['Monthly GDP'].iloc[-2]
    st.metric(
        label='Monthly Gross Domestic Product (£)',
        value=float("{:.2f}".format(curr_gdp)),
        delta=float("{:.2f}".format(gdp_change)),
        # delta_color='off'
    )

with kpi_hpi.container():
    curr_hpi = ukhpi_df['UKHPI United Kingdom'].iloc[-1] 
    hpi_change = ukhpi_df['UKHPI United Kingdom'].iloc[-1] - ukhpi_df['UKHPI United Kingdom'].iloc[-2]
    st.metric(
        label='UK House Price Index',
        value=float("{:.2f}".format(curr_hpi)),
        delta=float("{:.2f}".format(hpi_change)),
        # delta_color='off'
    )

with kpi_avg_price.container():
    curr_avg_price=avg_price_df['Average Property Price United Kingdom'].iloc[-1] 
    avg_price_change=avg_price_df['Average Property Price United Kingdom'].iloc[-1] - \
                        avg_price_df['Average Property Price United Kingdom'].iloc[-2]
    st.metric(
        label='UK Average Property Price (£)',
        value=float("{:.2f}".format(curr_avg_price)),
        delta=float("{:.2f}".format(avg_price_change)),
        # delta_color='off'
    )

with kpi_mortgages.container():
    curr_mortgages=mortgage_df['Mortgage Approvals'].iloc[-1] 
    mortgages_change=mortgage_df['Mortgage Approvals'].iloc[-1] - \
                        mortgage_df['Mortgage Approvals'].iloc[-2]
    st.metric(
        label='UK Mortage Approvals Rate',
        value=float("{:.2f}".format(curr_mortgages)),
        delta=float("{:.2f}".format(mortgages_change)),
        # delta_color='off'
    )

with kpi_interest.container():
    curr_interest=interest_df['Base Interest Rate'].iloc[-1] 
    interest_change=interest_df['Base Interest Rate'].iloc[-1] - \
                        interest_df['Base Interest Rate'].iloc[-2]
    st.metric(
        label='Bank of England Base Interest Rate',
        value=float("{:.2f}".format(curr_interest)),
        delta=float("{:.2f}".format(interest_change)),
        # delta_color='off'
    )


#####MAIN SECTION OPTIONS
    
with option_left.container():
    options = ['Consumer Price Index',
               'Monthly Gross Domestic Product',
               'Mortgage Approval Rate',
               'Bank of England Base Rate'
              ]
    selected_option = st.selectbox(
        "Which variable would you like to compare against?",
        options,
        index=0
    )
    if selected_option == options[0]:
        y_columns = ['Housing Associated Costs', 'Overall Index']
        y_title = 'Consumer Price Index'
        chart_title = 'Consumer Price Index (CPI) - A measure of inflation'
    elif selected_option == options[1]:
        y_columns = ['Monthly GDP']
        y_title = 'British Poumd Sterling (£)'
        chart_title = 'Monthly Gross Domestic Product (GDP) for UK'
    elif selected_option == options[2]:
        y_columns = ['Mortgage Approvals']
        y_title = 'No. of Mortgage Approvals'
        chart_title = 'Monthly Mortgage Approvals Rate'
    elif selected_option == options[3]:
        y_columns = ['Base Interest Rate']
        y_title = 'Interest Rate (%)'
        chart_title = 'Bank of England Base Interest Rate'

with option_right.container():
    date_from_col, date_to_col = st.columns(2)
    with date_from_col.container():
        date_from = st.date_input("Show data from:",
                                  value=datetime.datetime(1997, 1, 1),
                                  min_value=datetime.datetime(1997, 1, 1),
                                  max_value=datetime.datetime.now().replace(day=1) - datetime.timedelta(days=1),
                                 )
    with date_to_col.container():
        date_to = st.date_input("up to:", 
                                value=datetime.datetime.now(),
                                min_value=datetime.datetime(1997, 2, 1),
                                max_value=datetime.datetime.now(),
                               )

date_from = datetime.datetime.combine(date_from, datetime.datetime.min.time())
date_to = datetime.datetime.combine(date_to, datetime.datetime.min.time())
sliced_df = df.loc[(df.index >= date_from) &
         (df.index <= date_to)]
avg_price_df_sliced = avg_price_df.loc[(avg_price_df.index >= date_from) &
         (avg_price_df.index <= date_to)]
ukhpi_df_sliced = ukhpi_df.loc[(ukhpi_df.index >= date_from) &
         (ukhpi_df.index <= date_to)]
    
######MAIN SECTION GRAPHICS

with graphic_ukhpi.container():
    ukhpi_df_sliced.drop(columns=[x for x in ukhpi_df_sliced if '%' in x], inplace=True)
    ukhpi_df_sliced.columns = [x.replace('UKHPI ', '') for x in ukhpi_df_sliced.columns]
    ukhpi_chart = px.line(ukhpi_df_sliced, x=ukhpi_df_sliced.index, y=ukhpi_df_sliced.columns,
                         color_discrete_sequence=px.colors.qualitative.Bold)
    ukhpi_chart.update_layout(template='simple_white',
        yaxis_title='House Price Index',
        title='UK House Price Index (HPI) ',
    )    
    st.plotly_chart(ukhpi_chart, use_container_width=True)

with graphic_variable.container():
    variable_chart = px.line(sliced_df, x=df.index, y=y_columns,
                            color_discrete_sequence=px.colors.qualitative.Safe)
    variable_chart.update_layout(template='simple_white',
        yaxis_title=y_title,
        xaxis_title='Date',
        title=chart_title,
    )    
    st.plotly_chart(variable_chart, use_container_width=True)

with graphic_avg_price.container():
    avg_price_df_sliced.columns = [x.replace('Average Property Price ', '') for x in avg_price_df_sliced.columns]
    avg_price_chart = px.line(avg_price_df_sliced, x=avg_price_df_sliced.index, y=avg_price_df_sliced.columns,
                             color_discrete_sequence=px.colors.qualitative.Bold)
    avg_price_chart.update_layout(template='simple_white',
        yaxis_title='British Pound Sterling (£)',
        title='Average Property Price',
    )
    st.plotly_chart(avg_price_chart, use_container_width=True)



#####DATAFRAME SECTION

with df_left.container():
    show_dataframe = st.checkbox('Show selected timeframe in a table for all variables?')
with df_right.container():
    
    def convert_df(df):
        return df.to_csv().encode('utf-8')

    csv = convert_df(sliced_df)

    st.download_button(
        label="Download data for selected timeframe as CSV",
        data=csv,
        file_name='PropertyPriceVariablesData.csv',
        mime='text/csv',
    )
if show_dataframe:
    # data frame view of sliced data
    st.dataframe(sliced_df, hide_index=False)