import customtkinter as ctk
import math

# Configure CustomTkinter appearance (opcional, mas recomendado)
ctk.set_appearance_mode("Dark")  # "Dark", "Light", ou "System"
ctk.set_default_color_theme("green")  # "blue", "green", "dark-blue"


num = 0

def command():
    global num
    num += 1
    botao.configure(text=f"Cliques: {num}")
    label.configure(text=f"""{math.sqrt(num):.5f} {math.pow(num, 2)}""")

janela = ctk.CTk()
janela.title("Minha Janela CustomTkinter")

janela.grid_columnconfigure(0, weight=1)
janela.grid_rowconfigure(0, weight=1)
janela.grid_rowconfigure(1, weight=1)
janela.grid_rowconfigure(2, weight=1)

label = ctk.CTkLabel(master=janela, text="raizes quadradas", font=("Ubuntu Mono", 50))
label.grid(column=0, row=0, padx=20, pady=20, sticky="nsew")
botao = ctk.CTkButton(master=janela, text="Clique Aqui", font=("Ubuntu Mono", 30), command=command, corner_radius=10)
botao.grid(column=0, row=2, padx=20, pady=20, sticky="nsew")


janela.update()
janela.geometry("800x600")
janela.mainloop()