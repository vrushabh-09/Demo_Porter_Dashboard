import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Porter Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    file = "porter_indian_logistics_dataset.xlsx"
    users = pd.read_excel(file, sheet_name="User")
    drivers = pd.read_excel(file, sheet_name="Driver")
    vendors = pd.read_excel(file, sheet_name="Vendor")
    bookings = pd.read_excel(file, sheet_name="Booking")
    return users, drivers, vendors, bookings

users, drivers, vendors, bookings = load_data()

# ---------------- PREPROCESS ----------------
bookings["createdAt"] = pd.to_datetime(bookings["createdAt"], errors="coerce")

bookings["city"] = bookings["pickupAddress"].astype(str).apply(
    lambda x: x.split(",")[-1].strip() if "," in x else "Unknown"
)

# ---------------- SIDEBAR NAVIGATION ----------------
st.sidebar.title("🚚 Navigation")

page = st.sidebar.radio(
    "Go to",
    ["📊 Overview", "📦 Bookings", "🚗 Drivers", "🏢 Vendors"]
)

# ---------------- COMMON FILTERS ----------------
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

# =====================================================
# 📊 OVERVIEW PAGE
# =====================================================
if page == "📊 Overview":

    st.title("📊 Overview Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Orders", len(df))
    col2.metric("Revenue ₹", int(df["totalFare"].sum()))
    col3.metric("Cancelled", len(df[df["bookingStatus"] == "cancelled"]))
    col4.metric("Avg Rating", round(df["driverRating.rating"].mean(), 2))

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

# =====================================================
# 📦 BOOKINGS PAGE
# =====================================================
elif page == "📦 Bookings":

    st.title("📦 Booking Insights")

    st.subheader("Booking Table")
    st.dataframe(df)

    st.subheader("Distance vs Fare")

    fig, ax = plt.subplots()
    ax.scatter(df["distanceKm"], df["totalFare"])
    ax.set_xlabel("Distance (KM)")
    ax.set_ylabel("Fare ₹")
    st.pyplot(fig)

# =====================================================
# 🚗 DRIVERS PAGE
# =====================================================
elif page == "🚗 Drivers":

    st.title("🚗 Driver Insights")

    st.metric("Total Drivers", len(drivers))

    st.subheader("Driver Availability")

    availability = drivers["isAvailable"].value_counts()

    fig, ax = plt.subplots()
    ax.pie(availability, labels=availability.index, autopct="%1.1f%%")
    st.pyplot(fig)

    st.subheader("Vehicle Types")

    vehicle_counts = drivers["vehicleType"].value_counts()

    fig, ax = plt.subplots()
    ax.bar(vehicle_counts.index, vehicle_counts.values)
    st.pyplot(fig)

# =====================================================
# 🏢 VENDORS PAGE
# =====================================================
elif page == "🏢 Vendors":

    st.title("🏢 Vendor Insights")

    st.metric("Total Vendors", len(vendors))

    st.subheader("Approval Status")

    approval = vendors["isApproved"].value_counts()

    fig, ax = plt.subplots()
    ax.pie(approval, labels=approval.index, autopct="%1.1f%%")
    st.pyplot(fig)

    st.subheader("Vendor Table")

    st.dataframe(vendors.head(100))
