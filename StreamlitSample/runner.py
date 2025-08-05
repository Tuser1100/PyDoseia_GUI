import os
import yaml
import random
import subprocess
import streamlit as st
from datetime import datetime

vedic_quotes = [
    "Tat Tvam Asi (तत्त्वमसि) - Thou art that. - Chandogya Upanishad",
    "Aham Brahmasmi (अहं ब्रह्मास्मि) - I am Brahman. - Brihadaranyaka Upanishad",
    "Atman is Brahman. The self and the cosmic are one. - Advaita Vedanta",
    "Satyam eva jayate - Truth alone triumphs. - Mundaka Upanishad",
    "All that we are is the result of what we have thought. - Buddha",
    "He who sees all beings in his own self, and his own self in all beings, loses all fear. - Isa Upanishad",
    "There is no joy in the finite; there is joy only in the Infinite. - Chandogya Upanishad",
    "From the unreal, lead me to the real. From darkness, lead me to light. From death, lead me to immortality. - Brihadaranyaka Upanishad",
    "The self is not the body; the self is eternal, indestructible, and infinite. - Bhagavad Gita",
    "One who sees all beings as the Self and the Self in all beings has no hatred for any. - Isa Upanishad",
    "As the rivers flowing east and west merge in the sea and become one, so do all beings merge into the One. - Chandogya Upanishad",
    "He who knows himself to be the atman of all beings and all beings in the atman, hates none. - Isa Upanishad",
    "Where there is duality, there one sees another; but where everything has become one's own self, then who shall see whom? - Brihadaranyaka Upanishad",
    "Let your mind be clear and calm, like a serene lake. - Vedic Wisdom",
    "Be steadfast in performing your duty, O Arjuna, abandon attachment and remain balanced in success and failure. - Bhagavad Gita, Chapter 2, Verse 47",
    "The enlightened sees that Brahman is actionless and eternal, beyond good and evil. - Bhagavad Gita",
    "Knowing oneself to be Brahman, and seeing the self in all beings, one attains supreme peace. - Upanishadic Thought",
    "The wise see the same in all, be it a scholar, an outcast, an animal, or a sage. - Bhagavad Gita, Chapter 5, Verse 18",
    "Meditation brings wisdom; lack of meditation leaves ignorance. Know well what leads you forward and what holds you back. - Buddha",
    "Yoga is the journey of the self, through the self, to the self. - Bhagavad Gita",
    "The mind is restless, turbulent, powerful, and obstinate. It is like controlling the wind. - Bhagavad Gita, Chapter 6, Verse 34",
    "One who has control over the mind is tranquil in heat and cold, in pleasure and pain, and in honor and dishonor. - Bhagavad Gita, Chapter 6, Verse 7",
    "All creation is Brahman; and the universe is its play. - Upanishadic Thought",
    "The seeker of the Self should keep the mind calm, like the flame of a lamp in a windless place. - Bhagavad Gita, Chapter 6, Verse 19",
    "Look within. Be still. Free from fear and attachment, know the sweet joy of the way. - Dhammapada",
    "By pure thought, the wise man attains the supreme goal. - Vedic Wisdom"
]

def handle_run(existing_inputs):
    # Retrieve values from sidebar session_state or set defaults
    dir_name = st.session_state.get("custom_dir", f"PyDoseia_Run_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    inp_name = st.session_state.get("inp_file_name", "pydoseia_inp")
    out_name = st.session_state.get("out_file_name", "pydoseia_out")

    # Define paths
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    run_dir = os.path.join(downloads_path, dir_name)
    os.makedirs(run_dir, exist_ok=True)

    log_path = os.path.join(run_dir, f"{inp_name}_info.log")
    input_path = os.path.join(run_dir, f"{inp_name}.yaml")
    output_path = os.path.join(run_dir, f"{out_name}.out")

    existing_inputs["logdir_name"] = run_dir
    existing_inputs["input_file_name"] = inp_name
    existing_inputs["output_file_name"] = out_name

    # Save YAML
    yaml_data = yaml.dump(existing_inputs, sort_keys=False, allow_unicode=True, default_flow_style=False)
    with open(input_path, "w") as f:
        f.write(yaml_data)

    # backend(Pydoseia) call subprocess
    command = [
        "python", "main.py",
        "--config_file", input_path,
        "--logdir", run_dir,
        "--output_file_name", output_path
    ]
    try:
        result = subprocess.run(command, cwd="../", shell=True, capture_output=True, text=True)
    except Exception as e:
        st.error(f"⚠️ Subprocess launch error: {e}")
        st.session_state["run_triggered"] = False
        return

    #Handle subprocess result
    if result.returncode != 0:
        st.error("❌ Backend processing failed:")
        st.code(result.stderr)
        st.text(result.stdout)
        st.session_state["run_triggered"] = False
    else:
        st.success("✅ Simulation complete. Files saved.", icon=":material/published_with_changes:")
        st.session_state["run_triggered"] = True
        #Show downloads after success
        st.download_button("📘 Download YAML Input File", data=yaml_data, file_name=inp_name, mime="text/yaml")

        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                st.download_button("🗂️ Download Log File", f.read(), file_name=os.path.basename(log_path))

        if os.path.exists(output_path):
            with open(output_path, "r") as f:
                st.download_button("📊 Download Output File", f.read(), file_name=os.path.basename(output_path))
        
        random_quote = random.choice(vedic_quotes)
        st.markdown("### 🕉️ *Vedas Teach Us*")
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #f3e7e9 0%, #e3eeff 100%);
                border-left: 6px solid #7d5ba6;
                padding: 1.5em;
                border-radius: 12px;
                font-size: 1.15em;
                font-style: italic;
                color: #333;
                text-align: center;
                margin-top: 1.5em;
            ">
                “{random_quote}”
            </div>
            """,
            unsafe_allow_html=True
        )

    return existing_inputs
