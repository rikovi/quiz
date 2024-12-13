
import tkinter as tk
from tkinter import messagebox
import socket
import json
from tkinter import simpledialog
from tkinter import ttk


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Game")
        self.root.geometry("500x500")
        self.root.configure(bg="#1c1c1e")

        # Connect to the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(('localhost', 5555))
        except ConnectionError:
            messagebox.showerror("Connection Error", "Failed to connect to the server.")
            self.root.destroy()
            return

        # Get the user's name
        name_prompt = self.client.recv(1024).decode()
        self.name = tk.simpledialog.askstring("Enter Name", name_prompt, parent=self.root)
        if not self.name:
            messagebox.showerror("Error", "Name cannot be empty!")
            self.root.destroy()
            return
        self.client.send(self.name.encode())

        # Display welcome message
        welcome_message = self.client.recv(1024).decode()
        messagebox.showinfo("Welcome", welcome_message)

        # Initialize UI components
        self.create_ui()
        self.load_next_question()

    def create_ui(self):
        """Create the UI layout for the quiz app."""
        # Question label
        self.question_label = tk.Label(
            self.root, text="", font=("Arial", 16, "bold"),
            bg="#1c1c1e", fg="#ffffff", wraplength=450, justify="center"
        )
        self.question_label.pack(pady=20)

        # Frame for options
        self.options_frame = tk.Frame(self.root, bg="#1c1c1e")
        self.options_frame.pack(pady=10)

        self.option_vars = []
        self.radio_buttons = []

        for i in range(4):  # Assuming 4 options
            var = tk.StringVar(value="")
            self.option_vars.append(var)

            rb = tk.Radiobutton(
                self.options_frame, text="", variable=var, value=chr(65 + i),
                font=("Arial", 14), bg="#2c2c2e", fg="#ffffff",
                selectcolor="#007BFF", activeforeground="#007BFF", width=30,
                indicatoron=0, padx=10, pady=5, command=self.change_color
            )
            rb.grid(row=i, column=0, pady=5, padx=5, sticky="w")
            self.radio_buttons.append(rb)

        # Submit button
        self.submit_button = ttk.Button(
            self.root, text="Submit Answer", command=self.submit_answer
        )
        self.submit_button.pack(pady=20)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, length=400, mode="determinate")
        self.progress.pack(pady=10)

    def load_next_question(self):
        """Load the next question from the server."""
        try:
            question_data = self.client.recv(1024).decode()
            self.question_data = json.loads(question_data)
            self.display_question(self.question_data)
        except (json.JSONDecodeError, socket.error):
            self.show_final_score()

    def display_question(self, question):
        """Display the question and its options."""
        self.question_label.config(text=question["question"])
        for i, option in enumerate(question["options"]):
            self.radio_buttons[i].config(
                text=option, value=option[0], state="normal", bg="#2c2c2e", fg="#ffffff"
            )
            self.option_vars[i].set("")
        self.progress["value"] += 10

    def change_color(self):
        """Highlight the selected option."""
        selected_value = self.get_selected_answer()
        for rb in self.radio_buttons:
            if rb["value"] == selected_value:
                rb.config(bg="#007BFF", fg="#ffffff")
            else:
                rb.config(bg="#2c2c2e", fg="#ffffff")

    def get_selected_answer(self):
        """Retrieve the selected answer."""
        for var in self.option_vars:
            if var.get():
                return var.get()
        return None

    def submit_answer(self):
        """Submit the selected answer to the server."""
        answer = self.get_selected_answer()
        if not answer:
            messagebox.showwarning("Warning", "Please select an answer!")
            return

        # Send the answer to the server
        self.client.send(answer.encode())
        self.load_next_question()

    def show_final_score(self):
        """Display the final score and exit the app."""
        try:
            final_score = self.client.recv(1024).decode()
            messagebox.showinfo("Final Score", final_score)
        except socket.error:
            messagebox.showerror("Error", "Failed to retrieve final score.")
        finally:
            self.client.close()
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
