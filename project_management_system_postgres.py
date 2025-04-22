import tkinter as tk
from tkinter import messagebox, ttk
import psycopg2
from datetime import datetime

DB_NAME = "project_management"
DB_USER = "postgres"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"

def connect_db():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )

def save_project(data):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO projects (name, owner, team_members, functional_requirements, nonfunctional_requirements, effort_hours, risks)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, data)
    conn.commit()
    cur.close()
    conn.close()

class RequirementsTab:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create project selection frame
        self.create_project_selection()
        
        # Create buttons frame
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(fill=tk.X, pady=10)
        
        # Add buttons
        self.add_btn = ttk.Button(self.buttons_frame, text="Add Requirement", command=self.show_add_requirement_dialog, state=tk.DISABLED)
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_btn = ttk.Button(self.buttons_frame, text="Edit Requirement", command=self.show_edit_requirement_dialog, state=tk.DISABLED)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(self.buttons_frame, text="Delete Requirement", command=self.delete_requirement, state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Create requirements treeview
        self.create_requirements_treeview()
        
    def create_project_selection(self):
        # Create frame
        frame = ttk.Frame(self.main_frame)
        frame.pack(fill=tk.X)
        
        # Add label
        ttk.Label(frame, text="Select Project:").pack(side=tk.LEFT, padx=5)
        
        # Add combobox
        self.project_combo = ttk.Combobox(frame, width=40, state="readonly")
        self.project_combo.pack(side=tk.LEFT, padx=5)
        
        # Bind event
        self.project_combo.bind("<<ComboboxSelected>>", self.on_project_selected)
        
        # Load projects
        self.load_projects()
        
    def load_projects(self):
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM projects ORDER BY name")
            projects = cur.fetchall()
            cur.close()
            conn.close()
            
            self.projects = {p[1]: p[0] for p in projects}
            self.project_combo['values'] = list(self.projects.keys())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load projects: {e}")
        
    def on_project_selected(self, event):
        selected_project = self.project_combo.get()
        if selected_project:
            self.current_project_id = self.projects[selected_project]
            self.load_requirements()
            self.add_btn['state'] = tk.NORMAL
        else:
            self.current_project_id = None
            self.add_btn['state'] = tk.DISABLED
            self.edit_btn['state'] = tk.DISABLED
            self.delete_btn['state'] = tk.DISABLED
        
    def create_requirements_treeview(self):
        # Create treeview frame
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        self.tree = ttk.Treeview(tree_frame, columns=("name", "type", "status"), show="headings")
        self.tree.heading("name", text="Requirement Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("status", text="Status")
        
        # Set column widths
        self.tree.column("name", width=300)
        self.tree.column("type", width=150)
        self.tree.column("status", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_requirement_selected)
        
    def on_requirement_selected(self, event):
        selected = self.tree.selection()
        if selected:
            self.edit_btn['state'] = tk.NORMAL
            self.delete_btn['state'] = tk.NORMAL
        else:
            self.edit_btn['state'] = tk.DISABLED
            self.delete_btn['state'] = tk.DISABLED
        
    def load_requirements(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not hasattr(self, 'current_project_id'):
            return
            
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, requirement_name, requirement_type, status 
                FROM requirements 
                WHERE project_id = %s 
                ORDER BY requirement_name
            """, (self.current_project_id,))
            requirements = cur.fetchall()
            cur.close()
            conn.close()
            
            for req in requirements:
                self.tree.insert("", tk.END, values=(req[1], req[2], req[3]), tags=(req[0],))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load requirements: {e}")
            
    def show_add_requirement_dialog(self):
        if not hasattr(self, 'current_project_id'):
            messagebox.showwarning("Warning", "Please select a project first")
            return
            
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Requirement")
        dialog.geometry("500x400")
        dialog.grab_set()  # Make dialog modal
        
        # Create form
        ttk.Label(dialog, text="Requirement Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Type:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        type_combo = ttk.Combobox(dialog, width=20, values=["functional", "non-functional"], state="readonly")
        type_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        type_combo.current(0)
        
        ttk.Label(dialog, text="Status:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        status_combo = ttk.Combobox(dialog, width=20, values=["pending", "in progress", "completed", "rejected"], state="readonly")
        status_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        status_combo.current(0)
        
        ttk.Label(dialog, text="Description:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        desc_text = tk.Text(dialog, width=40, height=10)
        desc_text.grid(row=3, column=1, padx=5, pady=5)
        
        def save_requirement():
            name = name_entry.get()
            req_type = type_combo.get()
            status = status_combo.get()
            description = desc_text.get("1.0", tk.END).strip()
            
            if not name:
                messagebox.showerror("Error", "Requirement name is required")
                return
                
            try:
                conn = connect_db()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO requirements (project_id, requirement_name, description, requirement_type, status)
                    VALUES (%s, %s, %s, %s, %s)
                """, (self.current_project_id, name, description, req_type, status))
                conn.commit()
                cur.close()
                conn.close()
                self.load_requirements()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save requirement: {e}")
            
        ttk.Button(dialog, text="Save", command=save_requirement).grid(row=4, column=1, pady=10)
        
    def show_edit_requirement_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a requirement to edit")
            return
            
        requirement_id = self.tree.item(selected[0])["tags"][0]
        
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT requirement_name, description, requirement_type, status 
                FROM requirements 
                WHERE id = %s
            """, (requirement_id,))
            requirement = cur.fetchone()
            cur.close()
            conn.close()
            
            dialog = tk.Toplevel(self.parent)
            dialog.title("Edit Requirement")
            dialog.geometry("500x400")
            dialog.grab_set()
            
            ttk.Label(dialog, text="Requirement Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            name_entry = ttk.Entry(dialog, width=40)
            name_entry.insert(0, requirement[0])
            name_entry.grid(row=0, column=1, padx=5, pady=5)
            
            ttk.Label(dialog, text="Type:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            type_combo = ttk.Combobox(dialog, width=20, values=["functional", "non-functional"], state="readonly")
            type_combo.set(requirement[2])
            type_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
            
            ttk.Label(dialog, text="Status:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            status_combo = ttk.Combobox(dialog, width=20, values=["pending", "in progress", "completed", "rejected"], state="readonly")
            status_combo.set(requirement[3])
            status_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
            
            ttk.Label(dialog, text="Description:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
            desc_text = tk.Text(dialog, width=40, height=10)
            desc_text.insert("1.0", requirement[1] or "")
            desc_text.grid(row=3, column=1, padx=5, pady=5)
            
            def save_changes():
                name = name_entry.get()
                req_type = type_combo.get()
                status = status_combo.get()
                description = desc_text.get("1.0", tk.END).strip()
                
                if not name:
                    messagebox.showerror("Error", "Requirement name is required")
                    return
                    
                try:
                    conn = connect_db()
                    cur = conn.cursor()
                    cur.execute("""
                        UPDATE requirements 
                        SET requirement_name = %s, description = %s, requirement_type = %s, status = %s, 
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (name, description, req_type, status, requirement_id))
                    conn.commit()
                    cur.close()
                    conn.close()
                    self.load_requirements()
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update requirement: {e}")
                
            ttk.Button(dialog, text="Save Changes", command=save_changes).grid(row=4, column=1, pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load requirement details: {e}")
        
    def delete_requirement(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a requirement to delete")
            return
            
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this requirement?"):
            return
            
        requirement_id = self.tree.item(selected[0])["tags"][0]
        
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM requirements WHERE id = %s", (requirement_id,))
            conn.commit()
            cur.close()
            conn.close()
            self.load_requirements()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete requirement: {e}")

class ProjectManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Management System")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Projects Tab
        self.projects_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.projects_tab, text="Projects")
        self.setup_projects_tab()
        
        # Requirements Tab
        self.requirements_tab = RequirementsTab(self.notebook)
        self.notebook.add(self.requirements_tab.main_frame, text="Requirements")

    def setup_projects_tab(self):
        tk.Label(self.projects_tab, text="Project Name").grid(row=0, column=0)
        self.entry_name = tk.Entry(self.projects_tab)
        self.entry_name.grid(row=0, column=1)

        tk.Label(self.projects_tab, text="Owner").grid(row=1, column=0)
        self.entry_owner = tk.Entry(self.projects_tab)
        self.entry_owner.grid(row=1, column=1)

        tk.Label(self.projects_tab, text="Team Members (comma separated)").grid(row=2, column=0)
        self.entry_team = tk.Entry(self.projects_tab)
        self.entry_team.grid(row=2, column=1)

        tk.Label(self.projects_tab, text="Functional Requirements").grid(row=3, column=0)
        self.entry_func_req = tk.Entry(self.projects_tab)
        self.entry_func_req.grid(row=3, column=1)

        tk.Label(self.projects_tab, text="Non-Functional Requirements").grid(row=4, column=0)
        self.entry_nonfunc_req = tk.Entry(self.projects_tab)
        self.entry_nonfunc_req.grid(row=4, column=1)

        tk.Label(self.projects_tab, text="Effort Hours").grid(row=5, column=0)
        self.entry_effort = tk.Entry(self.projects_tab)
        self.entry_effort.grid(row=5, column=1)

        tk.Label(self.projects_tab, text="Risks").grid(row=6, column=0)
        self.entry_risks = tk.Entry(self.projects_tab)
        self.entry_risks.grid(row=6, column=1)

        tk.Button(self.projects_tab, text="Save Project", command=self.save_project).grid(row=7, column=0, pady=10)
        tk.Button(self.projects_tab, text="View Projects", command=self.view_projects).grid(row=7, column=1)

    def save_project(self):
        try:
            data = (
                self.entry_name.get(),
                self.entry_owner.get(),
                self.entry_team.get(),
                self.entry_func_req.get(),
                self.entry_nonfunc_req.get(),
                int(self.entry_effort.get()),
                self.entry_risks.get()
            )
            if all(str(x).strip() for x in data):
                conn = connect_db()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO projects (name, owner, team_members, functional_requirements, 
                                        nonfunctional_requirements, effort_hours, risks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, data)
                conn.commit()
                cur.close()
                conn.close()
                
                messagebox.showinfo("Success", "Project saved successfully!")
                
                # Clear form
                for entry in [self.entry_name, self.entry_owner, self.entry_team, self.entry_func_req,
                            self.entry_nonfunc_req, self.entry_effort, self.entry_risks]:
                    entry.delete(0, tk.END)
                    
                # Refresh requirements tab project list
                self.requirements_tab.load_projects()
            else:
                messagebox.showwarning("Incomplete Data", "Please fill all fields.")
        except ValueError:
            messagebox.showerror("Error", "Effort hours must be a number")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def view_projects(self):
        top = tk.Toplevel(self.root)
        top.title("All Projects")

        tree = ttk.Treeview(top, columns=("Project Name", "Owner", "Team", "Functional", "Non-Functional", "Effort", "Risks"), show='headings')
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.pack(fill=tk.BOTH, expand=True)

        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT name, owner, team_members, functional_requirements, 
                       nonfunctional_requirements, effort_hours, risks 
                FROM projects
            """)
            rows = cur.fetchall()
            for row in rows:
                tree.insert('', tk.END, values=row)
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectManagementApp(root)
    root.mainloop()
