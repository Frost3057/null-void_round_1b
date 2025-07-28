from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

model.save('./multilingual_model')

print("✅ Model downloaded and saved to ./multilingual_model") 