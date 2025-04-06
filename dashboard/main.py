import streamlit as st
import pandas as pd

from numerize.numerize import numerize

def load_data():
    orders_df = pd.read_csv('data/dashboard/orders_analyzed.csv')
    orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
    orders_df['order_purchase_timestamp'] = orders_df['order_purchase_timestamp'].dt.date

    # add geolocation data
    geodata_df = load_geodata()
    orders_df = pd.merge(orders_df, geodata_df, how='left', on='customer_state')

    # add state count
    orders_df['state_count'] = orders_df['customer_state'].map(orders_df['customer_state'].value_counts())

    order_items_df = pd.read_csv('data/dashboard/order_items_analyzed.csv')
    order_items_df['shipping_limit_date'] = pd.to_datetime(order_items_df['shipping_limit_date'])
    order_items_df['shipping_limit_date'] = order_items_df['shipping_limit_date'].dt.date

    return orders_df, order_items_df

def load_geodata():
    geodata_df = pd.read_csv('data/dashboard/geolocation_dataset.csv')
    geodata_df = geodata_df.drop_duplicates(subset=['geolocation_state'], keep='first')
    geodata_df = geodata_df[["geolocation_state", "geolocation_lat", "geolocation_lng"]]
    geodata_df.columns = ["customer_state", "lat", "lon"]
    return geodata_df

def get_metrics_data(df1, df2):
    total_orders = len(df1)
    total_items = len(df2)
    total_revenue = df2['price'].sum()
    
    return total_orders, total_items, total_revenue

def get_daily_orders(df):
    daily_orders = df['order_purchase_timestamp'].value_counts().reset_index()
    daily_orders = daily_orders.set_index("order_purchase_timestamp").sort_index()
    return daily_orders

def get_product_category(df):
    product_category = df.groupby(['product_category_name_english']).size().sort_values(ascending=False)
    return product_category

def dashboard_components(filtered_orders, filtered_order_items):
    # Metrics
    col1, col2, col3 = st.columns(3)
    total_orders, total_items, total_revenue = get_metrics_data(filtered_orders, filtered_order_items)

    col1.metric("Total Orders", numerize(total_orders), border=True)
    col2.metric("Total Items", numerize(total_items), border=True)
    col3.metric("Total Revenue", numerize(total_revenue), border=True)
    
    # Daily Line Chart
    st.write("Daily Orders Over Time")
    daily_orders = get_daily_orders(filtered_orders)
    st.line_chart(daily_orders, x_label= "Order Date", y_label= "Number of Orders")
    
    # Bar Chart
    product_category = get_product_category(filtered_order_items)
    most_ordered_items = product_category.head()
    least_ordered_items = product_category.tail()

    st.write("Top 5 and Bottom 5 Sold Product Categories")
    col1, col2 = st.columns(2)
    col1.bar_chart(most_ordered_items, x_label= "Total", y_label= "Product Category", horizontal=True, color="#0000FF")
    col2.bar_chart(least_ordered_items, x_label= "Total", horizontal=True, color="#FF0000")

    # Map
    st.write("Top 5 Cities")
    top_5_city = filtered_orders['customer_city'].value_counts().head(5)
    st.bar_chart(top_5_city)

    st.write("Top 5 States")
    top_5_state = filtered_orders['customer_state'].value_counts().head(5)
    st.bar_chart(top_5_state)

    st.write("States Distribution")
    st.map(filtered_orders, size="state_count")


def main():
    st.title("Ecommerce Data Dashboard")

    orders_df, order_items_df = load_data()

    with st.sidebar as sidebar:
        st.write("Filter Date")

        start_date = st.date_input("Start Date", value="2016-09-15")
        end_date = st.date_input("End Date", value="2018-08-29")
        apply_filter = st.button("Apply Filter")
    
    if apply_filter:
        st.write(f"Filter applied from {start_date} to {end_date}")

        filtered_orders = orders_df[(orders_df['order_purchase_timestamp'] >= start_date) & (orders_df['order_purchase_timestamp'] <= end_date)]
        filtered_order_items = order_items_df[(order_items_df['shipping_limit_date'] >= start_date) & (order_items_df['shipping_limit_date'] <= end_date)]

        dashboard_components(filtered_orders, filtered_order_items)
    
    else:
        st.write(f"Filter applied from {start_date} to {end_date}")
        dashboard_components(orders_df, order_items_df)
        

if __name__ == "__main__":
    st.set_page_config(
        page_title="Ecommerce Data Dashboard",
        page_icon=":chart_with_upwards_trend:",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    main()