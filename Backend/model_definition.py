import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v3_small
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Step 1: Frequency Domain Conversion
def frequency_domain_conversion(batch_images):
    frequency_features = []
    for image in batch_images:
        gray_image = torch.mean(image, dim=0, keepdim=True) 
        dft = torch.fft.fft2(gray_image)
        dft_shifted = torch.fft.fftshift(dft)
        magnitude = torch.abs(dft_shifted)
        phase = torch.angle(dft_shifted)
        magnitude = torch.log1p(magnitude)
        magnitude_normalized = (magnitude - magnitude.mean()) / magnitude.std()
        frequency_feature = torch.stack([magnitude_normalized, phase], dim=0)
        frequency_features.append(frequency_feature)
        plt.imshow(magnitude_normalized, cmap='gray')
        plt.title("Log-Magnitude Spectrum")
        plt.axis("off")
        plt.show()
    return torch.stack(frequency_features)

# Step 2: Spatial Feature Encoder
class SpatialFeatureEncoder(nn.Module):
    def __init__(self, input_shape=(256, 256, 3), embed_dim=128):
        super(SpatialFeatureEncoder, self).__init__()
        # Update for torchvision >= 0.13: use weights=None instead of pretrained=False
        self.base_model = mobilenet_v3_small(weights=None)
        self.base_model.classifier = nn.Identity()
        self.projection = nn.Linear(576, embed_dim)  # Adjust to match embed_dim

    def forward(self, x):
        x = self.base_model(x)
        return self.projection(x)

# Step 3: Frequency Feature Encoder
class FrequencyFeatureEncoder(nn.Module):
    def __init__(self, embed_dim=128):
        super(FrequencyFeatureEncoder, self).__init__()
        self.flatten = nn.Flatten()
        self.dense = nn.Linear(256 * 256 * 2, embed_dim)

    def forward(self, x):
        x = self.flatten(x)
        return F.relu(self.dense(x))

# Step 4: Cross-Stream Attention Fusion
class CrossStreamAttentionFusion(nn.Module):
    def __init__(self, embed_dim=128, num_heads=4):
        super(CrossStreamAttentionFusion, self).__init__()
        self.spatial_proj = nn.Linear(embed_dim, embed_dim)
        self.frequency_proj = nn.Linear(embed_dim, embed_dim)
        self.spatial_to_frequency = nn.MultiheadAttention(embed_dim, num_heads)
        self.frequency_to_spatial = nn.MultiheadAttention(embed_dim, num_heads)
        self.norm = nn.LayerNorm(embed_dim)

    def forward(self, spatial_features, frequency_features):
        spatial_proj = self.spatial_proj(spatial_features.unsqueeze(0))
        frequency_proj = self.frequency_proj(frequency_features.unsqueeze(0))

        spatial_to_frequency, _ = self.spatial_to_frequency(
            spatial_proj, frequency_proj, frequency_proj
        )
        #frequency_to_spatial, _ = self.frequency_to_spatial(
        #    frequency_proj, spatial_proj, spatial_proj
        #)

        #spatial_fused = self.norm(spatial_proj + frequency_to_spatial)
        #frequency_fused = self.norm(frequency_proj + spatial_to_frequency)
        #return (spatial_fused + frequency_fused).squeeze(0)
        return spatial_to_frequency.squeeze(0)

# Step 5: Multiscale Patch Embedding
class MultiScalePatchEmbedding(nn.Module):
    def __init__(self, patch_sizes=[2, 4, 8], embed_dim=128):
        super(MultiScalePatchEmbedding, self).__init__()
        self.patch_sizes = patch_sizes
        self.embed_dim = embed_dim

    def forward(self, features):
        if len(features.shape) == 2:
            batch_size = features.shape[0]
            feature_dim = features.shape[-1]
            spatial_size = feature_dim ** 0.5
            if not spatial_size.is_integer():
                target_dim = 196
                projection_layer = nn.Linear(feature_dim, target_dim)
                features = F.relu(projection_layer(features))
                spatial_size = int(target_dim ** 0.5)
            else:
                spatial_size = int(spatial_size)

            features = features.view(batch_size, 1, spatial_size, spatial_size)

        embeddings = []
        for patch_size in self.patch_sizes:
            unfold = nn.Unfold(kernel_size=patch_size, stride=patch_size)
            patches = unfold(features)
            patches = patches.transpose(1, 2)  # Switch dimensions for embedding

            projection_layer = nn.Linear(patch_size * patch_size * features.shape[1], self.embed_dim)
            projected_patches = F.relu(projection_layer(patches))
            embeddings.append(projected_patches)

        multiscale_embedding = torch.cat(embeddings, dim=1)
        #print(multiscale_embedding.shape)
        return multiscale_embedding

# Step 6: Class Token Refinement Module
class ClassTokenRefinementModule(nn.Module):
    def __init__(self, num_heads = 8, hidden_dim=128):
        super(ClassTokenRefinementModule, self).__init__()
        self.num_heads = num_heads
        self.hidden_dim = hidden_dim
        self.layer_norm_1 = nn.LayerNorm(hidden_dim)
        self.layer_norm_2 = nn.LayerNorm(hidden_dim)
        self.multihead_attention = nn.MultiheadAttention(embed_dim=hidden_dim, num_heads=num_heads, batch_first=True)
        self.dense_1 = nn.Linear(hidden_dim, hidden_dim)
        self.dense_2 = nn.Linear(hidden_dim, hidden_dim)

    def forward(self, feature_map):
        batch_size = feature_map.size(0)
        class_token_input = torch.zeros((batch_size, 1, self.hidden_dim), device=feature_map.device)

        attention_output, _ = self.multihead_attention(feature_map, feature_map, feature_map)
        add_norm_1 = self.layer_norm_1(attention_output + feature_map)

        dense_1_output = F.relu(self.dense_1(add_norm_1))
        dense_2_output = self.dense_2(dense_1_output)

        final_add = self.layer_norm_2(add_norm_1 + dense_2_output)
        #print("Final_add", final_add.shape)
        #print("Final_add", type(final_add))
        return final_add
    
# Step 7: Classification Layer
class ClassificationLayer(nn.Module):
    def __init__(self, num_classes=2):
        super(ClassificationLayer, self).__init__()
        self.num_classes = num_classes
        self.flatten = nn.Flatten()
        self.dense = nn.Linear(7552, num_classes)  # Assumes the input feature dimension is 128

    def forward(self, refined_class_token):
        flattened_class_token = self.flatten(refined_class_token)
        #print("flattened_class_token", flattened_class_token.shape)
        output_layer = F.softmax(self.dense(flattened_class_token), dim=-1)
        #print(type(output_layer))
        return output_layer

# Step 8: Full Model
class DeepfakeDetectionModel(nn.Module):
    def __init__(self, input_shape=(256, 256, 3), num_classes=2):
        super(DeepfakeDetectionModel, self).__init__()
        self.spatial_encoder = SpatialFeatureEncoder()
        self.frequency_encoder = FrequencyFeatureEncoder()
        self.cross_attention = CrossStreamAttentionFusion()
        self.patch_embedding = MultiScalePatchEmbedding()
        self.class_token_refinement = ClassTokenRefinementModule()
        self.classification_layer = ClassificationLayer(num_classes=num_classes)

    def forward(self, images, frequency_features):
        spatial_features = self.spatial_encoder(images)
        plt.imshow(spatial_features)
        plt.title("spatial_features of the Image")
        plt.axis("off")
        plt.show()

        frequency_features = self.frequency_encoder(frequency_features)
        plt.imshow(frequency_features)
        plt.title("frequency_features of the Image")
        plt.axis("off")
        plt.show()

        fused_features = self.cross_attention(spatial_features, frequency_features)
        #print("Fused Features",fused_features.shape)
        multiscale_embeddings = self.patch_embedding(fused_features)
        #print("Multi scale features", multiscale_embeddings.shape)
        #refined_class_token = self.class_token_refinement(multiscale_embeddings)
        #print("Refined Class Token", refined_class_token.shape)
        classification_out = self.classification_layer(multiscale_embeddings)
        #print("Classification Output",classification_out.shape)
        return classification_out
