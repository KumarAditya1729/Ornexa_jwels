<div align="center">
  <img src="docs/assets/banner.png" alt="ORNEXA Banner" width="100%" style="border-radius: 12px; margin-bottom: 20px;">
  
  # ORNEXA JEWLS
  
  **AI-Powered Jewelry Ecosystem: Generative Design, Vision Classification, and Intelligent Cataloging**
  
</div>

## 📖 Overview

**ORNEXA JEWLS** is a cutting-edge platform designed to revolutionize the jewelry industry through artificial intelligence. By combining advanced computer vision, generative AI (Text-to-Image with LoRA), and automated catalog ingestion, Ornexa provides a comprehensive suite of tools for jewelry designers, retailers, and catalog managers.

From extracting complex taxonomies from raw unstructured data to generating stunning photorealistic jewelry designs, Ornexa acts as a true AI co-pilot for the modern jeweler.

---

## 🌟 Key Features

- **🎨 Generative Design Studio:** Utilize fine-tuned Text-to-Image LoRA models to brainstorm and generate high-quality jewelry designs from simple text prompts.
- **👁️ AI Vision Classifier:** Automatically classify, tag, and organize jewelry pieces (rings, necklaces, earrings) using a custom-trained YOLOv8 computer vision model.
- **🧠 Knowledge Explorer & Copilot:** Interact with your entire catalog via an intelligent RAG (Retrieval-Augmented Generation) Copilot and Knowledge Graph.
- **⚙️ Automated Ingestion Pipeline:** Robust data mappers, sniffers, and taxonomy engines to seamlessly integrate and standardize messy vendor catalogs.
- **💻 Modern Web Interface:** A sleek, responsive React (Vite) frontend offering modules for Analytics, Orders, Search, and an AI Studio.

---

## 🏗️ System Architecture

```mermaid
graph TD
    %% Define Styles
    classDef frontend fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff;
    classDef api fill:#8b5cf6,stroke:#5b21b6,stroke-width:2px,color:#fff;
    classDef ai fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff;
    classDef ingestion fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#fff;

    %% Nodes
    subgraph Web_Frontend ["💻 Web Interface (React / Vite)"]
        UI_Copilot[AI Copilot]
        UI_Studio[Generative Studio]
        UI_Analytics[Analytics & Search]
    end

    subgraph API_Layer ["⚙️ API Layer"]
        Workflow[Workflow Orchestration]
    end

    subgraph AI_Engine ["🧠 AI Engine (product/)"]
        Vision[YOLOv8 Vision Classifier]
        GenAI[Text-to-Image LoRA]
        Knowledge[Knowledge Graph & RAG]
    end

    subgraph Data_Ingestion ["📥 Data Ingestion Pipeline (ingestion/)"]
        Sniffer[Data Sniffer]
        Mapper[Schema Mapper]
        Taxonomy[Taxonomy Engine]
    end

    %% Connections
    UI_Copilot -->|API Calls| Workflow
    UI_Studio -->|Prompts| Workflow
    UI_Analytics -->|Queries| Workflow
    
    Workflow -->|Classify Image| Vision
    Workflow -->|Generate Image| GenAI
    Workflow -->|Query Data| Knowledge
    
    Sniffer --> Mapper
    Mapper --> Taxonomy
    Taxonomy -->|Populates| Knowledge
    
    %% Apply Styles
    class UI_Copilot,UI_Studio,UI_Analytics frontend;
    class Workflow api;
    class Vision,GenAI,Knowledge ai;
    class Sniffer,Mapper,Taxonomy ingestion;
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have the following installed:
- Node.js (v18+)
- Python 3.10+
- Git LFS (Large File Storage)

### 2. Clone the Repository
Since the repository contains large model weights and datasets, make sure Git LFS is installed before cloning:
```bash
git lfs install
git clone https://github.com/KumarAditya1729/Ornexa_jwels.git
cd Ornexa_jwels
```

### 3. Setup Python Backend (AI Engine & API)
We recommend using a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 4. Setup React Frontend
```bash
cd web
npm install
npm run dev
```
The frontend will be available at `http://localhost:5173`.

---

## 📂 Project Structure

```text
ORNEXA JEWLS/
├── api/                  # API endpoints and workflow orchestration
├── benchmarks/           # Evaluation and testing metrics for models
├── data/                 # Local data storage and configuration
├── ingestion/            # Pipeline for sniffing, mapping, and taxonomy extraction
├── model_output/         # Trained checkpoints (e.g., LoRA safetensors)
├── product/              # Core AI modules (Vision, GenAI, Knowledge Explorer)
├── runs/                 # Training logs and outputs from YOLOv8
└── web/                  # React (Vite) frontend web application
```

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/KumarAditya1729/Ornexa_jwels/issues).

## 📄 License
This project is licensed under the MIT License.
