# config.py

OPENAI_API_KEY = "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"

AVAILABLE_MODELS = [
    "gpt-4o", "gpt-4-turbo", "gpt-4",
    "gpt-3.5-turbo-0125", "gpt-3.5-turbo", "gpt-3.5"
]

# POUR PEUPLER LA BASE LA PREMIÈRE FOIS
ASSISTANT_PRESETS = {
    "⚖️ Expert Droit FR": {
        "id": "asst_Mvgh704gZMYBZlF5D9YQYJz3",
        "vector_store_id": "vs_67e5f32c978081918af8ec549a71a127",
        "prompt": """# Rôle du Modèle
Agis comme un avocat expert en droit français, formé à partir des textes officiels..."""
    },
    "🌍 Expert Normes IFRS": {
        "id": "asst_zNkRZsFCLhCOv540ybxkbTPw",
        "vector_store_id": "vs_67e61f93293481918b3e155e1f9648ad",
        "prompt": """# Rôle du modèle
Agis comme un expert en normes IFRS disposant d'une solide expérience..."""
    },
    "👠 Expert Retail B2C": {
        "id": "asst_BO0FU5RgD9DieRtcLk0xSe9F",
        "vector_store_id": "vs_67e613a895f081918ba7993334b80e98",
        "prompt": """# Rôle du modèle
Agis comme un expert en comptabilité, fiscalité et finance, spécialisé dans le Retail B2C..."""
    },
    "💰 Expert Fiscalité FR": {
        "id": "asst_HSQneOOSWHqMsZ7yMxlyZuO0",
        "vector_store_id": "vs_67e61efab4208191b3cc419157d370e7",
        "prompt": """# Rôle du Modèle
Agis comme un expert en fiscalité française, formé à partir des sources officielles..."""
    },
    "💲 Expert Loi SOX": {
        "id": "asst_XGV9OW7LFDYUfiOQpqfRrcUYUY",
        "vector_store_id": "vs_67e5ff5072b481918d69b010f2c12c3e",
        "prompt": """# Rôle du Modèle
Tu agis comme un expert de la loi Sarbanes-Oxley (SOX)..."""
    },
    "💲 Expert US GAAP": {
        "id": "asst_pKfwZ0yFX9sPfgUmn5n4BMKX",
        "vector_store_id": "vs_67e5fec249288191bc1fc72b9747c2a2",
        "prompt": """# Rôle du Modèle
Agis comme un expert en normes comptables américaines (US GAAP)..."""
    },
    "🔢 Expert Compta FR": {
        "id": "asst_BjUOv484UB7ENdtGPexHkZHN",
        "vector_store_id": "vs_67e5ec3bc654819183e70131b2845963",
        "prompt": """# Rôle du Modèle
Agis comme un expert en comptabilité française issu du PCG, BOFiP et doctrine..."""
    },
    "🔢 Expert Compta Publique": {
        "id": "asst_QOj2w5JIXbFdJakbWiZG3e8k",
        "vector_store_id": "vs_67e5ff08d7788191b883c803e89a81aa",
        "prompt": """# Rôle du Modèle
Agis comme un expert en comptabilité publique française..."""
    }
}
