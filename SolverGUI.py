import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PythonApplication1 import solve
from cvModule import detect_and_crop_grid, detect_galaxy_centers
from i_o import print_solution

class GalaxyCenter:
    def __init__(self, canvas, x, y, r):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.r = r
        self.active = True

        # Draw circle (oval)
        self.circle = canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill="white",
            outline="black",
            width=2
        )

        # Bind click
        canvas.tag_bind(self.circle, "<Button-1>", self.toggle)

        self.update_visual()

    def toggle(self, event=None):
        self.active = not self.active
        self.update_visual()

    def update_visual(self):
        if self.active:
            # fully visible
            self.canvas.itemconfig(self.circle, fill="white")
        else:
            # "semi-transparent" look (gray instead of white)
            self.canvas.itemconfig(self.circle, fill="#cccccc")


def ai_click(width_str=1, height_str=1):

    cols = int(width_str)
    rows = int(height_str)
    
    # Open file dialog
    file_path = filedialog.askopenfilename(
        title="Select Grid Image",
        filetypes=[("PNG Images", "*.png"), ("All Files", "*.*")]
    )

    # User canceled
    if not file_path:
        print("No file selected.")
        return

    # Run your CV algorithm
    cropped, error = detect_and_crop_grid(file_path, rows, cols)

    if error:
        messagebox.showerror("Error", error)
        return

    print("Grid detected and cropped successfully.")
    theCenters = detect_galaxy_centers(cropped, rows, cols)
    solution, *_ = solve(cols, rows, theCenters)
    print_solution(cols, rows, solution)
    return

def on_click( width_str=1, height_str=1):
    cols = int(width_str)
    rows = int(height_str)

    cell_size = 40
    gc_radius = 5

    # Create new window
    win = tk.Toplevel()
    win.title("Galaxy Editor")

    # Title label
    tk.Label(win, text="Galaxy Grid: place galaxy centers here").pack(pady=5)

    canvas_width = cols * cell_size
    canvas_height = rows * cell_size

    canvas = tk.Canvas(win, width=canvas_width+2, height=canvas_height+2)
    canvas.pack()

    # Draw grid
    for i in range(rows + 2):
        y = i * cell_size + 1.5
        canvas.create_line(1.5, y, canvas_width+1.5, y)

    for j in range(cols + 2):
        x = j * cell_size + 1.5
        canvas.create_line(x, 1.5, x, canvas_height + 1.5)

    # Create GalaxyCenters grid
    gc_rows = 2 * rows - 1
    gc_cols = 2 * cols - 1

    galaxy_centers = [[None for _ in range(gc_cols)] for _ in range(gc_rows)]

    for i in range(gc_rows):
        for j in range(gc_cols):
            # Position mapping:
            # even index => cell center
            # odd index => edge/intersection
            x = (j + 1) * (cell_size / 2)
            y = (i + 1) * (cell_size / 2)

            gc = GalaxyCenter(canvas, x, y, gc_radius)
            gc.toggle()
            galaxy_centers[i][j] = gc


    def solveButtonFunction():
        active_centers = []

        for i in range(gc_rows):
            for j in range(gc_cols):
                gc = galaxy_centers[i][j]
                if gc.active:
                    # Convert matrix indices -> (x, y)
                    x = j
                    y = i
                    active_centers.append((y, x))

        solution, *_ = solve(cols, rows, active_centers)
        print_solution(cols, rows, solution)

    # Optional: store on window for later use
    win.galaxy_centers = galaxy_centers

    # Solve button
    solve_button = tk.Button(win, text="Solve", command=solveButtonFunction)
    solve_button.pack(pady=10)



if __name__ == '__main__':
    # Create main window
    root = tk.Tk()
    root.title("Simple Tkinter App")
    root.geometry("300x200")

    # Top label
    title_label = tk.Label(root, text="Enter grid dimensions Below:")
    title_label.pack(pady=10)

    # First input set
    frame1 = tk.Frame(root)
    frame1.pack(pady=5)

    label1 = tk.Label(frame1, text="Width:")
    label1.pack(side="left", padx=5)

    widthEntry = tk.Entry(frame1)
    widthEntry.pack(side="left")

    # Second input set
    frame2 = tk.Frame(root)
    frame2.pack(pady=5)

    label2 = tk.Label(frame2, text="Height:")
    label2.pack(side="left", padx=5)

    heightEntry = tk.Entry(frame2)
    heightEntry.pack(side="left")

    frame3 = tk.Frame(root)
    frame3.pack(pady=5)
    # Buttons
    button1 = tk.Button(frame3, text="Submit",
                       command=lambda: on_click(widthEntry.get(), heightEntry.get()))
    button1.pack(side="left", padx=5)

    button2 = tk.Button(frame3, text="use AI",
                       command=lambda: ai_click(widthEntry.get(), heightEntry.get()))
    button2.pack(side="left")


    # Run the app
    root.mainloop()




