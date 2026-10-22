import matplotlib.pyplot as plt
import numpy as np
from Shapes import Shape3D, Torus, Oloid, Square
import tkinter as tk
import scipy

def center_window(window, width, height):

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

first_shape = Torus("Torus", "Purple", 5, 1)
sec_shape = Oloid("Oloid", "Purple", 3)
third_shape = Square("Square", "Purple", 4)
shapes = [first_shape, sec_shape, third_shape]

for shape in shapes:
    print("Shape type: ", shape.get_type())
    print("Shape colour: ", shape.get_col())
    print("Shape volume: ", shape.volume())
    print("Shape surface area: ", shape.surface_area())
    print("-----------------------------")

def spawn_torus():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    first_shape.draw(ax)
    ax.set_title("3D Shape: " + first_shape.get_type())
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('Z-axis')
    ax.set_xticks(np.arange(-5, 6, 1))
    ax.set_yticks(np.arange(-5, 6, 1))
    ax.set_zticks(np.arange(-5, 6, 1))

    plt.show()

def spawn_oloid():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    sec_shape.draw(ax)
    ax.set_title("3D Shape: " + sec_shape.get_type())
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('Z-axis')
    ax.set_xticks(np.arange(-5, 6, 1))
    ax.set_yticks(np.arange(-5, 6, 1))
    ax.set_zticks(np.arange(-5, 6, 1))

    plt.show()

def spawn_square():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    third_shape.draw(ax)
    ax.set_title("3D Shape: " + third_shape.get_type())
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('Z-axis')
    ax.set_xticks(np.arange(-5, 6, 1))
    ax.set_yticks(np.arange(-5, 6, 1))
    ax.set_zticks(np.arange(-5, 6, 1))

    plt.show()

def homescreen():
    window = tk.Tk()
    window.title("3D Shape Viewer")
    center_window(window, 750, 500)
    window.configure(bg="Purple")
    window.resizable(False, False)

    welcome_label = tk.Label(window, text="Choose A Shape:", font=("Times New Roman", 20, "bold"), bg="Purple")
    welcome_label.pack(pady=20)

    buttons_frame = tk.Frame(window, bg="Purple")
    buttons_frame.pack(pady=10)

    torus_button = tk.Button(buttons_frame, text="Torus", command=spawn_torus)
    torus_button.pack(pady=5, padx=7)

    oloid_button = tk.Button(buttons_frame, text="Oloid", command=spawn_oloid)
    oloid_button.pack(pady=5, padx=7)

    square_button = tk.Button(buttons_frame, text="square", command=spawn_square)
    square_button.pack(pady=5, padx=7)
    
    window.mainloop()

homescreen()
