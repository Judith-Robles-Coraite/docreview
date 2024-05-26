from flask import Flask, render_template
from ebp_plagio import find_plagiarism, extract_text_by_page, preprocess_text, load_documents

app = Flask(__name__)

def process_main_document(main_pdf_path):
    main_doc_pages = extract_text_by_page(main_pdf_path)
    if main_doc_pages is None:
        print(f"Error al abrir el documento principal: {main_pdf_path}")
        return None
    # Omitir las primeras 7 páginas
    main_doc_pages = main_doc_pages[7:]
    main_doc_pages = [(page_num, preprocess_text(text)) for page_num, text in main_doc_pages]
    return main_doc_pages

@app.route('/')
def index():
    main_pdf_path = "C:/Users/ebpsi/OneDrive/Documentos/DOSUMENTO_COMPARACION/Trabajo Final.pdf"
    main_doc_pages = process_main_document(main_pdf_path)
    if main_doc_pages is None:
        return "Error al procesar el documento principal"
    # También necesitarás definir other_docs y filenames
    results = find_plagiarism(main_doc_pages, other_docs, filenames)
    return render_template('index.html', results=results)

if __name__ == '__main__':
    directory = "C:/Users/ebpsi/OneDrive/Escritorio/DOCUMENTOS"  # Cambia esto a la ruta donde están tus PDFs
    other_docs, filenames = load_documents(directory)
    app.run(debug=True)
