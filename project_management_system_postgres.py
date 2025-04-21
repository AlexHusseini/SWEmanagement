
import tkinter as tk
from tkinter import messagebox, ttk
import psycopg2

DB_NAME = "project_management"
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"

def connect_db():
    return psycopg2.connect(
        dbname=project_management,
        user=postgres,
        password=postgres,
        host=localhost
    )

def save_project(data):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO projects (project_name, owner, team_members, functional_requirements, nonfunctional_requirements, effort_hours, risks)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, data)
    conn.commit()
    cur.close()
    conn.close()

class ProjectManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Management System")

        tk.Label(root, text="Project Name").grid(row=0, column=0)
        self.entry_name = tk.Entry(root)
        self.entry_name.grid(row=0, column=1)

        tk.Label(root, text="Owner").grid(row=1, column=0)
        self.entry_owner = tk.Entry(root)
        self.entry_owner.grid(row=1, column=1)

        tk.Label(root, text="Team Members (comma separated)").grid(row=2, column=0)
        self.entry_team = tk.Entry(root)
        self.entry_team.grid(row=2, column=1)

        tk.Label(root, text="Functional Requirements").grid(row=3, column=0)
        self.entry_func_req = tk.Entry(root)
        self.entry_func_req.grid(row=3, column=1)

        tk.Label(root, text="Non-Functional Requirements").grid(row=4, column=0)
        self.entry_nonfunc_req = tk.Entry(root)
        self.entry_nonfunc_req.grid(row=4, column=1)

        tk.Label(root, text="Effort Hours").grid(row=5, column=0)
        self.entry_effort = tk.Entry(root)
        self.entry_effort.grid(row=5, column=1)

        tk.Label(root, text="Risks").grid(row=6, column=0)
        self.entry_risks = tk.Entry(root)
        self.entry_risks.grid(row=6, column=1)

        tk.Button(root, text="Save Project", command=self.save).grid(row=7, column=0, pady=10)
        tk.Button(root, text="View Projects", command=self.view_projects).grid(row=7, column=1)

    def save(self):
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
            if all(data):
                save_project(data)
                messagebox.showinfo("Success", "Project saved successfully!")
                for entry in [self.entry_name, self.entry_owner, self.entry_team, self.entry_func_req,
                              self.entry_nonfunc_req, self.entry_effort, self.entry_risks]:
                    entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Incomplete Data", "Please fill all fields.")
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
            cur.execute("SELECT project_name, owner, team_members, functional_requirements, nonfunctional_requirements, effort_hours, risks FROM projects")
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
