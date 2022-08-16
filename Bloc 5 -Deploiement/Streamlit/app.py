#### Streamlit App 
#### Import libraries
import streamlit as st

import pandas as pd
import numpy as np
#import seaborn as sns
#import matplotlib.pyplot as plt
#from matplotlib.pyplot import figure
import plotly.express as px
import plotly.io as pio

import statistics


### App config
st.set_page_config(layout="wide")
st.title(" Getaround Delay Analysis")
st.markdown(""" By Twix""")

st.markdown("---")

# IMPORT DATASET
@st.cache(allow_output_mutation=True)
def load_data():
  data = pd.read_excel("get_around_delay_analysis.xlsx")
  return data

data = load_data()


# ----------------------------------



### Content


# -------------------------------------

# Pages definition

def main():
    pages = {
        'Introduction and basics informations': Intro,
        'Exploratory data analysis': EDA,
        'Analysis Conclusion' : Report

        }

    if "page" not in st.session_state:
        st.session_state.update({
        # Default page
        'page': 'Intro'
        })

    with st.sidebar:
        page = st.selectbox("", tuple(pages.keys()))

    pages[page]()

# Part 1 : Basic informations of the dataset

def Intro():

    st.header("""About this dashboard""")
    st.markdown(""" This dashboard was made for the "Deployement project' as a part of a certification degree in data science. The aim of this EDA was to analyse the recorded delays \
        by the company, to suggest a time threshold between two reservations and the scope of this threshold.
""")


    st.title("""Part 1 : Basic informations of the dataset""")
    st.subheader('')
    st.subheader('')


    col3, col4 = st.columns(2)

    with col3:
        #Proportion of type of reservations
        df_checkin_type = (data['checkin_type'].value_counts(normalize=True)*100).rename_axis('checkin_type').reset_index(name='counts')
        fig = px.pie(df_checkin_type,
             values= 'counts',
             names = 'checkin_type',
             width= 1000,
             title='Proportions of type of reservation'
             )
        fig.update_traces(textposition = 'outside', textfont_size = 15)             
        fig.update_layout(title_x = 0.5, 
                  margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                  template = 'plotly_dark'
                  )    
        st.plotly_chart(fig , use_container_width=True)

    with col4:
 
        st.markdown("This page shows basic information on the dataset like the distribution on the type of reservation and the ratio of cancelations VS ended reservations \
            **_In this dataset, the reservations with delayed checkout represents 44%_** ")
        st.subheader('')
        st.markdown("""For the detailled analysis please select -Exploratory data analyis on the checkbox on the left to got to the next page.""")

    #Statistics on ended vs canceled reservations
    col1, col2 = st.columns(2)

    with col1:# global proportions
        data_ratio_state = (data['state'].value_counts(normalize=True)*100).rename_axis('state').reset_index(name='counts')
        fig = px.pie(data_ratio_state,
             values='counts',
             names='state', 
             width= 1000,
             title='Proportions of ended versus canceled rentals'
             )
        fig.update_traces(textposition = 'outside', textfont_size = 15)             
        fig.update_layout(title_x = 0.5, 
                  margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                  template = 'plotly_dark'
                  )    
        st.plotly_chart(fig , use_container_width=True)


    with col2:# Proportions for each type
        fig = px.histogram(data, x = "state",
                   title = 'Ended VS canceled rentals proportions',
                   color = 'checkin_type',
                   barmode ='group',
                   width= 1000,
                   height = 600,
                   histnorm = 'percent',
                   text_auto = True
                  )       
        fig.update_traces(textposition = 'outside', textfont_size = 15,texttemplate= '%{value:.2f}')
        fig.update_layout(title_x = 0.5,
                  margin=dict(l=50,r=50,b=50,t=50,pad=4),
                  yaxis = {'visible': False}, 
                  xaxis = {'visible': True}, 
                  xaxis_title = '',
                  template = 'plotly_dark'
                  )
        fig.update_xaxes(tickfont_size=15)                     
        st.plotly_chart(fig , use_container_width=True)

#PART 2 - A - Analysis of the delay statistics  ---- Specific delays


def EDA():
    st.title('Part 2: Exploratory Data Analysis')

    st.subheader('')

    st.subheader('          Analysis of the cancelations')
    st.subheader('')
    st.subheader('')

    col5, col6 = st.columns(2)

    with col5:
        data['time_delta_with_previous_rental_in_minutes'] = data['time_delta_with_previous_rental_in_minutes'].fillna('over 12 hours')
        df_canceled_temp = data[ data['state'] == 'canceled'].groupby('time_delta_with_previous_rental_in_minutes').count()

        # piechart for delay at checkout
        fig = px.pie(df_canceled_temp,
             values='state',
             names=df_canceled_temp.index,
            # title='Proportions of canceled reservations per category of time delta',
             width= 2000
             )
        fig.update_traces(textposition = 'outside', textfont_size = 15)             
        fig.update_layout(title_x = 0, 
                  margin=dict(l=50,r=50,b=50,t=50,pad=4),
                  template = 'plotly_dark' )   
        st.plotly_chart(fig , use_container_width=True)

    with col6:

        st.subheader('Proportions of canceled reservations per category of time delta')
        print()
        st.markdown('This chart shows that most of canceled reservations had a time delta with the previous one which was over 12 hours. They represent 93% of the dataset which is a lot. \
        We can assume that the delay at the checkout of the previous user was not the reason why those reservations were canceled. \
        Although a +12hours delay is possible, it seems highly unlikely that this happen so often.') 
        st.markdown('**For the next part I will focus my analysis on the -less than 12 hours- delays.**')

    
    col7, col8 = st.columns(2)


    df_with_previous = data[ data['time_delta_with_previous_rental_in_minutes'] != 'over 12 hours' ]
    df_canceled_with_previous = df_with_previous[ df_with_previous['state'] == 'canceled']
    df_canceled_ratio = df_canceled_with_previous.groupby('time_delta_with_previous_rental_in_minutes').count()
    canceled_mean = df_canceled_with_previous['time_delta_with_previous_rental_in_minutes'].mean()
    canceled_median = df_canceled_with_previous['time_delta_with_previous_rental_in_minutes'].median()

    with col7:

        # piechart for delay at checkout (under 12h)
        fig = px.pie(df_canceled_ratio,
             values = 'state',
             names = df_canceled_ratio.index,
            # title='Ratio of canceled reservation by time delta (Under12h only)',
             width= 1000
             )
        fig.update_traces(textposition = 'outside', textfont_size = 15)             
        fig.update_layout(title_x = 0.5, 
                  margin=dict(l=50,r=50,b=50,t=50,pad=4),
                  template = 'plotly_dark' )    
        st.plotly_chart(fig , use_container_width=True)

    with col8:

        st.subheader('Ratio of canceled reservations by time delta (Under12h only)')
        print()
        st.markdown('On this next chart I focused only on the canceled reservation when the time delta was below 12h.')
        print()
        st.markdown('Under 12hours it is easier to have an idea of the lack of time delta impact. \
            0min of time delta represents 15.3% of the chart and if we take for example all the data at 120min time delta or below this represents 38% of the chart. \
                That is more than a third of the canceled reservations (under 12hours delta).')


    col9, col10 = st.columns(2)

    with col9:
        
        fig = px.histogram(df_canceled_with_previous, x= 'time_delta_with_previous_rental_in_minutes',
                   #title = 'Count of time delta with previous rental in minutes',
                   color = 'checkin_type',
                   barmode = 'group',
                  ) 
        fig.update_layout(title_x = 0.5,
                  margin=dict(l=50,r=50,b=50,t=50,pad=4),
                  xaxis_title = 'minutes',
                  template = 'plotly_dark'
                  )   
        fig.add_vline(x = canceled_mean , line_width=2 , line_dash = 'dash' , line_color = 'yellow', annotation_text="Mean of values (300min)", annotation_position="top right")
        fig.add_vline(x = canceled_median , line_width=2 , line_dash = 'dash' , line_color = 'green', annotation_text="Median of values (210min)", annotation_position="top left")

        fig.update_xaxes(tickfont_size=15,)       

        st.plotly_chart(fig , use_container_width=True)

    with col10:

        st.subheader('Bar chart of the time delta with previous rental in min (under 12h)')
        print()
        st.markdown('As we began to see on the previous chart, time deltas below 2hours are a great share of our canceled reservations. \
            While the mean of the values is around 300min, it seems that 50% of those cancelations had a time delta below 210min.  ')

    #PART 2 - B - Analysis of the delay statistics  ---- global delays

    st.subheader('          Analysis of the delay statistics  ---- Global delays')
    print()
    print()
    print()
    st.markdown('For this part I took off of extremes values for a better analysis. Some delay at checkout were too long and I considered them as exceptions. I kept all the values below 2x the standard deviation')


    col11, col12 = st.columns(2)

    with col11:

        range = data.delay_at_checkout_in_minutes.mean() + data.delay_at_checkout_in_minutes.std()
        data_delay_cleaned = data[ (data.delay_at_checkout_in_minutes < range ) & ( data.delay_at_checkout_in_minutes > (-range))]

        fig = px.histogram(data_delay_cleaned, x= 'delay_at_checkout_in_minutes',

                   title = 'delay_at_checkout_in_minutes',
                   color = 'checkin_type',
                   barmode = 'group',
                  ) 
        fig.update_layout(title_x = 0.5,
                  margin=dict(l=50,r=50,b=50,t=50,pad=4),
                  xaxis_title = 'minutes',
                  template = 'plotly_dark'
                  )   
        fig.update_xaxes(tickfont_size=15,)    
        st.plotly_chart(fig , use_container_width=True)

    with col12:
        
        st.subheader('Distribution of the delay at checkout')
        print()
        print()
        print()
        st.markdown('We can see that the distribution of the delay is quite centered around 0 but the bars do down really fast after 0. \
            So it appears most of the delayed checkout are closer to the original time than the large and extreme values.            ')
        print()

    st.markdown('**Note:**') 
    st.markdown('the average delay at checkout is 17 minutes')
    st.markdown('the average delay at checkout FOR DELAYED CHECKOUT ONLY is 107 minutes')
    st.markdown('the median delay at checkout FOR DELAYED CHECKOUT ONLY  is 50 minutes')


    col13, col14 = st.columns(2)

    with col13:

        cleaned_delay_mean = data_delay_cleaned['delay_at_checkout_in_minutes'].mean()
        delay_only_mean = data_delay_cleaned['delay_at_checkout_in_minutes'][ data_delay_cleaned['delay_at_checkout_in_minutes'] > 0].mean()
        delay_only_median = data_delay_cleaned['delay_at_checkout_in_minutes'][ data_delay_cleaned['delay_at_checkout_in_minutes'] > 0].median()

        quantile70 = data_delay_cleaned['delay_at_checkout_in_minutes'][ data_delay_cleaned['delay_at_checkout_in_minutes'] > 0].quantile(.7)

        df_fig = data_delay_cleaned[ data['delay_at_checkout_in_minutes'] > 0]
        fig = px.box(df_fig, x = 'delay_at_checkout_in_minutes')

        fig.add_vline(x = delay_only_mean , line_width=2 , line_dash = 'dash' , line_color = 'red', annotation_text="Mean of values", annotation_position="top right")
        #fig.add_vline(x = delay_only_median , line_color = 'black' , annotation_text="Median of values", annotation_position="bottom right")
        fig.add_vline(x = quantile70 , line_color = 'green' , annotation_text="70 per cent of delayed checkout", annotation_position="bottom right")

        st.plotly_chart(fig , use_container_width=True)

    with col14:

        st.subheader('Statitics on the delays ONLY')
        print()
        st.markdown('With this chart it is clear that most of the delays are group "close" to 0. \
            We can see that a bit more than 70% of the delayed checkout are below the average delay (107min)')

    #PART 2 - C - Analysis of the delay statistics  ---- Specific delays


    st.subheader('          Analysis of the delay statistics  ---- Specific delays')

    st.markdown('To go further I decided to have a look on a specific category of delays. **I filtered the dataset to keep the reservations where the following one was canceled.** The aim was to see if the cancelation were due to a different delay than our global analysis.')
    st.subheader('')
    st.subheader('')
    st.subheader('')

    col15, col16 = st.columns(2)

    with col15:

        a_list = []

        for val in df_canceled_with_previous['previous_ended_rental_id']:
            a_list.append(val)

        df_shortlist = data[ data['rental_id'].isin(a_list)]
        df_shortlist['Late_or_Not'] = df_shortlist['delay_at_checkout_in_minutes'].apply(lambda x: 'Yes' if x > 0 else 'No')

        df_shortlist_type = (df_shortlist['checkin_type'].value_counts(normalize=True)*100).rename_axis('checkin_type').reset_index(name='counts')

        fig = px.pie(df_shortlist_type,
             values= 'counts',
             names = 'checkin_type',
             width= 1000,
             title='Proportions of type of reservation'
             )
        fig.update_traces(textposition = 'outside', textfont_size = 15)             
        fig.update_layout(title_x = 0.5, 
                  margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                  template = 'plotly_dark'
                  )  
        st.plotly_chart(fig , use_container_width=True)

    with col16:

        df_shortlist_late = (df_shortlist['Late_or_Not'].value_counts(normalize=True)*100).rename_axis('Late_or_Not').reset_index(name='counts')

        fig = px.pie(df_shortlist_late,
             values= 'counts',
             names = 'Late_or_Not',
             width= 1000,
             title='Ratio of delayed checkout or not'
             )
        fig.update_traces(textposition = 'outside', textfont_size = 15)             
        fig.update_layout(title_x = 0.5, 
                  margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                  template = 'plotly_dark'
                  )    
        st.plotly_chart(fig , use_container_width=True)

    st.subheader('')
    st.subheader('')
    st.markdown('**Note: The above charts shows that within this category only 47.9% of the checkout were delayed. That is a lot but this means that the delays themself dont explain all cancelations**. \
        We can also see that, like most charts, the distributions of type reservations in this category is quite similar.') 
    st.subheader('')
    st.subheader('')


    col17, col18 = st.columns(2)

    with col17:

        shortlist_delay_mean = df_shortlist['delay_at_checkout_in_minutes'].mean()
        shortlist_delay_only_mean = df_shortlist['delay_at_checkout_in_minutes'][ df_shortlist['delay_at_checkout_in_minutes'] > 0].mean()
        shortlist_delay_only_median = df_shortlist['delay_at_checkout_in_minutes'][ df_shortlist['delay_at_checkout_in_minutes'] > 0].median()
        quantile70 = df_shortlist['delay_at_checkout_in_minutes'][ df_shortlist['delay_at_checkout_in_minutes'] > 0].quantile(.7)

        df_fig = df_shortlist[ df_shortlist['delay_at_checkout_in_minutes'] > 0]        

        fig = px.box(df_fig, x = 'delay_at_checkout_in_minutes')

        fig.add_vline(x = shortlist_delay_only_mean , line_width=2 , line_dash = 'dash' , line_color = 'red', annotation_text= f"Average delay {shortlist_delay_only_mean} min", annotation_position="top right")
        #fig.add_vline(x = shortlist_delay_only_median , line_color = 'yellow' , annotation_text="Median of values", annotation_position="bottom right")
        fig.add_vline(x = quantile70 , line_color = 'green' , annotation_text="70 percent of the delayed checkout", annotation_position="bottom right")

        st.plotly_chart(fig , use_container_width=True)

    with col18:

        st.subheader('Statitics on the delays ONLY for the specific category')
        st.subheader('')
        st.markdown('This last chart shows a similar distribution with the first one.')
        st.markdown(' For this specific category the new values are:')
        st.markdown(' - average delay at checkout FOR DELAYED CHECKOUT ONLY is 129 minutes')
        st.markdown(' - median delay at checkout FOR DELAYED CHECKOUT ONLY  is 52 minutes')
        st.subheader('')
        st.subheader('')
        st.markdown(' The median delay is almost the same than before but the average delay went from 107 to 129min. \
            This conclude my EDA.')


# PART 3: Conclusion

def Report():
    st.title('Part 3: Analysis conclusion')

    st.subheader('')

    st.subheader('The aim of this study was to suggest a threshold between two reservations for the same vehicle and the scope of the reservations it should concern.')
    st.subheader('')
    st.subheader('First, the scope.')
    st.subheader('')
    st.markdown('The connect type represents only 20% of the bookings which not a lot but not negligible either. Most of the charts with both checkin type category shown that \
        the distributions of cancelations or delays were quite even. For this reason I believe the threshold should concern both types.')
    st.subheader('')
    st.subheader('Finally, the threshold.')
    st.subheader('')
    st.markdown('In the first part of the EDA we notice that if we exclude the reservations with a time delta over 12h \
        (or no previous reservation at all), the time delta below 120 minutes represents a big third of the canceled reservations and the ones below 210 min a half of them.')
    st.markdown('Then we analysed the delays and observed a mean between 107 and 129 minutes. We also noticed that around 70% of our delayed checkout were below those values and that half of the delays were under 50min. \
        We also need to keep in mind that the bigger the threshold is, the more impact it has on the ability of the user to loan his vehicle. \
        For those reasons I would suggest a threshold betweend 50min and 210min. Since I assume that most cancelations were not due to some delay at the checkout from the previous rental, i will take less the cancelations in consideration. \
            I would focus between 50 and 120 min and I would choose 120min as a threshold. This would absord around 70% of the usual delay and a third of canceled reservations.')




if __name__ == "__main__":
    main()