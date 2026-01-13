"""
Pathway Real-Time Pipeline
This demonstrates Pathway's streaming capabilities
"""
import pathway as pw
import os

DATA_FOLDER = "./data/articles"

def run_pathway_pipeline():
    """Run the Pathway real-time document processing pipeline"""
    print("🚀 Starting Pathway Real-Time Pipeline...")
    print(f"📁 Watching folder: {DATA_FOLDER}")
    print("=" * 50)
    
    # Ensure data folder exists
    os.makedirs(DATA_FOLDER, exist_ok=True)
    
    # 1. INGEST: Watch folder for new/updated files (STREAMING MODE)
    # This is the KEY Pathway feature - it automatically detects changes!
    documents = pw.io.fs.read(
        path=DATA_FOLDER,
        format="plaintext",
        mode="streaming",  # Real-time streaming mode
        with_metadata=True
    )
    
    # 2. TRANSFORM: Process documents
    processed = documents.select(
        content=pw.this.data,
        file_path=pw.this._metadata
    )
    
    # 3. OUTPUT: Log processed documents
    pw.io.fs.write(
        processed,
        filename="./data/pathway_output.jsonl",
        format="json"
    )
    
    print("✅ Pipeline configured!")
    print("📡 Listening for new documents...")
    print("💡 Add .txt files to data/articles/ to see real-time processing")
    print("=" * 50)
    
    # 4. RUN the pipeline (blocks and runs forever)
    pw.run(monitoring_level=pw.MonitoringLevel.ALL)

if __name__ == "__main__":
    run_pathway_pipeline()