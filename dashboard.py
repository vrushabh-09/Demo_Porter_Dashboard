import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Porter Dashboard", layout="wide")
st.title("🚚 Porter Logistics Dashboard")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    file = "porter_indian_logistics_dataset.xlsx"
    bookings = pd.read_excel(file, sheet_name="Booking")
    return bookings

bookings = load_data()

# ---------------- PREPROCESS ----------------
bookings["createdAt"] = pd.to_datetime(bookings["createdAt"], errors="coerce")

bookings["city"] = bookings["pickupAddress"].astype(str).apply(
    lambda x: x.split(",")[-1].strip() if "," in x else "Unknown"
)

# ---------------- FILTERS ----------------
st.sidebar.header("Filters")

city_filter = st.sidebar.multiselect(
    "City",
    bookings["city"].dropna().unique(),
    default=bookings["city"].dropna().unique()
)

status_filter = st.sidebar.multiselect(
    "Status",
    bookings["bookingStatus"].dropna().unique(),
    default=bookings["bookingStatus"].dropna().unique()
)

df = bookings[
    (bookings["city"].isin(city_filter)) &
    (bookings["bookingStatus"].isin(status_filter))
]

# ---------------- KPIs ----------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Orders", len(df))
col2.metric("Revenue ₹", int(df["totalFare"].sum()))
col3.metric("Cancelled", len(df[df["bookingStatus"] == "cancelled"]))
col4.metric("Avg Rating", round(df["driverRating.rating"].mean(), 2))

# ---------------- CHARTS ----------------

st.subheader("Orders Trend")

daily = df.groupby(df["createdAt"].dt.date).size()

fig, ax = plt.subplots()
ax.plot(daily.index, daily.values)
plt.xticks(rotation=45)
st.pyplot(fig)

st.subheader("Status Distribution")

status_counts = df["bookingStatus"].value_counts()

fig, ax = plt.subplots()
ax.pie(status_counts, labels=status_counts.index, autopct="%1.1f%%")
st.pyplot(fig)

st.subheader("City Orders")

city_counts = df["city"].value_counts()

fig, ax = plt.subplots()
ax.bar(city_counts.index, city_counts.values)
plt.xticks(rotation=45)
st.pyplot(fig)

st.subheader("Driver Ratings")

fig, ax = plt.subplots()
ax.hist(df["driverRating.rating"].dropna(), bins=10)
st.pyplot(fig)

# ---------------- TABLE ----------------
st.subheader("Data Preview")
st.dataframe(df.head(100))