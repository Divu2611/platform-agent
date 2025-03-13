# Importing Python Libraries.
import logging

from tools.embeddings import open_ai_embeddings


def setup_logger(name, log_file, level):
    """Function to create a logger for different log levels."""
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

error_logger = setup_logger("error_logger", "logs/embeddings/error.log", logging.ERROR)


def chunk_text(text, delimiter, chunk_size):
    chunks = []
    current_chunk = []
    current_length = 0

    try:
        sentences = text.split(delimiter)

        for sentence in sentences:
            sentence_length = len(sentence.split())

            if current_length + sentence_length > chunk_size:
                chunks.append(delimiter.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        if current_chunk:
            chunks.append(delimiter.join(current_chunk))
    except Exception as exception:
        error_logger.error(f"Failed to chunk text: {exception}")

    return chunks


def get_embeddings(texts, model="text-embedding-ada-002", delimiter='.', chunk_size=100):
    all_embeddings = []
    chunks = []

    for text in texts:
        chunks = chunk_text(text, delimiter, chunk_size)

        for chunk in chunks:
            try:
                response = open_ai_embeddings([chunk], model)
                embeddings = response.data[0].embedding
                all_embeddings.append(embeddings)
            except Exception as exception:
                error_logger.error(f"Failed to get embeddings: {exception}")
                return None, None

    return all_embeddings, chunks