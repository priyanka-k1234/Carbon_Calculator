import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from database import setup_database, save_to_db
from calculations import calculate_footprint, calculate_offset
from pdf_generator import generate_pdf
from charts import plot_charts
import logging
import json
import sqlite3
from config import CO2_PER_KWH, CO2_PER_GAS, CO2_PER_LITER_FUEL
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Set up logging
logging.basicConfig(filename='app.log', level=logging.ERROR)

# Set up database
setup_database()

# GUI settings
ctk.set_appearance_mode("dark")  # Dark theme
ctk.set_default_color_theme("blue")  # Blue color theme
ctk.set_widget_scaling(1.0)  # Disable DPI scaling

# Input validation function
def validate_inputs(electricity, gas, fuel, waste, recycling, travel, efficiency):
    """Validate user inputs to ensure they are valid numbers."""
    try:
        electricity = float(electricity)
        gas = float(gas)
        fuel = float(fuel)
        waste = float(waste)
        recycling = float(recycling)
        travel = float(travel)
        efficiency = float(efficiency)

        if recycling < 0 or recycling > 100:
            raise ValueError("Recycling percentage must be between 0 and 100.")
        if efficiency <= 0:
            raise ValueError("Fuel efficiency must be greater than 0.")

        return True
    except ValueError as error:
        messagebox.showerror("Input Error", str(error))
        return False

# Recommendations function
def provide_recommendations(footprint: float) -> list:
    """Provide personalized recommendations based on the carbon footprint."""
    recommendations = []
    if footprint > 10000:
        recommendations.append("- Consider switching to renewable energy sources for electricity.")
        recommendations.append("- Improve insulation in your home to reduce natural gas usage.")
        recommendations.append("- Use public transportation or carpool to reduce fuel consumption.")
    elif footprint > 5000:
        recommendations.append("- Increase recycling and composting efforts.")
        recommendations.append("- Opt for more fuel-efficient vehicles.")
        recommendations.append("- Reduce unnecessary business travel by using video conferencing.")
    else:
        recommendations.append("- You are doing well! Keep up the good work and look for additional ways to reduce your footprint.")
    return recommendations

# Login Page
class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.geometry("400x400")
        self.root.title("Carbon Footprint Calculator")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle window close event

        # Create a frame for the login UI
        self.frame = ctk.CTkFrame(master=self.root)
        self.frame.pack(pady=20, padx=40, fill='both', expand=True)

        # Title label
        self.label = ctk.CTkLabel(master=self.frame, text='Carbon Footprint Login')
        self.label.pack(pady=12, padx=10)

        # Username entry
        self.user_entry = ctk.CTkEntry(master=self.frame, placeholder_text="Username")
        self.user_entry.pack(pady=12, padx=10)

        # Password entry
        self.user_pass = ctk.CTkEntry(master=self.frame, placeholder_text="Password", show="*")
        self.user_pass.pack(pady=12, padx=10)

        # Show Password Checkbox
        self.show_password_var = tk.BooleanVar(value=False)
        self.show_password_check = ctk.CTkCheckBox(master=self.frame, text="Show Password",
                                                   variable=self.show_password_var,
                                                   command=self.toggle_password_visibility)
        self.show_password_check.pack(pady=5, padx=10)

        # Login button
        self.login_button = ctk.CTkButton(master=self.frame, text='Login', command=self.login)
        self.login_button.pack(pady=12, padx=10)

        # Register button
        self.register_button = ctk.CTkButton(master=self.frame, text='Register', command=self.register)
        self.register_button.pack(pady=12, padx=10)

        # Bind the Enter key to the login function
        self.root.bind('<Return>', lambda event: self.login())

    def toggle_password_visibility(self):
        """Toggle password visibility based on the checkbox state."""
        if self.show_password_var.get():
            self.user_pass.configure(show="")  # Show password
        else:
            self.user_pass.configure(show="*")  # Hide password

    def on_closing(self):
        """Handle the window close event."""
        self.root.destroy()

    def login(self):
        """Handle login button click."""
        username = self.user_entry.get()
        password = self.user_pass.get()

        conn = None
        try:
            conn = sqlite3.connect('carbon_footprint.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE id = ? AND password = ?", (username, password))
            user = c.fetchone()
            if user:
                messagebox.showinfo(title="Login Successful", message="You have logged in Successfully")
                self.root.withdraw()  # Hide the login window instead of destroying it
                main_root = ctk.CTk()  # Use CTk for the main application window
                app = CarbonFootprintApp(main_root, username)
                main_root.mainloop()
            else:
                messagebox.showerror(title="Login Failed", message="Invalid Username and password")
        except sqlite3.Error as error:
            logging.error(f"Database error: {error}")
            messagebox.showerror("Database Error", "An error occurred while accessing the database.")
        finally:
            if conn:
                conn.close()

    def register(self):
        """Register a new user."""
        username = self.user_entry.get()
        password = self.user_pass.get()

        if not username or not password:
            messagebox.showerror("Error", "Username and Password are required.")
            return

        conn = None
        try:
            conn = sqlite3.connect('carbon_footprint.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (id, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "User registered successfully.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        except sqlite3.Error as error:
            logging.error(f"Database error: {error}")
            messagebox.showerror("Database Error", "An error occurred while registering the user.")
        finally:
            if conn:
                conn.close()

# Main Application
class CarbonFootprintApp:
    def __init__(self, root, user_id):
        self.root = root
        self.user_id = user_id
        self.root.title("Carbon Footprint Calculator")
        self.root.geometry("1200x800")  # Set window size
        self._setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle window close event

    def on_closing(self):
        """Handle the window close event."""
        print("Main window is closing...")  # Debugging statement
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()  # Destroy the canvas widget
        self.root.destroy()  # Close the main window

        # Reopen the login window
        print("Reopening login window...")  # Debugging statement
        login_root = ctk.CTk()
        app = LoginPage(login_root)
        login_root.mainloop()

    def _setup_ui(self):
        """Set up the user interface."""
        # Main container frame
        self.main_frame = ctk.CTkFrame(master=self.root, fg_color="#2E3440")  # Dark background
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Top Frame (contains Input Frame and Buttons Frame)
        self.top_frame = ctk.CTkFrame(master=self.main_frame, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=10, pady=10)

        # Input Frame (left side of the top frame)
        self.input_frame = ctk.CTkFrame(master=self.top_frame, corner_radius=15, fg_color="#3B4252")
        self.input_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        # Input fields
        fields = [
            ("Monthly Electricity Bill (€):", 0),
            ("Monthly Natural Gas Bill (€):", 1),
            ("Monthly Fuel Bill (€):", 2),
            ("Waste Generated (kg):", 3),
            ("Recycling Percentage (%):", 4),
            ("Business Travel (km):", 5),
            ("Fuel Efficiency (L/100km):", 6),
        ]

        self.entries = {}
        for label_text, row in fields:
            label = ctk.CTkLabel(master=self.input_frame, text=label_text, text_color="#ECEFF4", font=("Arial", 12))
            label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            entry = ctk.CTkEntry(master=self.input_frame, corner_radius=10, fg_color="#4C566A", border_color="#5E81AC")
            entry.grid(row=row, column=1, padx=10, pady=5)
            self.entries[label_text] = entry

        # Buttons Frame (right side of the top frame)
        self.buttons_frame = ctk.CTkFrame(master=self.top_frame, corner_radius=15, fg_color="#3B4252")
        self.buttons_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        # Buttons
        self.calculate_button = ctk.CTkButton(master=self.buttons_frame, text="Calculate", corner_radius=10,
                                              fg_color="#5E81AC", hover_color="#81A1C1", command=self.calculate)
        self.calculate_button.pack(pady=5, padx=10, fill="x")

        self.print_pdf_button = ctk.CTkButton(master=self.buttons_frame, text="Print PDF", corner_radius=10,
                                              fg_color="#5E81AC", hover_color="#81A1C1", command=self.print_pdf)
        self.print_pdf_button.pack(pady=5, padx=10, fill="x")

        self.offset_button = ctk.CTkButton(master=self.buttons_frame, text="Calculate Offset", corner_radius=10,
                                           fg_color="#5E81AC", hover_color="#81A1C1", command=self.calculate_offset)
        self.offset_button.pack(pady=5, padx=10, fill="x")

        self.clear_button = ctk.CTkButton(master=self.buttons_frame, text="Clear Input", corner_radius=10,
                                          fg_color="#5E81AC", hover_color="#81A1C1", command=self.clear_input)
        self.clear_button.pack(pady=5, padx=10, fill="x")

        self.save_button = ctk.CTkButton(master=self.buttons_frame, text="Save Inputs", corner_radius=10,
                                         fg_color="#5E81AC", hover_color="#81A1C1", command=self.save_data)
        self.save_button.pack(pady=5, padx=10, fill="x")

        self.load_button = ctk.CTkButton(master=self.buttons_frame, text="Load Inputs", corner_radius=10,
                                         fg_color="#5E81AC", hover_color="#81A1C1", command=self.load_data)
        self.load_button.pack(pady=5, padx=10, fill="x")

        # Bottom Frame (contains Result Frame and Graph Frame)
        self.bottom_frame = ctk.CTkFrame(master=self.main_frame, fg_color="transparent")
        self.bottom_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Result Frame (left side of the bottom frame)
        self.result_frame = ctk.CTkFrame(master=self.bottom_frame, corner_radius=15, fg_color="#3B4252")
        self.result_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.result_label = ctk.CTkLabel(master=self.result_frame, text="", justify=tk.LEFT, text_color="#ECEFF4",
                                         font=("Arial", 12))
        self.result_label.pack(pady=10, padx=10)

        # Graph Frame (right side of the bottom frame)
        self.graph_frame = ctk.CTkFrame(master=self.bottom_frame, corner_radius=15, fg_color="#3B4252")
        self.graph_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.figure = plt.Figure(figsize=(8, 6), dpi=100, facecolor="#3B4252")  # Match background color
        self.plot = self.figure.add_subplot(111)
        self.plot.set_facecolor("#3B4252")  # Match background color
        self.plot.tick_params(colors="#ECEFF4")  # Light text for axes
        self.plot.xaxis.label.set_color("#ECEFF4")  # Light text for x-axis label
        self.plot.yaxis.label.set_color("#ECEFF4")  # Light text for y-axis label
        self.plot.title.set_color("#ECEFF4")  # Light text for title

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Configure grid weights for resizing
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        self.bottom_frame.grid_rowconfigure(0, weight=1)

    def calculate(self):
        """Calculate the carbon footprint and display results."""
        try:
            # Get input values
            electricity = self.entries["Monthly Electricity Bill (€):"].get()
            gas = self.entries["Monthly Natural Gas Bill (€):"].get()
            fuel = self.entries["Monthly Fuel Bill (€):"].get()
            waste = self.entries["Waste Generated (kg):"].get()
            recycling = self.entries["Recycling Percentage (%):"].get()
            travel = self.entries["Business Travel (km):"].get()
            efficiency = self.entries["Fuel Efficiency (L/100km):"].get()

            # Validate inputs
            if not validate_inputs(electricity, gas, fuel, waste, recycling, travel, efficiency):
                return

            # Convert inputs to floats
            electricity = float(electricity)
            gas = float(gas)
            fuel = float(fuel)
            waste = float(waste)
            recycling = float(recycling) / 100  # Convert percentage to decimal
            travel = float(travel)
            efficiency = float(efficiency)

            # Calculate footprint
            results = calculate_footprint(electricity, gas, fuel, waste, recycling, travel, efficiency)

            # Save to database
            save_to_db(self.user_id, electricity, gas, fuel, waste, recycling, travel, efficiency,
                       results["total_emissions"])

            # Update layout with all required variables
            self._update_layout(results)

        except ValueError as e:
            logging.error(f"Input validation error: {e}")
            messagebox.showerror("Input Error", str(e))
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            messagebox.showerror("Database Error", "An error occurred while accessing the database.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            messagebox.showerror("Error", "An unexpected error occurred.")

    def _update_layout(self, results):
        """Update the layout after calculation."""
        # Clear the previous graph
        self.plot.clear()

        # Extract results
        total_emissions = results["total_emissions"]
        energy_emissions = results["energy_emissions"]
        waste_emissions = results["waste_emissions"]
        travel_emissions = results["travel_emissions"]

        # Plot the new graph
        labels = ['Energy', 'Waste', 'Travel']
        sizes = [energy_emissions, waste_emissions, travel_emissions]

        # Ensure all sizes are non-negative
        sizes = [max(size, 0) for size in sizes]

        self.plot.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, shadow=True,
                      colors=['#ff9999', '#66b3ff', '#99ff99'])
        self.plot.legend(labels, loc="upper right")  # Add legend
        self.plot.set_title('Carbon Footprint Breakdown', fontsize=16, color='black')

        # Show graph on the right
        self.canvas.draw()

        # Create a fancy result box
        if hasattr(self, 'result_frame'):
            self.result_frame.destroy()  # Remove the old result frame if it exists

        self.result_frame = ctk.CTkFrame(master=self.bottom_frame, corner_radius=15,
                                         fg_color="#2E3440")  # Custom background color
        self.result_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Add a title to the result box
        result_title = ctk.CTkLabel(master=self.result_frame, text="Results", font=("Arial", 16, "bold"),
                                    text_color="#ECEFF4")
        result_title.pack(pady=(10, 5))

        # Add a separator
        separator = ctk.CTkFrame(master=self.result_frame, height=2, fg_color="#4C566A")
        separator.pack(fill="x", padx=10, pady=5)

        # Display the total carbon footprint
        footprint_label = ctk.CTkLabel(
            master=self.result_frame,
            text=f"Total Emissions: {total_emissions:.2f} kgCO2",
            font=("Arial", 14),
            text_color="#ECEFF4"
        )
        footprint_label.pack(pady=(5, 10))

        # Display energy emissions
        energy_label = ctk.CTkLabel(
            master=self.result_frame,
            text=f"Energy Emissions: {energy_emissions:.2f} kgCO2",
            font=("Arial", 12),
            text_color="#D8DEE9"
        )
        energy_label.pack(pady=(0, 5))

        # Display waste emissions
        waste_label = ctk.CTkLabel(
            master=self.result_frame,
            text=f"Waste Emissions: {waste_emissions:.2f} kgCO2",
            font=("Arial", 12),
            text_color="#D8DEE9"
        )
        waste_label.pack(pady=(0, 5))

        # Display travel emissions
        travel_label = ctk.CTkLabel(
            master=self.result_frame,
            text=f"Travel Emissions: {travel_emissions:.2f} kgCO2",
            font=("Arial", 12),
            text_color="#D8DEE9"
        )
        travel_label.pack(pady=(0, 10))

        # Display recommendations
        recommendations = provide_recommendations(total_emissions)
        recommendations_text = "Recommendations:\n" + "\n".join(recommendations)
        recommendations_label = ctk.CTkLabel(
            master=self.result_frame,
            text=recommendations_text,
            font=("Arial", 12),
            text_color="#D8DEE9",
            justify="left"
        )
        recommendations_label.pack(pady=(0, 10), padx=10)

    def calculate_offset(self):
        """Calculate the carbon offset required."""
        try:
            # Get input values
            electricity = self.entries["Monthly Electricity Bill (€):"].get()
            gas = self.entries["Monthly Natural Gas Bill (€):"].get()
            fuel = self.entries["Monthly Fuel Bill (€):"].get()
            waste = self.entries["Waste Generated (kg):"].get()
            recycling = self.entries["Recycling Percentage (%):"].get()
            travel = self.entries["Business Travel (km):"].get()
            efficiency = self.entries["Fuel Efficiency (L/100km):"].get()

            # Validate inputs
            if not validate_inputs(electricity, gas, fuel, waste, recycling, travel, efficiency):
                return

            # Convert inputs to floats
            electricity = float(electricity)
            gas = float(gas)
            fuel = float(fuel)
            waste = float(waste)
            recycling = float(recycling) / 100  # Convert percentage to decimal
            travel = float(travel)
            efficiency = float(efficiency)

            # Calculate footprint
            results = calculate_footprint(electricity, gas, fuel, waste, recycling, travel, efficiency)
            total_footprint = results["total_emissions"]  # Extract the numeric value

            # Calculate offset
            trees_needed = calculate_offset(total_footprint)  # Pass the numeric value
            messagebox.showinfo("Carbon Offset",
                                f"You need to plant {trees_needed:.2f} trees to offset your carbon footprint.")

            # Update layout
            self._update_layout(results)

        except Exception as error:
            logging.error(f"Offset calculation error: {error}")
            messagebox.showerror("Error", "An error occurred while calculating the offset.")

    def save_data(self):
        """Save user inputs to a JSON file."""
        data = {
            "electricity": self.entries["Monthly Electricity Bill (€):"].get(),
            "gas": self.entries["Monthly Natural Gas Bill (€):"].get(),
            "fuel": self.entries["Monthly Fuel Bill (€):"].get(),
            "waste": self.entries["Waste Generated (kg):"].get(),
            "recycling": self.entries["Recycling Percentage (%):"].get(),
            "travel": self.entries["Business Travel (km):"].get(),
            "efficiency": self.entries["Fuel Efficiency (L/100km):"].get(),
        }
        try:
            with open(f"{self.user_id}_data.json", "w") as f:
                json.dump(data, f)
            messagebox.showinfo("Success", "Inputs saved successfully.")
        except Exception as error:
            logging.error(f"Error saving data: {error}")
            messagebox.showerror("Error", "An error occurred while saving data.")

    def load_data(self):
        """Load user inputs from a JSON file."""
        try:
            if os.path.exists(f"{self.user_id}_data.json"):
                with open(f"{self.user_id}_data.json", "r") as f:
                    data = json.load(f)

                # Map JSON keys to input field labels
                key_mapping = {
                    "electricity": "Monthly Electricity Bill (€):",
                    "gas": "Monthly Natural Gas Bill (€):",
                    "fuel": "Monthly Fuel Bill (€):",
                    "waste": "Waste Generated (kg):",
                    "recycling": "Recycling Percentage (%):",
                    "travel": "Business Travel (km):",
                    "efficiency": "Fuel Efficiency (L/100km):",
                }

                # Update input fields
                for json_key, label_text in key_mapping.items():
                    if json_key in data:
                        self.entries[label_text].delete(0, tk.END)
                        self.entries[label_text].insert(0, data[json_key])

                messagebox.showinfo("Success", "Inputs loaded successfully.")
            else:
                messagebox.showinfo("Info", "No saved data found.")
        except Exception as error:
            logging.error(f"Error loading data: {error}")
            messagebox.showerror("Error", "An error occurred while loading data.")

    def print_pdf(self):
        """Generate a PDF report."""
        try:
            # Get input values
            electricity = self.entries["Monthly Electricity Bill (€):"].get()
            gas = self.entries["Monthly Natural Gas Bill (€):"].get()
            fuel = self.entries["Monthly Fuel Bill (€):"].get()
            waste = self.entries["Waste Generated (kg):"].get()
            recycling = self.entries["Recycling Percentage (%):"].get()
            travel = self.entries["Business Travel (km):"].get()
            efficiency = self.entries["Fuel Efficiency (L/100km):"].get()

            # Validate inputs
            if not validate_inputs(electricity, gas, fuel, waste, recycling, travel, efficiency):
                return

            # Convert inputs to floats
            electricity = float(electricity)
            gas = float(gas)
            fuel = float(fuel)
            waste = float(waste)
            recycling = float(recycling) / 100
            travel = float(travel)
            efficiency = float(efficiency)

            # Calculate footprint
            results = calculate_footprint(electricity, gas, fuel, waste, recycling, travel, efficiency)
            total_footprint = results["total_emissions"]
            energy_emissions = results["energy_emissions"]
            waste_emissions = results["waste_emissions"]
            travel_emissions = results["travel_emissions"]

            # Ask user for file path to save PDF
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if not file_path:
                return  # User canceled the save dialog

            # Save the current graph as a PNG image
            image_path = "temp_chart.png"
            self.figure.savefig(image_path, bbox_inches='tight', dpi=100)

            # Generate PDF with the current graph
            recommendations = provide_recommendations(total_footprint)
            generate_pdf(
                self.user_id, electricity, gas, fuel, waste, recycling, travel, efficiency, total_footprint,
                energy_emissions, waste_emissions, travel_emissions, recommendations, file_path, image_path
            )

            # Clean up the temporary image file
            os.remove(image_path)

            messagebox.showinfo("Success", f"PDF report saved to {file_path}")

        except Exception as error:
            logging.error(f"PDF generation error: {error}")
            messagebox.showerror("Error", "An error occurred while generating the PDF.")

        except Exception as error:
            logging.error(f"PDF generation error: {error}")
            messagebox.showerror("Error", "An error occurred while generating the PDF.")

    def clear_input(self):
        """Clear all input fields."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.result_label.configure(text="")
        self.plot.clear()
        self.canvas.draw()

    def destroy(self):
        """Clean up resources before closing the application."""
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()  # Destroy the canvas widget
        self.root.destroy()  # Close the main window

# Run the application
if __name__ == "__main__":
    login_root = ctk.CTk()
    app = LoginPage(login_root)
    login_root.mainloop()