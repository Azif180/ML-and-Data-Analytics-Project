import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
df = pd.read_csv("Jan-Dec Dataset.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# Clean 'Amount_lost' column to numeric
df['amount_lost'] = (
    df['amount_lost']
    .astype(str)
    .str.replace(r'[$,]', '', regex=True)
    .astype(float)
)

# Streamlit setup
st.set_page_config(page_title="Azif's FYP2", layout="wide")
st.title("Australia Scam Cases Dashboard (Jan-July 2024)")

total_cases = df['number_of_reports'].sum()
total_loss = df['amount_lost'].sum()
australia_population_2025 = 26800000

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.markdown(f"""
        <div style="background-color:#f2f2f2; padding:20px; border-radius:10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.05); text-align:center;">
            <h3> Total Cases</h3>
            <h2>{total_cases:,.0f}</h2>
        </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
        <div style="background-color:#f2f2f2; padding:20px; border-radius:10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.05); text-align:center;">
            <h3> Total Loss ($)</h3>
            <h2>${total_loss:,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
        <div style="background-color:#f2f2f2; padding:20px; border-radius:10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.05); text-align:center;">
            <h3> Population (2025)</h3>
            <h2>{australia_population_2025:,}</h2>
        </div>
    """, unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("Filters")

# Global State filter (for all graph)
unique_states = sorted(df['state'].dropna().unique())
selected_states = st.sidebar.multiselect("Filter by State:", unique_states, default=unique_states)

# Filter dataframe globally based on selected states
df = df[df['state'].isin(selected_states)]

# Scam Category filter (for VIZ 3)
unique_categories = sorted(df['scam_category'].dropna().unique())
select_all = st.sidebar.checkbox("Select All Scam Categories", value=True)
if select_all:
    selected_categories = st.sidebar.multiselect("Filter by Scam Category:", unique_categories, default=unique_categories)
else:
    selected_categories = st.sidebar.multiselect("Filter by Scam Category:", unique_categories)

# Age Group filter (for VIZ 2 & VIZ 4)
unique_age_groups = sorted(df['age_group'].dropna().unique())
selected_age_groups = st.sidebar.multiselect("Filter by Age Group:", unique_age_groups, default=unique_age_groups)

# ----------------------------------------
# VIZ 1: Treemap of Reports by State
# ----------------------------------------
report_counts = df['state'].value_counts().reset_index()
report_counts.columns = ['state', 'number_of_reports']
report_counts = report_counts.sort_values(by='number_of_reports', ascending=False)
fig1 = px.treemap(
    report_counts,
    path=['state'],
    values='number_of_reports',
    color='number_of_reports',
    color_continuous_scale='Oranges',
    title=""
)
fig1.update_layout(margin=dict(t=50, l=10, r=10, b=10))

# ----------------------------------------
# VIZ 2: Bar Chart - Reports by Age Group & Gender (with age filter)
# ----------------------------------------
age_gender_counts = df[df['age_group'].isin(selected_age_groups)].groupby(['age_group', 'gender'])['number_of_reports'].sum().reset_index()

gender_order = ['Male', 'Female']

fig2 = px.bar(
    age_gender_counts,
    x='age_group',
    y='number_of_reports',
    color='gender',
    barmode='group',
    title="",
    category_orders={'gender': gender_order},
    color_discrete_map={
        'Male': '#87CEFA',   # Blue
        'Female': '#e377c2'  # Pink
    }
)
fig2.update_layout(xaxis_title="Age Group", yaxis_title="Number of Reports", margin=dict(t=50, l=10, r=10, b=10))

# VIZ 3: Bar Chart - Reports by Scam Category and Scam Type
filtered_df3 = df[df['scam_category'].isin(selected_categories)].copy()
filtered_df3['scam_category_type'] = filtered_df3['scam_category'].str.strip() + ' / ' + filtered_df3['scam_type'].str.strip()
scam_counts = filtered_df3.groupby('scam_category_type')['number_of_reports'].sum().reset_index()
scam_counts = scam_counts.sort_values(by='number_of_reports', ascending=True)

fig3 = px.bar(
    scam_counts,
    x='number_of_reports',
    y='scam_category_type',
    orientation='h',
    title="",
    color_discrete_sequence=['#EF553B']
)
fig3.update_layout(
    xaxis_title="Number of Reports",
    yaxis_title="",
    showlegend=False,
    margin=dict(l=40, r=10, t=50, b=10)
)

# Layout with columns: VIZ 1, 2, 3 side by side
col1, col2, col3 = st.columns([1,1,1])

with col1:
    st.subheader("Scam Reports by State")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Scam Reports by Age Group and Gender")
    st.plotly_chart(fig2, use_container_width=True)

with col3:
    st.subheader("Number of Reports by Scam Category and Scam Type")
    st.plotly_chart(fig3, use_container_width=True)

# ----------------------------------------
# VIZ 4 and VIZ 5: Side by side layout
# ----------------------------------------
col4, col5 = st.columns(2)

with col4:
    st.subheader("Total Amount Lost by State and Age Group")

    filtered_age_df = df[df['age_group'].isin(selected_age_groups)].copy()
    amount_lost_grouped = filtered_age_df.groupby(['state', 'age_group'])['amount_lost'].sum().reset_index()

    #checkbox_top3 = st.checkbox("Top 3 States", key="top3")
    #checkbox_next5 = st.checkbox("Bottom 5 States", key="next5")

    cb_col1, cb_col2 = st.columns(2)
    with cb_col1:
        checkbox_top3 = st.checkbox("Top 3 States", key="top3")
    with cb_col2:
        checkbox_next5 = st.checkbox("Bottom 5 States", key="next5")

    state_totals = amount_lost_grouped.groupby('state')['amount_lost'].sum().sort_values(ascending=False)
    top_states = state_totals.head(3).index.tolist()
    next_states = state_totals.iloc[3:8].index.tolist()

    if checkbox_top3:
        amount_lost_grouped = amount_lost_grouped[amount_lost_grouped['state'].isin(top_states)]
    elif checkbox_next5:
        amount_lost_grouped = amount_lost_grouped[amount_lost_grouped['state'].isin(next_states)]

    fig4 = px.bar(
        amount_lost_grouped,
        x='state',
        y='amount_lost',
        color='age_group',
        barmode='group',
        title="",
        labels={'amount_lost': 'Total Amount Lost', 'state': 'State', 'age_group': 'Age Group'}
    )
    fig4.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    st.plotly_chart(fig4, use_container_width=True)

with col5:
    st.subheader("Total Amount Lost by Scam Type")

    amount_lost_by_scam = df.groupby('scam_type')['amount_lost'].sum().reset_index()
    amount_lost_by_scam = amount_lost_by_scam.sort_values(by='amount_lost', ascending=True)

    fig5 = px.bar(
        amount_lost_by_scam,
        x='amount_lost',
        y='scam_type',
        orientation='h',
        title="",
        labels={'amount_lost': 'Total Amount Lost ($)', 'scam_type': 'Scam Type'},
        color_discrete_sequence=['#EF553B']
    )
    fig5.update_layout(margin=dict(l=200, t=50, r=25, b=25), yaxis=dict(tickmode='linear'))
    st.plotly_chart(fig5, use_container_width=True)

    # "See More" section for detailed breakdown
    if "show_drilldown" not in st.session_state:
        st.session_state.show_drilldown = False

    if st.button("See More", key="seemore_button"):
        st.session_state.show_drilldown = not st.session_state.show_drilldown

    if st.session_state.show_drilldown:
        st.subheader("Detail Breakdown of Scam Types")
        tab_high, tab_low = st.tabs(["Losses ≥ $1M", "Losses < $1M"])

        with tab_high:
            df_above_1m = amount_lost_by_scam[amount_lost_by_scam['amount_lost'] >= 1_000_000]
            fig_high = px.bar(
                df_above_1m,
                x='amount_lost',
                y='scam_type',
                orientation='h',
                title="Scam Types with Losses ≥ $1M",
                labels={'amount_lost': 'Total Amount Lost ($)', 'scam_type': 'Scam Type'},
                color_discrete_sequence=['#FFD700']
            )
            fig_high.update_layout(margin=dict(l=200, t=50, r=25, b=25))
            st.plotly_chart(fig_high, use_container_width=True)

        with tab_low:
            df_below_1m = amount_lost_by_scam[amount_lost_by_scam['amount_lost'] < 1_000_000]
            fig_low = px.bar(
                df_below_1m,
                x='amount_lost',
                y='scam_type',
                orientation='h',
                title="Scam Types with Losses < $1M",
                labels={'amount_lost': 'Total Amount Lost ($)', 'scam_type': 'Scam Type'},
                color_discrete_sequence=['#FFDAB9']
            )
            fig_low.update_layout(margin=dict(l=200, t=50, r=25, b=25))
            st.plotly_chart(fig_low, use_container_width=True)
