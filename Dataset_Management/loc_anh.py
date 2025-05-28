import cv2
import os
import shutil

folder_path = "D:\\dataset\\images\\train_resized"
bad_quality_folder = "D:\\dataset\\images\\Bad_quality"

# Tạo thư mục lưu ảnh kém chất lượng nếu chưa tồn tại
os.makedirs(bad_quality_folder, exist_ok=True)

for img_name in os.listdir(folder_path):
    img_path = os.path.join(folder_path, img_name)
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

    if img is not None:
        # Kiểm tra độ sắc nét 
        variance = cv2.Laplacian(img, cv2.CV_64F).var()
        
        if variance < 50:  # Ngưỡng phát hiện ảnh mờ
            # Chuyển ảnh kém chất lượng vào thư mục mới
            shutil.copy(img_path, os.path.join(bad_quality_folder, img_name))

print("Ảnh kém chất lượng đã được chuyển vào thư mục: " + bad_quality_folder)

