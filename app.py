"""
Enhanced Voice Cloning Application based on Hugging Face Chatterbox
Features:
- No character limit for text input
- Dark mode support
- All original parameters maintained
- Responsive design for cross-platform compatibility
"""

import random
import numpy as np
import torch
from chatterbox.src.chatterbox.tts import ChatterboxTTS
import gradio as gr
import spaces

# Device configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🚀 Running on device: {DEVICE}")

# --- Global Model Initialization ---
MODEL = None

def get_or_load_model():
    """Loads the ChatterboxTTS model if it hasn't been loaded already, and ensures it's on the correct device."""
    global MODEL
    if MODEL is None:
        print("Model not loaded, initializing...")
        try:
            MODEL = ChatterboxTTS.from_pretrained(DEVICE)
            if hasattr(MODEL, 'to') and str(MODEL.device) != DEVICE:
                MODEL.to(DEVICE)
            print(f"Model loaded successfully. Internal device: {getattr(MODEL, 'device', 'N/A')}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    return MODEL

# Attempt to load the model at startup.
try:
    get_or_load_model()
except Exception as e:
    print(f"CRITICAL: Failed to load model on startup. Application may not function. Error: {e}")

def set_seed(seed: int):
    """Sets the random seed for reproducibility across torch, numpy, and random."""
    torch.manual_seed(seed)
    if DEVICE == "cuda":
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    random.seed(seed)
    np.random.seed(seed)

@spaces.GPU
def generate_tts_audio(
    text_input: str,
    audio_prompt_path_input: str,
    exaggeration_input: float,
    temperature_input: float,
    seed_num_input: int,
    cfgw_input: float
) -> tuple[int, np.ndarray]:
    """
    Generates TTS audio using the ChatterboxTTS model.
    
    Args:
        text_input: The text to synthesize (no character limit).
        audio_prompt_path_input: Path to the reference audio file.
        exaggeration_input: Exaggeration parameter for the model.
        temperature_input: Temperature parameter for the model.
        seed_num_input: Random seed (0 for random).
        cfgw_input: CFG/Pace weight.
        
    Returns:
        A tuple containing the sample rate (int) and the audio waveform (numpy.ndarray).
    """
    current_model = get_or_load_model()
    if current_model is None:
        raise RuntimeError("TTS model is not loaded.")
        
    if seed_num_input != 0:
        set_seed(int(seed_num_input))
        
    print(f"Generating audio for text: '{text_input[:50]}...'")
    
    # No character limit - use the full text
    wav = current_model.generate(
        text_input,  # No truncation
        audio_prompt_path=audio_prompt_path_input,
        exaggeration=exaggeration_input,
        temperature=temperature_input,
        cfg_weight=cfgw_input,
    )
    
    print("Audio generation complete.")
    return (current_model.sr, wav.squeeze(0).numpy())

# CSS for dark mode and responsive design
css = """
/* Light mode (default) */
:root {
    --background-color: #ffffff;
    --text-color: #000000;
    --secondary-background: #f6f6f6;
    --border-color: #e0e0e0;
    --primary-color: #2e7eff;
    --secondary-color: #6b7280;
}

/* Dark mode */
.dark-mode {
    --background-color: #121212;
    --text-color: #e1e1e1;
    --secondary-background: #1e1e1e;
    --border-color: #333333;
    --primary-color: #bb86fc;
    --secondary-color: #b0b0b0;
}

body.dark-mode {
    background-color: var(--background-color);
    color: var(--text-color);
}

.dark-mode .gradio-container {
    background-color: var(--background-color);
}

.dark-mode .gr-button {
    background-color: var(--secondary-background);
    color: var(--text-color);
    border-color: var(--border-color);
}

.dark-mode .gr-button-primary {
    background-color: var(--primary-color);
    color: white;
}

.dark-mode .gr-input, 
.dark-mode .gr-textarea,
.dark-mode .gr-dropdown {
    background-color: var(--secondary-background);
    color: var(--text-color);
    border-color: var(--border-color);
}

.dark-mode .gr-panel {
    background-color: var(--secondary-background);
    border-color: var(--border-color);
}

.dark-mode .gr-box {
    background-color: var(--secondary-background);
    border-color: var(--border-color);
}

.dark-mode .gr-form {
    background-color: var(--secondary-background);
    border-color: var(--border-color);
}

.dark-mode .gr-accordion {
    background-color: var(--secondary-background);
    border-color: var(--border-color);
}

.dark-mode .gr-slider {
    background-color: var(--secondary-background);
}

.dark-mode .gr-slider-handle {
    background-color: var(--primary-color);
}

/* Responsive design */
@media (max-width: 768px) {
    .container {
        flex-direction: column !important;
    }
    
    .gr-box {
        width: 100% !important;
        margin-right: 0 !important;
        margin-left: 0 !important;
    }
    
    .gr-input, .gr-textarea {
        font-size: 16px !important; /* Better for mobile touch */
    }
    
    .gr-button {
        padding: 10px !important;
        margin: 5px 0 !important;
        width: 100% !important;
    }
    
    .gr-form > div {
        flex-direction: column !important;
    }
    
    /* Improve touch targets */
    .gr-slider-handle {
        width: 24px !important;
        height: 24px !important;
    }
    
    /* Adjust spacing */
    .gr-padded {
        padding: 10px !important;
    }
    
    /* Ensure audio controls are usable on mobile */
    audio {
        width: 100% !important;
    }
}

/* File upload improvements */
.gr-file-drop {
    border: 2px dashed var(--border-color) !important;
    border-radius: 8px !important;
    padding: 20px !important;
    text-align: center !important;
    transition: all 0.3s ease !important;
}

.gr-file-drop:hover, .gr-file-drop.dragging {
    border-color: var(--primary-color) !important;
    background-color: rgba(var(--primary-color-rgb), 0.05) !important;
}

/* Progress indicator styling */
.status-box {
    padding: 10px;
    border-radius: 4px;
    margin-top: 10px;
    transition: all 0.3s ease;
}

.status-ready {
    background-color: #e8f5e9;
    color: #2e7d32;
}

.status-processing {
    background-color: #e3f2fd;
    color: #1976d2;
}

.status-error {
    background-color: #ffebee;
    color: #c62828;
}

.dark-mode .status-ready {
    background-color: rgba(46, 125, 50, 0.2);
    color: #81c784;
}

.dark-mode .status-processing {
    background-color: rgba(25, 118, 210, 0.2);
    color: #64b5f6;
}

.dark-mode .status-error {
    background-color: rgba(198, 40, 40, 0.2);
    color: #ef9a9a;
}

/* Character counter */
.char-counter {
    text-align: right;
    font-size: 0.8em;
    color: var(--secondary-color);
    margin-top: 4px;
}
"""

def toggle_dark_mode(dark_mode):
    """Toggle between light and dark mode"""
    if dark_mode:
        return gr.update(css=css + "\nbody.dark-mode {}")
    else:
        return gr.update(css=css)

def count_characters(text):
    """Count characters in the text input"""
    count = len(text)
    return f"Character count: {count}"

with gr.Blocks(css=css, theme=gr.themes.Base()) as demo:
    gr.Markdown(
        """
        # Enhanced Voice Cloning Application
        Generate high-quality speech from text with reference audio styling. No character limit!
        """
    )
    
    # Dark mode toggle in the header
    with gr.Row():
        gr.Markdown("## Settings")
        dark_mode = gr.Checkbox(label="Dark Mode", value=False)
    
    dark_mode.change(fn=toggle_dark_mode, inputs=dark_mode, outputs=gr.update())
    
    # Main content in responsive layout
    with gr.Row(equal_height=True) as container:
        with gr.Column(scale=1):
            text = gr.Textbox(
                value="Now let's make my mum's favourite. So three mars bars into the pan. Then we add the tuna and just stir for a bit, just let the chocolate and fish infuse. A sprinkle of olive oil and some tomato ketchup. Now smell that. Oh boy this is going to be incredible.",
                label="Text to synthesize (no character limit)",
                lines=10,  # Increased for better UX with longer texts
                max_lines=20,
                elem_id="text-input"
            )
            
            # Character counter
            char_counter = gr.Markdown("Character count: 0", elem_id="char-counter", elem_classes="char-counter")
            
            # Update character count when text changes
            text.change(fn=count_characters, inputs=text, outputs=char_counter)
            
            ref_wav = gr.Audio(
                sources=["upload", "microphone"],
                type="filepath",
                label="Reference Audio File (Optional)",
                value="https://storage.googleapis.com/chatterbox-demo-samples/prompts/female_shadowheart4.flac",
                elem_id="audio-input"
            )
            
            with gr.Row():
                with gr.Column(scale=1):
                    exaggeration = gr.Slider(
                        0.25, 2, step=.05, 
                        label="Exaggeration (Neutral = 0.5, extreme values can be unstable)", 
                        value=.5,
                        elem_id="exaggeration-slider"
                    )
                
                with gr.Column(scale=1):
                    cfg_weight = gr.Slider(
                        0.2, 1, step=.05, 
                        label="CFG/Pace", 
                        value=0.5,
                        elem_id="cfg-slider"
                    )
            
            with gr.Accordion("More options", open=False):
                with gr.Row():
                    with gr.Column(scale=1):
                        seed_num = gr.Number(value=0, label="Random seed (0 for random)")
                    
                    with gr.Column(scale=1):
                        temp = gr.Slider(0.05, 5, step=.05, label="Temperature", value=.8)
            
            # Progress indicator with styling
            progress = gr.Textbox(
                label="Status", 
                value="Ready", 
                interactive=False,
                elem_id="status-box",
                elem_classes="status-box status-ready"
            )
            
            run_btn = gr.Button("Generate", variant="primary", elem_id="generate-btn")
            
        with gr.Column(scale=1):
            gr.Markdown("## Output")
            audio_output = gr.Audio(label="Generated Audio", elem_id="audio-output")
            
            # Audio format info
            audio_info = gr.Markdown("", elem_id="audio-info")
    
    def update_progress(text_input):
        """Update progress indicator based on text length"""
        char_count = len(text_input)
        if char_count > 1000:
            return "Long text detected. Generation may take longer.", "status-box status-processing"
        return "Ready", "status-box status-ready"
    
    # Update progress indicator when text changes
    text.change(fn=update_progress, inputs=text, outputs=[progress, lambda: gr.update(elem_classes="")])
    
    def generate_with_progress(text_input, audio_prompt_path_input, exaggeration_input, temperature_input, seed_num_input, cfgw_input):
        """Wrapper to update progress during generation"""
        progress_value = "Generating audio..."
        progress_class = "status-box status-processing"
        audio_info_value = ""
        
        yield progress_value, progress_class, None, audio_info_value
        
        try:
            sample_rate, audio_data = generate_tts_audio(
                text_input, 
                audio_prompt_path_input, 
                exaggeration_input, 
                temperature_input, 
                seed_num_input, 
                cfgw_input
            )
            
            # Calculate audio duration
            duration = len(audio_data) / sample_rate
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            
            progress_value = "Audio generation complete!"
            progress_class = "status-box status-ready"
            audio_info_value = f"Audio format: {sample_rate}Hz, Duration: {minutes}m {seconds}s"
            
            yield progress_value, progress_class, (sample_rate, audio_data), audio_info_value
            
        except Exception as e:
            progress_value = f"Error: {str(e)}"
            progress_class = "status-box status-error"
            audio_info_value = "Generation failed"
            
            yield progress_value, progress_class, None, audio_info_value
    
    run_btn.click(
        fn=generate_with_progress,
        inputs=[
            text,
            ref_wav,
            exaggeration,
            temp,
            seed_num,
            cfg_weight,
        ],
        outputs=[
            progress,
            lambda: gr.update(elem_classes=""),
            audio_output,
            audio_info
        ]
    )

# Launch with sharing enabled for testing across devices
demo.launch(share=True)
