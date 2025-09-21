# tipico.py

from IPython.display import HTML, display
from google.colab import files
import os
from IPython.utils import io
import subprocess
import re
import sys
import time

# Fonction pour masquer le code
def hide_code():
    display(HTML('''<script>
        code_show=true; 
        function code_toggle() {
         if (code_show){
         $('div.input').hide();
         } else {
         $('div.input').show();
         }
         code_show = !code_show
        } 
        $( document ).ready(code_toggle);
    </script>
    <form><input type="button" value="Afficher/Masquer le code" onclick="code_toggle()"></form>'''))

hide_code()

# 1️⃣ Téléverser le fichier audio
uploaded = files.upload()
audio_file = list(uploaded.keys())[0]

# 2️⃣ Écrire le fichier sur le disque
with open(audio_file, "wb") as f:
    f.write(uploaded[audio_file])
del uploaded

# 3️⃣ Installer Whisper et ffmpeg
with io.capture_output() as captured:
    subprocess.run(["pip", "install", "--upgrade", "openai-whisper"], check=True)
    subprocess.run(["apt", "update", "-y"], check=True)
    subprocess.run(["apt", "install", "ffmpeg", "-y"], check=True)

# 4️⃣ Récupérer la durée totale de l'audio
def get_audio_duration(file_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout)

total_duration = get_audio_duration(audio_file)

def timestamp_to_seconds(ts):
    h, m, s = ts.split(":")
    return int(h)*3600 + int(m)*60 + float(s)

# 5️⃣ Transcrire avec Whisper et afficher une barre d'avancement
print("Transcription en cours...")

process = subprocess.Popen(
    ["whisper", audio_file, "--model", "large"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True,
    bufsize=1
)

for line in process.stdout:
    line = line.strip()
    # Chercher les timestamps du type [00:03.000 --> 00:04.000]
    match = re.search(r'\[(\d+:\d+\.\d+) --> (\d+:\d+\.\d+)\]', line)
    if match:
        end_time = match.group(2)
        progress = (timestamp_to_seconds(end_time) / total_duration) * 100
        bar_length = 30
        filled_length = int(bar_length * progress // 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f'\rProgression : |{bar}| {progress:.1f}%')
        sys.stdout.flush()

process.wait()
print("\nTranscription terminée !")

# 6️⃣ Préparer le nom du fichier texte généré
txt_file = os.path.splitext(audio_file)[0] + ".txt"

# 7️⃣ Télécharger automatiquement le fichier texte
files.download(txt_file)
