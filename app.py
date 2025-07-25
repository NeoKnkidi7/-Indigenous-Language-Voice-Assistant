import streamlit as st
from gtts import gTTS
import pandas as pd
import numpy as np
import plotly.express as px
import os
import tempfile

# App configuration
st.set_page_config(
    page_title="Indigenous Language Assistant",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern UI with new color scheme
st.markdown("""
<style>
    :root {
        --primary: #4CAF50;
        --secondary: #4DB6AC;
        --accent: #C0CA33;
        --vibrant1: #4DB6AC;
        --vibrant2: #263238;
        --background: #FFFFFF;
        --card: #FFFFFF;
        --text: #263238;
        --success: #4CAF50;
        --warning: #FFC107;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: var(--background);
        background-image: linear-gradient(135deg, #FFFFFF 0%, #E0E0E0 100%);
        animation: gradientBG 15s ease infinite;
        background-size: 400% 400%;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .st-bb {background-color: var(--card);}
    
    header[data-testid="stHeader"] {
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border-radius: 15px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: none;
        box-shadow: 0 6px 12px rgba(76, 175, 80, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 12px 20px rgba(76, 175, 80, 0.4);
    }
    
    .stButton>button:after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: 0.5s;
    }
    
    .stButton>button:hover:after {
        left: 100%;
    }
    
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 15px;
        padding: 14px 18px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
        transform: scale(1.01);
    }
    
    .stRadio>div {
        flex-direction: row;
        gap: 20px;
    }
    
    .stRadio>div>label {
        background: var(--card);
        padding: 18px 24px;
        border-radius: 15px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.08);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 2px solid transparent;
        cursor: pointer;
    }
    
    .stRadio>div>label:hover {
        transform: translateY(-5px) scale(1.03);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        border-color: var(--primary);
    }
    
    .stRadio>div>label[data-baseweb="radio"]:has(> div:first-child[aria-checked="true"]) {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(77, 182, 172, 0.15));
        border-color: var(--primary);
        transform: translateY(-3px);
    }
    
    .card {
        background: var(--card);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        margin-bottom: 30px;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 1px solid rgba(0,0,0,0.03);
        overflow: hidden;
        position: relative;
    }
    
    .card:before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background: linear-gradient(to bottom, var(--vibrant1), var(--vibrant2));
        transition: width 0.5s ease;
    }
    
    .card:hover {
        transform: translateY(-8px) scale(1.01);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .card:hover:before {
        width: 8px;
    }
    
    .language-badge {
        padding: 10px 22px;
        border-radius: 50px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 20px;
        background: linear-gradient(135deg, var(--vibrant1), var(--vibrant2));
        color: white;
        box-shadow: 0 6px 15px rgba(77, 182, 172, 0.3);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(77, 182, 172, 0.5); }
        70% { box-shadow: 0 0 0 15px rgba(77, 182, 172, 0); }
        100% { box-shadow: 0 0 0 0 rgba(77, 182, 172, 0); }
    }
    
    .user-msg {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border-radius: 22px 22px 5px 22px;
        padding: 18px 24px;
        margin: 15px 0;
        max-width: 80%;
        align-self: flex-end;
        box-shadow: 0 8px 20px rgba(76, 175, 80, 0.25);
        animation: slideInRight 0.5s ease;
    }
    
    .assistant-msg {
        background: white;
        color: var(--text);
        border-radius: 22px 22px 22px 5px;
        padding: 18px 24px;
        margin: 15px 0;
        max-width: 80%;
        align-self: flex-start;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        animation: slideInLeft 0.5s ease;
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .tab-content {
        animation: fadeIn 0.5s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .glowing-border {
        position: relative;
        box-shadow: 0 0 10px var(--accent);
        animation: glow 1.5s infinite alternate;
    }
    
    @keyframes glow {
        from { box-shadow: 0 0 10px -10px var(--accent); }
        to { box-shadow: 0 0 10px 10px rgba(192, 202, 51, 0.3); }
    }
    
    .floating {
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
        100% { transform: translateY(0px); }
    }
    
    .icon-hover {
        transition: all 0.5s ease;
    }
    
    .icon-hover:hover {
        transform: rotate(15deg) scale(1.2);
        filter: drop-shadow(0 5px 15px rgba(0,0,0,0.2));
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = "Zulu"
if 'audio_response' not in st.session_state:
    st.session_state.audio_response = None
if 'domain' not in st.session_state:
    st.session_state.domain = "Healthcare"
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# Load language resources
LANGUAGE_RESOURCES = {
    "Zulu": {
        "greeting": "Sawubona! Ngingakusiza ngani namuhla?",
        "agriculture": {
            "pests": "Ukulwa nezinambuzane, sebenzisa i-organic pesticide. Hlola izitshalo nsuku zonke.",
            "planting": "Isikhathi esihle sokutshala u-September kuya ku-October emaphandleni aseNingizimu Afrika.",
            "soil": "Hlola umhlabathi wakho ngonyaka. Geza ngomquba wemvelo ukuze uthuthukise isimo somhlabathi.",
            "water": "Qinisekisa ukuthi izitshalo zakho zithola amanzi anele, ikakhulukazi ehlobo."
        },
        "healthcare": {
            "symptoms": "Uma unezimpawu ezingajwayelekile, xhumana nogoti wezempilo ngokushesha.",
            "medication": "Ungaphuze umuthi ngaphandle kokweluleka kudokotela.",
            "hygiene": "Geza izandla zakho qhaba ngesikhathi eside ukuze uvimbele ukusakazeka kwegciwane.",
            "nutrition": "Idla ukudla okunomsoco okuhlanganisa imifino, izithelo kanye namaprotheni."
        }
    },
    "Tswana": {
        "greeting": "Dumela! O ka thusa jang kajeno?",
        "agriculture": {
            "pests": "Go lwa le disenyi, dirisa di-pesticide tsa tlhago. Sekaseka dimela letsatsi le letsatsi.",
            "planting": "Nako e e siameng go jala ke September go ya go October mo mafelong a Aforika Borwa.",
            "soil": "Sekaseka mmu wa gago ngwaga le ngwaga. O ka dirisa motswako wa tlhago go tokafatsa mmu.",
            "water": "Netefatsa gore dimela tsa gago di na le metsi a lekaneng, bogolo segologolo mo marung."
        },
        "healthcare": {
            "symptoms": "Fa o na le matshwao a a sa tlwaelegang, ikopanye le moapei wa tsa boitekanelo ka bonako.",
            "medication": "O se ka wa nwa ditlhare ntle le go laola ngaka.",
            "hygiene": "Hlatswa diatla tsa gago ka nako e telele go thibela phetiso ya diruiwa.",
            "nutrition": "Ja dijo tse di nonneng tse di akaretsang merogo, maungo le diprotein."
        }
    }
}

# Generate audio response with correct language codes
def generate_audio_response(text, language):
    try:
        # Correct language codes: Zulu = 'zu', Tswana = 'ts'
        lang_code = "zu" if language == "Zulu" else "ts"
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            audio_bytes = tmp.read()
        
        return audio_bytes
    except Exception as e:
        st.error(f"Audio generation failed: {str(e)}")
        return None

# App layout
st.title("🌍 Indigenous Language Assistant")
st.markdown("""
<div style="font-size:1.1rem; color:#555; margin-bottom:30px; animation: fadeIn 1.5s ease;">
Empowering communication in Zulu and Tswana through accessible language technology
</div>
""", unsafe_allow_html=True)

# Sidebar with modern design
with st.sidebar:
    st.markdown("<div style='text-align:center; margin-bottom:30px;'>"
                "<div class='floating' style='margin-bottom:20px;'>"
                "<img src='https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Flag_of_South_Africa.svg/1200px-Flag_of_South_Africa.svg.png' width='80' style='border-radius:50%; box-shadow:0 10px 30px rgba(0,0,0,0.2);'>"
                "</div>"
                "<h2 style='margin-top:10px;'>Settings</h2></div>", 
                unsafe_allow_html=True)
    
    with st.container():
        st.subheader("Language Preference")
        st.session_state.selected_language = st.radio(
            "Select Language",
            ["Zulu", "Tswana"],
            index=0 if st.session_state.selected_language == "Zulu" else 1,
            label_visibility="collapsed"
        )
    
    st.divider()
    
    with st.container():
        st.subheader("Application Domain")
        st.session_state.domain = st.radio(
            "Select Domain",
            ["Healthcare", "Agriculture"],
            index=0 if st.session_state.domain == "Healthcare" else 1,
            label_visibility="collapsed"
        )
    
    st.divider()
    
    with st.container():
        st.subheader("About")
        st.markdown("""
        <div class="icon-hover">
        - **🌐 Version:** 2.1
        - **👨‍💻 Developed by:** Language Access Initiative
        - **📊 Data Source:** NWU Language Lab
        - **🔊 Technology:** Google Text-to-Speech
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='margin-top:30px; text-align:center; color:#777; font-size:0.9rem;'>
        © 2023 | Bridging language barriers
        </div>
        """, unsafe_allow_html=True)

# Main content tabs
tab1, tab2, tab3 = st.tabs(["Assistant", "Resources", "Analytics"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 Conversation")
        st.markdown(f"<div class='language-badge'>{st.session_state.selected_language} • {st.session_state.domain}</div>", 
                    unsafe_allow_html=True)
        
        # Chat container
        with st.container():
            chat_container = st.container()
            
            # Display conversation
            if st.session_state.conversation:
                for msg in st.session_state.conversation:
                    if msg['speaker'] == "User":
                        chat_container.markdown(f"<div class='user-msg'><b>You:</b> {msg['text']}</div>", 
                                              unsafe_allow_html=True)
                    else:
                        chat_container.markdown(f"<div class='assistant-msg'><b>Assistant:</b> {msg['text']}</div>", 
                                              unsafe_allow_html=True)
            else:
                chat_container.info("✨ Start a conversation by typing a message below")
        
        # Input area
        with st.form("input_form", clear_on_submit=True):
            user_input = st.text_area("Your message:", value="", height=120, 
                                     placeholder=f"Type your message in {st.session_state.selected_language}...",
                                     key="user_input")
            submit_button = st.form_submit_button("🚀 Send", use_container_width=True)
            
            if submit_button and user_input:
                st.session_state.user_input = user_input
                
                # Process query
                domain_key = st.session_state.domain.lower()
                lang_data = LANGUAGE_RESOURCES[st.session_state.selected_language]
                
                # Enhanced intent recognition with multiple keywords
                user_text = user_input.lower()
                response = lang_data['greeting']
                
                # Agriculture intents
                if any(word in user_text for word in ["pest", "insect", "bug", "zinambuzane", "disenyi"]):
                    response = lang_data[domain_key]['pests']
                elif any(word in user_text for word in ["plant", "grow", "seed", "tshala", "jala"]):
                    response = lang_data[domain_key]['planting']
                elif any(word in user_text for word in ["soil", "dirt", "earth", "umhlabathi", "mmu"]):
                    response = lang_data[domain_key]['soil']
                elif any(word in user_text for word in ["water", "irrigate", "rain", "amanzi", "metsi"]):
                    response = lang_data[domain_key]['water']
                    
                # Healthcare intents
                elif any(word in user_text for word in ["symptom", "pain", "fever", "impawu", "matshwao"]):
                    response = lang_data[domain_key]['symptoms']
                elif any(word in user_text for word in ["medic", "pill", "drug", "umuthi", "dithlare"]):
                    response = lang_data[domain_key]['medication']
                elif any(word in user_text for word in ["hygiene", "clean", "wash", "hlanza", "hlatswa"]):
                    response = lang_data[domain_key]['hygiene']
                elif any(word in user_text for word in ["nutrition", "food", "diet", "ukudla", "dijo"]):
                    response = lang_data[domain_key]['nutrition']
                
                st.session_state.conversation.append({
                    "speaker": "User",
                    "text": user_input
                })
                
                st.session_state.conversation.append({
                    "speaker": "Assistant",
                    "text": response
                })
                
                # Generate audio response
                st.session_state.audio_response = generate_audio_response(
                    response, 
                    st.session_state.selected_language
                )
                st.rerun()
    
    with col2:
        st.markdown("### 🔊 Audio Response")
        
        # Audio playback card
        with st.container():
            card = st.container()
            card.markdown("<div class='card'>", unsafe_allow_html=True)
            
            if st.session_state.audio_response:
                card.audio(st.session_state.audio_response, format="audio/mp3")
                card.download_button(
                    label="📥 Download Audio",
                    data=st.session_state.audio_response,
                    file_name=f"{st.session_state.selected_language}_response.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
            else:
                card.info("🎤 Submit a message to generate an audio response")
            
            card.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("### ⚡ Quick Actions")
        
        # Quick actions card
        with st.container():
            card = st.container()
            card.markdown("<div class='card'>", unsafe_allow_html=True)
            
            domain_key = st.session_state.domain.lower()
            lang_data = LANGUAGE_RESOURCES[st.session_state.selected_language]
            
            # Fixed KeyError by using appropriate keys for each domain
            if domain_key == 'agriculture':
                action_key = 'pests'
                action_label = "🐜 Ask about pests"
            else:
                action_key = 'hygiene'
                action_label = "🧼 Ask about hygiene"
            
            if card.button(action_label, use_container_width=True):
                response = lang_data[domain_key][action_key]
                st.session_state.conversation.append({
                    "speaker": "Assistant",
                    "text": response
                })
                st.session_state.audio_response = generate_audio_response(
                    response, 
                    st.session_state.selected_language
                )
                st.rerun()
                
            if card.button("👋 Request greeting", use_container_width=True):
                response = lang_data['greeting']
                st.session_state.conversation.append({
                    "speaker": "Assistant",
                    "text": response
                })
                st.session_state.audio_response = generate_audio_response(
                    response, 
                    st.session_state.selected_language
                )
                st.rerun()
                
            if card.button("🗑️ Clear Conversation", use_container_width=True):
                st.session_state.conversation = []
                st.session_state.audio_response = None
                st.session_state.user_input = ""
                st.rerun()
            
            card.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.subheader("Language Resources")
    st.markdown("""
    <div class="card">
        <h4>📚 Indigenous Language Support</h4>
        <p>Explore resources for Zulu and Tswana languages</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("#### isiZulu Resources")
            st.markdown("""
            - **Common Phrases:**
              - Hello: Sawubona
              - Thank you: Ngiyabonga
              - How are you?: Unjani?
              - Goodbye: Hamba kahle
            
            - **Agriculture Terms:**
              - Soil: Umhlabathi
              - Crops: Izitshalo
              - Harvest: Isivuno
            
            - **Healthcare Terms:**
              - Doctor: Udokotela
              - Medicine: Umuthi
              - Symptoms: Izimpawu
            """)
            st.markdown("</div>", unsafe_allow_html=True)
            
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("#### Learning Materials")
                st.markdown("""
                - [📖 Zulu Grammar Guide](https://example.com)
                - [📚 Zulu-English Dictionary](https://example.com)
                - [🌍 Cultural Resources](https://example.com)
                """)
                st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("#### Setswana Resources")
            st.markdown("""
            - **Common Phrases:**
              - Hello: Dumela
              - Thank you: Ke a leboga
              - How are you?: O tsogile jang?
              - Goodbye: Tsamaya sentle
            
            - **Agriculture Terms:**
              - Soil: Mmu
              - Crops: Dimerela
              - Harvest: Go roba
            
            - **Healthcare Terms:**
              - Doctor: Ngaka
              - Medicine: Dithlare
              - Symptoms: Matshwao
            """)
            st.markdown("</div>", unsafe_allow_html=True)
            
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("#### Learning Materials")
                st.markdown("""
                - [📖 Tswana Grammar Guide](https://example.com)
                - [📚 Tswana-English Dictionary](https://example.com)
                - [🌍 Cultural Resources](https://example.com)
                """)
                st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Community Contributions")
    st.markdown("""
    ### 👥 Join Our Community
    Help us improve our language resources:
    """)
    
    with st.form("contribution_form"):
        cols = st.columns(2)
        with cols[0]:
            name = st.text_input("Your Name")
        with cols[1]:
            email = st.text_input("Email")
        
        language = st.selectbox("Language", ["Zulu", "Tswana"])
        contribution = st.text_area("Contribution (phrase, translation, or resource)")
        
        submitted = st.form_submit_button("✨ Submit Contribution")
        if submitted:
            st.success("🌟 Thank you for your contribution! Our language team will review it.")
    
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.subheader("Usage Analytics")
    st.markdown("""
    <div class="card">
        <h4>📊 Adoption Metrics</h4>
        <p>Track the impact of our indigenous language technology</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate mock analytics data
    languages = ["Zulu", "Tswana", "Zulu", "Tswana", "Zulu", "Tswana", "Zulu"]
    domains = ["Healthcare", "Agriculture", "Healthcare", "Agriculture", "Healthcare", "Agriculture", "Healthcare"]
    regions = ["KwaZulu-Natal", "North West", "Gauteng", "Limpopo", "Eastern Cape", "Free State", "Western Cape"]
    usage = [150, 95, 120, 85, 140, 90, 130]
    
    analytics_df = pd.DataFrame({
        "Language": languages,
        "Domain": domains,
        "Region": regions,
        "Usage": usage
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("#### Language Distribution")
            lang_counts = analytics_df["Language"].value_counts().reset_index()
            fig1 = px.pie(
                lang_counts, 
                names="Language", 
                values="count",
                color="Language",
                color_discrete_map={"Zulu": "#4DB6AC", "Tswana": "#263238"},
                hole=0.3
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            fig1.update_layout(showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("#### Regional Adoption")
            region_counts = analytics_df.groupby("Region")["Usage"].sum().reset_index()
            fig2 = px.bar(
                region_counts, 
                x="Region", 
                y="Usage",
                color="Region",
                color_discrete_sequence=["#4CAF50", "#4DB6AC", "#C0CA33", "#263238", "#E0E0E0"],
                title="Usage by Region",
                height=350
            )
            fig2.update_layout(showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("#### Domain Usage")
            domain_counts = analytics_df["Domain"].value_counts().reset_index()
            fig3 = px.pie(
                domain_counts, 
                names="Domain", 
                values="count",
                color="Domain",
                color_discrete_map={"Healthcare": "#4CAF50", "Agriculture": "#4DB6AC"},
                title="Usage by Application Domain",
                hole=0.3
            )
            fig3.update_traces(textposition='inside', textinfo='percent+label')
            fig3.update_layout(showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("#### Monthly Growth")
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            zulu_growth = [80, 110, 150, 190, 240, 300]
            tswana_growth = [50, 75, 110, 150, 190, 240]
            
            fig4 = px.line(
                x=months,
                y=[zulu_growth, tswana_growth],
                title="Monthly Active Users",
                labels={"x": "Month", "value": "Users"},
                color_discrete_sequence=["#4DB6AC", "#263238"]
            )
            fig4.update_layout(
                showlegend=True,
                legend_title="Language",
                yaxis_title="Users",
                xaxis_title="Month",
                height=350
            )
            fig4.data[0].name = "Zulu"
            fig4.data[1].name = "Tswana"
            st.plotly_chart(fig4, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("""
<div style="text-align:center; color:#777; font-size:0.9em; padding:20px;">
    Indigenous Language Assistant v2.1 | 
    <a href="#" style="color:#4CAF50;">Privacy Policy</a> | 
    <a href="#" style="color:#4CAF50;">Research Methodology</a> | 
    <a href="#" style="color:#4CAF50;">Community Guidelines</a>
</div>
""", unsafe_allow_html=True)
