import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import whisper
from rapidfuzz import fuzz

def analyze_word_gaps(audio_path, target_words, fuzzy_threshold):
    model = whisper.load_model("small")
    result = model.transcribe(audio_path)
    
    # przygotowujemy słownik dla każdego target word
    word_timestamps = {w: [] for w in target_words}
    
    for segment in result["segments"]:
        text = segment["text"].lower()
        words_in_segment = text.split()
        
        for target in target_words:
            if fuzzy_threshold is None:
                if target in text:
                    word_timestamps[target].append(segment["start"])
            else:
                for word in words_in_segment:
                    if fuzz.ratio(word, target) >= fuzzy_threshold:
                        word_timestamps[target].append(segment["start"])
                        break  # znaleziono w tym segmencie
    
    # przygotowanie outputu
    output = ""
    for target, timestamps in word_timestamps.items():
        output += f"\n--- {target.upper()} ---\n"
        if not timestamps:
            output += "No occurrences found.\n"
            continue
        
        output += f"Total occurrences: {len(timestamps)}\n"
        output += "Occurrences at times:\n"
        for t in timestamps:
            output += f"- {t:.2f} s\n"
        
        gaps = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        if gaps:
            output += "Time gaps (seconds):\n"
            for g in gaps:
                output += f"- {g:.2f} s\n"
            output += f"Average gap: {sum(gaps)/len(gaps):.2f} s\n"
            output += f"Shortest gap: {min(gaps):.2f} s\n"
            output += f"Longest gap: {max(gaps):.2f} s\n"
        else:
            output += "Occurred only once, no gaps.\n"
    
    return output

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3 *.m4a *.wav")])
    if filename:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filename)

def run_analysis():
    audio_file = file_entry.get()
    words_input = words_entry.get()
    threshold_input = threshold_entry.get()
    
    if not audio_file:
        messagebox.showwarning("No file", "Please select an audio file!")
        return
    
    if not words_input:
        messagebox.showwarning("No words", "Enter at least one target word!")
        return
    
    target_words = [w.strip().lower() for w in words_input.split(",") if w.strip()]
    
    try:
        fuzzy_threshold = int(threshold_input) if threshold_input else None
    except ValueError:
        messagebox.showwarning("Invalid threshold", "Threshold must be a number between 0 and 100")
        return
    
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, "Analyzing, please wait...\n")
    root.update()
    
    try:
        output = analyze_word_gaps(audio_file, target_words, fuzzy_threshold)
        log_text.insert(tk.END, output)
    except Exception as e:
        log_text.insert(tk.END, f"Error: {e}")

# --- GUI ---
root = tk.Tk()
root.title("WordsCounter")

tk.Label(root, text="Audio file:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
file_entry = tk.Entry(root, width=50)
file_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Target words (comma-separated):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
words_entry = tk.Entry(root, width=50)
words_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

tk.Label(root, text="Fuzzy threshold (0-100, optional):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
threshold_entry = tk.Entry(root, width=10)
threshold_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

tk.Button(root, text="Analyze", command=run_analysis).grid(row=3, column=1, pady=10)

log_text = scrolledtext.ScrolledText(root, width=70, height=20)
log_text.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

root.mainloop()
