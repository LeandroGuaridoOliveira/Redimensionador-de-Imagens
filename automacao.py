#IDEIAS DE MELHORIAS EM CASO DE IMPLEMENTAÇÂO NA AUTOMAÇÃO:
# Pegar o nome do produto que for extraido e renomear a imagem com o mesmo nome.
# Criar um banco de dados apenas para as imagens, assim fazendo com que o upload das imagens dos produtos seja mais simples, ja que a automação vai fazer o trabalho de renomear e redimensionar as imagens.

from PIL import Image
import os
import logging
from tqdm import tqdm
from multiprocessing import Pool

# Garante que as pastas necessárias existem
os.makedirs("logs", exist_ok=True)
os.makedirs(r"C:\Automação Fotos IA\images\imagens a redimensionar", exist_ok=True)
os.makedirs(r"C:\Automação Fotos IA\images\imagens redimensionadas", exist_ok=True)

# Configurando o Logging
logging.basicConfig(
    filename="logs/automacao.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Caminhos para as pastas de imagens (A redimensionar, Redimensionadas)
imagens_a_redimensionar = r"C:\Automação Fotos IA\images\imagens a redimensionar"
imagens_redimensionadas = r"C:\Automação Fotos IA\images\imagens redimensionadas"

# Tamanhos das imagens a serem redimensionadas
tamanhos = {
    "grande": (500, 500),
    "pequena": (260, 240)
}

# Parâmetro de qualidade para WebP (melhor qualidade possível)
webp_quality = 100

# Função para redimensionar imagens
def redimensionar_imagem(nome_arquivo):
    try:
        if not nome_arquivo.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")):
            logging.info(f"Arquivo ignorado (formato não suportado): {nome_arquivo}")
            return
        image_path = os.path.join(imagens_a_redimensionar, nome_arquivo)
        nome_produto = os.path.splitext(nome_arquivo)[0]
        pasta_produto = os.path.join(imagens_redimensionadas, nome_produto)
        os.makedirs(pasta_produto, exist_ok=True)
        with Image.open(image_path) as img:
            for nome_tamanho, tamanho in tamanhos.items():
                img_copia = img.copy()
                img_copia.thumbnail(tamanho, Image.LANCZOS)
                fundo = Image.new("RGB", tamanho, (255, 255, 255))
                x = (tamanho[0] - img_copia.width) // 2
                y = (tamanho[1] - img_copia.height) // 2
                fundo.paste(img_copia, (x, y))
                webp_nome_arquivo = f"{nome_produto}_{nome_tamanho}.webp"
                webp_path = os.path.join(pasta_produto, webp_nome_arquivo)
                # Pula o arquivo caso ele já exista
                if os.path.exists(webp_path):
                    logging.info(f"Arquivo já existe, pulando: {webp_path} (Produto: {nome_produto}, Tamanho: {nome_tamanho})")
                    continue
                fundo.save(webp_path, "WEBP", quality=webp_quality, method=6)
                logging.info(f"Imagem convertida para WebP: {webp_path} (Produto: {nome_produto}, Tamanho: {nome_tamanho}, Origem: {image_path})")
    except Exception as e:
        logging.error(f"Erro ao processar '{nome_arquivo}' (Produto: {os.path.splitext(nome_arquivo)[0]}): {e}")

# Lista de arquivos para processar (apenas novos ou modificados)
arquivos = [f for f in os.listdir(imagens_a_redimensionar) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp'))]

# Processamento com barra de progresso e multiprocessing
if __name__ == "__main__":
    logging.info("Início do processamento de imagens.")
    with Pool() as pool:
        list(tqdm(pool.imap_unordered(redimensionar_imagem, arquivos), total=len(arquivos), desc="Processando imagens"))
    logging.info("Processamento de imagens finalizado.")