import os

# --- Scraping ---
REQUEST_TIMEOUT = 15          # secondes par requête HTTP
DELAY_BETWEEN_URLS = 1.5      # pause entre deux URLs
MAX_PDFS_PER_PAGE = 2         # nombre maximal de PDFs téléchargés par page
PDF_DOWNLOAD_TIMEOUT = 30     # secondes pour télécharger un PDF
MAX_PDF_SIZE_MB = 20          # on ignore les PDFs trop lourds

# --- Texte ---
MAX_TEXT_CHARS = 4000         # taille maximale du texte envoyé au LLM

# --- LLM ---
LLM_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
LLM_MAX_NEW_TOKENS = 1000        # ~600 mots ≈ 900 tokens
LLM_TEMPERATURE = 0.2
LLM_DEVICE = 0                # GPU index (0 = premier GPU)

# --- Stockage ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_CSV = os.path.join(DATA_DIR, "output.csv")

# --- HTTP headers ---
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}
