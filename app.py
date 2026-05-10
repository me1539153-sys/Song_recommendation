import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import hashlib
import urllib.parse
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. DATABASE SETUP ---
conn = sqlite3.connect('vibe_stream_final.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT, role TEXT)')
conn.commit()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# --- 2. AI ENGINE ---
@st.cache_resource
def get_engine():
    file_path = r"C:\Users\hp\Desktop\ml_mini_project\SONG_REC\ex.csv"
    if not os.path.exists(file_path):
        return None, None

    # Try different encodings to avoid UnicodeErrors
    for enc in ['utf-8', 'latin1', 'unicode_escape']:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except: continue
    
    df.fillna('', inplace=True)
    # Combine tags for AI analysis
    df['tags'] = (df['Singer/Artists'].astype(str) + " " + 
                  df['Genre'].astype(str) + " " + 
                  df['Album/Movie'].astype(str)).str.lower()
    
    cv = CountVectorizer(stop_words='english')
    count_matrix = cv.fit_transform(df['tags'])
    sim = cosine_similarity(count_matrix)
    return df, sim

def get_vibe_dna(genre):
    dna = {"Energy": 50, "Romance": 50}
    g = str(genre).lower()
    if 'dance' in g: dna["Energy"] += 30
    if 'romantic' in g: dna["Romance"] += 40
    return dna

# Initialize the engine
df, similarity = get_engine()

# --- 3. UI THEME ---
st.set_page_config(page_title="VibeStream AI", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: white; }
    .stButton>button { border-radius: 10px; background-color: #1DB954; color: white; font-weight: bold; width: 100%; }
    .song-card { background-color: #161b22; padding: 20px; border-radius: 15px; border-top: 4px solid #1DB954; margin-bottom: 20px; }
    .vibe-tag { background: #333; color: #1DB954; padding: 2px 8px; border-radius: 10px; font-size: 11px; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIN / SIGNUP ---
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': "", 'role': ""})

if not st.session_state['auth']:
    st.title("🎵 VibeStream AI: Login Portal")
    choice = st.sidebar.selectbox("Access", ["Login", "Sign Up"])
    if choice == "Login":
        u = st.text_input("Username")
        p = st.text_input("Password", type='password')
        if st.button("Login"):
            c.execute('SELECT * FROM users WHERE username = ?', (u,))
            data = c.fetchone()
            if data and check_hashes(p, data[1]):
                st.session_state.update({'auth': True, 'user': u, 'role': data[2]})
                st.rerun()
            else: st.error("Invalid Login. Please Sign Up if you haven't.")
    else:
        nu = st.text_input("Create Username")
        np = st.text_input("Create Password", type='password')
        nr = st.selectbox("Role", ["Listener", "Publisher"])
        if st.button("Register"):
            try:
                c.execute('INSERT INTO users VALUES (?,?,?)', (nu, make_hashes(np), nr))
                conn.commit()
                st.success("Account Created! Now switch to Login.")
            except: st.error("Username already taken.")

# --- 5. MAIN APP ---
elif df is not None:
    st.sidebar.title(f"Hi {st.session_state['user']}")
    if st.sidebar.button("Logout"):
        st.session_state.update({'auth': False})
        st.rerun()

    if st.session_state['role'] == "Publisher":
        st.title("👨‍🎨 Publisher Studio")
        tab1, tab2 = st.tabs(["➕ Add Song", "🗑️ Delete Song"])
        
        with tab1:
            with st.form("pub_form"):
                name = st.text_input("Song Name")
                art = st.text_input("Artist")
                gen = st.text_input("Genre")
                alb = st.text_input("Album")
                rat = st.text_input("Rating (e.g. 9/10)")
                if st.form_submit_button("Publish"):
                    if name and art:
                        new_row = pd.DataFrame([[name, art, gen, alb, rat]], columns=df.columns[:5])
                        new_row.to_csv('ex.csv', mode='a', index=False, header=False)
                        st.cache_resource.clear()
                        st.success("Indexed! Refreshing...")
                        st.rerun()
        
        with tab2:
            current_df = pd.read_csv('ex.csv', encoding='latin1')
            to_del = st.selectbox("Select song to remove:", current_df['Song-Name'].values)
            if st.button("Delete Permanently"):
                current_df = current_df[current_df['Song-Name'] != to_del]
                current_df.to_csv('ex.csv', index=False)
                st.cache_resource.clear()
                st.rerun()
    
    else: # LISTENER MODE
        st.title("🎧 AI Music Explorer")
        # Ensure fresh song list
        song_list = df['Song-Name'].unique().tolist()
        search = st.selectbox("Select a song to start discovery:", song_list)
        
        if st.button("🚀 Analyze & Recommend"):
            # Find the row of the searched song
            target_match = df[df['Song-Name'] == search]
            
            if not target_match.empty:
                # FIX: Find the correct numeric position in the current dataframe
                target_idx = target_match.index[0]
                pos_in_matrix = list(df.index).index(target_idx)
                
                # Get similarity scores
                distances = similarity[pos_in_matrix]
                
                # FIX: Unpack tuple correctly to avoid TypeError
                # sorted_indices will be a list of (integer_index, score)
                sorted_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[0:7]
                
                for count, (row_index, score) in enumerate(sorted_indices):
                    # Use .iloc with the integer index from the tuple
                    row = df.iloc[row_index]
                    
                    dna = get_vibe_dna(row['Genre'])
                    yt_query = urllib.parse.quote(f"{str(row['Song-Name'])} {str(row['Singer/Artists'])}")
                    yt_url = f"https://www.youtube.com/results?search_query={yt_query}"
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={yt_url}"
                    
                    if count == 0: st.subheader("🎯 Your Search Result")
                    elif count == 1: st.write("---"); st.subheader("🌟 Similar Recommendations")

                    st.markdown(f"""
                    <div class="song-card">
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <h2 style="color:#1DB954; margin:0;">{row['Song-Name']}</h2>
                                <p><b>{row['Singer/Artists']}</b> | {row['Album/Movie']}</p>
                                <span class="vibe-tag">⚡ Energy: {dna['Energy']}%</span>
                                <span class="vibe-tag">❤️ Romance: {dna['Romance']}%</span>
                            </div>
                            <img src="{qr_url}" width="100">
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([1, 4])
                    with c1: st.link_button("📺 YouTube", yt_url)
                    with c2: st.download_button("📥 Download", data="AudioData", file_name=f"{row['Song-Name']}.mp3", key=f"btn_{row_index}_{count}")