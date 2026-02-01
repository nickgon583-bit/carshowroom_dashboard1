import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Car Showroom | Interactive Dashboard",
    page_icon="🚗",
    layout="wide"
)

# =====================================================
# POWER BI COLOR PALETTE
# =====================================================
powerbi_colors = [
    "#01B8AA",  # Teal
    "#374649",  # Dark Gray
    "#FD625E",  # Red
    "#F2C80F",  # Yellow
    "#5F6B6D",  # Gray
    "#8AD4EB",  # Light Blue
    "#FE9666",  # Orange
    "#A66999",  # Purple
]

px.defaults.color_discrete_sequence = powerbi_colors
px.defaults.template = "plotly_white"

# =====================================================
# CUSTOM CSS FOR INTERACTIVE DASHBOARD
# =====================================================
st.markdown("""
<style>
/* Body background gradient */
body {
    background: linear-gradient(135deg, #f7f9fc, #e3e8f0);
}

/* Sidebar gradient like Power BI */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #01B8AA, #374649);
    color: white;
    font-weight: bold;
}

/* KPI Cards with different gradient colors */
.kpi-card-1 {
    background: linear-gradient(135deg, #FD625E, #F2C80F);
    color: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.15);
    text-align: center;
}
.kpi-card-2 {
    background: linear-gradient(135deg, #01B8AA, #8AD4EB);
    color: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.15);
    text-align: center;
}
.kpi-card-3 {
    background: linear-gradient(135deg, #FE9666, #A66999);
    color: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.15);
    text-align: center;
}

/* Section headers */
h1, h2, h3, h4, h5, h6 {
    color: #01B8AA;
    font-weight: bold;
}

/* Divider */
.stDivider {
    border-top: 2px solid #374649;
    margin: 20px 0px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# TITLE
# =====================================================
st.title("🚗 Car Showroom Sales Dashboard")

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data
def load_data():
    df = pd.read_csv("car_showroom_data.csv")
    df["SaleDate"] = pd.to_datetime(df["SaleDate"])
    df["Year"] = df["SaleDate"].dt.year.astype(str)
    df["Month"] = df["SaleDate"].dt.month
    df["MonthName"] = df["SaleDate"].dt.strftime("%b")
    return df

df = load_data()

# =====================================================
# SIDEBAR FILTERS
# =====================================================
st.sidebar.header("🎛 Filters")
year = st.sidebar.multiselect("Year", sorted(df["Year"].unique()), default=sorted(df["Year"].unique()))
city = st.sidebar.multiselect("City", sorted(df["City"].unique()), default=sorted(df["City"].unique()))
fuel = st.sidebar.multiselect("Fuel Type", sorted(df["FuelType"].unique()), default=sorted(df["FuelType"].unique()))

filtered_df = df[
    (df["Year"].isin(year)) &
    (df["City"].isin(city)) &
    (df["FuelType"].isin(fuel))
]

# =====================================================
# KPI CARDS (3 COLUMNS) WITH INTERACTIVE COLORS
# =====================================================
k1, k2, k3 = st.columns(3)

k1.markdown(f"""
<div class="kpi-card-1">
<h3>🚘 Cars Sold</h3>
<h2>{filtered_df.shape[0]:,}</h2>
</div>
""", unsafe_allow_html=True)

k2.markdown(f"""
<div class="kpi-card-2">
<h3>💰 Total Revenue</h3>
<h2>₹ {filtered_df['Price'].sum():,.0f}</h2>
</div>
""", unsafe_allow_html=True)

k3.markdown(f"""
<div class="kpi-card-3">
<h3>📊 Avg Price</h3>
<h2>₹ {filtered_df['Price'].mean():,.0f}</h2>
</div>
""", unsafe_allow_html=True)

st.divider()

# =====================================================
# SALES TRENDS
# =====================================================
st.subheader("📈 Sales Trend Analysis")
c1, c2 = st.columns(2)

with c1:
    yearly_sales = filtered_df.groupby("Year").size().reset_index(name="Sales")
    fig = px.line(yearly_sales, x="Year", y="Sales", markers=True, title="Year-wise Sales")
    fig.update_layout(plot_bgcolor='#f7f9fc', paper_bgcolor='#f7f9fc', font_color='#374649')
    st.plotly_chart(fig, use_container_width=True)

with c2:
    monthly_sales = filtered_df.groupby(["Year","MonthName"]).size().reset_index(name="Sales")
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    monthly_sales["MonthName"] = pd.Categorical(monthly_sales["MonthName"], categories=month_order, ordered=True)
    fig = px.bar(monthly_sales, x="MonthName", y="Sales", color="Year", title="Month-wise Sales")
    fig.update_layout(plot_bgcolor='#f7f9fc', paper_bgcolor='#f7f9fc', font_color='#374649')
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏙 City", "🚘 Product", "⛽ Fuel", "🧑‍💼 Salesperson", "🔥 Cross Analysis"
])

# TAB 1: CITY
with tab1:
    city_summary = filtered_df.groupby("City").agg(
        Sales=("Price","count"),
        Revenue=("Price","sum"),
        Avg_Price=("Price","mean")
    ).reset_index()
    fig = px.bar(city_summary, x="City", y="Revenue", text_auto=True, color_discrete_sequence=powerbi_colors)
    fig.update_layout(plot_bgcolor='#f7f9fc', paper_bgcolor='#f7f9fc', font_color='#374649')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(city_summary, use_container_width=True)

# TAB 2: PRODUCT
with tab2:
    model_perf = filtered_df.groupby("CarModel").agg(
        Units_Sold=("Price","count"),
        Revenue=("Price","sum")
    ).reset_index().sort_values("Revenue", ascending=False)
    fig = px.bar(model_perf.head(10), y="CarModel", x="Revenue", orientation="h",
                 text_auto=True, color_discrete_sequence=powerbi_colors)
    fig.update_layout(plot_bgcolor='#f7f9fc', paper_bgcolor='#f7f9fc', font_color='#374649')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(model_perf, use_container_width=True)

# TAB 3: FUEL
with tab3:
    fuel_count = filtered_df["FuelType"].value_counts().reset_index()
    fuel_count.columns = ["FuelType","Count"]
    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(fuel_count, names="FuelType", values="Count", hole=0.45, color_discrete_sequence=powerbi_colors)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fuel_revenue = filtered_df.groupby("FuelType")["Price"].sum().reset_index()
        fig = px.bar(fuel_revenue, x="FuelType", y="Price", text_auto=True, color_discrete_sequence=powerbi_colors)
        st.plotly_chart(fig, use_container_width=True)

# TAB 4: SALESPERSON
with tab4:
    sales_perf = filtered_df.groupby("SalesPersonID").agg(
        Cars_Sold=("Price","count"),
        Revenue=("Price","sum")
    ).reset_index().sort_values("Revenue", ascending=False)
    fig = px.bar(sales_perf.head(10), x="SalesPersonID", y="Revenue",
                 text_auto=True, color_discrete_sequence=powerbi_colors)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(sales_perf, use_container_width=True)

# TAB 5: CROSS ANALYSIS
with tab5:
    cross_df = pd.crosstab(filtered_df["City"], filtered_df["FuelType"])
    fig = px.imshow(cross_df, text_auto=True, color_continuous_scale=px.colors.sequential.Plasma)
    st.plotly_chart(fig, use_container_width=True)

# FOOTER
st.markdown("---")
st.caption("🚀 Power BI–style Interactive Dashboard (Colorful Theme)")