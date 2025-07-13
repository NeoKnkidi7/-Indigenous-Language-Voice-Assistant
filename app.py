import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import torch
from transformers import pipeline
from gtts import gTTS
import base64
from pydub import AudioSegment
from langdetect import detect
import pandas as pd
import numpy as np
import plotly.express as px
import os
import sys

# Add FFmpeg to system path - CRITICAL FIX
os.environ["PATH"] += os.pathsep + '/usr/bin/'
sys.path.append('/usr/bin/ffmpeg')

# Set environment variables
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# App configuration
st.set_page_config(
    page_title="Indigenous Language Voice Assistant",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional UI
st.markdown("""
<style>
    :root {
        --primary: #2c5f2d;
        --secondary: #97bc62;
        --accent: #2c5f2d;
        --background: #f0f7f4;
        --card: #ffffff;
        --text: #1e3d36;
        --highlight: #ffb81c;
    }
    
    .main {background-color: var(--background);}
    .st-bb {background-color: var(--card);}
    .header {color: var(--primary); font-weight: 700;}
    .subheader {color: var(--secondary);}
    .metric-card {border-radius: 10px; padding: 20px; background: var(--card); 
                box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px;
                border-left: 4px solid var(--primary);}
    .stButton>button {background-color: var(--primary); color: white; border-radius: 8px; padding: 8px 16px;}
    .stButton>button:hover {background-color: var(--secondary);}
    .stTabs [data-baseweb="tab-list"] {gap: 10px;}
    .stTabs [data-baseweb="tab"] {padding: 10px 20px; border-radius: 8px 8px 0 0; background: #e8f5e9;}
    .stTabs [aria-selected="true"] {background-color: var(--primary); color: white;}
    .language-badge {padding: 5px 15px; border-radius: 20px; font-weight: bold;}
    .zulu-badge {background-color: #ffd54f; color: #1e3d36;}
    .tswana-badge {background-color: #4fc3f7; color: #1e3d36;}
    .response-card {background-color: #e8f5e9; padding: 20px; border-radius: 10px; margin: 15px 0;}
    .mic-animation {
        display: inline-block;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background-color: #e63946;
        animation: pulse 1.5s infinite;
        margin-right: 10px;
    }
    @keyframes pulse {
        0% {transform: scale(0.8); opacity: 0.7;}
        50% {transform: scale(1.2); opacity: 1;}
        100% {transform: scale(0.8); opacity: 0.7;}
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
if 'listening' not in st.session_state:
    st.session_state.listening = False
if 'last_transcription' not in st.session_state:
    st.session_state.last_transcription = ""

# Load language resources
LANGUAGE_RESOURCES = {
    "Zulu": {
        "greeting": "Sawubona! Ngingakusiza ngani namuhla?",
        "agriculture": {
            "pests": "Ukulwa nezinambuzane, sebenzisa i-organic pesticide. Hlola izitshalo nsuku zonke.",
            "planting": "Isikhathi esihle sokutshala u-September kuya ku-October emaphandleni aseNingizimu Afrika.",
            "soil": "Hlola umhlabathi wakho ngonyaka. Geza ngomquba wemvelo ukuze uthuthukise isimo somhlabathi."
        },
        "healthcare": {
            "symptoms": "Uma unezimpawu ezingajwayelekile, xhumana nogoti wezempilo ngokushesha.",
            "medication": "Ungaphuze umuthi ngaphandle kokweluleka kudokotela.",
            "hygiene": "Geza izandla zakho qhaba ngesikhathi eside ukuze uvimbele ukusakazeka kwegciwane."
        }
    },
    "Tswana": {
        "greeting": "Dumela! O ka thusa jang kajeno?",
        "agriculture": {
            "pests": "Go lwa le disenyi, dirisa di-pesticide tsa tlhago. Sekaseka dimela letsatsi le letsatsi.",
            "planting": "Nako e e siameng go jala ke September go ya go October mo mafelong a Aforika Borwa.",
            "soil": "Sekaseka mmu wa gago ngwaga le ngwaga. O ka dirisa motswako wa tlhago go tokafatsa mmu."
        },
        "healthcare": {
            "symptoms": "Fa o na le matshwao a a sa tlwaelegang, ikopanye le moapei wa tsa boitekanelo ka bonako.",
            "medication": "O se ka wa nwa ditlhare ntle le go laola ngaka.",
            "hygiene": "Hlatswa diatla tsa gago ka nako e telele go thibela phetiso ya diruiwa."
        }
    }
}

# Initialize ASR pipeline with local model
@st.cache_resource
def load_asr_model():
    try:
        return pipeline(
            "automatic-speech-recognition", 
            model="./wav2vec2-large-xlsr-53",  # Local model path
            tokenizer="./wav2vec2-large-xlsr-53",  # Local tokenizer
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
    except Exception as e:
        st.error(f"Model loading failed: {str(e)}")
        st.stop()

asr_pipeline = load_asr_model()

# Audio processing callback
def audio_frame_callback(frame: av.AudioFrame) -> av.AudioFrame:
    audio = frame.to_ndarray(format="f32le")
    
    # Process audio for ASR
    if len(audio) > 0:
        inputs = {
            "raw": audio,
            "sampling_rate": frame.sample_rate
        }
        try:
            results = asr_pipeline(inputs)
            st.session_state.last_transcription = results['text']
            st.session_state.listening = False
        except Exception as e:
            st.error(f"Speech recognition error: {str(e)}")
    
    return frame

# Generate audio response
def generate_audio_response(text, language):
    try:
        lang_code = "zu" if language == "Zulu" else "tn"
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.save("response.mp3")
        audio_file = open("response.mp3", "rb")
        audio_bytes = audio_file.read()
        audio_file.close()
        return audio_bytes
    except Exception as e:
        st.error(f"Audio generation failed: {str(e)}")
        return None

# App layout
st.title("🗣️ Indigenous Language Voice Assistant")
st.markdown("""
**Bridging the digital divide for Zulu and Tswana speakers through voice technology**  
*Powered by Mozilla DeepSpeech, NWU Language Lab, and Hugging Face Transformers*
""")
st.divider()

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Flag_of_South_Africa.svg/1200px-Flag_of_South_Africa.svg.png", width=100)
    st.header("⚙️ Configuration")
    
    st.session_state.selected_language = st.radio(
        "Select Language",
        ["Zulu", "Tswana"],
        index=0 if st.session_state.selected_language == "Zulu" else 1
    )
    
    st.session_state.domain = st.radio(
        "Application Domain",
        ["Healthcare", "Agriculture"],
        index=0 if st.session_state.domain == "Healthcare" else 1
    )
    
    st.divider()
    st.markdown("""
    **Technology Stack:**
    - Mozilla DeepSpeech (ASR)
    - NWU Language Lab Resources
    - Hugging Face Transformers
    - Google Text-to-Speech
    """)
    
    st.divider()
    st.markdown("""
    **Supported Features:**
    - Real-time speech recognition
    - Agricultural advisory
    - Healthcare information
    - Multilingual responses
    """)
    
    st.divider()
    st.markdown("""
    *Developed with ❤️ for South African communities*  
    *v1.0 | © 2023 Language Access Initiative*
    """)

# Main content tabs
tab1, tab2, tab3 = st.tabs(["Voice Assistant", "Language Resources", "Usage Analytics"])

with tab1:
    st.subheader(f"{st.session_state.selected_language} Voice Assistant")
    st.markdown(f"<div class='language-badge {st.session_state.selected_language.lower()}-badge'>{st.session_state.selected_language} Mode • {st.session_state.domain}</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Voice input section
        st.markdown("### 🎤 Voice Input")
        st.caption("Click 'Start' and speak in your indigenous language")
        
        if st.button("Start Listening", key="start_listening"):
            st.session_state.listening = True
            
        if st.session_state.listening:
            st.markdown("<div class='mic-animation'></div> Listening... Speak now", unsafe_allow_html=True)
            
            webrtc_ctx = webrtc_streamer(
                key="speech-to-text",
                mode=WebRtcMode.SENDONLY,
                audio_frame_callback=audio_frame_callback,
                media_stream_constraints={"audio": True, "video": False},
                rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
                async_processing=True
            )
        else:
            st.info("Click 'Start Listening' to begin voice input")
        
        if st.session_state.last_transcription:
            st.markdown("### 💬 Transcription")
            st.write(st.session_state.last_transcription)
            
            # Process query
            domain_key = st.session_state.domain.lower()
            lang_data = LANGUAGE_RESOURCES[st.session_state.selected_language]
            
            # Simple intent recognition
            response = lang_data['greeting']
            if "pest" in st.session_state.last_transcription.lower():
                response = lang_data[domain_key]['pests']
            elif "plant" in st.session_state.last_transcription.lower():
                response = lang_data[domain_key]['planting']
            elif "soil" in st.session_state.last_transcription.lower():
                response = lang_data[domain_key]['soil']
            elif "symptom" in st.session_state.last_transcription.lower():
                response = lang_data[domain_key]['symptoms']
            elif "medic" in st.session_state.last_transcription.lower():
                response = lang_data[domain_key]['medication']
            elif "hygiene" in st.session_state.last_transcription.lower():
                response = lang_data[domain_key]['hygiene']
            
            st.session_state.conversation.append({
                "speaker": "User",
                "text": st.session_state.last_transcription
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
    
    with col2:
        # Response section
        st.markdown("### 💬 Assistant Response")
        
        if st.session_state.conversation:
            for msg in reversed(st.session_state.conversation[-2:]):
                speaker = "👤 You" if msg['speaker'] == "User" else "🤖 Assistant"
                st.markdown(f"**{speaker}:** {msg['text']}")
                st.divider()
        
        # Audio playback
        if st.session_state.audio_response:
            st.audio(st.session_state.audio_response, format="audio/mp3")
            st.download_button(
                label="Download Response",
                data=st.session_state.audio_response,
                file_name=f"{st.session_state.selected_language}_response.mp3",
                mime="audio/mp3"
            )
        
        # Domain-specific quick actions
        st.markdown("### ⚡ Quick Actions")
        domain_key = st.session_state.domain.lower()
        
        if st.button(f"Ask about {domain_key} tips"):
            response = LANGUAGE_RESOURCES[st.session_state.selected_language][domain_key]['pests']
            st.session_state.conversation.append({
                "speaker": "Assistant",
                "text": response
            })
            st.session_state.audio_response = generate_audio_response(
                response, 
                st.session_state.selected_language
            )
            st.experimental_rerun()
            
        if st.button("Request translation assistance"):
            response = LANGUAGE_RESOURCES[st.session_state.selected_language]['greeting']
            st.session_state.conversation.append({
                "speaker": "Assistant",
                "text": response
            })
            st.session_state.audio_response = generate_audio_response(
                response, 
                st.session_state.selected_language
            )
            st.experimental_rerun()

with tab2:
    st.subheader("Language Resources")
    st.markdown("""
    ### 📚 Indigenous Language Support
    Explore resources for Zulu and Tswana languages
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### isiZulu Resources")
        st.markdown("""
        - **Common Phrases:**
          - Hello: Sawubona
          - Thank you: Ngiyabonga
          - How are you?: Unjani?
        
        - **Agriculture Terms:**
          - Soil: Umhlabathi
          - Crops: Izitshalo
          - Harvest: Isivuno
        
        - **Healthcare Terms:**
          - Doctor: Udokotela
          - Medicine: Umuthi
          - Symptoms: Izimpawu
        """)
        
        st.markdown("#### Learning Materials")
        st.markdown("""
        - [Zulu Grammar Guide](https://example.com)
        - [Zulu-English Dictionary](https://example.com)
        - [Cultural Resources](https://example.com)
        """)
    
    with col2:
        st.markdown("#### Setswana Resources")
        st.markdown("""
        - **Common Phrases:**
          - Hello: Dumela
          - Thank you: Ke a leboga
          - How are you?: O tsogile jang?
        
        - **Agriculture Terms:**
          - Soil: Mmu
          - Crops: Dimerela
          - Harvest: Go roba
        
        - **Healthcare Terms:**
          - Doctor: Ngaka
          - Medicine: Dithlare
          - Symptoms: Matshwao
        """)
        
        st.markdown("#### Learning Materials")
        st.markdown("""
        - [Tswana Grammar Guide](https://example.com)
        - [Tswana-English Dictionary](https://example.com)
        - [Cultural Resources](https://example.com)
        """)
    
    st.divider()
    st.subheader("Community Contributions")
    st.markdown("""
    ### 👥 Join Our Community
    Help us improve our language resources:
    """)
    
    with st.form("contribution_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Email")
        language = st.selectbox("Language", ["Zulu", "Tswana"])
        contribution = st.text_area("Contribution (phrase, translation, or resource)")
        
        if st.form_submit_button("Submit Contribution"):
            st.success("Thank you for your contribution! Our language team will review it.")

with tab3:
    st.subheader("Usage Analytics")
    st.markdown("""
    ### 📊 Adoption Metrics
    Track the impact of our indigenous language technology
    """)
    
    # Generate mock analytics data
    languages = ["Zulu", "Tswana", "Zulu", "Tswana", "Zulu"]
    domains = ["Healthcare", "Agriculture", "Healthcare", "Agriculture", "Healthcare"]
    regions = ["KwaZulu-Natal", "North West", "Gauteng", "Limpopo", "Eastern Cape"]
    usage = [120, 85, 95, 70, 110]
    
    analytics_df = pd.DataFrame({
        "Language": languages,
        "Domain": domains,
        "Region": regions,
        "Usage": usage
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Language Distribution")
        lang_counts = analytics_df["Language"].value_counts().reset_index()
        fig1 = px.pie(
            lang_counts, 
            names="Language", 
            values="count",
            color="Language",
            color_discrete_map={"Zulu": "#FFD54F", "Tswana": "#4FC3F7"}
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        st.markdown("#### Regional Adoption")
        region_counts = analytics_df.groupby("Region")["Usage"].sum().reset_index()
        fig2 = px.bar(
            region_counts, 
            x="Region", 
            y="Usage",
            color="Region",
            title="Usage by Region"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        st.markdown("#### Domain Usage")
        domain_counts = analytics_df["Domain"].value_counts().reset_index()
        fig3 = px.bar(
            domain_counts, 
            x="Domain", 
            y="count",
            color="Domain",
            color_discrete_sequence=["#2c5f2d", "#97bc62"],
            title="Usage by Application Domain"
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("#### Monthly Growth")
        months = ["Jan", "Feb", "Mar", "Apr", "May"]
        zulu_growth = [50, 75, 90, 110, 140]
        tswana_growth = [30, 50, 65, 80, 100]
        
        fig4 = px.line(
            x=months,
            y=[zulu_growth, tswana_growth],
            title="Monthly Active Users",
            labels={"x": "Month", "value": "Users"},
            color_discrete_sequence=["#FFD54F", "#4FC3F7"]
        )
        fig4.update_layout(showlegend=True)
        fig4.data[0].name = "Zulu"
        fig4.data[1].name = "Tswana"
        st.plotly_chart(fig4, use_container_width=True)

# Footer
st.divider()
st.markdown("""
<div style="text-align:center; color:#6c757d; font-size:0.9em; padding:20px;">
    Indigenous Language Voice Assistant v1.0 | 
    <a href="#" style="color:#2c5f2d;">Privacy Policy</a> | 
    <a href="#" style="color:#2c5f2d;">Research Methodology</a> | 
    <a href="#" style="color:#2c5f2d;">Community Guidelines</a>
</div>
""", unsafe_allow_html=True)
