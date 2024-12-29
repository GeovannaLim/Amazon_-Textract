import boto3
import requests
from pdf2image import convert_from_path
from io import BytesIO

# Configuração da AWS
aws_region = "us-east-1"  # Altere conforme sua região
textract = boto3.client('textract', region_name=aws_region)

# API de busca de imagens (exemplo: Unsplash)
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"
UNSPLASH_API_KEY = "sua_chave_unsplash"  # Substitua pela sua chave de API

def extract_text_from_pdf(pdf_path):
    """Extrai o texto de um arquivo PDF usando o Amazon Textract."""
    images = convert_from_path(pdf_path)
    words = []

    for i, image in enumerate(images):
        # Convertendo a imagem para bytes
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format="JPEG")
        img_byte_arr = img_byte_arr.getvalue()

        # Enviar imagem para Textract
        response = textract.detect_document_text(Document={'Bytes': img_byte_arr})

        # Processar a resposta para extrair palavras
        for item in response['Blocks']:
            if item['BlockType'] == 'WORD':
                words.append(item['Text'])
    
    return words

def search_image(word):
    """Busca uma imagem no Unsplash com base em uma palavra."""
    params = {
        'query': word,
        'client_id': UNSPLASH_API_KEY,
        'per_page': 1
    }
    response = requests.get(UNSPLASH_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][0]['urls']['small']  # Retorna o link da imagem
    return None

def main():
    # Solicitar o arquivo PDF ao usuário
    pdf_path = input("Insira o caminho do arquivo PDF: ")

    # Validar o caminho do arquivo
    if not pdf_path or not pdf_path.lower().endswith('.pdf'):
        print("Por favor, insira um arquivo PDF válido.")
        return

    try:
        # Extrair palavras do PDF
        print("Extraindo palavras do PDF...")
        words = extract_text_from_pdf(pdf_path)

        if not words:
            print("Nenhuma palavra foi encontrada no PDF.")
            return

        print("Palavras extraídas:", words)

        # Buscar imagens para as palavras
        print("Buscando imagens correspondentes...")
        for word in set(words):  # Remove duplicatas
            image_url = search_image(word)
            if image_url:
                print(f"Imagem para '{word}': {image_url}")
            else:
                print(f"Não foi encontrada uma imagem para '{word}'.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()
