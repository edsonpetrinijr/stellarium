import tkinter as tk
from tkinter import messagebox

from utils.conversions import *

def open_input_window():
    def on_submit():
        # try:
        print(entry_ra.get())
        print(entry_dec.get())
        # ra = ra_to_deg(entry_ra.get())
        # dec = dec_to_deg(entry_dec.get())
        # print(ra,dec)
        # move_to_ra_dec(ra, dec)

        # except ValueError:
        #     messagebox.showerror("Entrada inválida", "Use valores numéricos para RA e Dec.")

    window = tk.Tk()
    window.title("Mover para RA/Dec")

    tk.Label(window, text="RA (0-360°):").grid(row=0, column=0, padx=10, pady=5)
    entry_ra = tk.Entry(window)
    entry_ra.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(window, text="Dec (-90° a 90°):").grid(row=1, column=0, padx=10, pady=5)
    entry_dec = tk.Entry(window)
    entry_dec.grid(row=1, column=1, padx=10, pady=5)

    submit_btn = tk.Button(window, text="Mover", command=on_submit)
    submit_btn.grid(row=2, column=0, columnspan=2, pady=10)

    window.mainloop()