import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import requests
from PIL import Image, ImageTk
import io

# Path to Excel file to store user data
USER_DATA_FILE = "Book1.xlsx"

# Initialize Excel file if it doesn't exist
def initialize_excel():
    try:
        df = pd.read_excel(USER_DATA_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Email", "Password"])
        df.to_excel(USER_DATA_FILE, index=False)

# Validate login credentials
def validate_login(email, password):
    try:
        df = pd.read_excel(USER_DATA_FILE)
        user = df[(df["Email"] == email) & (df["Password"] == password)]
        return not user.empty
    except FileNotFoundError:
        return False

# Register a new user
def register_user(email, password):
    try:
        df = pd.read_excel(USER_DATA_FILE)
        if email in df["Email"].values:
            return False, "Email already exists!"
        new_user = pd.DataFrame([[email, password]], columns=["Email", "Password"])
        df = pd.concat([df, new_user], ignore_index=True)
        df.to_excel(USER_DATA_FILE, index=False)
        return True, "Registration successful!"
    except Exception as e:
        return False, f"Error: {e}"

# Fetch movie recommendations using API
def get_movie_recommendations(category="popular"):
    API_URL = f"https://api.themoviedb.org/3/movie/{category}"
    API_KEY = "4bfbf52dae4fdb49596b09fcdafd90a2"  # Replace with your actual TMDB API key
    try:
        response = requests.get(API_URL, params={"api_key": API_KEY})
        if response.status_code == 200:
            movies = response.json().get("results", [])
            return movies
        else:
            return []
    except Exception as e:
        return []

# Fetch and display movie details
def fetch_movie_details(movie):
    # API URL for movie details
    API_URL = f"https://api.themoviedb.org/3/movie/{movie['id']}"
    API_KEY = "4bfbf52dae4fdb49596b09fcdafd90a2"  # Replace with your TMDB API key
    try:
        response = requests.get(API_URL, params={"api_key": API_KEY})
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get("poster_path")
            summary = data.get("overview", "No summary available.")
            rating = data.get("vote_average", "N/A")
            
            # Full poster URL
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            show_movie_details(movie["title"], poster_url, summary, rating)
        else:
            messagebox.showerror("Error", "Could not fetch movie details!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def show_movie_details(title, poster_url, summary, rating):
    details_window = tk.Toplevel()
    details_window.title(title)
    details_window.geometry("600x800")
    details_window.configure(bg="black")

    # Load and display the background image
    try:
        bg_image = Image.open("bg\\background.jpg")
        bg_image = bg_image.resize((600, 800), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)

        canvas = tk.Canvas(details_window, width=600, height=800)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    except FileNotFoundError:
        messagebox.showerror("Error", "Background image not found!")
        return

    # Title
    tk.Label(details_window, text=title, fg="white", bg="black", font=("Arial", 16, "bold")).place(relx=0.5, y=20, anchor="center")

    # Poster
    if poster_url:
        try:
            response = requests.get(poster_url)
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((200, 300), Image.Resampling.LANCZOS)
            poster_image = ImageTk.PhotoImage(img)
            poster_label = tk.Label(details_window, image=poster_image, bg="black")
            poster_label.image = poster_image
            poster_label.place(relx=0.5, rely=0.3, anchor="center")
        except:
            tk.Label(details_window, text="Poster not available", fg="white", bg="black", font=("Arial", 12)).place(relx=0.5, rely=0.3, anchor="center")

    # Summary
    tk.Label(details_window, text="Summary:", fg="red", bg="black", font=("Arial", 14)).place(relx=0.1, rely=0.5, anchor="w")
    tk.Label(details_window, text=summary, wraplength=500, justify="left", fg="white", bg="black", font=("Arial", 12)).place(relx=0.5, rely=0.6, anchor="center")

    # Rating
    tk.Label(details_window, text=f"Rating: {rating}/10", fg="yellow", bg="black", font=("Arial", 14)).place(relx=0.5, rely=0.8, anchor="center")

    tk.Button(details_window, text="Close", command=details_window.destroy, bg="red", fg="white").place(relx=0.5, rely=0.9, anchor="center")

    # Keep a reference to the background image
    canvas.image = bg_photo
# Show registration form
def show_register():
    def register():
        email = email_entry.get()
        password = password_entry.get()
        success, message = register_user(email, password)
        if success:
            messagebox.showinfo("Success", message)
            root.destroy()
            show_login()  # Go back to login after successful registration
        else:
            messagebox.showerror("Error", message)

    root = tk.Tk()
    root.title("Filmfluence - Register")

    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Set the window size as a percentage of screen size
    root.geometry(f"{int(screen_width * 0.6)}x{int(screen_height * 0.5)}")  # 60% width, 50% height
    root.configure(bg="black")

    tk.Label(root, text="Filmfluence", fg="red", bg="black", font=("Arial", 20, "bold")).pack(pady=20)
    tk.Label(root, text="Email", fg="white", bg="black").pack()
    email_entry = tk.Entry(root)
    email_entry.pack()

    tk.Label(root, text="Password", fg="white", bg="black").pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    tk.Button(root, text="Register", command=register, bg="red", fg="white").pack(pady=10)
    tk.Button(root, text="Back to Login", command=lambda: [root.destroy(), show_login()], bg="gray", fg="white").pack(pady=10)

    root.mainloop()

def show_login():
    def login():
        email = email_entry.get()
        password = password_entry.get()
        if validate_login(email, password):
            messagebox.showinfo("Success", "Login successful!")
            root.destroy()
            show_categories()
        else:
            messagebox.showerror("Error", "Invalid email or password!")

    def open_register():
        root.destroy()
        show_register()

    # Create the main Tkinter window
    root = tk.Tk()
    root.title("Filmfluence - Login")

    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Set the window size as a percentage of screen size
    root.geometry(f"{int(screen_width * 0.6)}x{int(screen_height * 0.5)}")  # 60% width, 50% height
    root.configure(bg="black")

    # Load and display the background image
    try:
        # Replace "background.jpg" with the path to your background image
        bg_image = Image.open("bg\\front.jpg")
        bg_image = bg_image.resize((int(screen_width * 0.6), int(screen_height * 0.5)), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)

        canvas = tk.Canvas(root, width=int(screen_width * 0.6), height=int(screen_height * 0.5))
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    except FileNotFoundError:
        messagebox.showerror("Error", "Background image not found!")
        return

    # Add the title label
    title_label = tk.Label(root, text="Filmfluence", fg="red", bg="black", font=("Arial", 20, "bold"))
    title_label.place(relx=0.5, y=30, anchor="center")

    # Email label and entry
    email_label = tk.Label(root, text="Email", fg="white", bg="black")
    email_label.place(relx=0.3, rely=0.3, anchor="center")
    email_entry = tk.Entry(root)
    email_entry.place(relx=0.5, rely=0.3, anchor="center")

    # Password label and entry
    password_label = tk.Label(root, text="Password", fg="white", bg="black")
    password_label.place(relx=0.3, rely=0.4, anchor="center")
    password_entry = tk.Entry(root, show="*")
    password_entry.place(relx=0.5, rely=0.4, anchor="center")

    # Login button
    login_button = tk.Button(root, text="Log In", command=login, bg="red", fg="white")
    login_button.place(relx=0.5, rely=0.5, anchor="center")

    # Register button
    register_button = tk.Button(root, text="Register", command=open_register, bg="gray", fg="white")
    register_button.place(relx=0.5, rely=0.6, anchor="center")

    # Keep a reference to the background image to prevent garbage collection
    canvas.image = bg_photo

    root.mainloop()

def show_categories():
    def fetch_recommendations(category):
        movies = get_movie_recommendations(category)
        if movies:
            for widget in movie_frame.winfo_children():
                widget.destroy()
            for index, movie in enumerate(movies):
                movie_btn = tk.Button(movie_frame, text=movie["title"], command=lambda m=movie: fetch_movie_details(m), wraplength=200, justify="center", bg="black", fg="white")
                movie_btn.grid(row=index // 5, column=index % 5, padx=10, pady=10)
        else:
            messagebox.showinfo("Info", "No movies found for this category!")

    root = tk.Tk()
    root.title("Filmfluence - Categories")

    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Set the window size
    root.geometry(f"{int(screen_width * 0.8)}x{int(screen_height * 0.8)}")
    root.configure(bg="black")

    # Load and display the background image
    try:
        bg_image = Image.open("bg//background.jpg")
        bg_image = bg_image.resize((int(screen_width * 0.8), int(screen_height * 0.8)), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)

        canvas = tk.Canvas(root, width=int(screen_width * 0.8), height=int(screen_height * 0.8))
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    except FileNotFoundError:
        messagebox.showerror("Error", "Background image not found!")
        return

    tk.Label(root, text="Select a Category", fg="red", bg="black", font=("Arial", 20, "bold")).place(relx=0.5, y=30, anchor="center")

    categories = ["popular", "top_rated", "upcoming", "now_playing"]
    for index, category in enumerate(categories):
        tk.Button(root, text=category.title(), command=lambda c=category: fetch_recommendations(c), bg="red", fg="white").place(relx=0.5, rely=0.2 + (index * 0.1), anchor="center")

    # Scrollable frame for movies
    scrollable_frame = tk.Frame(root, bg="black")
    scrollable_frame.place(relx=0.5, rely=0.7, anchor="center", width=int(screen_width * 0.75), height=int(screen_height * 0.4))

    movie_frame = tk.Frame(scrollable_frame, bg="black")
    movie_frame.pack()

    # Keep a reference to the background image
    canvas.image = bg_photo
    root.mainloop()

# Initialize and start the program
if __name__ == "__main__":
    initialize_excel()
    show_login()