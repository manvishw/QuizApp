import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import json
import datetime
import os
import importlib.util
from tkinter import ttk

# Global Variables
file_path = None
quiz_name = None
quiz_data = []
user_name = None
current_question = 0
user_answers = []
quiz_window = None
score_data = []
progress = None
progress_bar_label = None
start_time = None
end_time = None

# Color Styles
BACKGROUND_COLOR = "#f4f4f9"
BUTTON_COLOR = "#4CAF50"
BUTTON_HOVER_COLOR = "#45a049"
LABEL_COLOR = "#333333"
PROGRESS_BAR_COLOR = "#ff9800"
PROGRESS_BAR_BG_COLOR = "#e0e0e0"
HEADER_COLOR = "#4CAF50"
TEXT_COLOR = "#ffffff"
ERROR_COLOR = "#ff0000"
RESULTS_FILE_COLOR = "#2196F3"


def open_file():
    global file_path, quiz_name, quiz_data, user_name, user_answers
    file_path = filedialog.askopenfilename(title="Select a File",
                                           filetypes=[("JSON Files", "*.json"), ("Python Files", "*.py")])
    if file_path:
        try:
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == '.json':
                with open(file_path, "r") as file:
                    data = json.load(file)
                    if not isinstance(data, dict) or 'quiz_name' not in data or 'questions' not in data:
                        raise ValueError("Invalid quiz file format.")
                    quiz_name = data.get('quiz_name', "Unnamed Quiz")
                    quiz_data = data.get('questions', [])
                    if not isinstance(quiz_data, list) or not all(isinstance(q, dict) and 'question' in q and 'options' in q and 'answer' in q for q in quiz_data):
                        raise ValueError("Invalid questions format.")
                    user_answers = [None] * len(quiz_data)

            elif file_extension == '.py':
                # Load the Python file as a module
                module_name = os.path.basename(file_path).replace('.py', '')
                spec = importlib.util.spec_from_file_location(
                    module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Check if quiz_data is defined and is a list
                if hasattr(module, 'quiz_data') and isinstance(module.quiz_data, list):
                    quiz_data = module.quiz_data
                    # Validate each question in quiz_data
                    if not all(isinstance(q, dict) and 'question' in q and 'options' in q and 'answer' in q for q in quiz_data):
                        raise ValueError(
                            "Invalid format in quiz_data. Each item must be a dictionary with 'question', 'options', and 'answer'.")
                    quiz_name = getattr(module, 'quiz_name', "Unnamed Quiz")
                    user_answers = [None] * len(quiz_data)
                else:
                    raise ValueError(
                        "Invalid Python file format: 'quiz_data' must be a list of questions.")

            # Only ask for the username if it hasn't been set yet
            if not user_name:
                user_name = simpledialog.askstring(
                    "User Name", "Enter your name:")
                if user_name and user_name.strip():
                    start_button.pack(pady=10, padx=20, fill=tk.X)
                else:
                    messagebox.showwarning(
                        "Warning", "You must enter a valid username to proceed.")

        except (json.JSONDecodeError, ValueError, ImportError) as e:
            messagebox.showwarning(
                'Warning', f'Invalid file. Please select a valid quiz file. Error: {e}')
            file_path = None
            quiz_data = []
            user_answers = []


def select_answer():
    global user_answers
    user_answers[current_question] = answer_var.get()


def start_quiz():
    global quiz_window, current_question, progress, progress_bar_label, start_time
    current_question = 0
    start_time = datetime.datetime.now()
    quiz_window = tk.Toplevel(root)
    quiz_window.title("Quiz App")
    quiz_window.geometry("600x500")
    quiz_window.config(bg=BACKGROUND_COLOR)
    quiz_window.columnconfigure(0, weight=1)

    ttk.Label(quiz_window, text=quiz_name, background='Purple',
              style='Main.TLabel').pack(pady=10, padx=10, fill=tk.X)

    global question_label, answer_var, option_buttons, prev_button, next_button, submit_button
    question_label = ttk.Label(quiz_window, text="",
                               wraplength=500, background='purple', foreground='White', justify=tk.CENTER,
                               font=('Verdana', '14'))
    question_label.pack(pady=20, padx=10, fill=tk.X)

    answer_var = tk.StringVar()
    option_frame = tk.Frame(quiz_window, bg=BACKGROUND_COLOR)
    option_frame.pack(pady=10, fill=tk.X)
    option_buttons = [ttk.Radiobutton(option_frame, text="", variable=answer_var, value="",
                                      command=select_answer, style='TRadiobutton',)for _ in range(4)]
    for btn in option_buttons:
        btn.pack(anchor="w", padx=20, pady=2, fill=tk.X)

    progress = ttk.Progressbar(quiz_window, orient=tk.HORIZONTAL,
                               length=300, mode='determinate', style="TProgressbar")
    progress.pack(pady=10, fill=tk.X)

    nav_frame = tk.Frame(quiz_window, bg=BACKGROUND_COLOR)
    nav_frame.pack(pady=10, fill=tk.X)
    nav_frame.columnconfigure((0, 1, 2), weight=1)

    prev_button = ttk.Button(nav_frame, text="Previous",
                             command=previous_question, style='Main.TButton')
    prev_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

    progress_bar_label = ttk.Label(
        nav_frame, text="0%", background='Purple', foreground='white', padding=5, font=('Arial', '16'))
    progress_bar_label.grid(row=0, column=1)

    next_button = ttk.Button(nav_frame, text="Next", command=next_question,
                             style='Main.TButton')
    next_button.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

    submit_button = ttk.Button(quiz_window, text="Submit", command=submit_quiz,
                               style='Main.TButton')
    submit_button.pack(pady=10, fill=tk.X)

    display_question()


def display_question():
    global quiz_data, current_question, option_buttons
    if quiz_data:
        question_label.config(
            text=f"Q{current_question + 1}: {quiz_data[current_question]['question']}")
        options = quiz_data[current_question]['options']
        for i, option in enumerate(options):
            option_buttons[i].config(text=option, value=option)

        update_navigation_buttons()
        update_progress()


def previous_question():
    global current_question
    if current_question > 0:
        current_question -= 1
        display_question()


def next_question():
    global current_question
    if current_question < len(quiz_data) - 1:
        current_question += 1
        display_question()


def update_navigation_buttons():
    prev_button.config(state=tk.NORMAL if current_question >
                       0 else tk.DISABLED)
    next_button.config(state=tk.NORMAL if current_question <
                       len(quiz_data) - 1 else tk.DISABLED)


def update_progress():
    percentage = ((current_question + 1) / len(quiz_data)) * 100
    progress['value'] = percentage
    progress_bar_label.config(text=f"{int(percentage)}%")


def save_results_to_file():
    global user_name, quiz_name, start_time, end_time, user_answers
    score = sum(1 for i, answer in enumerate(user_answers)
                if answer == quiz_data[i]['answer'])
    total_time = (end_time - start_time).total_seconds()

    # If quiz_name is None or empty, use "Unnamed Quiz"
    if not quiz_name:
        quiz_name = "Unnamed Quiz"

    result_data = {
        "User Name": user_name,
        "Score": f"{score}/{len(quiz_data)}",
        "Start Time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "End Time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Total Time (in seconds)": total_time
    }

    # Ensure the results filename uses the correct quiz_name
    results_filename = f"{quiz_name}_results.txt"

    try:
        with open(results_filename, 'a') as file:
            file.write("\n\n\n")
            for key, value in result_data.items():
                file.write(f"{key}: {value}\n")
            file.write("\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save results: {e}")


def submit_quiz():
    global score_data, quiz_window, file_path, end_time
    if None in user_answers:
        messagebox.showwarning(
            "Warning", "Please answer all questions before submitting.")
        return
    score = sum(1 for i, answer in enumerate(user_answers)
                if answer == quiz_data[i]['answer'])

    end_time = datetime.datetime.now()
    save_results_to_file()

    score_data.append((user_name, score))
    messagebox.showinfo("Quiz Completed", f"{user_name}, your score is {
                        score}/{len(quiz_data)}")
    quiz_window.destroy()
    reset_quiz()


def reset_quiz():
    global file_path, quiz_data, user_answers, user_name
    file_path = None
    quiz_data = []
    user_answers = []
    user_name = None
    start_button.pack_forget()
    update_score_table()


def update_score_table():
    for widget in score_frame.winfo_children():
        widget.destroy()

    if score_data:
        ttk.Label(score_frame, text="User Name").grid(
            row=0, column=0, padx=10, pady=5)
        ttk.Label(score_frame, text="Score",).grid(
            row=0, column=1, padx=10, pady=5)

        for i, (name, score) in enumerate(score_data):
            ttk.Label(score_frame, text=name).grid(
                row=i+1, column=0, padx=10, pady=5)
            ttk.Label(score_frame, text=str(score)).grid(
                row=i+1, column=1, padx=10, pady=5)


root = tk.Tk()
root.title("Quiz App")
root.geometry("600x500")
root.config(bg='White')
root.columnconfigure(0, weight=1)

style = ttk.Style()

style.map('Main.TButton',
          background=[('disabled', 'White'),
                      ('active', 'Purple'),
                      ],
          foreground=[('disabled', 'Black'), ('active', TEXT_COLOR)],
          relief=[('pressed', '!disabled', 'sunken')],
          font='helvetica 24',)
style.configure('TRadiobutton', background=BACKGROUND_COLOR,
                font='helvetica 14', padding=10)
style.configure('Main.TLabel', background=HEADER_COLOR,
                foreground=TEXT_COLOR, font='helvetica 24', padding=5)

open_file_button = ttk.Button(root, text="Open Quiz File", command=open_file,
                              style='Main.TButton')
open_file_button.pack(pady=20, padx=20, fill=tk.X)

start_button = ttk.Button(root, text="Start Quiz", command=start_quiz,
                          style='Main.TButton')
start_button.pack(pady=10, padx=20, fill=tk.X)
start_button.pack_forget()

score_frame = ttk.Frame(root, style='TFrame')
score_frame.pack(pady=20, padx=20, fill=tk.X)
update_score_table()


root.mainloop()
