# loading in the clip model here
from transformers import CLIPProcessor, CLIPModel  # type: ignore
import torch  # type: ignore

print("Loading CLIP model...")

class CLIPWrapper:
    def __init__(self): # Load the pre-trained CLIP model and processor
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32") # model: does the actual feature extraction
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32") # processor: handles preprocessing of images/text into tensors

        self.model.to(self.device)



    def encode_image(self, image):
        # Converts an image (PIL or similar) into a normalized vector.
        # Normalization ensures the vector has length 1 so cosine similarity works.

        # Preprocess image into PyTorch tensor
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        
        with torch.no_grad(): # Disable gradient computation for speed and memory
            # Extract image features
            outputs = self.model.get_image_features(**inputs)
            
            # Some versions of Transformers return a tensor directly,
            # others return an object with pooler_output
            features = outputs if isinstance(outputs, torch.Tensor) else outputs.pooler_output
        # Normalize vector to unit length
        return features / features.norm(dim=-1, keepdim=True)



    def encode_text(self, text):
        # Converts a text string into a normalized vector.

        # Preprocess text into PyTorch tensor
        inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            # Extract text features
            outputs = self.model.get_text_features(**inputs)
            features = outputs if isinstance(outputs, torch.Tensor) else outputs.pooler_output
        
        # Normalize vector to unit length
        return features / features.norm(dim=-1, keepdim=True)