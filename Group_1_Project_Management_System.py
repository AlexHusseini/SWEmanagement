# === IMPORTS AND DATABASE CONFIGURATION ===
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import psycopg2
from datetime import datetime
import csv
import os
import hashlib
import re

# Optional ReportLab import - for PDF export
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Import custom styles if available
try:
    import styles
    import style_integration
    STYLES_AVAILABLE = True
    print("Custom styles loaded successfully!")
except ImportError:
    STYLES_AVAILABLE = False
    print("Custom styles not found. Using default styling.")

# PostgreSQL connection configuration
DB_NAME = "project_management"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"

# === USER AUTHENTICATION ===

class LoginWindow:
    def __init__(self, root, on_login_success, skip_allowed=True):
        self.root = root
        self.on_login_success = on_login_success
        self.skip_allowed = skip_allowed
        
        # Set up the login window
        self.root.title("Project Management System - Login")
        self.root.geometry("450x550")  # Reduced height from 600 to 550
        self.root.resizable(False, False)
        
        # Configure style
        style = ttk.Style()
        style.configure("TButton", padding=6, font=('Arial', 10))
        style.configure("TLabel", font=('Arial', 10))
        style.configure("Header.TLabel", font=('Arial', 12, 'bold'))
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # App title
        title_label = ttk.Label(main_frame, text="Project Management System", font=("Arial", 16, "bold"))
        title_label.pack(pady=(5, 0))  # Reduced top padding
        
        subtitle_label = ttk.Label(main_frame, text="User Authentication", font=("Arial", 12))
        subtitle_label.pack(pady=(0, 10))  # Reduced bottom padding
        
        # Create tab control for login/register tabs
        tab_control = ttk.Notebook(main_frame)
        tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Login tab
        login_tab = ttk.Frame(tab_control, padding=10)
        tab_control.add(login_tab, text="Login")
        
        # Register tab
        register_tab = ttk.Frame(tab_control, padding=10)
        tab_control.add(register_tab, text="Register")
        
        # Setup login tab
        self.setup_login_tab(login_tab)
        
        # Setup register tab
        self.setup_register_tab(register_tab)
        
        # Status label at the bottom of main frame
        self.status_var = tk.StringVar()
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="red")
        status_label.pack(pady=5)  # Reduced padding
        
        # Ensure users table exists
        self.create_users_table()
    
    def setup_login_tab(self, parent):
        """Set up the login tab"""
        # Create form frame
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Username
        ttk.Label(form_frame, text="Username:", style="Header.TLabel").pack(anchor="w", pady=(5, 3))
        self.username_entry = ttk.Entry(form_frame, width=40)
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Password
        ttk.Label(form_frame, text="Password:", style="Header.TLabel").pack(anchor="w", pady=(5, 3))
        self.password_entry = ttk.Entry(form_frame, width=40, show="*")
        self.password_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Button frame
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # Login button
        login_button = ttk.Button(button_frame, text="Login", command=self.login, width=10)
        login_button.pack(side=tk.RIGHT, padx=1)
        
        # Skip login button
        if self.skip_allowed:
            skip_button = ttk.Button(button_frame, text="Skip Login", command=self.skip_login, width=12)
            skip_button.pack(side=tk.RIGHT, padx=5)
    
    def setup_register_tab(self, parent):
        """Set up the register tab"""
        # Use a canvas with scrollbar to ensure everything fits
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Instructions
        instruction_label = ttk.Label(scroll_frame, text="Create a new account", style="Header.TLabel")
        instruction_label.pack(anchor="w", pady=(5, 10))
        
        # Create form with compact spacing
        form_frame = ttk.Frame(scroll_frame)
        form_frame.pack(fill=tk.BOTH)
        
        # Username
        ttk.Label(form_frame, text="Username:", style="Header.TLabel").pack(anchor="w", pady=(0, 3))
        self.reg_username_entry = ttk.Entry(form_frame, width=40)
        self.reg_username_entry.pack(fill=tk.X, pady=(0, 8))
        
        # Password
        ttk.Label(form_frame, text="Password:", style="Header.TLabel").pack(anchor="w", pady=(0, 3))
        self.reg_password_entry = ttk.Entry(form_frame, width=40, show="*")
        self.reg_password_entry.pack(fill=tk.X, pady=(0, 3))
        
        # Password hint
        password_hint = ttk.Label(form_frame, text="Password must be at least 6 characters", foreground="gray", font=("Arial", 9, "italic"))
        password_hint.pack(anchor="w", pady=(0, 8))
        
        # Confirm Password
        ttk.Label(form_frame, text="Confirm Password:", style="Header.TLabel").pack(anchor="w", pady=(0, 3))
        self.reg_confirm_entry = ttk.Entry(form_frame, width=40, show="*")
        self.reg_confirm_entry.pack(fill=tk.X, pady=(0, 8))
        
        # Role
        ttk.Label(form_frame, text="Role:", style="Header.TLabel").pack(anchor="w", pady=(0, 3))
        self.reg_role_combo = ttk.Combobox(form_frame, width=38, values=["Project Manager", "Developer", "Tester"], state="readonly")
        self.reg_role_combo.pack(fill=tk.X, pady=(0, 15))
        self.reg_role_combo.current(0)
        
        # Register button
        register_button = ttk.Button(form_frame, text="Create Account", command=self.register, width=20)
        register_button.pack(pady=5)
    
    def create_users_table(self):
        """Create users table if it doesn't exist"""
        try:
            conn = connect_db()
            cur = conn.cursor()
            
            # Check if users table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                )
            """)
            table_exists = cur.fetchone()[0]
            
            if not table_exists:
                # Create users table
                cur.execute("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password_hash VARCHAR(128) NOT NULL,
                        role VARCHAR(20) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create default admin user
                hashed_password = hashlib.sha256("admin".encode()).hexdigest()
                cur.execute("""
                    INSERT INTO users (username, password_hash, role)
                    VALUES ('admin', %s, 'Project Manager')
                """, (hashed_password,))
                
                conn.commit()
                self.status_var.set("Default user created: admin/admin")
            
            cur.close()
            conn.close()
        except Exception as e:
            self.status_var.set(f"Database error: {e}")
    
    def validate_password(self, password):
        """Validate password strength"""
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        return True, ""
    
    def register(self):
        """Register a new user"""
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get()
        confirm = self.reg_confirm_entry.get()
        role = self.reg_role_combo.get()
        
        # Validate inputs
        if not username or not password or not confirm:
            self.status_var.set("All fields are required")
            return
        
        if password != confirm:
            self.status_var.set("Passwords do not match")
            return
        
        valid, message = self.validate_password(password)
        if not valid:
            self.status_var.set(message)
            return
        
        try:
            # Hash password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Insert new user
            conn = connect_db()
            cur = conn.cursor()
            
            # Check if username exists
            cur.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
            if cur.fetchone()[0] > 0:
                self.status_var.set("Username already exists")
                cur.close()
                conn.close()
                return
            
            # Insert user
            cur.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (%s, %s, %s)
            """, (username, hashed_password, role))
            
            conn.commit()
            cur.close()
            conn.close()
            
            # Clear registration fields
            self.reg_username_entry.delete(0, tk.END)
            self.reg_password_entry.delete(0, tk.END)
            self.reg_confirm_entry.delete(0, tk.END)
            
            self.status_var.set("Registration successful! You can now login.")
            
        except Exception as e:
            self.status_var.set(f"Registration failed: {e}")
    
    def login(self):
        """Authenticate user login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.status_var.set("Username and password are required")
            return
        
        try:
            # Hash password for comparison
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Check credentials
            conn = connect_db()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT id, role FROM users 
                WHERE username = %s AND password_hash = %s
            """, (username, hashed_password))
            
            result = cur.fetchone()
            cur.close()
            conn.close()
            
            if result:
                user_id, role = result
                # Login successful
                self.root.withdraw()  # Hide login window
                self.on_login_success(user_id, username, role)
            else:
                self.status_var.set("Invalid username or password")
                
        except Exception as e:
            self.status_var.set(f"Login failed: {e}")
    
    def skip_login(self):
        """Skip login for backward compatibility"""
        self.root.withdraw()  # Hide login window
        self.on_login_success(None, "Guest", "Guest")


# Function to establish connection to PostgreSQL database
def connect_db():
    return psycopg2.connect(
        dbname="project_management",
        user="postgres",
        password="postgres",
        host="localhost"
    )


# === PROJECTS TAB ===

# Save a new project to the database
def save_project(data):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO projects (project_name, owner, project_description, project_scope, target_users, technology_stack, platform)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, data)
    conn.commit()
    cur.close()
    conn.close()

# Delete a project by name
def delete_project(project_name):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM projects WHERE project_name = %s", (project_name,))
    conn.commit()
    cur.close()
    conn.close()

# Update project details
def update_project(data):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE projects
        SET project_name = %s,
            owner = %s,
            project_description = %s,
            project_scope = %s,
            target_users = %s,
            technology_stack = %s,
            platform = %s
        WHERE project_name = %s
    """, data)
    conn.commit()
    cur.close()
    conn.close()


# === TEAM TAB ===


class TeamMembersTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(self.parent)
        self.setup_ui()

    def setup_ui(self):
        # Create UI elements to select project and display team members
   
        title_label = ttk.Label(self.frame, text="Team Members", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 15), sticky='nw')

        # Dropdown to select project
        ttk.Label(self.frame, text="Select Project:").grid(row=1, column=0, padx=20, pady=10, sticky='w')
        self.project_combo = ttk.Combobox(self.frame, width=40, state="readonly")
        self.project_combo.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        self.project_combo.bind("<<ComboboxSelected>>", self.load_team_members)

        # Treeview to display team member details
        self.tree = ttk.Treeview(self.frame, columns=("Name", "Role", "Responsibilities", "Skill"), show='headings')
        for col in ("Name", "Role", "Responsibilities", "Skill"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=245)
        self.tree.grid(row=2, column=0, columnspan=3, padx=20, pady=5, sticky='nsew')

        # Allow treeview expansion
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)

        # Buttons to add, edit, and delete team members
        btn_frame = ttk.Frame(self.frame)
        btn_frame.grid(row=3, column=0, columnspan=3, sticky='e', padx=10, pady=10)

        ttk.Button(btn_frame, text="Add Member", command=self.add_member).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edit Member", command=self.edit_member).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Member", command=self.delete_member).pack(side="left", padx=5)

        # Load projects into the dropdown
        self.load_projects()

    # Load all project names from the database into the project dropdown
    def load_projects(self):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT id, project_name FROM projects")
        self.project_map = {name: pid for pid, name in cur.fetchall()}
        self.project_combo['values'] = list(self.project_map.keys())
        cur.close()
        conn.close()

    # Load team members for the selected project
    def load_team_members(self, event=None):
        self.tree.delete(*self.tree.get_children())
        project_id = self.project_map.get(self.project_combo.get())

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, role, responsibilities, skill_level
            FROM team_members
            WHERE project_id = %s
        """, (project_id,))
        self.member_id_map = {}
        for row in cur.fetchall():
            member_id, name, role, responsibilities, skill = row
            self.tree.insert('', 'end', values=(name, role, responsibilities, skill), tags=(str(member_id),))
        cur.close()
        conn.close()

    def get_selected_member(self):
        # Get details of the currently selected member in the tree
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected)['values']
            member_id = self.tree.item(selected)['tags'][0]
            return selected, member_id, values
        return None, None, None

    def add_member(self):
        # Open the form to add a new member
        self.open_member_form("Add Member")

    def edit_member(self):
        # Open the form to edit the selected member
        selected, member_id, values = self.get_selected_member()
        if not selected:
            messagebox.showwarning("Select", "Please select a member to edit.")
            return
        self.open_member_form("Edit Member", member_id, values)

    def delete_member(self):
        # Delete the selected team member
        selected, member_id, _ = self.get_selected_member()
        if not selected:
            messagebox.showwarning("Select", "Please select a member to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete this member?"):
            return
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM team_members WHERE id = %s", (member_id,))
        conn.commit()
        cur.close()
        conn.close()
        self.load_team_members()

    def open_member_form(self, title, member_id=None, values=None):
        # Opens the popup form to add/edit a team member
        win = tk.Toplevel(self.frame)
        win.title(title)

        # Name
        ttk.Label(win, text="Name").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        name_entry = ttk.Entry(win, width=30)
        name_entry.grid(row=0, column=1, padx=(10, 20), pady=5, sticky="w")

        # Role
        ttk.Label(win, text="Role").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        role_entry = ttk.Entry(win, width=30)
        role_entry.grid(row=1, column=1, padx=(10, 20), pady=5, sticky="w")

        # Responsibilities
        ttk.Label(win, text="Responsibilities").grid(row=2, column=0, padx=10, pady=5, sticky="ne")
        resp_entry = tk.Text(win, width=23, height=4)
        resp_entry.grid(row=2, column=1, padx=(10, 20), pady=5, sticky="w")


        # Skill Level
        ttk.Label(win, text="Skill Level").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        skill_entry = ttk.Entry(win, width=30)
        skill_entry.grid(row=3, column=1, padx=(10, 20), pady=(5,10), sticky="w")

        # If editing, prefill existing values
        if values:
            name_entry.insert(0, values[0])
            role_entry.insert(0, values[1])
            resp_entry.insert(0, values[2])
            skill_entry.insert(0, values[3])

        def save():
            # Save the new or edited member to the database
            new_values = [
                name_entry.get(),
                role_entry.get(),
                resp_entry.get("1.0", tk.END).strip(),
                skill_entry.get()
            ]
            if not all(new_values):
                messagebox.showwarning("Incomplete", "Please fill in all fields.")
                return

            project_id = self.project_map[self.project_combo.get()]
            conn = connect_db()
            cur = conn.cursor()
            if member_id:
                # Update existing member
                cur.execute("""
                    UPDATE team_members
                    SET name = %s, role = %s, responsibilities = %s, skill_level = %s
                    WHERE id = %s
                """, (*new_values, member_id))
            else:
                # Insert new member
                cur.execute("""
                    INSERT INTO team_members (project_id, name, role, responsibilities, skill_level)
                    VALUES (%s, %s, %s, %s, %s)
                """, (project_id, *new_values))
            conn.commit()
            cur.close()
            conn.close()
            self.load_team_members()
            win.destroy()

        # Save button for the form
        ttk.Button(win, text="Save", command=save).grid(row=4, column=0, columnspan=2, pady=(1,10), sticky="")


# === RISKS TAB ===


class RisksTab:
    def __init__(self, parent):
        # Initialize the tab with parent notebook
        self.parent = parent
        self.frame = ttk.Frame(self.parent)
        self.risk_details = {}  # Store risk details for matrix visualization
        
        # Update database schema if needed
        self.update_risk_table_if_needed()
        
        # Set up the UI
        self.setup_ui()
        
        # Initialize project data
        self.load_projects()
        
        # Force an initial synchronization after a short delay to ensure UI is ready
        self.frame.after(100, self.sync_project_dropdowns)

    def setup_ui(self):
        # Create a notebook for Risk tabs
        self.risk_notebook = ttk.Notebook(self.frame)
        self.risk_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.risks_list_tab = ttk.Frame(self.risk_notebook)
        self.risk_matrix_tab = ttk.Frame(self.risk_notebook)
        
        # Add tabs to notebook
        self.risk_notebook.add(self.risks_list_tab, text="Risk List")
        self.risk_notebook.add(self.risk_matrix_tab, text="Risk Matrix")
        
        # Set up Risk List tab UI
        self.setup_risk_list_ui()
        
        # Set up Risk Matrix tab UI
        self.setup_risk_matrix_ui()
        
    def setup_risk_list_ui(self):
        # Title 
        title_label = ttk.Label(self.risks_list_tab, text="Risk Management", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(20, 10), sticky='w')

        # Dropdown to select the project
        ttk.Label(self.risks_list_tab, text="Select Project:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.project_combo = ttk.Combobox(self.risks_list_tab, width=40, state="readonly")
        self.project_combo.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        self.project_combo.bind("<<ComboboxSelected>>", self.load_risks)

        # Add a prominent button to show risk matrix right after project selection
        matrix_btn = ttk.Button(self.risks_list_tab, text="Show Risk Matrix", 
                               command=self.show_risk_matrix,
                               style="Accent.TButton")
        matrix_btn.grid(row=1, column=2, padx=10, pady=10, sticky='w')
        
        # Treeview to show risk entries with enhanced columns
        self.tree = ttk.Treeview(self.risks_list_tab, columns=("Risk", "Description", "Status"), show='headings')
        self.tree.heading("Risk", text="Risk")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Status", text="Status")
        self.tree.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

        # Configure row/column resizing behavior
        self.risks_list_tab.grid_rowconfigure(2, weight=1)
        self.risks_list_tab.grid_columnconfigure(2, weight=1)

        # Buttons to Add, Edit, Delete Risk
        btn_frame = ttk.Frame(self.risks_list_tab)
        btn_frame.grid(row=3, column=0, columnspan=3, sticky='e', padx=10, pady=10)
        ttk.Button(btn_frame, text="Add Risk", command=self.add_risk).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edit Risk", command=self.edit_risk).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Risk", command=self.delete_risk).pack(side="left", padx=5)
        
        # Add another visible button at the bottom for showing the matrix
        ttk.Button(btn_frame, text="View Risk Matrix", command=self.show_risk_matrix,
                  style="Accent.TButton").pack(side="left", padx=15)

        # Load project names into dropdown
        self.load_projects()

    def setup_risk_matrix_ui(self):
        # Create a custom style for accent buttons
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))
        
        # This frame will contain the matrix visualization
        self.matrix_frame = ttk.Frame(self.risk_matrix_tab)
        self.matrix_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        ttk.Label(self.matrix_frame, 
                  text="Risk Matrix Visualization", 
                  font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Project selector for risk matrix tab
        select_frame = ttk.Frame(self.matrix_frame)
        select_frame.pack(fill="x", pady=10)
        
        ttk.Label(select_frame, text="Select Project:").pack(side="left", padx=5)
        self.matrix_project_combo = ttk.Combobox(select_frame, width=40, state="readonly")
        self.matrix_project_combo.pack(side="left", padx=5)
        
        # Bind the matrix dropdown to also load risks when changed
        self.matrix_project_combo.bind("<<ComboboxSelected>>", self.load_risks)
        
        # Populate the matrix dropdown immediately
        self.sync_project_dropdowns()
        
        # Add binding to notebook to update dropdowns when tab changes
        self.risk_notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Button to generate the matrix
        ttk.Button(select_frame, text="Generate Risk Matrix", 
                  command=self.show_risk_matrix,
                  style="Accent.TButton").pack(side="left", padx=5)
        
        # Instructions label with improved styling
        instruction_frame = ttk.Frame(self.matrix_frame)
        instruction_frame.pack(fill="x", pady=20)
        
        ttk.Label(instruction_frame, 
                 text="Select a project and click 'Generate Risk Matrix' to visualize risks based on impact and probability.",
                 wraplength=500,
                 font=("Arial", 10, "italic")).pack(anchor="center")
    
    def sync_project_dropdowns(self):
        """Synchronize both project dropdowns"""
        if hasattr(self, 'project_combo') and hasattr(self, 'matrix_project_combo'):
            projects = list(self.project_map.keys()) if hasattr(self, 'project_map') else []
            
            # Update both dropdowns
            self.project_combo['values'] = projects
            self.matrix_project_combo['values'] = projects
            
            # If main dropdown has a selection, copy it to matrix dropdown
            if self.project_combo.get():
                self.matrix_project_combo.set(self.project_combo.get())
            # If matrix dropdown has a selection, copy it to main dropdown
            elif self.matrix_project_combo.get():
                self.project_combo.set(self.matrix_project_combo.get())
    
    def on_tab_changed(self, event):
        """Handle tab change event to update dropdowns"""
        self.sync_project_dropdowns()
            
    def load_projects(self):
        # Fetch all projects and populate dropdown
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT id, project_name FROM projects")
        self.project_map = {name: pid for pid, name in cur.fetchall()}
        
        # Synchronize both dropdowns
        self.sync_project_dropdowns()
                
        cur.close()
        conn.close()

    def load_risks(self, event=None):
        # Get source of the event
        is_from_matrix = False
        if event and event.widget == self.matrix_project_combo:
            is_from_matrix = True
        
        # Get project name from the appropriate dropdown
        if is_from_matrix:
            project_name = self.matrix_project_combo.get()
            # Update main dropdown to match
            self.project_combo.set(project_name)
        else:
            project_name = self.project_combo.get()
            # Update matrix dropdown to match
            if hasattr(self, 'matrix_project_combo'):
                self.matrix_project_combo.set(project_name)
                
        project_id = self.project_map.get(project_name)
        self.tree.delete(*self.tree.get_children())
        self.risk_details = {}  # Reset risk details

        if not project_id:
            return
            
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT id, name, description, status FROM risks WHERE project_id = %s", (project_id,))
        self.risk_id_map = {}
        for row in cur.fetchall():
            risk_id, name, desc, status = row
            self.tree.insert('', 'end', values=(name, desc, status), tags=(str(risk_id),))
            self.risk_id_map[name] = risk_id
        cur.close()
        conn.close()

    def get_selected_risk(self):
        # Return ID and data of selected risk
        selected = self.tree.focus()
        if not selected:
            return None, None, None
        return selected, self.tree.item(selected)['tags'][0], self.tree.item(selected)['values']

    def add_risk(self):
        # Open empty form to add new risk
        self.open_risk_form("Add Risk")

    def edit_risk(self):
        # Open form prefilled with selected risk's data for editing
        selected, risk_id, values = self.get_selected_risk()
        if not selected:
            messagebox.showwarning("Select", "Select a risk to edit.")
            return
        self.open_risk_form("Edit Risk", risk_id, values)

    def delete_risk(self):
        # Delete selected risk after confirmation
        selected, risk_id, _ = self.get_selected_risk()
        if not selected:
            messagebox.showwarning("Select", "Select a risk to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete this risk?"):
            return
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM risks WHERE id = %s", (risk_id,))
        conn.commit()
        cur.close()
        conn.close()
        self.load_risks()

    def open_risk_form(self, title, risk_id=None, values=None):
        # Popup window for adding/editing a risk
        win = tk.Toplevel(self.frame)
        win.title(title)

        # Name
        ttk.Label(win, text="Name/ID").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        name = ttk.Entry(win, width=40)
        name.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Description
        ttk.Label(win, text="Description").grid(row=1, column=0, padx=10, pady=5, sticky="ne")
        desc = tk.Text(win, width=30, height=4)
        desc.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Status
        ttk.Label(win, text="Status").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        status = ttk.Combobox(win, values=["low", "medium", "high"], state="readonly", width=37)
        status.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        status.set("low")

        # Prefill if editing
        if values:
            name.insert(0, values[0])
            desc.insert("1.0", values[1])
            status.set(values[2])

        def submit():
            # Save or update the risk in the database
            project_id = self.project_map[self.project_combo.get()]
            conn = connect_db()
            cur = conn.cursor()
            if risk_id:
                cur.execute("""
                    UPDATE risks SET name = %s, description = %s, status = %s
                    WHERE id = %s
                """, (name.get(), desc.get("1.0", tk.END).strip(), status.get(), risk_id))
            else:
                cur.execute("""
                    INSERT INTO risks (project_id, name, description, status)
                    VALUES (%s, %s, %s, %s)
                """, (project_id, name.get(), desc.get("1.0", tk.END).strip(), status.get()))
            conn.commit()
            cur.close()
            conn.close()
            self.load_risks()
            win.destroy()

        # Save button for the popup
        ttk.Button(win, text="Save", command=submit).grid(row=3, column=1, pady=(3,10), padx=10)
        
    def show_risk_matrix(self):
        """Display risk matrix visualization with proper scaling and background"""
        # Get project name from appropriate dropdown based on which tab is active
        current_tab = self.risk_notebook.index(self.risk_notebook.select())
        
        if current_tab == 0:  # Risk List tab
            project_name = self.project_combo.get()
        else:  # Risk Matrix tab
            project_name = self.matrix_project_combo.get()
            
        if not project_name:
            messagebox.showwarning("Select Project", "Please select a project first")
            return
            
        # Create a new window for the matrix
        matrix_win = tk.Toplevel(self.frame)
        matrix_win.title(f"Risk Matrix - {project_name}")
        matrix_win.geometry("900x750")  # Increased size to accommodate larger margins
        matrix_win.configure(background="#f0f0f0")  # Light gray background
        matrix_win.resizable(True, True)  # Allow resizing
        
        # Main frame to hold everything
        main_frame = ttk.Frame(matrix_win, padding=10, style="Main.TFrame")
        main_frame.pack(fill="both", expand=True)
        
        # Configure styles
        style = ttk.Style()
        style.configure("Main.TFrame", background="#f0f0f0")
        style.configure("Header.TLabel", font=("Arial", 16, "bold"), background="#f0f0f0")
        style.configure("Subheader.TLabel", font=("Arial", 11), background="#f0f0f0", foreground="#555555")
        style.configure("Footer.TLabel", font=("Arial", 10, "italic"), background="#f0f0f0")
        
        # Header section
        header_frame = ttk.Frame(main_frame, style="Main.TFrame")
        header_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(header_frame, 
                 text=f"Risk Matrix: {project_name}", 
                 style="Header.TLabel").pack(anchor="w")
        
        ttk.Label(header_frame, 
                 text="Visualization of project risks based on impact and probability", 
                 style="Subheader.TLabel").pack(anchor="w", pady=(0, 10))
        
        # Matrix frame - will contain the actual visualization
        matrix_frame = ttk.Frame(main_frame, style="Main.TFrame")
        matrix_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Define matrix dimensions and spacing
        # These are carefully calculated to fit properly
        matrix_cell_size = 80  # Size of each cell
        matrix_width = 5 * matrix_cell_size  # 5 columns
        matrix_height = 5 * matrix_cell_size  # 5 rows
        left_margin = 130  # Space for impact labels - increased
        top_margin = 100   # Space for probability labels - increased
        right_margin = 20  # Additional right margin
        bottom_margin = 20  # Additional bottom margin
        
        # Calculate total canvas size
        canvas_width = left_margin + matrix_width + right_margin
        canvas_height = top_margin + matrix_height + bottom_margin
        
        # Create canvas that will hold the matrix
        canvas = tk.Canvas(matrix_frame, 
                          width=canvas_width, 
                          height=canvas_height,
                          background="#f0f0f0",  # Match the background
                          highlightthickness=0)  # Remove border
        canvas.pack(fill="both", expand=True)
        
        # Define colors for matrix cells - using more professional color scheme
        colors = {
            "critical": "#e53935",  # Red
            "high": "#f57c00",      # Orange
            "medium": "#fbc02d",    # Amber
            "low": "#7cb342"        # Green
        }
        
        # Draw matrix cells with shadow effect
        for i in range(5):  # Rows (impact)
            for j in range(5):  # Columns (probability)
                # Calculate priority value
                priority = (5-i) * (j+1)  # Impact (5-i) * Probability (j+1)
                
                # Get cell color based on priority
                if priority >= 16:
                    color = colors["critical"]
                    border_color = "#c62828"  # Darker red
                elif priority >= 10:
                    color = colors["high"]
                    border_color = "#e65100"  # Darker orange
                elif priority >= 5:
                    color = colors["medium"]
                    border_color = "#f9a825"  # Darker amber
                else:
                    color = colors["low"]
                    border_color = "#558b2f"  # Darker green
                
                # Cell position
                x1 = left_margin + j * matrix_cell_size
                y1 = top_margin + i * matrix_cell_size
                x2 = x1 + matrix_cell_size
                y2 = y1 + matrix_cell_size
                
                # Draw subtle shadow for 3D effect
                canvas.create_rectangle(
                    x1+3, y1+3, x2+3, y2+3,
                    fill="#d0d0d0", outline="", width=0
                )
                
                # Draw cell
                cell_id = canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color, outline=border_color, width=2
                )
                
                # Add priority text
                canvas.create_text(
                    x1 + matrix_cell_size/2,
                    y1 + matrix_cell_size/2,
                    text=str(priority),
                    font=("Arial", 11, "bold"),
                    fill="#ffffff"  # White text for better contrast
                )
        
        # Draw axis titles with improved positioning
        canvas.create_text(
            20,  # Moved even further left to avoid any overlap
            top_margin + matrix_height/2,
            text="IMPACT",
            font=("Arial", 12, "bold"),
            angle=90,
            anchor="center",
            fill="#333333"
        )
        
        canvas.create_text(
            left_margin + matrix_width/2, 
            20,  # Moved even higher to avoid any overlap
            text="PROBABILITY",
            font=("Arial", 12, "bold"),
            anchor="center",
            fill="#333333"
        )
        
        # Draw impact axis labels (y-axis) with more spacing
        impact_labels = ["Severe (5)", "Significant (4)", "Moderate (3)", "Minor (2)", "Minimal (1)"]
        for i, label in enumerate(impact_labels):
            y = top_margin + i * matrix_cell_size + matrix_cell_size/2
            canvas.create_text(
                left_margin - 15,  # Increased distance from matrix even more
                y,
                text=label,
                font=("Arial", 10),
                anchor="e",
                fill="#333333"
            )
        
        # Draw probability axis labels (x-axis) with more spacing
        prob_labels = ["Rare (1)", "Unlikely (2)", "Possible (3)", "Likely (4)", "Almost Certain (5)"]
        for j, label in enumerate(prob_labels):
            x = left_margin + j * matrix_cell_size + matrix_cell_size/2
            canvas.create_text(
                x, 
                top_margin - 15,  # Increased distance from matrix even more
                text=label,
                font=("Arial", 10),
                anchor="s",
                fill="#333333"
            )
            
        # Fetch risks data for the selected project
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, description, status, 
                   COALESCE(impact, 3) as impact,  
                   COALESCE(probability, 3) as probability
            FROM risks 
            WHERE project_id = %s
        """, (self.project_map[project_name],))
        
        # Store risk data
        risks = {}
        risk_positions = {}
        
        for row in cur.fetchall():
            risk_id, name, desc, status, impact, probability = row
            # Use default values if none stored
            impact = impact if impact else 3
            probability = probability if probability else 3
            
            # Store risk data
            risks[risk_id] = {
                'name': name,
                'description': desc,
                'impact': impact,
                'probability': probability,
                'priority': impact * probability,
                'status': status
            }
            
            # Calculate cell position for this risk
            cell_x = probability - 1
            cell_y = 5 - impact
            
            # Track risks in each cell
            cell_key = f"{cell_x},{cell_y}"
            if cell_key not in risk_positions:
                risk_positions[cell_key] = []
            risk_positions[cell_key].append(risk_id)
        
        cur.close()
        conn.close()
        
        # Plot risks on the matrix
        for cell_key, risk_ids in risk_positions.items():
            cell_x, cell_y = map(int, cell_key.split(','))
            num_risks = len(risk_ids)
            
            # Base position for this cell
            base_x = left_margin + cell_x * matrix_cell_size + matrix_cell_size/2
            base_y = top_margin + cell_y * matrix_cell_size + matrix_cell_size/2
            
            # Choose visualization based on number of risks in cell
            if num_risks == 1:
                # Single risk
                self._draw_risk_dot(canvas, base_x, base_y, risk_ids[0], risks)
            elif num_risks == 2:
                # Two risks side by side
                self._draw_risk_dot(canvas, base_x - 15, base_y, risk_ids[0], risks)
                self._draw_risk_dot(canvas, base_x + 15, base_y, risk_ids[1], risks)
            elif num_risks == 3:
                # Three risks in triangle
                self._draw_risk_dot(canvas, base_x, base_y - 15, risk_ids[0], risks)
                self._draw_risk_dot(canvas, base_x - 15, base_y + 10, risk_ids[1], risks)
                self._draw_risk_dot(canvas, base_x + 15, base_y + 10, risk_ids[2], risks)
            elif num_risks == 4:
                # Four risks in square
                self._draw_risk_dot(canvas, base_x - 15, base_y - 15, risk_ids[0], risks)
                self._draw_risk_dot(canvas, base_x + 15, base_y - 15, risk_ids[1], risks)
                self._draw_risk_dot(canvas, base_x - 15, base_y + 15, risk_ids[2], risks)
                self._draw_risk_dot(canvas, base_x + 15, base_y + 15, risk_ids[3], risks)
            else:
                # More than 4 risks - show count
                # Draw shadow for 3D effect
                canvas.create_oval(
                    base_x - 18 + 2, base_y - 18 + 2, 
                    base_x + 18 + 2, base_y + 18 + 2, 
                    fill="#d0d0d0", outline=""
                )
                # Draw main circle
                circle_id = canvas.create_oval(
                    base_x - 20, base_y - 20, 
                    base_x + 20, base_y + 20, 
                    fill="#3949ab", outline="#1a237e", width=2
                )
                text_id = canvas.create_text(
                    base_x, base_y, 
                    text=f"{num_risks}", 
                    fill="white", 
                    font=("Arial", 11, "bold")
                )
                
                # Create tooltip text
                tooltip_text = f"Multiple risks ({num_risks}) in this cell:\n\n"
                for i, risk_id in enumerate(risk_ids):
                    tooltip_text += f"{i+1}. {risks[risk_id]['name']}\n"
                
                # Bind hover events for multiple risks indicator
                self._bind_tooltip(canvas, circle_id, tooltip_text)
                self._bind_tooltip(canvas, text_id, tooltip_text)
        
        # Legend section
        legend_frame = ttk.LabelFrame(main_frame, text="Risk Priority Legend", padding=10)
        legend_frame.pack(fill="x", pady=10)
        
        # Create legend items
        legend_items = [
            ("Low (1-4)", colors["low"]),
            ("Medium (5-9)", colors["medium"]),
            ("High (10-15)", colors["high"]),
            ("Critical (16-25)", colors["critical"])
        ]
        
        # Layout legend items horizontally
        for text, color in legend_items:
            item_frame = ttk.Frame(legend_frame)
            item_frame.pack(side="left", padx=20, pady=2)
            
            # Color box
            color_box = tk.Canvas(item_frame, width=20, height=20, bg="#f0f0f0", highlightthickness=0)
            color_box.create_rectangle(0, 0, 18, 18, fill=color, outline="#666666")
            color_box.pack(side="left", padx=5)
            
            # Text label
            ttk.Label(item_frame, text=text).pack(side="left")
        
        # Instructions at the bottom
        footer_frame = ttk.Frame(main_frame, style="Main.TFrame")
        footer_frame.pack(fill="x", pady=10)
        
        ttk.Label(
            footer_frame, 
            text="Hover over risk indicators to see details. Blue dots show individual risks.",
            style="Footer.TLabel"
        ).pack(side="left")
        
        ttk.Button(
            footer_frame, 
            text="Close", 
            command=matrix_win.destroy
        ).pack(side="right")
        
        # Store active tooltips
        self.active_tooltips = {}
        
        # Store risk data for tooltips
        self.current_risks = risks
        
        # Cleanup on window close
        def on_window_close():
            if hasattr(self, 'active_tooltips'):
                for tooltip in self.active_tooltips.values():
                    if tooltip and tooltip.winfo_exists():
                        tooltip.destroy()
            matrix_win.destroy()
            
        matrix_win.protocol("WM_DELETE_WINDOW", on_window_close)
    
    def _draw_risk_dot(self, canvas, x, y, risk_id, risks):
        """Draw a single risk dot on the matrix"""
        # Draw shadow for 3D effect
        shadow_id = canvas.create_oval(
            x - 10 + 2, y - 10 + 2, 
            x + 10 + 2, y + 10 + 2, 
            fill="#d0d0d0", outline=""
        )
        
        # Different shade of blue for each risk
        fill_color = "#3f51b5"  # Indigo
        outline_color = "#303f9f"  # Darker indigo
        
        # Draw dot
        dot_id = canvas.create_oval(
            x - 12, y - 12, 
            x + 12, y + 12, 
            fill=fill_color, outline=outline_color, width=2
        )
        
        # Add risk ID
        text_id = canvas.create_text(
            x, y, 
            text=str(risk_id), 
            fill="white", 
            font=("Arial", 9, "bold")
        )
        
        # Prepare tooltip text
        risk = risks[risk_id]
        tooltip_text = f"Risk ID: {risk_id}\n"
        tooltip_text += f"Name: {risk['name']}\n"
        if risk['description']:
            tooltip_text += f"Description: {risk['description'][:50]}...\n" if len(risk['description']) > 50 else f"Description: {risk['description']}\n"
        tooltip_text += f"Impact: {risk['impact']}\n"
        tooltip_text += f"Probability: {risk['probability']}\n"
        tooltip_text += f"Priority: {risk['priority']}\n"
        tooltip_text += f"Status: {risk['status']}\n"
        
        # Bind tooltip to both dot and text
        self._bind_tooltip(canvas, dot_id, tooltip_text)
        self._bind_tooltip(canvas, text_id, tooltip_text)
        
    def _bind_tooltip(self, canvas, item_id, tooltip_text):
        """Bind tooltip to canvas item"""
        canvas.tag_bind(item_id, "<Enter>", lambda e, id=item_id, txt=tooltip_text: self._show_tooltip(e, id, txt))
        canvas.tag_bind(item_id, "<Leave>", lambda e, id=item_id: self._hide_tooltip(id))
        
    def _show_tooltip(self, event, item_id, tooltip_text):
        """Show tooltip when hovering over an item"""
        # Hide any existing tooltip for this item
        self._hide_tooltip(item_id)
        
        # Create new tooltip
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)  # Remove window border
        
        # Position near mouse
        tooltip.geometry(f"+{event.x_root+15}+{event.y_root+10}")
        
        # Create tooltip content
        frame = ttk.Frame(tooltip, relief="solid", borderwidth=1)
        frame.pack(fill="both", expand=True)
        
        label = ttk.Label(
            frame, 
            text=tooltip_text,
            background="#fffde7",  # Light yellow
            padding=8,
            justify="left",
            font=("Arial", 10)
        )
        label.pack()
        
        # Store tooltip reference
        self.active_tooltips[item_id] = tooltip
        
    def _hide_tooltip(self, item_id):
        """Hide tooltip when mouse leaves an item"""
        if item_id in self.active_tooltips:
            tooltip = self.active_tooltips[item_id]
            if tooltip and tooltip.winfo_exists():
                tooltip.destroy()
            self.active_tooltips[item_id] = None

    def update_risk_table_if_needed(self):
        """Check if the risks table needs to be updated with impact and probability columns"""
        try:
            conn = connect_db()
            cur = conn.cursor()
            
            # First make sure the risks table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'risks'
                )
            """)
            
            table_exists = cur.fetchone()[0]
            if not table_exists:
                # Create the risks table if it doesn't exist
                cur.execute("""
                    CREATE TABLE risks (
                        id SERIAL PRIMARY KEY,
                        project_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT,
                        status TEXT,
                        impact INTEGER DEFAULT 3,
                        probability INTEGER DEFAULT 3,
                        priority INTEGER DEFAULT 9,
                        mitigation_strategy TEXT
                    )
                """)
                conn.commit()
                print("Created risks table")
            
            # Check if impact column exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'risks' AND column_name = 'impact'
                )
            """)
            impact_exists = cur.fetchone()[0]
            
            # Check if probability column exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'risks' AND column_name = 'probability'
                )
            """)
            probability_exists = cur.fetchone()[0]
            
            # If columns don't exist, add them
            if not impact_exists:
                cur.execute("ALTER TABLE risks ADD COLUMN impact INTEGER DEFAULT 3")
                print("Added impact column to risks table")
                
            if not probability_exists:
                cur.execute("ALTER TABLE risks ADD COLUMN probability INTEGER DEFAULT 3")
                print("Added probability column to risks table")
                
            # Add priority column if it doesn't exist
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'risks' AND column_name = 'priority'
                )
            """)
            priority_exists = cur.fetchone()[0]
            
            if not priority_exists:
                cur.execute("ALTER TABLE risks ADD COLUMN priority INTEGER DEFAULT 9")
                print("Added priority column to risks table")
                
            # Add mitigation_strategy column if it doesn't exist
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'risks' AND column_name = 'mitigation_strategy'
                )
            """)
            mitigation_exists = cur.fetchone()[0]
            
            if not mitigation_exists:
                cur.execute("ALTER TABLE risks ADD COLUMN mitigation_strategy TEXT DEFAULT ''")
                print("Added mitigation_strategy column to risks table")
                
            # Check for the old columns to handle the transition
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'risks' AND column_name = 'risk_name'
                )
            """)
            old_name_exists = cur.fetchone()[0]
            
            if old_name_exists:
                # Rename the columns if using the old naming convention
                print("Converting old risk column names to new format...")
                cur.execute("ALTER TABLE risks RENAME COLUMN risk_name TO name")
                cur.execute("ALTER TABLE risks RENAME COLUMN risk_description TO description")
                cur.execute("ALTER TABLE risks RENAME COLUMN risk_status TO status")
                print("Column names updated successfully")
            
            # If we have risks without impact/probability, calculate default values
            cur.execute("""
                UPDATE risks 
                SET impact = 3,
                    probability = 3,
                    priority = 9
                WHERE impact IS NULL OR probability IS NULL OR priority IS NULL
            """)
            
            # Commit all changes
            conn.commit()
            print("Risk table schema update complete")
            
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error updating risk table: {e}")
            messagebox.showerror("Database Error", f"Error updating risk table: {e}")


# === REQUIREMENTS TAB ===


class RequirementsTab:
    def __init__(self, parent, effort_tab):
        self.parent = parent
        self.effort_tab = effort_tab
        self.frame = ttk.Frame(self.parent)
        self.setup_ui()

    def setup_ui(self):

        # Title
        title_label = ttk.Label(self.frame, text="Requirements", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 15), sticky='nw')

        # Project selector dropdown
        ttk.Label(self.frame, text="Select Project:").grid(row=1, column=0, padx=20, pady=10, sticky='w')
        self.project_combo = ttk.Combobox(self.frame, width=40, state="readonly")
        self.project_combo.grid(row=1, column=1, padx=20, pady=10, sticky='w')
        self.project_combo.bind("<<ComboboxSelected>>", self.load_requirements)

        # Functional Requirements Treeview
        ttk.Label(self.frame, text="Functional Requirements:").grid(row=2, column=0, columnspan=3, sticky='w', padx=20)
        self.func_tree = ttk.Treeview(self.frame, columns=("Name/ID", "Status", "Description"), show='headings')
        for col in self.func_tree["columns"]:
            self.func_tree.heading(col, text=col)
        self.func_tree.grid(row=3, column=0, columnspan=3, padx=20, pady=5, sticky="nsew")

        # Non-Functional Requirements Treeview
        ttk.Label(self.frame, text="Non-Functional Requirements:").grid(row=4, column=0, columnspan=3, sticky='w', padx=20)
        self.nonfunc_tree = ttk.Treeview(self.frame, columns=("Name/ID", "Status", "Description"), show='headings')
        for col in self.nonfunc_tree["columns"]:
            self.nonfunc_tree.heading(col, text=col)
        self.nonfunc_tree.grid(row=5, column=0, columnspan=3, padx=20, pady=5, sticky="nsew")

        # Allow the treeviews to expand with the window
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_rowconfigure(4, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)

        # Buttons for requirement operations
        btn_frame = ttk.Frame(self.frame)
        btn_frame.grid(row=6, column=0, columnspan=3, sticky='e', padx=10, pady=10) 
        ttk.Button(btn_frame, text="Add Requirement", command=self.add_requirement).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edit Requirement", command=self.edit_requirement).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Requirement", command=self.delete_requirement).pack(side="left", padx=5)

        self.load_projects()

    def load_projects(self):
        # Load all projects from DB and populate the dropdown
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT id, project_name FROM projects")
        self.project_map = {name: pid for pid, name in cur.fetchall()}
        self.project_combo['values'] = list(self.project_map.keys())
        cur.close()
        conn.close()

    def load_requirements(self, event=None):
        # Load all requirements for selected project and populate treeviews
        project_name = self.project_combo.get()
        project_id = self.project_map.get(project_name)
        self.func_tree.delete(*self.func_tree.get_children())
        self.nonfunc_tree.delete(*self.nonfunc_tree.get_children())

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT id, requirement_name, requirement_type, status, description FROM requirements WHERE project_id = %s", (project_id,))
        self.req_id_map = {}
        for row in cur.fetchall():
            req_id, name, rtype, status, desc = row
            tree = self.func_tree if rtype == "functional" else self.nonfunc_tree
            tree.insert('', 'end', values=(name, status, desc), tags=(str(req_id),))
            self.req_id_map[name] = req_id
        cur.close()
        conn.close()

    def get_selected_requirement(self):
        # Returns the selected row's ID and values from either treeview
        for tree in [self.func_tree, self.nonfunc_tree]:
            selected = tree.focus()
            if selected:
                return selected, tree.item(selected)['tags'][0], tree.item(selected)['values']
        return None, None, None

    def add_requirement(self):
        # Opens the add requirement form
        self.open_requirement_form("Add Requirement")

    def edit_requirement(self):
        # Opens the edit form with prefilled values
        selected, req_id, values = self.get_selected_requirement()
        if not selected:
            messagebox.showwarning("Select", "Select a requirement to edit.")
            return
        self.open_requirement_form("Edit Requirement", req_id, values)

    def delete_requirement(self):
        # Deletes selected requirement after confirmation
        selected, req_id, _ = self.get_selected_requirement()
        if not selected:
            messagebox.showwarning("Select", "Select a requirement to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete this requirement?"):
            return
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM requirements WHERE id = %s", (req_id,))
        conn.commit()
        cur.close()
        conn.close()
        self.load_requirements()

    def open_requirement_form(self, title, req_id=None, values=None):
        # Opens form to add or edit a requirement
        win = tk.Toplevel(self.frame)
        win.title(title)

        field_width = 30

        # Name/ID
        ttk.Label(win, text="Name/ID").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        name = ttk.Entry(win, width=40)
        name.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Type
        ttk.Label(win, text="Type").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        rtype = ttk.Combobox(win, values=["functional", "non-functional"], state="readonly", width=37)
        rtype.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        rtype.set("functional")

        # Status
        ttk.Label(win, text="Status").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        status = ttk.Combobox(win, values=["pending", "in progress", "completed", "rejected"], state="readonly", width=37)
        status.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        status.set("pending")

        # Description
        ttk.Label(win, text="Description").grid(row=3, column=0, padx=10, pady=5, sticky="ne")
        desc = tk.Text(win, width=field_width, height=5)
        desc.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # If editing, prefill the form
        if values:
            name.insert(0, values[0])
            status.set(values[1])
            desc.insert("1.0", values[2])

        def submit():
            # Save new or updated requirement to DB
            project_id = self.project_map[self.project_combo.get()]
            conn = connect_db()
            cur = conn.cursor()
            if req_id:
                # Update existing requirement
                cur.execute("""
                    UPDATE requirements 
                    SET requirement_name = %s, requirement_type = %s, status = %s, description = %s
                    WHERE id = %s
                """, (name.get(), rtype.get(), status.get(), desc.get("1.0", tk.END).strip(), req_id))
            else:
                # Add new requirement
                cur.execute("""
                    INSERT INTO requirements (project_id, requirement_name, description, requirement_type, status)
                    VALUES (%s, %s, %s, %s, %s)
                """, (project_id, name.get(), desc.get("1.0", tk.END).strip(), rtype.get(), status.get()))
            conn.commit()
            cur.close()
            conn.close()
            self.load_requirements()
            self.effort_tab.load_requirements()
            win.destroy()

        ttk.Button(win, text="Save", command=submit).grid(row=4, column=1, pady=10)


# === EFFORT TRACKING & MONITORING TAB ===


class EffortTrackingTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(self.parent)
        self.setup_ui()

    def setup_ui(self):

        # Title
        title_label = ttk.Label(self.frame, text="Effort Tracking & Monitoring", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 15), sticky='nw')

        # Project selection 
        ttk.Label(self.frame, text="Select Project:").grid(row=1, column=0, padx=30, pady=5, sticky='e')
        self.project_combo = ttk.Combobox(self.frame, width=40, state="readonly")
        self.project_combo.grid(row=1, column=1, padx=30, pady=5, sticky='w')
        self.project_combo.bind("<<ComboboxSelected>>", self.load_requirements)
        
        # Requirement selection 
        ttk.Label(self.frame, text="Select Requirement:").grid(row=2, column=0, padx=30, pady=5, sticky='e')
        self.requirement_combo = ttk.Combobox(self.frame, width=40, state="readonly")
        self.requirement_combo.grid(row=2, column=1, padx=30, pady=5, sticky='w')
        self.requirement_combo.bind("<<ComboboxSelected>>", lambda e: self.load_effort_entries())

        # Date entry 
        ttk.Label(self.frame, text="Date:").grid(row=3, column=0, padx=30, pady=5, sticky='e')
        self.date_entry = ttk.Entry(self.frame, width=12)
        self.date_entry.grid(row=3, column=1, padx=30, pady=5, sticky='w')
        self.date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))

        # Effort category input fields 
        self.entries = {}
        categories = ["Requirements Analysis", "Designing", "Coding", "Testing", "Project Management"]
        for i, cat in enumerate(categories, start=4):
            ttk.Label(self.frame, text=cat + " Hours:").grid(row=i, column=0, padx=30, pady=5, sticky='e')
            entry = ttk.Entry(self.frame, width=12)
            entry.grid(row=i, column=1, padx=30, pady=5, sticky='w')
            self.entries[cat] = entry

        # Action buttons 
        btn_frame = ttk.Frame(self.frame)
        btn_frame.grid(row=9, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        ttk.Button(btn_frame, text="Save Entry", command=self.save_effort).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Selected Entry", command=self.delete_selected_entry).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="View Total Hours", command=self.view_totals).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Hide Total Hours", command=self.hide_totals).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear All Entries", command=self.clear_all_entries).pack(side="left", padx=5)

        # Effort entries table 
        self.tree = ttk.Treeview(self.frame, columns=["Date"] + categories, show='headings')
        for col in ["Date"] + categories:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.grid(row=10, column=0, columnspan=2, padx=20, pady=1, sticky="nsew")

        # Allow table to expand with window
        self.frame.grid_rowconfigure(9, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        self.load_projects()

    def load_projects(self):
        # Fetch all projects and populate the dropdown
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT id, project_name FROM projects")
        self.project_map = {name: pid for pid, name in cur.fetchall()}
        self.project_combo['values'] = list(self.project_map.keys())
        cur.close()
        conn.close()

    def load_requirements(self, event=None):
        # Fetch and populate the requirements dropdown for selected project
        self.requirement_combo.set("")
        project_id = self.project_map.get(self.project_combo.get())
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT id, requirement_name FROM requirements WHERE project_id = %s", (project_id,))
        self.requirement_map = {name: rid for rid, name in cur.fetchall()}
        self.requirement_combo['values'] = list(self.requirement_map.keys())
        cur.close()
        conn.close()

    def save_effort(self):
        # Validate and save a new effort entry
        req_id = self.requirement_map.get(self.requirement_combo.get())
        if not req_id:
            messagebox.showwarning("Select Requirement", "Please select a requirement")
            return

        date = self.date_entry.get().strip()
        if not date:
            messagebox.showwarning("Missing Date", "Please enter a date.")
            return

        # Check if all fields are filled
        if not all(self.entries[cat].get().strip() for cat in self.entries):
            messagebox.showwarning("Incomplete Entry", "Please enter all effort hours.")
            return

        try:
            # Check if entry already exists for this requirement and date
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*) FROM effort_tracking
                WHERE requirement_id = %s AND date = %s
            """, (req_id, date))
            exists = cur.fetchone()[0] > 0
            if exists:
                messagebox.showwarning("Duplicate Entry", "An entry for this date already exists for the selected requirement.")
                cur.close()
                conn.close()
                return

            # Prepare and insert the data
            values = tuple(float(self.entries[cat].get()) for cat in self.entries)

            cur.execute("""
                INSERT INTO effort_tracking (requirement_id, date, requirements_analysis, designing, coding, testing, project_management)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (req_id, date, *values))
            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("Saved", "Effort saved successfully.")

            # Clear entries
            for entry in self.entries.values():
                entry.delete(0, tk.END)

            # Show newly saved entry
            self.tree.insert('', 'end', values=(date, *values))

        except ValueError:
            messagebox.showerror("Invalid Input", "All hour fields must be numeric.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_totals(self):
        # Get current project ID
        project_id = self.project_map.get(self.project_combo.get())
        if not project_id:
            messagebox.showwarning("Select Project", "Please select a project.")
            return

        # Fetch summed totals per requirement
        conn = connect_db()
        cur = conn.cursor()
        req_id = self.requirement_map.get(self.requirement_combo.get())
        cur.execute("""
            SELECT 
                SUM(requirements_analysis), 
                SUM(designing), 
                SUM(coding), 
                SUM(testing), 
                SUM(project_management)
            FROM effort_tracking
            WHERE requirement_id = %s
        """, (req_id,))
        row = cur.fetchone()
        total_row = cur.fetchone()
        cur.close()
        conn.close()

        # Insert totals row at the end of the Treeview
        self.tree.insert('', 'end', values=("Total", *row), tags=("total",))

    def load_effort_entries(self):
        # Load all saved entries for the selected requirement
        self.tree.delete(*self.tree.get_children())
        req_id = self.requirement_map.get(self.requirement_combo.get())
        if not req_id:
            return

        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT date, requirements_analysis, designing, coding, testing, project_management
            FROM effort_tracking
            WHERE requirement_id = %s
            ORDER BY date
        """, (req_id,))
        for row in cur.fetchall():
            self.tree.insert('', 'end', values=row)
        cur.close()
        conn.close()

    def hide_totals(self):
        # Remove the totals row if displayed
        for item in self.tree.get_children():
            if "total" in self.tree.item(item, "tags"):
                self.tree.delete(item)

    def delete_selected_entry(self):
        # Delete a specific effort entry based on selection
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select Entry", "Please select a row to delete.")
            return

        values = self.tree.item(selected, 'values')
        if values[0] == "Total":
            messagebox.showinfo("Info", "Totals row cannot be deleted.")
            return

        confirm = messagebox.askyesno("Confirm", "Delete selected entry?")
        if not confirm:
            return

        # Identify and delete from DB
        date = values[0]
        req_id = self.requirement_map.get(self.requirement_combo.get())
        if not req_id:
            return

        # Remove from database  
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM effort_tracking 
            WHERE requirement_id = %s AND date = %s
        """, (req_id, date))
        conn.commit()
        cur.close()
        conn.close()

        # Remove from treeview
        self.tree.delete(selected)

    def clear_all_entries(self):
        # Clear all entries for the selected requirement after confirmation
        req_name = self.requirement_combo.get()
        req_id = self.requirement_map.get(req_name)
        if not req_id:
            messagebox.showwarning("Select Requirement", "Please select a requirement.")
            return

        if not messagebox.askyesno("Confirm", f"Delete all effort entries for '{req_name}'?"):
            return

        # Delete from database
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM effort_tracking WHERE requirement_id = %s", (req_id,))
        conn.commit()
        cur.close()
        conn.close()

        self.load_effort_entries()
        messagebox.showinfo("Cleared", "All entries have been deleted.")


# === EXPORTS TAB ===

class ExportsTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(self.parent)
        self.setup_ui()
    
    def setup_ui(self):
        # Title label
        title_label = ttk.Label(self.frame, text="Exports", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="nw")
        
        # Description label
        desc_label = ttk.Label(self.frame, text="Select data to export in CSV or PDF format.")
        desc_label.grid(row=1, column=0, columnspan=2, padx=20, pady=1, sticky="w")
        
        # Export Projects section
        projects_frame = ttk.LabelFrame(self.frame, text="Projects")
        projects_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        
        ttk.Label(projects_frame, text="Export all project data").pack(padx=10, pady=5, anchor="w")
        proj_btn_frame = ttk.Frame(projects_frame)
        proj_btn_frame.pack(padx=10, pady=10)
        ttk.Button(proj_btn_frame, text="CSV", command=self.export_projects_csv).pack(side="left", padx=5)
        ttk.Button(proj_btn_frame, text="PDF", command=self.export_projects_pdf).pack(side="left", padx=5)
        
        # Export Requirements section
        requirements_frame = ttk.LabelFrame(self.frame, text="Requirements")
        requirements_frame.grid(row=2, column=1, padx=20, pady=10, sticky="nsew")
        
        ttk.Label(requirements_frame, text="Export all requirements data").pack(padx=10, pady=5, anchor="w")
        req_btn_frame = ttk.Frame(requirements_frame)
        req_btn_frame.pack(padx=10, pady=10)
        ttk.Button(req_btn_frame, text="CSV", command=self.export_requirements_csv).pack(side="left", padx=5)
        ttk.Button(req_btn_frame, text="PDF", command=self.export_requirements_pdf).pack(side="left", padx=5)
        
        # Export Effort Tracking section
        effort_frame = ttk.LabelFrame(self.frame, text="Effort Tracking")
        effort_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        
        ttk.Label(effort_frame, text="Export all effort tracking data").pack(padx=10, pady=5, anchor="w")
        eff_btn_frame = ttk.Frame(effort_frame)
        eff_btn_frame.pack(padx=10, pady=10)
        ttk.Button(eff_btn_frame, text="CSV", command=self.export_effort_csv).pack(side="left", padx=5)
        ttk.Button(eff_btn_frame, text="PDF", command=self.export_effort_pdf).pack(side="left", padx=5)
        
        # Export Risks section
        risks_frame = ttk.LabelFrame(self.frame, text="Risks")
        risks_frame.grid(row=3, column=1, padx=20, pady=10, sticky="nsew")
        
        ttk.Label(risks_frame, text="Export all risk management data").pack(padx=10, pady=5, anchor="w")
        risk_btn_frame = ttk.Frame(risks_frame)
        risk_btn_frame.pack(padx=10, pady=10)
        ttk.Button(risk_btn_frame, text="CSV", command=self.export_risks_csv).pack(side="left", padx=5)
        ttk.Button(risk_btn_frame, text="PDF", command=self.export_risks_pdf).pack(side="left", padx=5)
        
        # Export All section
        all_frame = ttk.LabelFrame(self.frame, text="Export All")
        all_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        
        ttk.Label(all_frame, text="Export all project management data").pack(padx=10, pady=5, anchor="w")
        all_btn_frame = ttk.Frame(all_frame)
        all_btn_frame.pack(padx=10, pady=10)
        ttk.Button(all_btn_frame, text="CSV", command=self.export_all_csv).pack(side="left", padx=5)
        ttk.Button(all_btn_frame, text="PDF", command=self.export_all_pdf).pack(side="left", padx=5)
        
        # Status section
        status_frame = ttk.LabelFrame(self.frame, text="Export Status")
        status_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to export")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(padx=10, pady=10, fill="x")
        
        # Configure grid weights for responsive layout
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
    
    def check_reportlab(self):
        """Check if ReportLab is available, show message if not"""
        if not REPORTLAB_AVAILABLE:
            messagebox.showwarning(
                "ReportLab Not Available", 
                "PDF export requires the ReportLab library.\n\n"
                "To install it, run: pip install reportlab"
            )
            return False
        return True
        
    def export_projects_pdf(self):
        """Export projects to PDF format"""
        if not self.check_reportlab():
            return
            
        # Get file path from user
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Export Projects to PDF"
        )
        if not file_path:
            return
            
        try:
            # Get project data
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT project_name, owner, project_description, project_scope, target_users, technology_stack, platform FROM projects ORDER BY project_name")
            projects = cur.fetchall()
            cur.close()
            conn.close()
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Add title
            title = Paragraph("Project Management System - Projects Report", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            # Add date
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_paragraph = Paragraph(f"Generated on: {date_str}", styles['Normal'])
            elements.append(date_paragraph)
            elements.append(Spacer(1, 20))
            
            # Create table data
            table_data = [["Project Name", "Owner", "Description", "Scope", "Target Users", "Tech Stack", "Platform"]]
            for project in projects:
                # Truncate long fields
                desc = project[2][:100] + "..." if len(project[2]) > 100 else project[2]
                scope = project[3][:100] + "..." if len(project[3]) > 100 else project[3]
                
                table_data.append([
                    project[0],  # project_name
                    project[1],  # owner
                    desc,        # description (truncated)
                    scope,       # scope (truncated)
                    project[4],  # target_users
                    project[5],  # tech_stack
                    project[6]   # platform
                ])
            
            # Create the table
            table = Table(table_data, repeatRows=1)
            
            # Add style to the table
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            self.status_var.set(f"Projects exported successfully to {os.path.basename(file_path)}")
            messagebox.showinfo("Success", "Projects exported successfully to PDF!")
        except Exception as e:
            self.status_var.set(f"Error exporting projects to PDF: {e}")
            messagebox.showerror("Error", f"Failed to export projects to PDF: {e}")
    
    def export_requirements_pdf(self):
        """Export requirements to PDF format"""
        if not self.check_reportlab():
            return
            
        # Get file path from user
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Export Requirements to PDF"
        )
        if not file_path:
            return
            
        try:
            # Get requirements data
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT p.project_name, r.requirement_name, r.requirement_type, r.status, r.description
                FROM requirements r
                JOIN projects p ON r.project_id = p.id
                ORDER BY p.project_name, r.requirement_name
            """)
            requirements = cur.fetchall()
            cur.close()
            conn.close()
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Add title
            title = Paragraph("Project Management System - Requirements Report", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            # Add date
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_paragraph = Paragraph(f"Generated on: {date_str}", styles['Normal'])
            elements.append(date_paragraph)
            elements.append(Spacer(1, 20))
            
            # Create table data
            table_data = [["Project", "Requirement Name", "Type", "Status", "Description"]]
            for req in requirements:
                # Truncate description
                desc = req[4][:100] + "..." if len(req[4]) > 100 else req[4]
                
                table_data.append([
                    req[0],  # project_name
                    req[1],  # requirement_name
                    req[2],  # requirement_type
                    req[3],  # status
                    desc     # description (truncated)
                ])
            
            # Create the table
            table = Table(table_data, repeatRows=1)
            
            # Add style to the table
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            self.status_var.set(f"Requirements exported successfully to {os.path.basename(file_path)}")
            messagebox.showinfo("Success", "Requirements exported successfully to PDF!")
        except Exception as e:
            self.status_var.set(f"Error exporting requirements to PDF: {e}")
            messagebox.showerror("Error", f"Failed to export requirements to PDF: {e}")
    
    def export_effort_pdf(self):
        """Export effort tracking data to PDF format"""
        if not self.check_reportlab():
            return
            
        # Get file path from user
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Export Effort Tracking to PDF"
        )
        if not file_path:
            return
            
        try:
            # Get effort tracking data
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT p.project_name, r.requirement_name, e.date, 
                       e.requirements_analysis, e.designing, e.coding, 
                       e.testing, e.project_management
                FROM effort_tracking e
                JOIN requirements r ON e.requirement_id = r.id
                JOIN projects p ON r.project_id = p.id
                ORDER BY p.project_name, r.requirement_name, e.date
            """)
            effort = cur.fetchall()
            cur.close()
            conn.close()
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Add title
            title = Paragraph("Project Management System - Effort Tracking Report", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            # Add date
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_paragraph = Paragraph(f"Generated on: {date_str}", styles['Normal'])
            elements.append(date_paragraph)
            elements.append(Spacer(1, 20))
            
            # Create table data
            table_data = [["Project", "Requirement", "Date", "Req. Analysis", "Design", "Coding", "Testing", "PM"]]
            for entry in effort:
                table_data.append([
                    entry[0],  # project_name
                    entry[1],  # requirement_name
                    entry[2],  # date
                    entry[3],  # requirements_analysis
                    entry[4],  # designing
                    entry[5],  # coding
                    entry[6],  # testing
                    entry[7]   # project_management
                ])
            
            # Create the table
            table = Table(table_data, repeatRows=1)
            
            # Add style to the table
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            self.status_var.set(f"Effort tracking data exported successfully to {os.path.basename(file_path)}")
            messagebox.showinfo("Success", "Effort tracking data exported successfully to PDF!")
        except Exception as e:
            self.status_var.set(f"Error exporting effort tracking data to PDF: {e}")
            messagebox.showerror("Error", f"Failed to export effort tracking data to PDF: {e}")
    
    def export_risks_csv(self):
        # Get file path from user
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Risks"
        )
        if not file_path:
            return
            
        try:
            # Get risks data
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT p.project_name, r.name, r.description, r.risk_status
                FROM risks r
                JOIN projects p ON r.project_id = p.id
                ORDER BY p.project_name, r.name
            """)
            risks = cur.fetchall()
            cur.close()
            conn.close()
            
            # Write to CSV
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Project", "Risk Name", "Description", "Status"])
                writer.writerows(risks)
                
            self.status_var.set(f"Risks exported successfully to {os.path.basename(file_path)}")
            messagebox.showinfo("Success", "Risks exported successfully!")
        except Exception as e:
            self.status_var.set(f"Error exporting risks: {e}")
            messagebox.showerror("Error", f"Failed to export risks: {e}")
    
    def export_risks_pdf(self):
        """Export risks to PDF format"""
        if not self.check_reportlab():
            return
            
        # Get file path from user
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Export Risks to PDF"
        )
        if not file_path:
            return
            
        try:
            # Get risks data
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT p.project_name, r.name, r.description, r.risk_status
                FROM risks r
                JOIN projects p ON r.project_id = p.id
                ORDER BY p.project_name, r.name
            """)
            risks = cur.fetchall()
            cur.close()
            conn.close()
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Add title
            title = Paragraph("Project Management System - Risk Management Report", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            # Add date
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_paragraph = Paragraph(f"Generated on: {date_str}", styles['Normal'])
            elements.append(date_paragraph)
            elements.append(Spacer(1, 20))
            
            # Create table data
            table_data = [["Project", "Risk", "Description", "Status"]]
            for risk in risks:
                # Truncate description
                desc = risk[2][:100] + "..." if len(risk[2]) > 100 else risk[2]
                
                table_data.append([
                    risk[0],  # project_name
                    risk[1],  # name
                    desc,     # description (truncated)
                    risk[3]   # status
                ])
            
            # Create the table
            table = Table(table_data, repeatRows=1)
            
            # Add style to the table
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            self.status_var.set(f"Risks exported successfully to {os.path.basename(file_path)}")
            messagebox.showinfo("Success", "Risks exported successfully to PDF!")
        except Exception as e:
            self.status_var.set(f"Error exporting risks to PDF: {e}")
            messagebox.showerror("Error", f"Failed to export risks to PDF: {e}")
    
    def export_all_pdf(self):
        """Export all data to PDF format"""
        if not self.check_reportlab():
            return
            
        # Get directory from user
        directory = filedialog.askdirectory(title="Select Export Directory")
        if not directory:
            return
            
        success_count = 0
        try:
            # Connect to database
            conn = connect_db()
            cur = conn.cursor()
            
            # Export projects
            projects_file = os.path.join(directory, "projects_export.pdf")
            try:
                # Get project data
                cur.execute("SELECT project_name, owner, project_description, project_scope, target_users, technology_stack, platform FROM projects ORDER BY project_name")
                projects = cur.fetchall()
                
                # Create PDF
                doc = SimpleDocTemplate(projects_file, pagesize=letter)
                styles = getSampleStyleSheet()
                elements = []
                
                # Add title
                title = Paragraph("Project Management System - Projects Report", styles['Title'])
                elements.append(title)
                elements.append(Spacer(1, 20))
                
                # Add date
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                date_paragraph = Paragraph(f"Generated on: {date_str}", styles['Normal'])
                elements.append(date_paragraph)
                elements.append(Spacer(1, 20))
                
                # Create table data
                table_data = [["Project Name", "Owner", "Description", "Scope", "Target Users", "Tech Stack", "Platform"]]
                for project in projects:
                    # Truncate description and scope
                    desc = project[2][:100] + "..." if len(project[2]) > 100 else project[2]
                    scope = project[3][:100] + "..." if len(project[3]) > 100 else project[3]
                    
                    table_data.append([
                        project[0],  # project_name
                        project[1],  # owner
                        desc,        # description (truncated)
                        scope,       # scope (truncated)
                        project[4],  # target_users
                        project[5],  # tech_stack
                        project[6]   # platform
                    ])
                
                # Create the table
                table = Table(table_data, repeatRows=1)
                
                # Add style to the table
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table)
                
                # Build PDF
                doc.build(elements)
                success_count += 1
            except Exception as e:
                messagebox.showwarning("Warning", f"Failed to export projects to PDF: {e}")
            
            # Export requirements
            requirements_file = os.path.join(directory, "requirements_export.pdf")
            try:
                # Get requirements data
                cur.execute("""
                    SELECT p.project_name, r.requirement_name, r.requirement_type, r.status, r.description
                    FROM requirements r
                    JOIN projects p ON r.project_id = p.id
                    ORDER BY p.project_name, r.requirement_name
                """)
                requirements = cur.fetchall()
                
                # Create PDF
                doc = SimpleDocTemplate(requirements_file, pagesize=letter)
                styles = getSampleStyleSheet()
                elements = []
                
                # Add title
                title = Paragraph("Project Management System - Requirements Report", styles['Title'])
                elements.append(title)
                elements.append(Spacer(1, 20))
                
                # Add date
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                date_paragraph = Paragraph(f"Generated on: {date_str}", styles['Normal'])
                elements.append(date_paragraph)
                elements.append(Spacer(1, 20))
                
                # Create table data
                table_data = [["Project", "Requirement Name", "Type", "Status", "Description"]]
                for req in requirements:
                    # Truncate description
                    desc = req[4][:100] + "..." if len(req[4]) > 100 else req[4]
                    
                    table_data.append([
                        req[0],  # project_name
                        req[1],  # requirement_name
                        req[2],  # requirement_type
                        req[3],  # status
                        desc     # description (truncated)
                    ])
                
                # Create the table
                table = Table(table_data, repeatRows=1)
                
                # Add style to the table
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table)
                
                # Build PDF
                doc.build(elements)
                success_count += 1
            except Exception as e:
                messagebox.showwarning("Warning", f"Failed to export requirements to PDF: {e}")
            
            # Export effort tracking
            effort_file = os.path.join(directory, "effort_export.pdf")
            cur.execute("""
                SELECT p.project_name, r.requirement_name, e.date, 
                       e.requirements_analysis, e.designing, e.coding, 
                       e.testing, e.project_management
                FROM effort_tracking e
                JOIN requirements r ON e.requirement_id = r.id
                JOIN projects p ON r.project_id = p.id
                ORDER BY p.project_name, r.requirement_name, e.date
            """)
            effort = cur.fetchall()
            with open(effort_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Project", "Requirement", "Date", "Requirements Analysis", 
                                "Designing", "Coding", "Testing", "Project Management"])
                writer.writerows(effort)
                
            cur.close()
            conn.close()
            
            self.status_var.set(f"All data exported successfully to {directory}")
            messagebox.showinfo("Success", f"All data exported successfully to {directory}!")
        except Exception as e:
            self.status_var.set(f"Error exporting data: {e}")
            messagebox.showerror("Error", f"Failed to export all data: {e} ({success_count} files were exported successfully)")
    
    # Original CSV export methods
    def export_projects_csv(self):
        # Get file path from user
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Projects"
        )
        if not file_path:
            return
            
        try:
            # Get project data
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT project_name, owner, project_description, project_scope, target_users, technology_stack, platform FROM projects ORDER BY project_name")
            projects = cur.fetchall()
            cur.close()
            conn.close()
            
            # Write to CSV
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Project Name", "Owner", "Description", "Scope", "Target Users", "Technology Stack", "Platform"])
                writer.writerows(projects)
                
            self.status_var.set(f"Projects exported successfully to {os.path.basename(file_path)}")
            messagebox.showinfo("Success", "Projects exported successfully!")
        except Exception as e:
            self.status_var.set(f"Error exporting projects: {e}")
            messagebox.showerror("Error", f"Failed to export projects: {e}")
            
    def export_requirements_csv(self):
        # Get file path from user
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Requirements"
        )
        if not file_path:
            return
            
        try:
            # Get requirements data
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT p.project_name, r.requirement_name, r.requirement_type, r.status, r.description
                FROM requirements r
                JOIN projects p ON r.project_id = p.id
                ORDER BY p.project_name, r.requirement_name
            """)
            requirements = cur.fetchall()
            cur.close()
            conn.close()
            
            # Write to CSV
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Project", "Requirement Name", "Type", "Status", "Description"])
                writer.writerows(requirements)
                
            self.status_var.set(f"Requirements exported successfully to {os.path.basename(file_path)}")
            messagebox.showinfo("Success", "Requirements exported successfully!")
        except Exception as e:
            self.status_var.set(f"Error exporting requirements: {e}")
            messagebox.showerror("Error", f"Failed to export requirements: {e}")
            
    def export_effort_csv(self):
        # Get file path from user
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Effort Tracking"
        )
        if not file_path:
            return
            
        try:
            # Get effort tracking data
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT p.project_name, r.requirement_name, e.date, 
                       e.requirements_analysis, e.designing, e.coding, 
                       e.testing, e.project_management
                FROM effort_tracking e
                JOIN requirements r ON e.requirement_id = r.id
                JOIN projects p ON r.project_id = p.id
                ORDER BY p.project_name, r.requirement_name, e.date
            """)
            effort = cur.fetchall()
            cur.close()
            conn.close()
            
            # Write to CSV
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Project", "Requirement", "Date", "Requirements Analysis", 
                                "Designing", "Coding", "Testing", "Project Management"])
                writer.writerows(effort)
                
            self.status_var.set(f"Effort tracking data exported successfully to {os.path.basename(file_path)}")
            messagebox.showinfo("Success", "Effort tracking data exported successfully!")
        except Exception as e:
            self.status_var.set(f"Error exporting effort tracking data: {e}")
            messagebox.showerror("Error", f"Failed to export effort tracking data: {e}")
            
    def export_all_csv(self):
        # Get directory from user
        directory = filedialog.askdirectory(title="Select Export Directory")
        if not directory:
            return
            
        success_count = 0
        try:
            # Export projects
            projects_file = os.path.join(directory, "projects_export.csv")
            conn = connect_db()
            cur = conn.cursor()
            
            # Export projects
            cur.execute("SELECT project_name, owner, project_description, project_scope, target_users, technology_stack, platform FROM projects ORDER BY project_name")
            projects = cur.fetchall()
            with open(projects_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Project Name", "Owner", "Description", "Scope", "Target Users", "Technology Stack", "Platform"])
                writer.writerows(projects)
            success_count += 1
            
            # Export requirements
            requirements_file = os.path.join(directory, "requirements_export.csv")
            cur.execute("""
                SELECT p.project_name, r.requirement_name, r.requirement_type, r.status, r.description
                FROM requirements r
                JOIN projects p ON r.project_id = p.id
                ORDER BY p.project_name, r.requirement_name
            """)
            requirements = cur.fetchall()
            with open(requirements_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Project", "Requirement Name", "Type", "Status", "Description"])
                writer.writerows(requirements)
            success_count += 1
            
            # Export effort tracking
            effort_file = os.path.join(directory, "effort_export.csv")
            cur.execute("""
                SELECT p.project_name, r.requirement_name, e.date, 
                       e.requirements_analysis, e.designing, e.coding, 
                       e.testing, e.project_management
                FROM effort_tracking e
                JOIN requirements r ON e.requirement_id = r.id
                JOIN projects p ON r.project_id = p.id
                ORDER BY p.project_name, r.requirement_name, e.date
            """)
            effort = cur.fetchall()
            with open(effort_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Project", "Requirement", "Date", "Requirements Analysis", 
                                "Designing", "Coding", "Testing", "Project Management"])
                writer.writerows(effort)
            success_count += 1
            
            # Export risks
            risks_file = os.path.join(directory, "risks_export.csv")
            cur.execute("""
                SELECT p.project_name, r.name, r.description, r.risk_status
                FROM risks r
                JOIN projects p ON r.project_id = p.id
                ORDER BY p.project_name, r.name
            """)
            risks = cur.fetchall()
            with open(risks_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Project", "Risk Name", "Description", "Status"])
                writer.writerows(risks)
            success_count += 1
            
            cur.close()
            conn.close()
            
            self.status_var.set(f"All data exported successfully to {directory}")
            messagebox.showinfo("Success", f"All data exported successfully to {directory}!")
        except Exception as e:
            self.status_var.set(f"Error exporting data: {e}")
            messagebox.showerror("Error", f"Failed to export all data: {e} ({success_count} files were exported successfully)")


# === PROJECT MANAGEMENT GUI ===

class ProjectManagementApp:
    def __init__(self, root):
        self.root = root
        
        # Get the current user information
        global current_user
        self.current_user = current_user if 'current_user' in globals() else {"id": None, "username": "Guest", "role": "Guest"}
        
        # Set window title with user info if not a guest
        if self.current_user["role"] != "Guest":
            self.root.title(f"Project Management System - {self.current_user['username']} ({self.current_user['role']})")
        else:
            self.root.title("Project Management System")
        
        # Create a notebook widget to hold multiple tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        # Projects Tab
        self.projects_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.projects_tab, text="Projects")
        self.setup_projects_tab()

        # Team Members Tab
        self.team_tab = TeamMembersTab(self.notebook)
        self.notebook.add(self.team_tab.frame, text="Team")

        # Risks Tab
        self.risks_tab = RisksTab(self.notebook)
        self.notebook.add(self.risks_tab.frame, text="Risks")

        # Effort Tracking & Monitoring Tab (must be created first)
        self.effort_tab = EffortTrackingTab(self.notebook)

        # Requirements Tab (pass reference to effort_tab)
        self.requirements_tab = RequirementsTab(self.notebook, self.effort_tab)

        # Add to notebook
        self.notebook.add(self.requirements_tab.frame, text="Requirements")
        self.notebook.add(self.effort_tab.frame, text="Effort Tracking")
        
        # Exports Tab
        self.exports_tab = ExportsTab(self.notebook)
        self.notebook.add(self.exports_tab.frame, text="Exports")
        
        # User Profile Tab - only show if logged in
        if self.current_user["id"] is not None:
            self.user_profile_tab = ttk.Frame(self.notebook)
            self.notebook.add(self.user_profile_tab, text="My Profile")
            self.setup_user_profile_tab()
        
        # Add tab change event handler to preserve content
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Dictionary to track if a tab has been visited
        self.tab_visited = {i: False for i in range(self.notebook.index('end'))}
        # Mark first tab as visited
        self.tab_visited[0] = True
    
    def on_tab_changed(self, event):
        """Handle tab changes and ensure content is preserved"""
        current_tab = self.notebook.index(self.notebook.select())
        
        # If this is the first visit to this tab, mark it as visited
        if not self.tab_visited.get(current_tab, False):
            self.tab_visited[current_tab] = True
            
            # Force a refresh of the tab content based on which tab it is
            if current_tab == 1:  # Team tab
                if hasattr(self.team_tab, 'project_combo') and self.team_tab.project_combo.get():
                    self.team_tab.load_team_members()
            elif current_tab == 2:  # Risks tab
                if hasattr(self.risks_tab, 'project_combo') and self.risks_tab.project_combo.get():
                    self.risks_tab.load_risks()
            elif current_tab == 3:  # Requirements tab
                if hasattr(self.requirements_tab, 'project_combo') and self.requirements_tab.project_combo.get():
                    self.requirements_tab.load_requirements()
            elif current_tab == 4:  # Effort Tracking tab
                if hasattr(self.effort_tab, 'project_combo') and self.effort_tab.project_combo.get():
                    if hasattr(self.effort_tab, 'req_combo') and self.effort_tab.req_combo.get():
                        self.effort_tab.load_effort_entries()
        
        # For specific tabs that need extra handling on every visit
        if current_tab == 2 and hasattr(self.risks_tab, 'risk_notebook'):  # Risks tab with internal notebook
            selected_risk_tab = self.risks_tab.risk_notebook.index(self.risks_tab.risk_notebook.select())
            if selected_risk_tab == 1:  # Matrix tab
                self.risks_tab.sync_project_dropdowns()
    
    def setup_user_profile_tab(self):
        """Set up the user profile tab"""
        frame = ttk.Frame(self.user_profile_tab, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # User info section
        info_frame = ttk.LabelFrame(frame, text="User Information", padding="10")
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text="Username:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text=self.current_user["username"]).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(info_frame, text="Role:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text=self.current_user["role"]).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Change password section
        if self.current_user["id"] is not None:
            pwd_frame = ttk.LabelFrame(frame, text="Change Password", padding="10")
            pwd_frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(pwd_frame, text="Current Password:").grid(row=0, column=0, sticky=tk.W, pady=5)
            current_pwd_entry = ttk.Entry(pwd_frame, width=30, show="*")
            current_pwd_entry.grid(row=0, column=1, padx=5, pady=5)
            
            ttk.Label(pwd_frame, text="New Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
            new_pwd_entry = ttk.Entry(pwd_frame, width=30, show="*")
            new_pwd_entry.grid(row=1, column=1, padx=5, pady=5)
            
            ttk.Label(pwd_frame, text="Confirm Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
            confirm_pwd_entry = ttk.Entry(pwd_frame, width=30, show="*")
            confirm_pwd_entry.grid(row=2, column=1, padx=5, pady=5)
            
            # Status label
            status_var = tk.StringVar()
            status_label = ttk.Label(pwd_frame, textvariable=status_var, foreground="red")
            status_label.grid(row=3, column=0, columnspan=2, pady=5)
            
            def change_password():
                current = current_pwd_entry.get()
                new = new_pwd_entry.get()
                confirm = confirm_pwd_entry.get()
                
                if not current or not new or not confirm:
                    status_var.set("All fields are required")
                    return
                    
                if new != confirm:
                    status_var.set("New passwords do not match")
                    return
                    
                if len(new) < 6:
                    status_var.set("Password must be at least 6 characters")
                    return
                
                try:
                    # Verify current password
                    current_hash = hashlib.sha256(current.encode()).hexdigest()
                    new_hash = hashlib.sha256(new.encode()).hexdigest()
                    
                    conn = connect_db()
                    cur = conn.cursor()
                    
                    cur.execute("""
                        SELECT COUNT(*) FROM users 
                        WHERE id = %s AND password_hash = %s
                    """, (self.current_user["id"], current_hash))
                    
                    if cur.fetchone()[0] == 0:
                        status_var.set("Current password is incorrect")
                        cur.close()
                        conn.close()
                        return
                    
                    # Update password
                    cur.execute("""
                        UPDATE users 
                        SET password_hash = %s
                        WHERE id = %s
                    """, (new_hash, self.current_user["id"]))
                    
                    conn.commit()
                    cur.close()
                    conn.close()
                    
                    # Clear entries
                    current_pwd_entry.delete(0, tk.END)
                    new_pwd_entry.delete(0, tk.END)
                    confirm_pwd_entry.delete(0, tk.END)
                    
                    status_var.set("Password changed successfully")
                except Exception as e:
                    status_var.set(f"Error: {e}")
            
            ttk.Button(pwd_frame, text="Change Password", command=change_password).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Logout button
        ttk.Button(frame, text="Logout", command=self.logout).pack(pady=20)
    
    def logout(self):
        """Log out the current user"""
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.root.destroy()
            
            # Show login window again
            login_root = tk.Tk()
            login_window = LoginWindow(login_root, lambda user_id, username, role: on_login_success(user_id, username, role))
            login_root.mainloop()

    def setup_projects_tab(self):
        # UI for Projects tab 

        # Instructional label at the top
        tk.Label(self.projects_tab, text="Please fill in all fields. Use commas to separate multiple items.",
        font=('Segoe UI', 9, 'italic'), foreground="gray").grid(row=0, column=0, columnspan=2, padx=10, pady=(15, 12), sticky='w')

        # Project Name
        tk.Label(self.projects_tab, text="Project Name").grid(row=1, column=0, padx=(60,1), pady=(0,12), sticky='ne')
        self.entry_name = tk.Entry(self.projects_tab, width=53)
        self.entry_name.grid(row=1, column=1, padx=(20, 0), sticky='nw')

        # Project Owner
        tk.Label(self.projects_tab, text="Owner").grid(row=2, column=0, padx=10, pady=(0,3), sticky='ne')
        self.entry_owner = tk.Entry(self.projects_tab, width=53)
        self.entry_owner.grid(row=2, column=1, padx=(20, 0), sticky='nw')

        # Project Description 
        tk.Label(self.projects_tab, text="Project Description").grid(row=3, column=0, pady=(7, 55), sticky='ne')
        self.entry_description = tk.Text(self.projects_tab, width=40, height=4)
        self.entry_description.grid(row=3, column=1, padx=(20, 0), pady=(10, 0), sticky='nw')

        # Project Scope
        tk.Label(self.projects_tab, text="Project Scope").grid(row=4, column=0, padx=10, pady=(7,55), sticky='ne')
        self.entry_scope = tk.Text(self.projects_tab, width=40, height=4)
        self.entry_scope.grid(row=4, column=1, padx=(20, 0), pady=(10, 0), sticky='nw')

        # Target Users
        tk.Label(self.projects_tab, text="Target Users").grid(row=5, column=0, padx=10, pady=(8, 8), sticky='ne')
        self.entry_users = tk.Entry(self.projects_tab, width=53)
        self.entry_users.grid(row=5, column=1, padx=(0, 0))

        # Technology Stack
        tk.Label(self.projects_tab, text="Technology Stack").grid(row=6, column=0, padx=10, pady=(8, 8), sticky='ne')
        self.entry_stack = tk.Entry(self.projects_tab, width=53)
        self.entry_stack.grid(row=6, column=1, padx=(0, 0))

        # Platform
        tk.Label(self.projects_tab, text="Platform").grid(row=7, column=0, padx=10, pady=(8, 8), sticky='ne')
        self.entry_platform = tk.Entry(self.projects_tab, width=53)
        self.entry_platform.grid(row=7, column=1, padx=(0, 0))

        # Create a frame for buttons and place it at the bottom right
        btn_frame = tk.Frame(self.projects_tab)
        btn_frame.grid(row=11, column=0, columnspan=2, sticky='e', padx=20, pady=10)
        tk.Button(btn_frame, text="Save Project", command=self.save).pack(side="left", padx=(310,10))
        tk.Button(btn_frame, text="View Projects", command=self.view_projects).pack(side="left")

    def save(self):
        # Save new project to the database
        try:
            data = (
                self.entry_name.get(),
                self.entry_owner.get(),
                self.entry_description.get("1.0", tk.END).strip(),
                self.entry_scope.get("1.0", tk.END).strip(),
                self.entry_users.get(),
                self.entry_stack.get(),
                self.entry_platform.get()
            )
            if all(data):
                save_project(data)
                self.refresh_project_lists()
                messagebox.showinfo("Success", "Project saved successfully!")

                # Clear inputs
                for entry in [self.entry_name, self.entry_owner, self.entry_users, self.entry_stack, self.entry_platform]:
                    entry.delete(0, tk.END)
                self.entry_description.delete("1.0", tk.END)
                self.entry_scope.delete("1.0", tk.END)

                # Also reload comboboxes in other tabs
                self.requirements_tab.load_projects()  # refresh combobox
                self.effort_tab.load_projects()

            else:
                messagebox.showwarning("Incomplete Data", "Please fill all fields.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def view_projects(self):
        # Open a new window to view/edit/delete existing projects
        top = tk.Toplevel(self.root)
        top.title("All Projects")

        # TreeView widget to display all project info
        tree = ttk.Treeview(top, columns=("Project Name", "Owner", "Description", "Scope", "Users", "Stack", "Platform"), show='headings')
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.W, stretch=True)
        tree.pack(fill=tk.BOTH, expand=True)

        # Fetch projects from DB and insert into tree
        def refresh_tree():
            for row in tree.get_children():
                tree.delete(row)
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT project_name, owner, project_description, project_scope, target_users,
                       technology_stack, platform
                FROM projects
            """)
            for row in cur.fetchall():
                tree.insert('', tk.END, values=row)
            cur.close()
            conn.close()

        # Delete selected project
        def delete_selected():
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("Select Project", "Please select a project to delete.")
                return
            values = tree.item(selected, 'values')
            project_name = values[0]
            if messagebox.askyesno("Confirm Deletion", f"Delete project '{project_name}'?"):
                try:
                    delete_project(project_name)
                    tree.delete(selected)
                    self.refresh_project_lists()
                    self.effort_tab.load_projects()
                    messagebox.showinfo("Deleted", f"'{project_name}' was deleted.")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")

        # Edit selected project
        def edit_selected():
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("Select Project", "Please select a project to edit.")
                return
            values = tree.item(selected, 'values')

            edit_win = tk.Toplevel(top)
            edit_win.title(f"Edit: {values[0]}")

            # Generate fields for editing
            fields = ["project_name", "owner", "project_description", "project_scope", "target_users",
                       "technology_stack", "platform"]
            entries = []
            for i, field in enumerate(fields):
                tk.Label(edit_win, text=field).grid(row=i, column=0)
                e = tk.Entry(edit_win, width=50)
                e.insert(0, values[i])
                e.grid(row=i, column=1)
                entries.append(e)

            original_name = values[0]

            def save_changes():
                try:
                    updated = (
                        entries[0].get(), entries[1].get(), entries[2].get(), entries[3].get(),
                        entries[4].get(), entries[5].get(), entries[6].get(), original_name
                    )
                    update_project(updated)
                    refresh_tree()
                    messagebox.showinfo("Success", f"'{updated[0]}' updated.")
                    edit_win.destroy()
                    self.requirements_tab.load_projects() 

                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update project: {e}")

            tk.Button(edit_win, text="Save Changes", command=save_changes).grid(row=len(fields), column=0, columnspan=2, pady=10)

        # Buttons below the treeview
        btn_frame = tk.Frame(top)
        btn_frame.pack(fill=tk.X, anchor='se', pady=10, padx=10)
        tk.Button(btn_frame, text="Edit Selected", command=edit_selected).pack(side="right", padx=(5, 0))
        tk.Button(btn_frame, text="Delete Selected", command=delete_selected).pack(side="right")

        refresh_tree()

    def refresh_project_lists(self):
        # Reload all comboboxes in other tabs after saving or deleting a project
        self.team_tab.load_projects()
        self.risks_tab.load_projects()
        self.requirements_tab.load_projects()

# Entry Point 
if __name__ == "__main__":
    try:
        print("Starting Project Management System...")
        print(f"Database settings: {DB_NAME}@{DB_HOST} (user: {DB_USER})")
        
        # Test database connection
        try:
            print("Testing database connection...")
            conn = connect_db()
            print("Database connection successful!")
            conn.close()
        except Exception as e:
            print(f"ERROR: Database connection failed: {e}")
            print("Please make sure the PostgreSQL database is running and accessible.")
            print("You can run setup.bat to set up the database.")
            input("Press Enter to continue anyway (the application might not work properly)...")
        
        root = tk.Tk() # Create main window
        
        # Apply styles if available
        if 'STYLES_AVAILABLE' in globals() and STYLES_AVAILABLE:
            print("Applying custom styles...")
            styles.apply_styles(root)
        
        def on_login_success(user_id, username, role):
            # Create new window for the main application
            app_window = tk.Toplevel()
            app_window.title(f"Project Management System - Logged in as {username} ({role})")
            app_window.geometry("1024x768")
            app_window.protocol("WM_DELETE_WINDOW", root.destroy)  # Close the whole app when the main window is closed
            
            # Store user info
            global current_user
            current_user = {
                "id": user_id,
                "username": username,
                "role": role
            }
            
            # Launch app
            app = ProjectManagementApp(app_window)
            
            # Apply styles to main app if available
            if 'STYLES_AVAILABLE' in globals() and STYLES_AVAILABLE:
                try:
                    style_integration.style_main_app(app)
                except Exception as e:
                    print(f"Warning: Error applying styles to main app: {e}")
        
        # Show login window
        login_window = LoginWindow(root, on_login_success)
        
        # Apply styles to login window if available
        if 'STYLES_AVAILABLE' in globals() and STYLES_AVAILABLE:
            try:
                style_integration.style_login_window(login_window)
            except Exception as e:
                print(f"Warning: Error applying styles to login window: {e}")
        
        # Use this flag for demonstration/testing to skip the login screen
        # Set SKIP_LOGIN to True to automatically skip the login
        SKIP_LOGIN = False  # Don't skip login - show the login screen
        if SKIP_LOGIN:
            print("Debug mode: Skipping login screen")
            login_window.skip_login()
        
        print("Application initialized. Starting main loop...")
        root.mainloop() # Run main loop
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
