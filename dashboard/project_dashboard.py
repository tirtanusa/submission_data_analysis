import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set_theme(style='dark')

def create_highest_city_revenue_df(df):
    highest_city_revenue_df = df.groupby(by='customer_city').total_order_value.sum().reset_index()
    highest_city_revenue_df.sort_values(by='total_order_value',ascending=False,inplace=True)

    return highest_city_revenue_df

def create_top_categories_bycity_df(df):
    customer_in_city_df = df.rename(columns={"product_category_name_english" : "category_name"})

    return customer_in_city_df
def specified_city(df,city):
    lowercase_city = city.lower()
    customer_city_df = df[df.customer_city == lowercase_city]
    titles = "5 Most Popular Products in " + city
    return customer_city_df, titles

def show_figures(df,titles):
    city_agg_df = df.groupby(by="category_name").agg({
        'order_id' : 'nunique'
    },inplace=True).reset_index()

    city_agg_df.sort_values(by='order_id', ascending=False,inplace=True)
    fig, ax = plt.subplots(figsize=(20, 10))
    
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    
    sns.barplot(
        y="category_name", 
        x="order_id",
        data=city_agg_df.head(5),
        palette=colors
    )
    ax.set_title(titles, loc="center", fontsize=30)
    ax.set_ylabel("Amount of Transaction", fontsize=20)
    ax.set_xlabel("Category", fontsize=20)
    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20)
    st.pyplot(fig)

def create_transaction_df(df):
    transaction_df = df[["order_id","order_approved_at"]]
    transaction_df['order_approved_at'] = pd.to_datetime(transaction_df['order_approved_at'])
    transaction_df = transaction_df.resample(rule ='M', on='order_approved_at').agg({
        'order_id' : 'nunique'
    })
    transaction_df.index = transaction_df.index.strftime("%Y-%m")
    transaction_df.sort_values(by='order_approved_at', ascending=True,inplace=True)

    transaction_df = transaction_df.rename(columns={
        'order_id' : 'order_count'
    }).reset_index()

    return transaction_df

def create_rfm_df(df):
    df['order_approved_at'] = pd.to_datetime(df['order_approved_at'])
    rfm_df = df.groupby(by="customer_id", as_index = False).agg({
        "order_approved_at" : 'max', #Recency
        'order_id' : 'count', #Frequency
        'total_order_value' : 'sum' #Monetary
    })

    #Renaming Column 
    rfm_df.rename(columns={
        'order_approved_at' : 'Recency',
        'order_id' : 'Frequency',
        'total_order_value' : 'Monetary'
    },inplace=True)

    #Making the customer_id easier to read on visualization
    rfm_df['customer_unique_id'] = pd.factorize(rfm_df['customer_id'])[0]+1


    #Counting the latest Transaction (in days format)
    rfm_df['Recency'] = rfm_df['Recency'].dt.date
    recent_date = df['order_approved_at'].dt.date.max() #Taking the last purchase recorded
    rfm_df['Recency']= rfm_df['Recency'].apply(lambda x: (recent_date-x).days) #Counting days started from approved date to the last purchase recorded

    return rfm_df

def create_payment_method_df(df):
    customers_payment_df = all_df[['payment_type','order_id','payment_installments']]
    customers_payment_df =customers_payment_df .rename(columns={"product_category_name_english" : "category_name"})
    customers_payment_agg_df = customers_payment_df .groupby(by="payment_type").agg({
        'order_id' : 'nunique'
    },inplace=True).reset_index()

    customers_payment_agg_df.sort_values(by='order_id', ascending=False,inplace=True)
    return customers_payment_agg_df


all_df = pd.read_csv('https://raw.githubusercontent.com/tirtanusa/submission_data_analysis/main/dashboard/Project_data.csv')

st.header('Data Analysis Project : E-Commerce Public Dataset :flag-br: :shopping_trolley:',divider='red')

#Preparing Dataset for each Visuals
highest_city_revenue_df = create_highest_city_revenue_df(all_df)
top_categories_bycity_df= create_top_categories_bycity_df(all_df)
transaction_df = create_transaction_df(all_df)
rfm_df = create_rfm_df(all_df)
payment_method_df = create_payment_method_df(all_df)

st.subheader('Top 5 Highest Revenue-Generating City')

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    y = "total_order_value",
    x = "customer_city",
    data =highest_city_revenue_df.head(5),
    palette = colors
)

ax.set_title("Top 5 Highest Revenue-Generating City", loc = "center", fontsize =30)
ax.set_ylabel("Revenue (in Millions)",fontsize =20)
ax.set_xlabel("City",fontsize=20)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=20)
st.pyplot(fig)

st.subheader("Top 5 Most Popular Category in the Leading Cities")
tab1,tab2,tab3,tab4,tab5 = st.tabs(['Sao Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasilia', 'Curitiba'])

with tab1:
    sao_paulo_df,titles = specified_city(top_categories_bycity_df,'Sao Paulo')
    show_figures(sao_paulo_df,titles)
with tab2:
    rdj_df,titles= specified_city(top_categories_bycity_df,'Rio de Janeiro')
    show_figures(rdj_df,titles)
with tab3:
    belh_df,titles =specified_city(top_categories_bycity_df, 'Belo Horizonte')
    show_figures(belh_df,titles)
with tab4:
    bra_df,titles = specified_city(top_categories_bycity_df,'Brasilia')
    show_figures(bra_df,titles)
with tab5:
    cur_df,titles = specified_city(top_categories_bycity_df, 'Curitiba')
    show_figures(cur_df,titles)


tab1,tab2 = st.tabs(['Order Frequencies','RFM Analysis'])

with tab1:
    transaction_df['order_approved_at'] = pd.to_datetime(transaction_df['order_approved_at'])
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.plot(transaction_df['order_approved_at'],transaction_df['order_count'],marker ='o', linewidth =2, color = "#72BCD4")
    ax.set_title("Frequencies of Order Per Month", loc='center', fontsize = 20)
    ax.tick_params(axis='x',labelrotation =45,labelsize = 20)
    ax.tick_params(axis='y',labelsize= 20)
    st.pyplot(fig)
with tab2:
    #Taking only the top 5 so the proccess will go faster
    top_recent = rfm_df.sort_values(by='Recency',ascending=True).head(5)
    top_monetary = rfm_df.sort_values(by='Monetary',ascending=False).head(5)
    top_freq = rfm_df.sort_values(by='Frequency',ascending=False).head(5)

    # Create a figure with subplots
    fig, axes = plt.subplots(1, 3, figsize=(20, 10))  # Corrected `subplot` to `subplots`

    # Plot distribution of Recency Score
    sns.barplot(y='Recency', x='customer_unique_id', data=top_recent, palette='Blues', ax=axes[0])
    axes[0].set_title('Distribution of Recency Score (Days)', fontsize =25)
    axes[0].tick_params(axis='y',labelsize= 20)
    axes[0].tick_params(axis='x',labelsize= 20)
    axes[0].set_ylim(bottom=0)  # Ensure y-axis starts at 0

    # Plot distribution of Frequency Score
    sns.barplot(y='Frequency', x='customer_unique_id', data=top_freq, palette='Blues', ax=axes[1])
    axes[1].set_title('Distribution of Frequency Score',fontsize =25)
    axes[1].tick_params(axis='y',labelsize= 20)
    axes[1].tick_params(axis='x',labelsize= 20)
    axes[1].set_ylim(bottom=0)  # Ensure y-axis starts at 0

    # Plot distribution of Monetary Score
    sns.barplot(y='Monetary', x='customer_unique_id', data=top_monetary, palette='Blues', ax=axes[2])
    axes[2].set_title('Distribution of Monetary Score',fontsize =25)
    axes[2].tick_params(axis='y',labelsize= 20)
    axes[2].tick_params(axis='x',labelsize= 20)
    axes[2].set_ylim(bottom=0)  # Ensure y-axis starts at 0

    # Adjust layout
    plt.tight_layout()

    # Use Streamlit to display the figure
    st.pyplot(fig)
    with st.expander("See Explanation"):
        st.write(""" 1. ***Recency Score (Days)***: This chart displays the days elapsed since the last transaction for each customer. The scores are very close to zero, suggesting that these customers have made purchases very recently. Customers are represented by their encoded unique IDs on the x-axis, which makes the chart more readable.

2. ***Frequency Score***: The middle chart shows the number of transactions for each customer. Unlike the Recency scores, the Frequency scores have a wider range, indicating variability in how often customers make purchases. Some customers have made significantly more purchases than others, as seen by the varying heights of the bars.

3. ***Monetary Score***: The third chart on the right illustrates the total monetary value of purchases made by each customer. The values here differ considerably, indicating that some customers have spent much more than others. This could be due to either the number of transactions or the value of individual transactions.""")

st.subheader('Most Prefered Payment Method :credit_card:')
    
fig, ax = plt.subplots(figsize=(20,10))

ax.set_title('Most Prefered Payment Method', fontsize =30)
sns.barplot(
    y= 'payment_type',
    x='order_id',
    data = payment_method_df.head(5),
    palette = colors
)
ax.set_xlabel('Amount of Transaction',fontsize = 25)
ax.set_ylabel('Category', fontsize =25)
ax.tick_params(axis ='x',labelsize =20)
ax.tick_params(axis ='y',labelsize =20)
st.pyplot(fig)

st.header(" ", divider='red')
st.markdown("<footer style='text-align: center; color: white;'>Tirtanusa Kurnia Adhi Perdana - Bangkit 2024</footer>", unsafe_allow_html=True)
