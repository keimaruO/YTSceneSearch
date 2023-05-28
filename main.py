#version 0.1.0

import tkinter as tk
import re
import webbrowser
import os
import threading
from tkinter import filedialog, messagebox, StringVar
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize
def search_srt(file_name, keyword1, keyword2, keyword3, search_range):
    result = []

    with open(file_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    def search_keyword(keyword, start_index=0, end_index=len(lines)):
        found_indices = []
        for index in range(start_index, end_index):
            if keyword in lines[index]:
                found_indices.append(index)
        return found_indices

    def find_url(index, time_code):
        while index >= 0:
            if 'https://youtu.be/' in lines[index]:
                url = lines[index].strip()
                if "?t=" in url:
                    url = re.sub(r'\?t=[0-9hms]+', '', url)
                return f"{url}?t={time_code}"
            index -= 1
        return None

    indices_k1 = search_keyword(keyword1)

    for index_k1 in indices_k1:
        start_index = max(0, index_k1 - search_range)
        end_index = min(len(lines), index_k1 + search_range)

        indices_k2 = search_keyword(keyword2, start_index, end_index)

        for index_k2 in indices_k2:
            start_index = max(0, index_k2 - search_range)
            end_index = min(len(lines), index_k2 + search_range)

            indices_k3 = search_keyword(keyword3, start_index, end_index)

            for index_k3 in indices_k3:
                time_code_match = re.search(r'(\d+h)?(\d+m)?(\d+s)', lines[index_k3 - 1])
                if time_code_match:
                    time_code = time_code_match.group(0)
                    url = find_url(index_k3, time_code)
                    if url:
                        result.append((url, lines[index_k3].strip()))

    return result

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("字幕検索アプリ")
        self.geometry("1000x600")
        self.font = "Meiryo UI"
        self.configure(bg="white")
        
        self.file_path_var = StringVar()
        self.search_word1 = StringVar()
        self.search_word2 = StringVar()
        self.search_word3 = StringVar()
        
        # Menu
        menu = tk.Menu(self)
        self.config(menu=menu)
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="開く", command=self.browse_file)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.quit)
        
        # Frame for input and search button
        input_frame = tk.Frame(self, bg="white")
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="ファイルを選択:", font=(self.font, 12), bg="white").grid(row=0, column=0, pady=10)
        tk.Entry(input_frame, textvariable=self.file_path_var, width=50, font=(self.font, 12)).grid(row=0, column=1, pady=10)
        tk.Button(input_frame, text="参照", command=self.browse_file, font=(self.font, 12)).grid(row=0, column=2, pady=10)
        
        self.search_word1_entry = tk.Entry(input_frame, textvariable=self.search_word1, width=50, font=(self.font, 12))
        self.search_word1_entry.grid(row=1, column=1, pady=10)
        self.search_word1_entry.bind("<Return>", self.focus_next)

        self.search_word2_entry = tk.Entry(input_frame, textvariable=self.search_word2, width=50, font=(self.font, 12))
        self.search_word2_entry.grid(row=2, column=1, pady=10)
        self.search_word2_entry.bind("<Return>", self.focus_next)

        self.search_word3_entry = tk.Entry(input_frame, textvariable=self.search_word3, width=50, font=(self.font, 12))
        self.search_word3_entry.grid(row=3, column=1, pady=10)
        self.search_word3_entry.bind("<Return>", self.focus_next)

        tk.Button(input_frame, text="検索", command=self.search_word, font=(self.font, 12)).grid(row=4, column=1, pady=10)

        # Frame for output
        output_frame = tk.Frame(self, bg="white")
        output_frame.pack(padx=50, pady=10, fill="both", expand=True)
                # Text widget for output
        self.output_text = tk.Text(output_frame, wrap="word", font=(self.font, 12), state="disabled")
        self.output_text.pack(pady=10, fill="both", expand=True)

        scrollbar = tk.Scrollbar(output_frame, command=self.output_text.yview, width=20)
        scrollbar.pack(side="right", fill="y")
        self.output_text.configure(yscrollcommand=scrollbar.set)

        # Bind click event to output text
        self.output_text.tag_config("link", foreground="blue", underline=1)
        self.output_text.bind("<Button-1>", self.on_click)

        # Load indicator label
        self.load_label = tk.Label(input_frame, text="Now Loading...", font=(self.font, 12), fg="red", bg="white")
        
        # Window resize handling
        self.bind("<Configure>", self.on_resize)
    def search_srt_from_gui(self, keywords, search_range):
        file_name = self.file_path_var.get()
        srt_data = self.load_srt(file_name)
        tfidf_matrix, feature_names = self.compute_tfidf(srt_data)

        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")

        threads = []
        for keyword in keywords:
            thread = threading.Thread(target=self.search_srt_threaded, args=(keyword, srt_data, tfidf_matrix, feature_names, search_range))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Combine results from all threads and sort by score
        all_results = [thread.result for thread in threads]
        all_results.sort(reverse=True)

        for score, line in all_results:
            self.output_text.insert("end", f"Score: {score}\n{line}\n\n")

        self.output_text.configure(state="disabled")

    def search_word(self):
        """Search for the input words in the selected file"""
        keywords = [self.search_word1.get(), self.search_word2.get(), self.search_word3.get()]
        search_range = 50  # または任意の範囲値

        # Start loading indicator
        self.load_label.grid(row=4, column=0, pady=10)
        self.load_label.update()

        # Start search in a new thread
        threading.Thread(target=self.search_srt_from_gui, args=(keywords, search_range)).start()        
    def search_srt_threaded(self, keyword, srt_data, tfidf_matrix, feature_names, search_range):
        """Search for the keyword in the SRT data using a separate thread"""
        results = []
        keyword_index = feature_names.index(keyword) if keyword in feature_names else -1

        for i, line in enumerate(srt_data):
            if keyword in line:
                score = sum(tfidf_matrix[i, feature_names.index(word)] for word in word_tokenize(line) if word in feature_names)
                results.append((score, line))
        results.sort(reverse=True)
        return results[:search_range]
    def compute_tfidf(self, srt_data):
        """Compute the TF-IDF matrix for the SRT data"""
        tfidf = TfidfVectorizer(tokenizer=word_tokenize, stop_words='english')
        tfidf_matrix = tfidf.fit_transform(srt_data)
        return tfidf_matrix, tfidf.get_feature_names()
    def focus_next(self, event):
        """Move the focus to the next entry widget."""
        event.widget.tk_focusNext().focus()
        return "break"

    def on_resize(self, event):
        """Handle window resize event"""
        self.output_text.configure(width=event.width-20, height=event.height-160)

    def browse_file(self):
        """Browse file and set path to file_path variable"""
        file_path = filedialog.askopenfilename()
        self.file_path_var.set(file_path)

    def search_word(self):
        """Search for the input words in the selected file"""
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")

        # Check if file path is valid
        if not os.path.isfile(self.file_path_var.get()):
            messagebox.showerror("Error", "Invalid file path.")
            self.output_text.configure(state="disabled")
            return

        # Start loading indicator
        self.load_label.grid(row=4, column=0, pady=10)
        self.load_label.update()

        # Start search in a new thread
        threading.Thread(target=self.process_search).start()

    def on_click(self, event):
        index = self.output_text.index(tk.CURRENT)
        line_start = self.output_text.index(f"{index.split('.')[0]}.0")
        url = self.output_text.get(line_start, line_start + " lineend")
        if re.match(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", url):
            self.open_url(url)


    def open_url(self, url):
        webbrowser.open(url, new=2)

    # Move process_search method inside the App class
    def process_search(self):
        file = self.file_path_var.get()
    
        if not os.path.isfile(file):
            messagebox.showerror("Error", "Invalid file path.")
            self.load_label.grid_remove()
            self.output_text.configure(state="disabled")
            return
    
        search_words = [self.search_word1.get(), self.search_word2.get(), self.search_word3.get()]
        search_words = [word.split('|') for word in search_words if word.strip() != ""]
        
        search_range = 50
    
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    
        first_word_indexes = [i for i, line in enumerate(lines) if any(re.search(re.escape(word), line) for word in search_words[0])]
    
        search_indexes = []
        for index in first_word_indexes:
            for i in range(-search_range, search_range + 1):
                search_index = index + i
                if search_index < 0 or search_index >= len(lines):
                    continue
                search_indexes.append(search_index)
    
        result_indexes = [i for i in search_indexes if all(any(re.search(re.escape(word), lines[i]) for word in search_group) for search_group in search_words[1:])]
    
        if not result_indexes:
            self.output_text.insert("end", "検索候補が見つかりませんでした。\n")
    
        prev_url = ""
        prev_line = None
        for index in result_indexes:
            time = re.search(r"(\d{1,2}h)?(\d{1,2}m)?(\d{1,2}s)", lines[index - 1]).group(0)
            youtube_url = None
            for i in range(index - 1, -1, -1):
                if re.search(r"https://youtu.be/", lines[i]):
                    youtube_url = re.search(r"https://youtu.be/.*", lines[i]).group(0)
                    break
            if youtube_url is None:
                continue
            if prev_url != youtube_url:
                self.output_text.insert('end', '\n')
                prev_url = youtube_url
            current_line = lines[index].strip()
            if prev_line != current_line:
                self.output_text.insert('end', f'{youtube_url}?t={time}\n', 'link')
                self.output_text.insert('end', current_line + '\n')
            prev_line = current_line
    
        # Stop loading indicator
        self.load_label.grid_remove()
        self.output_text.configure(state="disabled")
    
    def search_srt_from_gui(self, keyword1, keyword2, keyword3, search_range):
        file_name = self.file_path_var.get()
        search_results = search_srt(file_name, keyword1, keyword2, keyword3, search_range)

        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")

        for result in search_results:
            url, line = result
            self.output_text.insert("end", url, "link")
            self.output_text.insert("end", "\n" + line + "\n\n")

        self.output_text.configure(state="disabled")

    # search_wordメソッドを変更して、新しいsearch_srt_from_guiメソッドを呼び出す
    def search_word(self):
        """Search for the input words in the selected file"""
        keyword1 = self.search_word1.get()
        keyword2 = self.search_word2.get()
        keyword3 = self.search_word3.get()
        search_range = 50  # または任意の範囲値

        # Start loading indicator
        self.load_label.grid(row=4, column=0, pady=10)
        self.load_label.update()

        # Start search in a new thread
        threading.Thread(target=self.search_srt_from_gui, args=(keyword1, keyword2, keyword3, search_range)).start()

if __name__ == "__main__":
    app = App()
    app.mainloop()
