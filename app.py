"""
EchoMinds - Voice Clone & Translate Application
Main Streamlit Application Entry Point
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

# Import core modules
from core.audio_recorder import AudioRecorder
from core.voice_cloner import VoiceCloner
from core.speech_to_text import SpeechToText
from core.translator import Translator
from core.text_to_speech import TextToSpeech
from utils.config import Config
from utils.audio_utils import AudioUtils

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="EchoMinds - Voice Clone & Translate",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .step-card {
        background-color: #000000;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #667eea;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #764ba2;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'cloned_voice_id' not in st.session_state:
        st.session_state.cloned_voice_id = None
    if 'cloned_voice_name' not in st.session_state:
        st.session_state.cloned_voice_name = None
    if 'original_audio_path' not in st.session_state:
        st.session_state.original_audio_path = None
    if 'transcribed_text' not in st.session_state:
        st.session_state.transcribed_text = None
    if 'translated_text' not in st.session_state:
        st.session_state.translated_text = None
    if 'output_audio_path' not in st.session_state:
        st.session_state.output_audio_path = None
    if 'recording_for_clone' not in st.session_state:
        st.session_state.recording_for_clone = True


def main():
    """Main application function"""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🎙️ EchoMinds</h1>
            <p>Voice Clone & Translate - Sesinizi Klonlayın, Dünyanın Dilini Konuşun</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check API key
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        st.error("⚠️ ElevenLabs API key bulunamadı! Lütfen .env dosyasını kontrol edin.")
        st.info("👉 .env.example dosyasını .env olarak kopyalayın ve API key'inizi ekleyin.")
        return
    
    # Initialize components
    config = Config()
    audio_recorder = AudioRecorder(config)
    voice_cloner = VoiceCloner(api_key)
    speech_to_text = SpeechToText(api_key)
    translator = Translator()
    text_to_speech = TextToSpeech(api_key)
    audio_utils = AudioUtils()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Ayarlar")
        
        # Language selection
        st.subheader("🌍 Dil Seçimi")
        target_language = st.selectbox(
            "Hedef Dil",
            options=list(config.SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: f"{config.SUPPORTED_LANGUAGES[x]['flag']} {config.SUPPORTED_LANGUAGES[x]['name']}"
        )
        
        # Voice settings
        st.subheader("🎚️ Ses Ayarları")
        stability = st.slider("Stability (Kararlılık)", 0.0, 1.0, 0.5, 0.05)
        similarity = st.slider("Similarity (Benzerlik)", 0.0, 1.0, 0.75, 0.05)
        
        # Recording duration
        st.subheader("⏱️ Kayıt Süresi")
        max_duration = st.number_input("Maksimum Süre (saniye)", 5, 60, 30)
        
        # Info
        st.markdown("---")
        st.info("💡 **İpucu**: Daha iyi klonlama için 10-30 saniye arası temiz bir ses kaydı yapın.")
        
        if st.session_state.cloned_voice_id:
            st.success(f"✅ Ses klonlandı: {st.session_state.cloned_voice_name}")
    
    # Main content
    col1, col2 = st.columns(2)
    
    # Step 1: Voice Cloning
    with col1:
        st.markdown("""
            <div class="step-card">
                <h3>📝 Adım 1: Sesinizi Klonlayın</h3>
                <p>Mikrofonunuzla 10-30 saniye kadar konuşarak sesinizi klonlayın.</p>
            </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.cloned_voice_id:
            st.warning("🎤 Önce sesinizi klonlamanız gerekiyor!")
            
            # Recording controls
            col_rec1, col_rec2 = st.columns(2)
            with col_rec1:
                if st.button("🔴 Kayda Başla", key="start_clone_recording"):
                    st.session_state.recording_for_clone = True
                    with st.spinner("Ses kaydediliyor..."):
                        audio_path = audio_recorder.record_audio(duration=max_duration)
                        if audio_path:
                            st.session_state.original_audio_path = audio_path
                            st.success("✅ Ses kaydedildi!")
            
            with col_rec2:
                if st.button("⏹️ Kaydı Durdur", key="stop_clone_recording"):
                    st.info("Kayıt tamamlandı.")
            
            # Play recorded audio
            if st.session_state.original_audio_path:
                st.audio(st.session_state.original_audio_path)
                
                # Clone voice button
                voice_name = st.text_input("Ses İsmi", value="MyClonedVoice")
                if st.button("🧬 Sesi Klonla", key="clone_voice"):
                    with st.spinner("Ses klonlanıyor... Bu işlem 10-15 saniye sürebilir."):
                        voice_id = voice_cloner.clone_voice(
                            audio_path=st.session_state.original_audio_path,
                            voice_name=voice_name
                        )
                        if voice_id:
                            st.session_state.cloned_voice_id = voice_id
                            st.session_state.cloned_voice_name = voice_name
                            st.success(f"🎉 Ses başarıyla klonlandı! Voice ID: {voice_id}")
                            st.balloons()
                            st.rerun()
        else:
            st.success(f"✅ Klonlanmış Ses: **{st.session_state.cloned_voice_name}**")
            st.info(f"🆔 Voice ID: `{st.session_state.cloned_voice_id}`")
            
            if st.button("🔄 Yeni Ses Klonla", key="reset_voice"):
                st.session_state.cloned_voice_id = None
                st.session_state.cloned_voice_name = None
                st.session_state.original_audio_path = None
                st.rerun()
    
    # Step 2: Record and Translate
    with col2:
        st.markdown("""
            <div class="step-card">
                <h3>🌍 Adım 2: Konuşun ve Çevirin</h3>
                <p>Çevrilmesini istediğiniz metni sesli olarak söyleyin.</p>
            </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.cloned_voice_id:
            st.info("👈 Önce sol taraftaki adımları tamamlayın.")
        else:
            # Recording for translation
            col_trans1, col_trans2 = st.columns(2)
            with col_trans1:
                if st.button("🎤 Konuşmaya Başla", key="start_translate_recording"):
                    with st.spinner("Ses kaydediliyor..."):
                        audio_path = audio_recorder.record_audio(duration=max_duration)
                        if audio_path:
                            st.session_state.original_audio_path = audio_path
                            st.success("✅ Ses kaydedildi!")
            
            with col_trans2:
                if st.button("⏹️ Durdur", key="stop_translate_recording"):
                    st.info("Kayıt tamamlandı.")
            
            # Process recorded audio
            if st.session_state.original_audio_path and st.session_state.cloned_voice_id:
                st.audio(st.session_state.original_audio_path)
                
                if st.button("🚀 Çevir ve Konuştur", key="process_translation"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        # Step 1: Speech to Text
                        status_text.text("🎯 Adım 1/4: Ses metne dönüştürülüyor...")
                        progress_bar.progress(25)
                        transcribed_text = speech_to_text.transcribe(
                            st.session_state.original_audio_path
                        )
                        st.session_state.transcribed_text = transcribed_text
                        
                        if transcribed_text:
                            st.success(f"📝 **Orijinal Metin**: {transcribed_text}")
                            
                            # Step 2: Translate
                            status_text.text("🌍 Adım 2/4: Metin çevriliyor...")
                            progress_bar.progress(50)
                            translated_text = translator.translate(
                                text=transcribed_text,
                                target_lang=target_language
                            )
                            st.session_state.translated_text = translated_text
                            
                            if translated_text:
                                st.success(f"🗣️ **Çevrilmiş Metin**: {translated_text}")
                                
                                # Step 3: Text to Speech with cloned voice
                                status_text.text("🎵 Adım 3/4: Klonlanmış ses ile konuşma oluşturuluyor...")
                                progress_bar.progress(75)
                                output_path = text_to_speech.synthesize(
                                    text=translated_text,
                                    voice_id=st.session_state.cloned_voice_id,
                                    stability=stability,
                                    similarity=similarity
                                )
                                
                                if output_path:
                                    st.session_state.output_audio_path = output_path
                                    
                                    # Step 4: Complete
                                    status_text.text("✅ Adım 4/4: Tamamlandı!")
                                    progress_bar.progress(100)
                                    
                                    st.success("🎉 İşlem başarıyla tamamlandı!")
                                    st.balloons()
                                    
                                    # Play output
                                    st.markdown("### 🔊 Çıktı Sesi")
                                    st.audio(output_path)
                                    
                                    # Download button
                                    with open(output_path, "rb") as f:
                                        st.download_button(
                                            label="💾 Ses Dosyasını İndir",
                                            data=f,
                                            file_name=f"echominds_output_{target_language}.mp3",
                                            mime="audio/mpeg"
                                        )
                                else:
                                    st.error("❌ Ses sentezleme başarısız!")
                            else:
                                st.error("❌ Çeviri başarısız!")
                        else:
                            st.error("❌ Ses metne dönüştürülemedi!")
                            
                    except Exception as e:
                        st.error(f"❌ Hata oluştu: {str(e)}")
                    finally:
                        progress_bar.empty()
                        status_text.empty()
    
    # Results section
    if st.session_state.transcribed_text or st.session_state.translated_text:
        st.markdown("---")
        st.header("📊 Sonuçlar")
        
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            if st.session_state.transcribed_text:
                st.markdown("### 📝 Orijinal Metin")
                st.info(st.session_state.transcribed_text)
        
        with col_res2:
            if st.session_state.translated_text:
                st.markdown("### 🌍 Çevrilmiş Metin")
                st.success(st.session_state.translated_text)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 2rem 0;'>
            <p>Made with ❤️ by EchoMinds Team | Powered by ElevenLabs AI</p>
            <p>🎙️ Voice Clone & Translate Application v1.0</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
