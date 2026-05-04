import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

# -------------------------
# LOAD + CLEAN DATA
# -------------------------

df = pd.read_csv("adult_income.csv")
df.columns = df.columns.str.strip().str.lower()

for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].str.strip()

# -------------------------
# EDUCATION ORDER
# -------------------------
education_order = [
    "Preschool", "1st-4th", "5th-6th", "7th-8th",
    "9th", "10th", "11th", "12th",
    "HS-grad", "Some-college",
    "Assoc-voc", "Assoc-acdm",
    "Bachelors", "Masters",
    "Prof-school", "Doctorate"
]

df['education'] = pd.Categorical(
    df['education'],
    categories=education_order,
    ordered=True
)

# -------------------------
# COLOR SCHEME (TABLEAU STYLE)
# -------------------------
color_map = {
    "<=50K": "#4C78A8",  # blue
    ">50K": "#F58518"    # orange
}

gender_colors = {
    "Male": "#2c7bb6",
    "Female": "#d7191c"
}

# -------------------------
# HELPERS
# -------------------------
def get_edu_pct_long(data):
    if data.empty:
        return pd.DataFrame()
    temp = data.groupby(['education', 'income']).size().reset_index(name='count')
    total = temp.groupby('education')['count'].transform('sum')
    temp['percent'] = temp['count'] / total
    return temp

def get_pct(df, group_col):
    temp = df.groupby([group_col, 'income']).size().reset_index(name='count')
    total = temp.groupby(group_col)['count'].transform('sum')
    temp['percent'] = temp['count'] / total
    return temp

# -------------------------
# FILTERS
# -------------------------
st.sidebar.header("Filters")

workclass_filter = st.sidebar.multiselect(
    "Workclass",
    options=df['workclass'].unique(),
    default=df['workclass'].unique()
)

df = df[df['workclass'].isin(workclass_filter)]

# -------------------------
# DATA PREP
# -------------------------
fed = df[df['workclass'] == 'Federal-gov']
state = df[df['workclass'] == 'State-gov']

edu_fed = get_edu_pct_long(fed)
edu_state = get_edu_pct_long(state)

marital = get_pct(df, 'marital-status')

# -------------------------
# ⭐ NEW: YOUR LOGIC (INTERACTIVE VERSION)
# -------------------------
df['education-num'] = pd.to_numeric(df['education-num'], errors='coerce')

df["is_high_income"] = (df["income"] == ">50K").astype(int)

edu_gender = (
    df.groupby(["sex", "education-num"])["is_high_income"]
    .mean()
    .reset_index()
    .rename(columns={"is_high_income": "proportion_high_income"})
)

# -------------------------
# TITLE
# -------------------------
st.title("Income & Demographics Dashboard")

# -------------------------
# ROW 1
# -------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Workclass: Federal Government")
    if not edu_fed.empty:
        fig = px.bar(
            edu_fed,
            x="education",
            y="percent",
            color="income",
            color_discrete_map=color_map,
            category_orders={"education": education_order}
        )
        fig.update_layout(barmode='stack', yaxis_title="Percentage")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Workclass: State Government")
    if not edu_state.empty:
        fig = px.bar(
            edu_state,
            x="education",
            y="percent",
            color="income",
            color_discrete_map=color_map,
            category_orders={"education": education_order}
        )
        fig.update_layout(barmode='stack', yaxis_title="Percentage")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

# -------------------------
# ROW 2
# -------------------------
col3, col4 = st.columns([2,1])

with col3:
    st.subheader("Marital Status Proportions")
    fig = px.bar(
        marital,
        x="marital-status",
        y="percent",
        color="income",
        color_discrete_map=color_map
    )
    fig.update_layout(barmode='stack', yaxis_title="Percentage")
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.write("")

# -------------------------
# ROW 3
# -------------------------
col5, col6 = st.columns(2)

with col5:
    st.subheader("Impact of Years of Education on Income")

    fig = px.line(
        edu_gender,
        x="education-num",
        y="proportion_high_income",
        color="sex",
        markers=True,
        color_discrete_map=gender_colors
    )

    fig.update_layout(
        yaxis_title="Percentage Earning >50K",
        xaxis_title="Years of Education"
    )

    fig.update_yaxes(tickformat=".0%")  # show as percent

    st.plotly_chart(fig, use_container_width=True)

with col6:
    st.subheader("Hours Worked per Week by Income")

    fig = px.box(
        df,
        x="income",
        y="hours-per-week",
        color="income",
        color_discrete_map=color_map
    )

    st.plotly_chart(fig, use_container_width=True)
