#version 0.1.2 Improved display of search results

import tkinter as tk
import re
import webbrowser
import os
import threading
import itertools  # Import the itertools module
from tkinter import filedialog, messagebox, StringVar
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize

def search_srt(file_name, keyword1, keyword2, keyword3, search_range):

    result = []
    with open(file_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    keyword_patterns = [re.compile(re.escape(word)) for word in [keyword1, keyword2, keyword3]]

    def is_match(line, patterns):
        return all(pattern.search(line) for pattern in patterns)

    search_window = search_range * 2

    for i, line in enumerate(lines):
        if is_match(line, [keyword_patterns[0]]):
            start_index = max(0, i - search_range)
            end_index = min(len(lines), i + search_range + 1)

            for j in range(start_index, end_index):
                if is_match(lines[j], keyword_patterns[1:]):
                    time_code_match = re.search(r'(\d+h)?(\d+m)?(\d+s)', lines[j - 1])
                    if time_code_match:
                        time_code = time_code_match.group(0)
                        url = find_url(lines, j, time_code)
                        if url:
                            result.append((url, lines[j].strip()))
    return result

def find_url(lines, index, time_code):

    for i in range(index, -1, -1):
        if 'https://youtu.be/' in lines[i]:
            url = lines[i].strip()
            if "?t=" in url:
                url = re.sub(r'\?t=[0-9hms]+', '', url)
            return f"{url}?t={time_code}"
    return None

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YTSceneSearch")
        self.geometry("900x550")
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
  
        
        # 入力・検索ボタン
        input_frame = tk.Frame(self, bg="white")
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="File Select:", font=(self.font, 11), bg="white").grid(row=0, column=0, pady=10)
        tk.Entry(input_frame, textvariable=self.file_path_var, width=50, font=(self.font, 11)).grid(row=0, column=1, pady=10)
        tk.Button(input_frame, text="Browse", command=self.browse_file, font=(self.font, 11)).grid(row=0, column=2, pady=10)
        
        self.search_word1_entry = tk.Entry(input_frame, textvariable=self.search_word1, width=50, font=(self.font, 11))
        self.search_word1_entry.grid(row=1, column=1, pady=10)
        self.search_word1_entry.bind("<Return>", self.focus_next)

        self.search_word2_entry = tk.Entry(input_frame, textvariable=self.search_word2, width=50, font=(self.font, 11))
        self.search_word2_entry.grid(row=2, column=1, pady=10)
        self.search_word2_entry.bind("<Return>", self.focus_next)

        self.search_word3_entry = tk.Entry(input_frame, textvariable=self.search_word3, width=50, font=(self.font, 11))
        self.search_word3_entry.grid(row=3, column=1, pady=10)
        self.search_word3_entry.bind("<Return>", self.focus_next)

        tk.Button(input_frame, text="Search", command=self.search_word, font=(self.font, 11)).grid(row=4, column=1, pady=10)

        # 出力
        output_frame = tk.Frame(self, bg="white")
        output_frame.pack(padx=50, pady=10, fill="both", expand=True)


        self.output_text = tk.Text(output_frame, wrap="none", font=(self.font, 11), state="disabled")
        self.output_text.grid(row=0, column=0, sticky='nsew')

        y_scrollbar = tk.Scrollbar(output_frame, command=self.output_text.yview, width=20)
        y_scrollbar.grid(row=0, column=1, sticky='ns')

        x_scrollbar = tk.Scrollbar(output_frame, command=self.output_text.xview, orient="horizontal", width=20)
        x_scrollbar.grid(row=1, column=0, sticky='ew')

        self.output_text.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(0, weight=1)



        self.output_text.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)


        self.output_text.tag_config("link", foreground="blue", underline=1)
        self.output_text.bind("<Button-1>", self.on_click)


        self.load_label = tk.Label(input_frame, text="Now Loading...", font=(self.font, 11), fg="red", bg="white")
        

        self.bind("<Configure>", self.on_resize)


    def search_word(self):
        # ... 
        search_groups = [
            self.search_word1.get().split('|'),
            self.search_word2.get().split('|'),
            self.search_word3.get().split('|'),
        ]
        search_range = 50  # 範囲値

        self.load_label.grid(row=4, column=0, pady=10)
        self.load_label.update()

        threading.Thread(target=self.search_srt_from_gui, args=(search_groups, search_range)).start()     
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

    def on_click(self, event):
        index = self.output_text.index(tk.CURRENT)
        line_start = self.output_text.index(f"{index.split('.')[0]}.0")
        url = self.output_text.get(line_start, line_start + " lineend")
        if re.match(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", url):
            self.open_url(url)

    def open_url(self, url):
        webbrowser.open(url, new=2)

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
    
        self.load_label.grid_remove()
        self.output_text.configure(state="disabled")
    
    def search_srt_from_gui(self, search_groups, search_range):
        file_name = self.file_path_var.get()
    
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
    
        displayed_urls = set()
    
        for combination in itertools.product(*search_groups):
            search_results = search_srt(file_name, *combination, search_range)
    
            for result in search_results:
                url, line = result

                if url not in displayed_urls:
                    self.output_text.insert("end", url, "link")
                    self.output_text.insert("end", "\n" + line + "\n\n")

                    displayed_urls.add(url)
    
        self.output_text.configure(state="disabled")
        self.after(0, self.load_label.grid_remove)
def parallel_search_srt_files(file_list, keywords):
    with ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(search_srt, file, keywords): file for file in file_list}
        results = {}
        for future in concurrent.futures.as_completed(future_to_file):
            file_name = future_to_file[future]
            try:
                file_name, matches = future.result()
                results[file_name] = matches
            except Exception as exc:
                print(f'{file_name} generated an exception: {exc}')
        return results
if __name__ == "__main__":
    app = App()
    app.mainloop()
