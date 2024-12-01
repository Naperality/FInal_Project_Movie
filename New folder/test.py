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

# Fetch movie recommendations based on category
def get_movie_recommendations(category="popular"):
    API_URL = f"https://api.themoviedb.org/3/movie/{category}" if isinstance(category, str) else f"https://api.themoviedb.org/3/discover/movie"
    API_KEY = "4bfbf52dae4fdb49596b09fcdafd90a2"  # Replace with your actual TMDB API key

    params = {"api_key": API_KEY}
    
    # If category is a genre ID (numeric), use the discover endpoint
    if isinstance(category, int):
        params["with_genres"] = category
    # Otherwise, use the category string for predefined categories
    elif isinstance(category, str):
        if category not in ["popular", "top_rated", "upcoming", "now_playing"]:
            return []  # Handle any invalid category strings

    try:
        response = requests.get(API_URL, params=params)
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

# Category data
categories = {
    "Popular": "popular",
    "Top Rated": "top_rated",
    "Upcoming": "upcoming",
    "Now Playing": "now_playing",
    "Horror": 27,
    "Drama": 18,
    "Comedy": 35,
    "Romance": 10749,
    "Sci-Fi": 878,
    "Action": 28
}

# Fetch and display recommendations
def fetch_recommendations(category):
    movies = get_movie_recommendations(category)
    if movies:
        display_movies(movies)
    else:
        messagebox.showinfo("No Movies", "No movies found for this category!")

# Global variable to keep track of the current movie index
# Global variable to keep track of the current movie index
current_index = 0
batch_size = 5

# Function to display movies in batches
def display_movies(movies):
    global current_index
    # Limit the list to the current batch (5 movies at a time)
    batch_movies = movies[current_index:current_index + batch_size]
    
    for widget in movie_frame.winfo_children():
        widget.destroy()

    for i, movie in enumerate(batch_movies):
        title = movie["title"]
        poster_path = movie.get("poster_path", None)

        # Fetch the poster image
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w200{poster_path}"
            try:
                response = requests.get(poster_url)
                if response.status_code == 200:
                    img_data = response.content
                    img = Image.open(io.BytesIO(img_data))
                    img = img.resize((100, 150), Image.Resampling.LANCZOS)  # Resize to fit the layout
                    poster_image = ImageTk.PhotoImage(img)

                    # Create a frame for each movie
                    movie_frame_inner = tk.Frame(movie_frame, bg="black")
                    movie_frame_inner.grid(row=i // 5, column=i % 5, padx=10, pady=10)

                    # Display poster image
                    poster_label = tk.Label(movie_frame_inner, image=poster_image, bg="black")
                    poster_label.image = poster_image
                    poster_label.pack()

                    # Display movie title
                    tk.Label(movie_frame_inner, text=title, wraplength=100, justify="center", fg="white", bg="black", font=("Arial", 10)).pack()

                    # Add button for movie details
                    tk.Button(
                        movie_frame_inner, text="Details", bg="red", fg="white", font=("Arial", 10),
                        command=lambda m=movie: fetch_movie_details(m)
                    ).pack()
                else:
                    display_placeholder(movie_frame, title, i)
            except:
                display_placeholder(movie_frame, title, i)
        else:
            display_placeholder(movie_frame, title, i)
    
    # Add "Next" and "Prev" buttons in the same row
    button_frame = tk.Frame(movie_frame, bg="black")
    button_frame.grid(row=(len(batch_movies) // 5) + 1, columnspan=5, pady=20)

    # Next button (always visible)
    next_button = tk.Button(
        button_frame, text="Next", bg="red", fg="white", font=("Arial", 14),
        command=lambda: load_next_batch(movies)
    )
    next_button.pack(side=tk.RIGHT, padx=10)
    prev_button = tk.Button(
            button_frame, text="Prev", bg="red", fg="white", font=("Arial", 14),
            command=lambda: load_prev_batch(movies)
        )
    prev_button.pack(side=tk.LEFT, padx=10)

def load_next_batch(movies):
    global current_index
    current_index += batch_size
    display_movies(movies)

def load_prev_batch(movies):
    global current_index
    current_index -= batch_size
    display_movies(movies)
            
def display_placeholder(parent, title, index):
    """
    Display a placeholder when a poster is unavailable.
    """
    # Create a frame for each movie
    movie_frame_inner = tk.Frame(parent, bg="black")
    movie_frame_inner.grid(row=index // 5, column=index % 5, padx=10, pady=10)

    # Display placeholder image
    placeholder_label = tk.Label(movie_frame_inner, text="Poster\nUnavailable", fg="gray", bg="black", font=("Arial", 10))
    placeholder_label.pack()

    # Display movie title
    tk.Label(movie_frame_inner, text=title, wraplength=100, justify="center", fg="white", bg="black", font=("Arial", 10)).pack()

    # Add button for movie details
    tk.Button(
        movie_frame_inner, text="Details", bg="red", fg="white", font=("Arial", 10),
        command=lambda m=movies[index]: fetch_movie_details(m)
    ).pack()
    
def show_categories():
    def fetch_recommendations_wrapper(category_key):
        category = categories[category_key]
        fetch_recommendations(category)

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
        bg_image = Image.open("bg\\background.jpg")
        bg_image = bg_image.resize((int(screen_width * 0.8), int(screen_height * 0.8)), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)

        canvas = tk.Canvas(root, width=int(screen_width * 0.8), height=int(screen_height * 0.8))
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    except FileNotFoundError:
        messagebox.showerror("Error", "Background image not found!")
        return

    # Title
    tk.Label(root, text="Select a Category", fg="red", bg="black", font=("Arial", 20, "bold")).place(relx=0.5, y=30, anchor="center")

    # Frame for category buttons
    category_frame = tk.Frame(root, bg="black")
    category_frame.place(relx=0.5, rely=0.2, anchor="center")

    # List of categories to keep in the same row
    fixed_row_categories = ["Horror", "Drama", "Romance", "Comedy","Action","Sci-Fi"]
    button_width = 12  # Width of each button
    max_buttons_per_row = 5  # Adjust for remaining categories
    current_row = 0

    # Place fixed row categories first
    for index, category_key in enumerate(fixed_row_categories):
        if category_key in categories:
            button = tk.Button(
                category_frame,
                text=category_key,
                command=lambda c=category_key: fetch_recommendations_wrapper(c),
                bg="red",
                fg="white",
                font=("Arial", 14),
                width=button_width
            )
            button.grid(row=current_row , column=index, padx=20, pady=10)

    # Adjust column weights for the fixed row
    for col in range(len(fixed_row_categories)):
        category_frame.grid_columnconfigure(col, weight=1)

    # Add the remaining categories dynamically
    remaining_categories = [key for key in categories.keys() if key not in fixed_row_categories]
    for index, category_key in enumerate(remaining_categories):
        row = current_row + 1 + index // max_buttons_per_row  # Start on the row below the fixed row
        col = index % max_buttons_per_row
        button = tk.Button(
            category_frame,
            text=category_key,
            command=lambda c=category_key: fetch_recommendations_wrapper(c),
            bg="red",
            fg="white",
            font=("Arial", 14),
            width=button_width
        )
        button.grid(row=row, column=col+1, padx=20, pady=10)

    # Adjust column weights for dynamic rows
    for col in range(max_buttons_per_row):
        category_frame.grid_columnconfigure(col, weight=1)

    # Scrollable frame for movies
    scrollable_frame = tk.Frame(root, bg="black")
    scrollable_frame.place(relx=0.5, rely=0.7, anchor="center", width=int(screen_width * 0.75), height=int(screen_height * 0.4))

    global movie_frame
    movie_frame = tk.Frame(scrollable_frame, bg="black")
    movie_frame.pack()

    # Keep a reference to the background image
    canvas.image = bg_photo

    root.mainloop()

# Show login form
def show_login():
    def login():
        email = email_entry.get()
        password = password_entry.get()
        if validate_login(email, password):
            messagebox.showinfo("Login", "Login successful!")
            root.destroy() 
            show_categories()
        else:
            messagebox.showerror("Error", "Invalid email or password!")
    def register():
        root.destroy() 
        show_register()

    # Create the Tkinter window
    root = tk.Tk()
    root.title("Filmfluence - Login")

    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Set window size
    root.geometry(f"{int(screen_width * 0.6)}x{int(screen_height * 0.5)}")  # 60% width, 50% height
    root.configure(bg="black")

    # Add background image
    try:
        bg_image = Image.open("bg\\front.jpg")
        bg_image = bg_image.resize((int(screen_width * 0.6), int(screen_height * 0.5)), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)

        canvas = tk.Canvas(root, width=int(screen_width * 0.6), height=int(screen_height * 0.5))
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    except FileNotFoundError:
        messagebox.showerror("Error", "Background image not found!")
        return

    # Title
    tk.Label(root, text="Login to Filmfluence", fg="red", bg="black", font=("Arial", 20, "bold")).place(relx=0.5, y=40, anchor="center")

    # Email entry
    tk.Label(root, text="Email:", fg="white", bg="black", font=("Arial", 14)).place(relx=0.3, rely=0.3, anchor="center")
    email_entry = tk.Entry(root, font=("Arial", 14))
    email_entry.place(relx=0.7, rely=0.3, anchor="center")

    # Password entry
    tk.Label(root, text="Password:", fg="white", bg="black", font=("Arial", 14)).place(relx=0.3, rely=0.4, anchor="center")
    password_entry = tk.Entry(root, show="*", font=("Arial", 14))
    password_entry.place(relx=0.7, rely=0.4, anchor="center")

    # Login button
    tk.Button(root, text="Login", command=login, bg="red", fg="white", font=("Arial", 14)).place(relx=0.5, rely=0.5, anchor="center")

    # Register button
    tk.Button(root, text="Register", command=register, bg="red", fg="white", font=("Arial", 14)).place(relx=0.5, rely=0.6, anchor="center")

    # Keep reference to background image to prevent garbage collection
    canvas.image = bg_photo

    root.mainloop()

# Show register form
def show_register():
    def register():
        email = email_entry.get()
        password = password_entry.get()
        success, message = register_user(email, password)
        messagebox.showinfo("Info", message)
        if success:
            root.destroy()
            show_login()

    # Create the Tkinter window
    root = tk.Tk()
    root.title("Filmfluence - Register")

    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Set window size
    root.geometry(f"{int(screen_width * 0.6)}x{int(screen_height * 0.5)}")  # 60% width, 50% height
    root.configure(bg="black")

    # Add background image
    try:
        bg_image = Image.open("bg\\background.jpg")
        bg_image = bg_image.resize((int(screen_width * 0.6), int(screen_height * 0.5)), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)

        canvas = tk.Canvas(root, width=int(screen_width * 0.6), height=int(screen_height * 0.5))
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    except FileNotFoundError:
        messagebox.showerror("Error", "Background image not found!")
        return

    # Title
    tk.Label(root, text="Register for Filmfluence", fg="red", bg="black", font=("Arial", 20, "bold")).place(relx=0.5, y=40, anchor="center")

    # Email entry
    tk.Label(root, text="Email:", fg="white", bg="black", font=("Arial", 14)).place(relx=0.3, rely=0.3, anchor="center")
    email_entry = tk.Entry(root, font=("Arial", 14))
    email_entry.place(relx=0.7, rely=0.3, anchor="center")

    # Password entry
    tk.Label(root, text="Password:", fg="white", bg="black", font=("Arial", 14)).place(relx=0.3, rely=0.4, anchor="center")
    password_entry = tk.Entry(root, show="*", font=("Arial", 14))
    password_entry.place(relx=0.7, rely=0.4, anchor="center")

    # Register button
    tk.Button(root, text="Register", command=register, bg="red", fg="white", font=("Arial", 14)).place(relx=0.5, rely=0.5, anchor="center")

    # Keep reference to background image
    canvas.image = bg_photo

    root.mainloop()

if __name__ == "__main__":
    initialize_excel()
    show_login()