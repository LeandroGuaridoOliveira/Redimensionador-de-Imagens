import tkinter as tk
from tkinter import messagebox, filedialog, Listbox, font, END
from PIL import Image, UnidentifiedImageError
import os
import logging
import zipfile
import subprocess
import sys


# cria pasta de logs, se não existir
os.makedirs("logs", exist_ok=True)

# define o diretório de saída onde imagens processadas serão salvas
output_dir = r"C:\Automação Fotos IA\images\imagens redimensionadas"
os.makedirs(output_dir, exist_ok=True)

# configura o log para registrar informações e erros
logging.basicConfig(
    filename="logs/automacao.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# define os tamanhos de redimensionamento desejados
tamanhos = {
    "grande": (500, 500),
    "pequena": (260, 240)
}
webp_quality = 100  # Qualidade da imagem WebP (máxima)

# lista global para armazenar caminhos dos arquivos selecionados
selected_files = []


# abre o seletor de arquivos para escolher imagens(evita duplicatas na lista)
    
def select_images():
    
    files = filedialog.askopenfilenames(
        title="Selecione as imagens",
        filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.webp")]
    )
    if files:
        novos = 0
        repetidos = []
        nomes_atuais = [os.path.basename(x) for x in selected_files]

        for f in files:
            nome = os.path.basename(f)
            if nome not in nomes_atuais:
                selected_files.append(f)
                listbox.insert(END, nome)
                novos += 1
            else:
                repetidos.append(nome)

        if repetidos:
            messagebox.showwarning("Aviso", "Os arquivos já estavam na lista:\n\n" + "\n".join(repetidos))

        if not novos:
            zip_button.config(state="disabled")
    else:
        # Nenhum arquivo selecionado e lista vazia → desativa o botao de extrair o ZIP
        if not selected_files:
            listbox.delete(0, END)
            zip_button.config(state="disabled")


# remove imagem da lista ao dar duplo clique.
def on_double_click(event):

    selection = listbox.curselection()
    if selection:
        idx = selection[0]
        nome = listbox.get(idx)
        listbox.delete(idx)

        # remove da lista de arquivos selecionados
        for i, f in enumerate(selected_files):
            if os.path.basename(f) == nome:
                del selected_files[i]
                break

        if not selected_files:
            zip_button.config(state="disabled")

# processa cada imagem selecionada, redimensionando e salvando em pastas separadas.

def process_images():
    if not selected_files:
        messagebox.showwarning("Aviso", "Nenhuma imagem selecionada para redimensionar")
        return

    try:
        import shutil
        if os.path.exists(output_dir):
            try:
                shutil.rmtree(output_dir)
            except Exception as e:
                logging.error(f"Erro ao limpar pasta de saída: {e}")
                messagebox.showerror("Erro", f"Feche a pasta de destino e tente novamente.{e}")
                return
        os.makedirs(output_dir, exist_ok=True)

        processed = []

        for idx, image_path in enumerate(selected_files):
            nome_arquivo = os.path.basename(image_path)
            nome_produto = os.path.splitext(nome_arquivo)[0]
            pasta_produto = os.path.join(output_dir, nome_produto)
            os.makedirs(pasta_produto, exist_ok=True)

            try:
                with Image.open(image_path) as img:
                    img.verify()  # Verifica se é uma imagem válida
                with Image.open(image_path) as img:
                    for nome_tamanho, tamanho in tamanhos.items():
                        img_copia = img.copy()
                        img_copia.thumbnail(tamanho, Image.LANCZOS)
                        fundo = Image.new("RGB", tamanho, (255, 255, 255))
                        x = (tamanho[0] - img_copia.width) // 2
                        y = (tamanho[1] - img_copia.height) // 2

                        if img_copia.mode in ("RGBA", "LA"):
                            fundo.paste(img_copia, (x, y), img_copia)
                        else:
                            fundo.paste(img_copia, (x, y))

                        webp_nome_arquivo = f"{nome_produto}_{nome_tamanho}.webp"
                        webp_path = os.path.join(pasta_produto, webp_nome_arquivo)
                        fundo.save(webp_path, "WEBP", quality=webp_quality, method=6)

                processed.append(nome_arquivo)
                logging.info(f"Imagem processada: {nome_arquivo} (Produto: {nome_produto})")
                root.title(f"Processando ({idx + 1}/{len(selected_files)})...")
            except UnidentifiedImageError:
                logging.error(f"Arquivo inválido ou corrompido: {nome_arquivo}")
            except Exception as e:
                logging.error(f"Erro ao processar '{nome_arquivo}': {e}")

        messagebox.showinfo("Sucesso", "Todas as imagens foram redimensionadas com sucesso!")
        listbox.delete(0, END)
        for item in processed:
            listbox.insert(END, item)
        if processed:
            zip_button.config(state="normal")
        root.title("Redimensionador de Imagens")
    except Exception as e:
        logging.critical(f"Erro inesperado: {e}", exc_info=True)
        messagebox.showerror("Erro crítico", f"Ocorreu um erro inesperado:{e}")


def download_zip():
    zip_path = filedialog.asksaveasfilename(
        defaultextension=".zip",
        filetypes=[("Arquivo ZIP", "*.zip")],
        title="Salvar imagens em um arquivo ZIP"
    )
    if not zip_path:
        return

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_dir)
                zipf.write(file_path, arcname)

    messagebox.showinfo("Download", f"Imagens salvas em: {zip_path}")

# o "!" abre o log)
def open_log():
    log_path = os.path.abspath("logs/automacao.log")
    if os.path.exists(log_path):
        if sys.platform == "win32":
            os.startfile(log_path)
        elif sys.platform == "darwin":
            subprocess.call(["open", log_path])
        else:
            subprocess.call(["xdg-open", log_path])
    else:
        messagebox.showinfo("Log", "Arquivo de log não encontrado.")


#Apaga as imagens que foram upadas
def clear_all():
    selected_files.clear()
    listbox.delete(0, END)
    zip_button.config(state="disabled")

"""
        INTERFACE GUI

"""

# Janela principal
root = tk.Tk()
root.title("Redimensionador de Imagens")
root.geometry("520x500")
root.configure(bg="#f0f0f0")

# Estilos de fonte
title_font = font.Font(family="Helvetica", size=18, weight="bold")
section_font = font.Font(family="Helvetica", size=12, weight="bold")

# Título da aplicação
tk.Label(root, text="Redimensionador de Imagens IA", font=title_font, bg="#f0f0f0", fg="#333").pack(pady=(20, 10))

# Frame principal
frame = tk.Frame(root, bg="#f0f0f0")
frame.pack(pady=10, padx=20, fill="both", expand=True)

# Etapa 1: Seleção de imagens
tk.Label(frame, text="1. Selecione as imagens:", font=section_font, bg="#f0f0f0").pack(pady=(0, 5), fill="x")
tk.Button(frame, text="Selecionar Imagens", command=select_images, width=25, bg="#4F8EF7", fg="white").pack(pady=5)

tk.Label(frame, text="Imagens selecionadas:", bg="#f0f0f0").pack(pady=(10, 0), fill="x")

# Lista de imagens selecionadas
frame_lista = tk.Frame(frame, bg="#f0f0f0")
frame_lista.pack(fill="x")

listbox = Listbox(frame_lista, width=55, height=8, justify="center")
listbox.pack(pady=5)
listbox.bind("<Double-Button-1>", on_double_click)

# Botão de limpar lista
tk.Button(frame_lista, text="X", command=clear_all, width=3, bg="#D32F2F", fg="white", font=("Helvetica", 12, "bold")).pack(anchor="center", pady=(0, 10))

# Etapa 2: Processamento
tk.Label(frame, text="2. Processar e baixar:", font=section_font, bg="#f0f0f0").pack(pady=(15, 5), fill="x")
tk.Button(frame, text="Iniciar Processamento", command=process_images, width=25, bg="#34A853", fg="white").pack(pady=5)

# Botão para salvar ZIP (desativado até processar)
zip_button = tk.Button(frame, text="Baixar Imagens Redimensionadas (ZIP)", command=download_zip, width=35, bg="#F7B32B", fg="white", state="disabled")
zip_button.pack(pady=5)

# Botão para abrir o log
tk.Button(root, text="!", command=open_log, width=2, bg="#888", fg="white", font=("Helvetica", 10, "bold")).place(relx=1.0, rely=1.0, anchor="se", x=-8, y=-8)

# Executa a janela
root.mainloop()
