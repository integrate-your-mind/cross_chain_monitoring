# Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp

# Layout
st.set_page_config(page_title='USDC Transfers - Cross Chain Monitoring', page_icon=':bar_chart:', layout='wide')
st.title('💸 USDC Transfers')

# Style
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

# Data Sources
@st.cache(ttl=600)
def get_data(data_sector, data_type):
    if data_sector == 'Transfers':
        if data_type == 'Overview':
            return pd.read_json('https://node-api.flipsidecrypto.com/api/v2/queries/41eb418f-d231-4a1f-a1c8-e7cc0ff2fddb/data/latest')
        elif data_type == 'Daily':
            return pd.read_json('https://node-api.flipsidecrypto.com/api/v2/queries/76276234-81ba-44fd-8341-7cde62d30abc/data/latest')
        elif data_type == 'Heatmap':
            return pd.read_json('https://node-api.flipsidecrypto.com/api/v2/queries/933b930f-b611-469e-9e03-b0d5c5b0242b/data/latest')
        elif data_type == 'Distribution':
            return pd.read_json('https://node-api.flipsidecrypto.com/api/v2/queries/a17c8548-2834-4600-bc78-a0efb6d12de4/data/latest')
        elif data_type == 'Transferring Users':
            return pd.read_json('https://node-api.flipsidecrypto.com/api/v2/queries/2f9e94d0-79b9-49a5-be9a-eb289e9890d4/data/latest')
        elif data_type == 'Wallet Types':
            return pd.read_json('https://node-api.flipsidecrypto.com/api/v2/queries/cc07b022-fd08-459f-a9a3-cf8082221414/data/latest')
    return None

transfers_overview = get_data('Transfers', 'Overview')
transfers_daily = get_data('Transfers', 'Daily')
transfers_heatmap = get_data('Transfers', 'Heatmap')
transfers_distribution = get_data('Transfers', 'Distribution')
transfers_transferring_users = get_data('Transfers', 'Transferring Users')
transfers_wallet_types = get_data('Transfers', 'Wallet Types')

# Filter the blockchains
options = st.multiselect(
    '**Select your desired blockchains:**',
    options=transfers_overview['Blockchain'].unique(),
    default=transfers_overview['Blockchain'].unique(),
    key='transfers_options'
)

# Selected Blockchain
if len(options) == 0:
    st.warning('Please select at least one blockchain to see the metrics.')

# Single chain Analysis
elif len(options) == 1:
    st.subheader('Overview')
    df = transfers_overview.query("Blockchain == @options")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label='Volume', value=df['Volume'].round(), help='USD')
        st.metric(label='Volume/Day', value=df['Volume/Day'].round(), help='USD')
    with c2:
        st.metric(label='Transfers', value=df['Transfers'])
        st.metric(label='Transfers/Day', value=df['Transfers/Day'].round())
    with c3:
        st.metric(label='Users', value=df['Users'])
        st.metric(label='Users/Day', value=df['Users/Day'].round())
    with c4:
        st.metric(label='Average Amount', value=df['AmountAverage'].round(2), help='USD')
        st.metric(label='Median Amount', value=df['AmountMedian'].round(2), help='USD')
    
    st.subheader('Distribution')
    df = transfers_distribution.query("Blockchain == @options")
    c1, c2, c3 = st.columns(3)
    with c1:
        fig = px.pie(df, values='Volume', names='Bucket', title='Share of Total Transferred Volume')
        fig.update_layout(showlegend=False)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.pie(df, values='Transfers', names='Bucket', title='Share of Total Transfers')
        fig.update_layout(showlegend=False)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)
    with c3:
        fig = px.pie(df, values='Users', names='Bucket', title='Share of Total Transferring Users')
        fig.update_layout(showlegend=False)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader('Activity Over Time')
    df = transfers_daily.query("Blockchain == @options")

    fig = px.area(df, x='Date', y='Volume', title='Daily Transferred Volume')
    fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = sp.make_subplots(specs=[[{'secondary_y': True}]])
        fig.add_trace(go.Bar(x=df['Date'], y=df['Transfers'], name='Transfers'), secondary_y=False)
        fig.add_trace(go.Line(x=df['Date'], y=df['Users'], name='Users'), secondary_y=True)
        fig.update_layout(title_text='Daily Transfers and Transferring Users')
        fig.update_yaxes(title_text='Transfers', secondary_y=False)
        fig.update_yaxes(title_text='Users', secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = sp.make_subplots(specs=[[{'secondary_y': True}]])
        fig.add_trace(go.Bar(x=df['Date'], y=df['AmountAverage'], name='Average'), secondary_y=False)
        fig.add_trace(go.Line(x=df['Date'], y=df['AmountMedian'], name='Median'), secondary_y=True)
        fig.update_layout(title_text='Daily Average and Median Transferred Amount')
        fig.update_yaxes(title_text='Average', secondary_y=False)
        fig.update_yaxes(title_text='Median', secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader('Activity Heatmap')
    df = transfers_heatmap.query("Blockchain == @options")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.scatter(df, x='Hour', y='Day', size='Volume', color='Volume', title='Heatmap of Transferred Volume')
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

        fig = px.scatter(df, x='Hour', y='Day', size='AmountAverage', color='AmountAverage', title='Heatmap of Average Transferred Amount')
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.scatter(df, x='Hour', y='Day', size='Transfers', color='Transfers', title='Heatmap of Transfers')
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

        fig = px.scatter(df, x='Hour', y='Day', size='Users', color='Users', title='Heatmap of Transferring Users')
        fig.update_layout(xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader('Wallet Types of Transferring Users')
    df = transfers_wallet_types.query('Blockchain == @options')
    c1, c2, c3 = st.columns(3)
    with c1:
        fig = px.bar(df, x='Wallet', y='Volume', color='Wallet', title='Total Transferred Volume of Each Wallet Type')
        fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, xaxis={'categoryorder':'total ascending'})
        fig.update_xaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)

        fig = px.pie(df, values='Volume', names='Wallet', title='Share of Total Transferred Volume of Each Wallet Type')
        fig.update_layout(showlegend=False)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(df, x='Wallet', y='Transfers', color='Wallet', title='Total Transfers of Each Wallet Type')
        fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, xaxis={'categoryorder':'total ascending'})
        fig.update_xaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)

        fig = px.pie(df, values='Transfers', names='Wallet', title='Share of Total Transfers of Each Wallet Type')
        fig.update_layout(showlegend=False)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)
    with c3:
        fig = px.bar(df, x='Wallet', y='Users', color='Wallet', title='Total Transferring Users of Each Wallet Type')
        fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, xaxis={'categoryorder':'total ascending'})
        fig.update_xaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)

        fig = px.pie(df, values='Users', names='Wallet', title='Share of Total Transferring Users of Each Wallet Type')
        fig.update_layout(showlegend=False)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader('Top Transferring Users')
    df = transfers_transferring_users.query("Blockchain == @options")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(df, x='User', y='Transfers', color='User', title='Total Transfers By Top Transferring Users')
        fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, xaxis={'categoryorder':'total ascending'})
        fig.update_xaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(df, x='User', y='Volume', color='User', title='Total Transferred Volume By Top Transferring Users')
        fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, xaxis={'categoryorder':'total ascending'})
        fig.update_xaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)

# Cross Chain Comparison
else:
    subtab_overview, subtab_amounts, subtab_heatmap, subtab_distribution = st.tabs(['Overview', 'Amounts', 'Heatmap', 'Distribution'])

    with subtab_overview:
        st.subheader('Overview')
        df = transfers_overview.query("Blockchain == @options")
        c1, c2, c3 = st.columns(3)
        with c1:
            fig = px.bar(df, x='Blockchain', y='Volume', color='Blockchain', title='Total Transferred Volume', log_y=True)
            fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, xaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

            fig = px.bar(df, x='Blockchain', y='Transfers', color='Blockchain', title='Total Transfers', log_y=True)
            fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, xaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

            fig = px.bar(df, x='Blockchain', y='Users', color='Blockchain', title='Total Transferring Users', log_y=True)
            fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, xaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.pie(df, values='Volume', names='Blockchain', title='Share of Total Transferred Volume')
            fig.update_layout(showlegend=False)
            fig.update_traces(textinfo='percent+label', textposition='inside')
            st.plotly_chart(fig, use_container_width=True)

            fig = px.pie(df, values='Transfers', names='Blockchain', title='Share of Total Transfers')
            fig.update_layout(showlegend=False)
            fig.update_traces(textinfo='percent+label', textposition='inside')
            st.plotly_chart(fig, use_container_width=True)

            fig = px.pie(df, values='Users', names='Blockchain', title='Share of Total Transferring Users')
            fig.update_layout(showlegend=False)
            fig.update_traces(textinfo='percent+label', textposition='inside')
            st.plotly_chart(fig, use_container_width=True)
        with c3:
            fig = px.bar(df, x='Blockchain', y='Volume/Day', color='Blockchain', title='Average Transferred Volume/Day', log_y=True)
            fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, xaxis={'categoryorder':'category ascending'})
            st.plotly_chart(fig, use_container_width=True)

            fig = px.bar(df, x='Blockchain', y='Transfers/Day', color='Blockchain', title='Average Transfers/Day', log_y=True)
            fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, xaxis={'categoryorder':'category ascending'})
            st.plotly_chart(fig, use_container_width=True)

            fig = px.bar(df, x='Blockchain', y='Users/Day', color='Blockchain', title='Average Transferring Users/Day', log_y=True)
            fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, xaxis={'categoryorder':'category ascending'})
            st.plotly_chart(fig, use_container_width=True)

        st.subheader('Transfers Over Time')
        df = transfers_daily.query("Blockchain == @options")
        c1, c2 = st.columns(2)
        with c1:
            fig = px.line(df, x='Date', y='Volume', color='Blockchain', title='Daily Transferred Volume', log_y=True)
            fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df, x='Date', y='Transfers', color='Blockchain', title='Daily Transfers', log_y=True)
            fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df, x='Date', y='Users', color='Blockchain', title='Daily Transferring Users', log_y=True)
            fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = go.Figure()
            for i in options:
                fig.add_trace(go.Scatter(
                    name=i,
                    x=df.query("Blockchain == @i")['Date'],
                    y=df.query("Blockchain == @i")['Volume'],
                    mode='lines',
                    stackgroup='one',
                    groupnorm='percent'
                ))
            fig.update_layout(title='Daily Share of Transferred Volume')
            st.plotly_chart(fig, use_container_width=True)
            
            fig = go.Figure()
            for i in options:
                fig.add_trace(go.Scatter(
                    name=i,
                    x=df.query("Blockchain == @i")['Date'],
                    y=df.query("Blockchain == @i")['Transfers'],
                    mode='lines',
                    stackgroup='one',
                    groupnorm='percent'
                ))
            fig.update_layout(title='Daily Share of Transfers')
            st.plotly_chart(fig, use_container_width=True)

            fig = go.Figure()
            for i in options:
                fig.add_trace(go.Scatter(
                    name=i,
                    x=df.query("Blockchain == @i")['Date'],
                    y=df.query("Blockchain == @i")['Users'],
                    mode='lines',
                    stackgroup='one',
                    groupnorm='percent'
                ))
            fig.update_layout(title='Daily Share of Transferring Users')
            st.plotly_chart(fig, use_container_width=True)

    with subtab_amounts:
        st.subheader("Transferred Amount")
        c1, c2 = st.columns([1, 2])
        with c1:
            df = transfers_overview.query("Blockchain == @options")

            fig = px.bar(transfers_overview, x='Blockchain', y='AmountAverage', color='Blockchain', title='Average Transferred Amount', log_y=True)
            fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, xaxis={'categoryorder':'category ascending'})
            st.plotly_chart(fig, use_container_width=True)

            fig = px.bar(transfers_overview, x='Blockchain', y='AmountMedian', color='Blockchain', title='Median Transferred Amount', log_y=True)
            fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, xaxis={'categoryorder':'category ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            df = transfers_daily.query("Blockchain == @options")

            fig = px.line(df, x='Date', y='AmountAverage', color='Blockchain', title='Daily Average Transferred Amount')
            fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df, x='Date', y='AmountMedian', color='Blockchain', title='Daily Median Transferred Amount')
            fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)

    with subtab_heatmap:
        st.subheader('Daily and Hourly Heatmap of Transfers')
        c1, c2 = st.columns(2)
        df = transfers_heatmap.query('Blockchain == @options')
        with c1:
            fig = px.scatter(df, x='Volume', y='Day', color='Blockchain', title='Daily Heatmap of Transferred Volume', log_x=True)
            fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)

            fig = px.scatter(df, x='Transfers', y='Day', color='Blockchain', title='Daily Heatmap of Transfers', log_x=True)
            fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)

            fig = px.scatter(df, x='Users', y='Day', color='Blockchain', title='Daily Heatmap of Transferring Users', log_x=True)
            fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)

            fig = px.scatter(df, x='AmountAverage', y='Day', color='Blockchain', title='Daily Heatmap of Average Transferred Amount', log_x=True)
            fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.scatter(df, x='Volume', y='Hour', color='Blockchain', title='Hourly Heatmap of Transferred Volume', log_x=True)
            fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)

            fig = px.scatter(df, x='Transfers', y='Hour', color='Blockchain', title='Hourly Heatmap of Transfers', log_x=True)
            fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)

            fig = px.scatter(df, x='Users', y='Hour', color='Blockchain', title='Hourly Heatmap of Transferring Users', log_x=True)
            fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)

            fig = px.scatter(df, x='AmountAverage', y='Hour', color='Blockchain', title='Hourly Heatmap of Average Transferred Amount', log_x=True)
            fig.update_layout(legend_title=None, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)

    with subtab_distribution:
        st.subheader('Transferred Amount Size Distribution')
        c1, c2 = st.columns(2)
        df = transfers_distribution.query("Blockchain == @options").sort_values(['Blockchain', 'Bucket'])
        with c1:
            fig = px.bar(df, x='Blockchain', y='Volume', color='Bucket', title='Total Transferred Volume of Each Group')
            fig.update_layout(xaxis_title=None, yaxis_title=None, xaxis={'categoryorder':'category ascending'})
            st.plotly_chart(fig, use_container_width=True)

            fig = px.bar(df, x='Blockchain', y='Transfers', color='Bucket', title='Total Transfers of Each Group')
            fig.update_layout(xaxis_title=None, yaxis_title=None, xaxis={'categoryorder':'category ascending'})
            st.plotly_chart(fig, use_container_width=True)

            fig = px.bar(df, x='Blockchain', y='Users', color='Bucket', title='Total Transferring Users of Each Group')
            fig.update_layout(xaxis_title=None, yaxis_title=None, xaxis={'categoryorder':'category ascending'})
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = go.Figure()
            for i in df['Bucket'].unique():
                fig.add_trace(go.Scatter(
                    name=i,
                    x=df.query("Bucket == @i")['Blockchain'],
                    y=df.query("Bucket == @i")['Volume'],
                    mode='lines',
                    stackgroup='one',
                    groupnorm='percent'
                ))
            fig.update_layout(title='Share of Total Transferred Volume of Each Group')
            st.plotly_chart(fig, use_container_width=True)

            fig = go.Figure()
            for i in df['Bucket'].unique():
                fig.add_trace(go.Scatter(
                    name=i,
                    x=df.query("Bucket == @i")['Blockchain'],
                    y=df.query("Bucket == @i")['Transfers'],
                    mode='lines',
                    stackgroup='one',
                    groupnorm='percent'
                ))
            fig.update_layout(title='Share of Total Transfers of Each Group')
            st.plotly_chart(fig, use_container_width=True)

            fig = go.Figure()
            for i in df['Bucket'].unique():
                fig.add_trace(go.Scatter(
                    name=i,
                    x=df.query("Bucket == @i")['Blockchain'],
                    y=df.query("Bucket == @i")['Users'],
                    mode='lines',
                    stackgroup='one',
                    groupnorm='percent'
                ))
            fig.update_layout(title='Share of Total Transferring Users of Each Group')
            st.plotly_chart(fig, use_container_width=True)