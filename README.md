# VisionQuery

VisionQuery is a semantic image search tool that lets users search a collection of images using natural language instead of fixed labels. By using CLIP embeddings, the project maps both images and text into a shared vector space, allowing queries like `"a dog in snow"` or `"red fruit on a table"` to retrieve the most relevant images.

This project was built because I wanted a better way to search through images on my own computer, and I was interested in building that system myself. It became an way to create a practical tool while learning more about multimodal AI and semantic search.


## Usage

**I recommend: "https://www.kaggle.com/datasets/shreyapmaher/fruits-dataset-images" for testing but any image dataset works**

**Place your images inside:**
```bash
visionquery/
│
├── data/
│   ├── images/          
```
**Nested folders are supported, for example:**
```bash
visionquery/
│
├── data/
│   ├── data/images/dataset1/dog1.jpg
│   ├── data/images/dataset2/fruits/apple.png         
```  

**Or**

**List dicrectories on your computer in text file (line by line):**
```bash
visionquery/
│
├── data/
│   ├── directories.txt          
```
**For Example:**
```bash
visionquery
│
├── data/directories.txt
│   ├── /run/media/Name/MainDrive/photos/
│   ├── /home/userName/  
``` 

**Program will recursively go through all files in given directory and find images**

**Then Run:**

    python app/listener.py
    python run.py
## Features

- Search images using natural language
- Uses CLIP for zero-shot image-text matching
- Recursively scans images in nested folders
- Precomputes and saves image embeddings for faster reuse
- encrypts the image embedding data & paths
- Ranks results by similarity score
- Clean modular architecture for scaling later

## How It Works

VisionQuery works in three main steps:

1. **Encode images**  
   Every image in the dataset is converted into a numerical embedding using CLIP.

2. **Encode text query**  
   A user’s search query is also converted into an embedding in the same vector space.

3. **Compare similarity**  
   The system compares the query embedding to all image embeddings and returns the most relevant matches.

Because CLIP embeds text and images into the same shared space, VisionQuery can search semantically instead of relying only on exact labels.

## Tech Stack

1. **Python**

2. **PyTorch**

3. **Hugging Face Transformers**

4. **Pillow**

5. **Keyring**

6. **Watchdog**

7. **CLIP (Contrastive Language–Image Pretraining)**

## How To Install
    git clone https://github.com/yourusername/visionquery.git
    cd visionquery
    pip install -r requirements.txt

## Or install manually:
    pip install torch torchvision transformers pillow keyring watchdog


## Project Structure

```bash
visionquery/
│
├── models/
│   └── clipModel.py        # Loads CLIP and encodes images/text
│
├── app/
│   ├── embeddings.py       # Generates, saves, and loads image embeddings
    ├── encryption.py       # Encrypts image paths and data, (optional but prevents image data from being in plain text)
    ├── listener.py         # On start, works in background to save embeddings
│   └── search.py           # Performs similarity search over embeddings
│
├── data/
│   ├── images/             # Image dataset (supports nested folders)
│   └── embeddings.pkl      # Saved image embeddings (gets created on first run)
│
├── run.py                  # Main entry point
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## Future Features/Changes

1. **Improving RAM/GPU usage for large amount of images (currently all embeddings are loaded in RAM)**

2. **Refactoring code**

3. **Looking into improving accuracy even further**