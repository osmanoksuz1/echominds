"""
Text to Speech Module
Handles speech synthesis using ElevenLabs API with cloned voices
"""

from elevenlabs import ElevenLabs, Voice, VoiceSettings
from pathlib import Path
from datetime import datetime


class TextToSpeech:
    """
    Text-to-speech synthesis using ElevenLabs API
    """
    
    def __init__(self, api_key):
        """
        Initialize TextToSpeech
        
        Args:
            api_key: ElevenLabs API key
        """
        self.api_key = api_key
        self.client = ElevenLabs(api_key=api_key)
        
        # Ensure output directory exists
        self.output_dir = Path("assets/outputs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def synthesize(self, text, voice_id, stability=0.5, similarity=0.75, output_path=None):
        """
        Synthesize speech from text using a specific voice
        
        Args:
            text: Text to convert to speech
            voice_id: ID of the voice to use (cloned or preset)
            stability: Voice stability (0.0 to 1.0, default: 0.5)
            similarity: Voice similarity boost (0.0 to 1.0, default: 0.75)
            output_path: Custom output path (optional)
        
        Returns:
            str: Path to generated audio file, or None if failed
        """
        try:
            print(f"🎵 Synthesizing speech...")
            print(f"📝 Text: {text}")
            print(f"🆔 Voice ID: {voice_id}")
            
            # Generate audio
            audio_generator = self.client.generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=VoiceSettings(
                        stability=stability,
                        similarity_boost=similarity
                    )
                ),
                model="eleven_monolingual_v1"  # or "eleven_multilingual_v2" for multiple languages
            )
            
            # Convert generator to bytes
            audio_bytes = b"".join(audio_generator)
            
            # Save to file
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"output_{timestamp}.mp3"
                output_path = self.output_dir / filename
            
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            
            print(f"✅ Audio generated successfully!")
            print(f"💾 Saved to: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Speech synthesis failed: {str(e)}")
            return None
    
    def synthesize_streaming(self, text, voice_id, stability=0.5, similarity=0.75):
        """
        Synthesize speech with streaming (for real-time playback)
        
        Args:
            text: Text to convert to speech
            voice_id: ID of the voice to use
            stability: Voice stability (0.0 to 1.0)
            similarity: Voice similarity boost (0.0 to 1.0)
        
        Returns:
            generator: Audio data generator
        """
        try:
            audio_generator = self.client.generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=VoiceSettings(
                        stability=stability,
                        similarity_boost=similarity
                    )
                ),
                stream=True
            )
            
            return audio_generator
            
        except Exception as e:
            print(f"❌ Streaming synthesis failed: {str(e)}")
            return None
    
    def synthesize_multilingual(self, text, voice_id, stability=0.5, similarity=0.75):
        """
        Synthesize speech using multilingual model
        
        Args:
            text: Text to convert to speech (any language)
            voice_id: ID of the voice to use
            stability: Voice stability
            similarity: Voice similarity boost
        
        Returns:
            str: Path to generated audio file
        """
        try:
            print(f"🌍 Multilingual synthesis started...")
            
            audio_generator = self.client.generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=VoiceSettings(
                        stability=stability,
                        similarity_boost=similarity
                    )
                ),
                model="eleven_multilingual_v2"  # Multilingual model
            )
            
            audio_bytes = b"".join(audio_generator)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"multilingual_{timestamp}.mp3"
            output_path = self.output_dir / filename
            
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            
            print(f"✅ Multilingual audio generated!")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Multilingual synthesis failed: {str(e)}")
            return None
    
    def batch_synthesize(self, texts, voice_id, stability=0.5, similarity=0.75):
        """
        Synthesize multiple texts
        
        Args:
            texts: List of texts to convert
            voice_id: Voice ID to use
            stability: Voice stability
            similarity: Voice similarity boost
        
        Returns:
            list: List of generated audio file paths
        """
        output_paths = []
        
        for i, text in enumerate(texts):
            print(f"\n📄 Synthesizing {i+1}/{len(texts)}...")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_{i+1}_{timestamp}.mp3"
            output_path = self.output_dir / filename
            
            result = self.synthesize(
                text=text,
                voice_id=voice_id,
                stability=stability,
                similarity=similarity,
                output_path=output_path
            )
            
            if result:
                output_paths.append(result)
        
        return output_paths
    
    def get_available_models(self):
        """
        Get list of available TTS models
        
        Returns:
            list: List of model names
        """
        return [
            "eleven_monolingual_v1",  # English only, highest quality
            "eleven_multilingual_v1",  # Multiple languages
            "eleven_multilingual_v2",  # Latest multilingual
            "eleven_turbo_v2"  # Fastest, lower quality
        ]
    
    def validate_text(self, text, max_length=5000):
        """
        Validate if text is suitable for TTS
        
        Args:
            text: Text to validate
            max_length: Maximum allowed length (default: 5000)
        
        Returns:
            tuple: (is_valid, message)
        """
        if not text or text.strip() == "":
            return False, "Text is empty"
        
        if len(text) > max_length:
            return False, f"Text too long ({len(text)} chars). Maximum: {max_length}"
        
        # Check for special characters that might cause issues
        # This is optional and depends on your requirements
        
        return True, "Text valid"
    
    def estimate_audio_duration(self, text, words_per_minute=150):
        """
        Estimate audio duration from text length
        
        Args:
            text: Text to estimate duration for
            words_per_minute: Average speaking rate (default: 150 WPM)
        
        Returns:
            float: Estimated duration in seconds
        """
        word_count = len(text.split())
        duration_minutes = word_count / words_per_minute
        duration_seconds = duration_minutes * 60
        
        return duration_seconds
    
    def get_voice_settings_preset(self, preset='balanced'):
        """
        Get preset voice settings
        
        Args:
            preset: Preset name ('stable', 'balanced', 'expressive')
        
        Returns:
            dict: Voice settings
        """
        presets = {
            'stable': {'stability': 0.75, 'similarity': 0.75},
            'balanced': {'stability': 0.50, 'similarity': 0.75},
            'expressive': {'stability': 0.30, 'similarity': 0.80}
        }
        
        return presets.get(preset, presets['balanced'])
    
    def synthesize_with_preset(self, text, voice_id, preset='balanced'):
        """
        Synthesize speech using preset settings
        
        Args:
            text: Text to convert
            voice_id: Voice ID
            preset: Settings preset name
        
        Returns:
            str: Path to generated audio file
        """
        settings = self.get_voice_settings_preset(preset)
        
        return self.synthesize(
            text=text,
            voice_id=voice_id,
            stability=settings['stability'],
            similarity=settings['similarity']
        )
    
    def get_audio_info(self, audio_path):
        """
        Get information about generated audio file
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            dict: Audio information
        """
        try:
            import soundfile as sf
            
            info = sf.info(audio_path)
            
            return {
                'duration': info.duration,
                'sample_rate': info.samplerate,
                'channels': info.channels,
                'format': info.format,
                'frames': info.frames,
                'file_size': Path(audio_path).stat().st_size
            }
            
        except Exception as e:
            print(f"❌ Error getting audio info: {str(e)}")
            return None
