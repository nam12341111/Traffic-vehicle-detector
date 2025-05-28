import os
import random
import shutil

# Đường dẫn đến thư mục ảnh gốc
dataset_path = "D:\\dataset\\images"
label_path = "D:\\dataset\\labels"

# Tạo thư mục train và val
train_img_dir = os.path.join(dataset_path, "train")
val_img_dir = os.path.join(dataset_path, "val")
train_label_dir = os.path.join(label_path, "train")
val_label_dir = os.path.join(label_path, "val")

os.makedirs(train_img_dir, exist_ok=True)
os.makedirs(val_img_dir, exist_ok=True)
os.makedirs(train_label_dir, exist_ok=True)
os.makedirs(val_label_dir, exist_ok=True)

# Lấy danh sách ảnh
images = [f for f in os.listdir(dataset_path) if f.endswith('.jpg')]
random.shuffle(images)

# Chia dữ liệu (80% train, 20% val)
split_ratio = 0.8
num_train = int(len(images) * split_ratio)

train_images = images[:num_train]
val_images = images[num_train:]

# Di chuyển file ảnh và nhãn vào thư mục train/val tương ứng
for img in train_images:
    shutil.move(os.path.join(dataset_path, img), os.path.join(train_img_dir, img))
    txt_file = img.replace(".jpg", ".txt")
    if os.path.exists(os.path.join(label_path, txt_file)):
        shutil.move(os.path.join(label_path, txt_file), os.path.join(train_label_dir, txt_file))

for img in val_images:
    shutil.move(os.path.join(dataset_path, img), os.path.join(val_img_dir, img))
    txt_file = img.replace(".jpg", ".txt")
    if os.path.exists(os.path.join(label_path, txt_file)):
        shutil.move(os.path.join(label_path, txt_file), os.path.join(val_label_dir, txt_file))

print("✅ Chia dữ liệu hoàn tất!")
