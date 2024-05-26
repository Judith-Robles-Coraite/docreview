import fitz  # PyMuPDF
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from multiprocessing import Pool, cpu_count

def extract_text_by_page(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except fitz.FileDataError:
        return None
    pages_text = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        pages_text.append((page_num + 1, text))  # Almacenamos el número de página comenzando desde 1
    return pages_text


def preprocess_text(text):
    text = re.sub(r'\n[A-Z\s]{2,}\n', ' ', text)
    text = text.lower()
    text = re.sub(r'\W+', ' ', text)
    return text

def load_documents(directory):
    documents = []
    filenames = []
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            filepath = os.path.join(directory, filename)
            pages_text = extract_text_by_page(filepath)
            if pages_text is not None:
                pages_text = [(page_num, text) for page_num, text in pages_text if page_num > 7]  # Omitir las primeras 7 páginas
                preprocessed_pages_text = [(page_num, preprocess_text(text)) for page_num, text in pages_text]
                documents.append(preprocessed_pages_text)
                filenames.append(filename)
    return documents, filenames

def calculate_similarity(doc1, doc2):
    try:
        vectorizer = TfidfVectorizer().fit_transform([doc1, doc2])
        vectors = vectorizer.toarray()
        return cosine_similarity(vectors)[0, 1]
    except ValueError:
        return 0.0

def find_similar_paragraphs(main_text, other_text, threshold=0.7):
    main_paragraphs = [p for p in main_text.split('\n') if p.strip()]
    other_paragraphs = [p for p in other_text.split('\n') if p.strip()]
    
    similar_paragraphs = []
    
    for main_paragraph in main_paragraphs:
        for other_paragraph in other_paragraphs:
            similarity = calculate_similarity(main_paragraph, other_paragraph)
            if similarity > threshold:
                similar_paragraphs.append((main_paragraph, other_paragraph, similarity))
    
    return similar_paragraphs

def compare_pages(params):
    main_page_num, main_text, doc_pages, threshold = params
    results = []
    for other_page_num, other_text in doc_pages:
        if not other_text.strip():
            continue
        similar_paragraphs = find_similar_paragraphs(main_text, other_text, threshold)
        if similar_paragraphs:
            results.append({
                'main_page': main_page_num - 8,
                'other_page': other_page_num - 8 ,
                'similar_paragraphs': similar_paragraphs
            })
    return results

def find_plagiarism(main_doc_pages, other_docs, filenames, threshold=0.7, paragraph_similarity_threshold=0.7):
    results = []
    pool = Pool(cpu_count())

    for i, doc_pages in enumerate(other_docs):
        params = [(main_page_num, main_text, doc_pages, paragraph_similarity_threshold) for main_page_num, main_text in main_doc_pages if main_text.strip()]
        doc_results = pool.map(compare_pages, params)
        doc_results = [res for sublist in doc_results for res in sublist]
        if any(any(similarity >= threshold for _, _, similarity in res['similar_paragraphs']) for res in doc_results):
            results.append({
                'filename': filenames[i],
                'results': doc_results
            })

    pool.close()
    pool.join()
    return results

def main():
    directory = "C:/Users/ebpsi/OneDrive/Escritorio/DOCUMENTOS"  # Cambia esto a la ruta donde están tus PDFs
    main_pdf = "C:/Users/ebpsi/OneDrive/Documentos/DOSUMENTO_COMPARACION/Trabajo Final.pdf"  # Cambia esto a la ruta de tu documento principal

    main_doc_pages = extract_text_by_page(main_pdf)
    if main_doc_pages is None:
        print(f"Error al abrir el documento principal: {main_pdf}")
        return

    main_doc_pages = [(page_num, text) for page_num, text in main_doc_pages if page_num > 7]  # Omitir las primeras 7 páginas
    main_doc_pages = [(page_num, preprocess_text(text)) for page_num, text in main_doc_pages]

    other_docs, filenames = load_documents(directory)

    results = find_plagiarism(main_doc_pages, other_docs, filenames)

    for result in results:
        print(f"Documento: {result['filename']}")
        for res in result['results']:
            if any(similarity >= 0.8 for _, _, similarity in res['similar_paragraphs']):
                main_page_num = res['main_page']
                other_page_num = res['other_page']
                print(f"Página en el documento principal: {main_page_num}")
                print(f"Página en el documento plagiado: {other_page_num}")
                print("Párrafos plagiados:")
                for main_para, other_para, similarity in res['similar_paragraphs']:
                    if similarity >= 0.72:
                        print(f"Similitud: {similarity:.2f}")
                        print(f"Documento principal: {main_para}")
                        print(f"Documento plagiado: {other_para}")
                        print('-' * 80)

if __name__ == "__main__":
    main()
