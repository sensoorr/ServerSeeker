import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import pycountry
import os
import time
import math

# --- CONFIGURATION ---
DB_URL = os.getenv("DB_URL", "postgresql://postgres:SuperSuperSecretPassword@db:5432/serverseeker")
engine = create_engine(DB_URL)

# --- COMPACT UI & SPACING FIXES ---
st.set_page_config(page_title="ServerSeeker Live", layout="wide")
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 0rem; }
        [data-testid="stMetric"] { 
            background-color: #1e2130; 
            padding: 15px; 
            border-radius: 10px; 
            border: 1px solid #30363d;
            height: 160px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        [data-testid="stMetricDelta"] svg { display: none; }
        .element-container { margin-bottom: 0.5rem; }
        /* Hide row numbers */
        thead tr th:first-child { display: none; }
        tbody th { display: none; }
    </style>
    """, unsafe_allow_html=True)

def format_region(country_val):
    if not country_val or pd.isna(country_val): return "❓ Unknown"
    country_val = str(country_val).strip()
    try:
        try: country = pycountry.countries.lookup(country_val)
        except: country = pycountry.countries.get(alpha_2=country_val.upper())
        if country:
            base = ord('🇦') - ord('A')
            flag = chr(ord(country.alpha_2[0].upper()) + base) + chr(ord(country.alpha_2[1].upper()) + base)
            return f"{flag} {country.name}"
        return country_val
    except: return country_val

@st.cache_data(ttl=5)
def get_stats():
    """Fetch only the numbers for metrics, not the whole DB."""
    with engine.connect() as conn:
        total_servers = conn.execute(text("SELECT COUNT(*) FROM servers")).scalar()
        total_online = conn.execute(text("SELECT COALESCE(SUM(online_players), 0) FROM servers")).scalar()
        
        now = time.time()
        disc_min = conn.execute(text(f"SELECT COUNT(*) FROM servers WHERE first_seen > {now - 60}")).scalar()
        disc_hour = conn.execute(text(f"SELECT COUNT(*) FROM servers WHERE first_seen > {now - 3600}")).scalar()
        
        db_size = conn.execute(text("SELECT pg_size_pretty(pg_database_size('serverseeker'))")).scalar()
        
    return total_servers, total_online, disc_min, disc_hour, db_size

def get_filtered_data(page, page_size, search_term, soft_filter, ver_filter, sort_col):
    """Fetches a specific page of data directly from SQL with filters applied."""
    offset = (page - 1) * page_size
    
    # Base Query
    query = """
        SELECT address, software, version, country, online_players, max_players, description_formatted, first_seen, last_seen 
        FROM servers 
        WHERE 1=1
    """
    params = {}
    
    # 1. Search Filter (SQL ILIKE)
    if search_term:
        query += " AND (description_formatted ILIKE :search OR address::text ILIKE :search)"
        params['search'] = f"%{search_term}%"

    # 2. Software Filter
    if soft_filter:
        # PostgreSQL requires treating list params carefully or manual formatting.
        # SQLAlchemy handles lists in 'IN' clauses if passed correctly.
        query += " AND software::text = ANY(:soft)"
        params['soft'] = soft_filter

    # 3. Version Filter
    if ver_filter:
        query += " AND version = ANY(:ver)"
        params['ver'] = ver_filter

    # 4. Sorting
    if sort_col == "Most Players":
        query += " ORDER BY online_players DESC"
    elif sort_col == "Newest Discovered":
        query += " ORDER BY first_seen DESC"
    else: # Recently Online
        query += " ORDER BY last_seen DESC"

    # 5. Pagination
    query += " LIMIT :limit OFFSET :offset"
    params['limit'] = page_size
    params['offset'] = offset

    df = pd.read_sql(text(query), engine, params=params)
    
    if not df.empty:
        df['address'] = df['address'].astype(str).str.replace('/32', '', regex=False)
        df['Players'] = df['online_players'].astype(str) + " / " + df['max_players'].astype(str)
        df['Region'] = df['country'].apply(format_region)
        df['Discovered'] = pd.to_datetime(df['first_seen'], unit='s').dt.strftime('%H:%M:%S %d/%m/%Y')
        df['Last Online'] = pd.to_datetime(df['last_seen'], unit='s').dt.strftime('%H:%M:%S %d/%m/%Y')
    
    return df

try:
    # --- METRICS ---
    total_servers, total_online, v_min, v_hour, db_size = get_stats()
    
    status_color = "normal" if v_min > 45 else "off" if v_min < 20 else "inverse"
    status_msg = "HEALTHY" if v_min > 40 else "PACKET LOSS?" if v_min < 20 else "STABLE"

    st.title("🔍 ServerSeeker Live Explorer")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Servers Found", f"{total_servers:,}")
    c2.metric("Total Online Players", f"{int(total_online):,}")
    c3.metric("Discovery / Minute", f"{v_min}", delta=status_msg, delta_color=status_color)
    c4.metric("Discovery / Hour", f"{v_hour}")
    c5.metric("Database Size", db_size)

    st.divider()

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("🔍 Database Filters")
    
    # Search Inputs
    search_q = st.sidebar.text_input("Search (IP or MOTD)", placeholder="e.g. Hypixel, 192.168...")
    
    # Fetch distinct dropdown options (Cached heavily)
    @st.cache_data(ttl=300)
    def get_dropdown_options():
        with engine.connect() as conn:
            s = [r[0] for r in conn.execute(text("SELECT DISTINCT software FROM servers WHERE software IS NOT NULL")).fetchall()]
            v = [r[0] for r in conn.execute(text("SELECT DISTINCT version FROM servers WHERE version IS NOT NULL ORDER BY version DESC")).fetchall()]
        return sorted(s), v # Versions are usually better sorted by logic, but alpha sort is okay for now

    try:
        all_soft, all_ver = get_dropdown_options()
    except:
        all_soft, all_ver = [], []

    selected_soft = st.sidebar.multiselect("Software", all_soft)
    selected_ver = st.sidebar.multiselect("Version", all_ver)
    sort_by = st.sidebar.selectbox("Sort By", ["Recently Online", "Most Players", "Newest Discovered"])
    
    st.sidebar.divider()
    
    # --- PAGINATION ---
    PAGE_SIZE = 100
    
    # Session state for page number
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 1

    # Reset page on filter change
    def reset_page(): st.session_state.page_number = 1
    
    # Load Data
    df = get_filtered_data(
        st.session_state.page_number, 
        PAGE_SIZE, 
        search_q, 
        selected_soft, 
        selected_ver, 
        sort_by
    )

    # --- TABLE DISPLAY ---
    cols = ['address', 'software', 'version', 'Region', 'Players', 'description_formatted', 'Last Online', 'Discovered']
    
    # Calculate height based on actual rows returned
    calc_height = min((len(df) * 35) + 38, 800)
    
    st.dataframe(
        df[cols] if not df.empty else pd.DataFrame(columns=cols), 
        height=calc_height, 
        width='stretch', 
        hide_index=True,
        column_config={
            "address": "IP Address",
            "description_formatted": "Description / MOTD",
            "software": "Software",
            "version": "Version"
        }
    )

    # --- PAGINATION CONTROLS ---
    # We place these at the bottom so the user scrolls down reading the list, then clicks next
    c_prev, c_info, c_next = st.columns([1, 2, 1])
    
    with c_prev:
        if st.session_state.page_number > 1:
            if st.button("Previous Page", use_container_width=True):
                st.session_state.page_number -= 1
                st.rerun()

    with c_info:
        st.markdown(f"<div style='text-align: center; padding-top: 10px;'>Page <b>{st.session_state.page_number}</b> (Showing {len(df)} results)</div>", unsafe_allow_html=True)

    with c_next:
        if len(df) == PAGE_SIZE: # If we got a full page, there's likely more
            if st.button("Next Page", use_container_width=True):
                st.session_state.page_number += 1
                st.rerun()

except Exception as e:
    st.error(f"Error loading UI: {e}")