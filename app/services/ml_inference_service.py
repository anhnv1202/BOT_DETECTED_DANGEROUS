import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
from typing import List, Dict
import io

from app.config import get_settings

settings = get_settings()


class MultilabelMobileNetV2(nn.Module):
    """MobileNetV2 for multilabel classification - PHẢI GIỐNG TRONG NOTEBOOK TRAINING"""
    
    def __init__(self, num_classes, pretrained=True):
        super(MultilabelMobileNetV2, self).__init__()
        
        # Load MobileNetV2 (dùng weights thay vì pretrained - PyTorch modern API)
        weights = models.MobileNet_V2_Weights.DEFAULT if pretrained else None
        self.backbone = models.mobilenet_v2(weights=weights)
        
        # Replace final classifier
        in_features = self.backbone.classifier[1].in_features
        
        # Create multilabel classifier (no Sigmoid - will use BCEWithLogitsLoss)
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(in_features, num_classes)
        )
    
    def forward(self, x):
        return self.backbone(x)


class MLInferenceService:
    """Service load model AI và thực hiện inference (detect dangerous objects)"""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.transform = None
        self.class_names = settings.MODEL_CLASSES
        self._load_model()
    
    def _load_model(self):
        """Load weights từ file .pth và chuẩn bị transform (resize 224x224, normalize ImageNet)"""
        try:
            # Tạo model với cùng kiến trúc như lúc training
            self.model = MultilabelMobileNetV2(num_classes=len(self.class_names), pretrained=False)
            
            # Load state dict
            state_dict = torch.load(settings.MODEL_PATH, map_location=self.device)
            self.model.load_state_dict(state_dict)
            
            self.model.to(self.device)
            self.model.eval()
            
            # Transform giống như trong notebook (validation transform)
            self.transform = transforms.Compose([
                transforms.Resize((settings.MODEL_IMG_SIZE, settings.MODEL_IMG_SIZE)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
        except Exception as e:
            raise RuntimeError(f"Failed to load ML model: {e}")
    
    def predict(self, image_bytes: bytes, threshold: float = 0.5) -> Dict:
        """Dự đoán dangerous objects trong ảnh (trả về classes, probabilities, active classes)"""
        if not self.model or not self.transform:
            raise RuntimeError("Model not loaded")
        
        # Load and preprocess image
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception:
            raise ValueError("Invalid image format")
        
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # Inference
        with torch.no_grad():
            logits = self.model(input_tensor)
            probabilities = torch.sigmoid(logits).cpu().numpy()[0].tolist()
        
        # Filter active classes
        active_classes = [
            cls for cls, prob in zip(self.class_names, probabilities)
            if prob >= threshold
        ]
        
        return {
            "classes": self.class_names,
            "probabilities": probabilities,
            "active": active_classes
        }

