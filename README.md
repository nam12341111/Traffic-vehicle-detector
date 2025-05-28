**1. Overview**

- Dự án Nhận Diện Các Phương Tiện Giao Thông sử dụng mô hình YOLOv8 kết hợp Attention Module (CBAM) để phát hiện và phân loại phương tiện trong ảnh hoặc video. Mục tiêu là xây dựng hệ thống có thể phát hiện các phương tiện như xe máy, ô tô, xe tải và xe buýt với độ chính xác cao, ứng dụng trong giao thông thông minh và xe tự hành.

**2. Features**

- Phát hiện đối tượng: Sử dụng YOLOv8 để nhận diện phương tiện.

- Phân loại: Nhận dạng 4 lớp phương tiện: motorbike, car, truck, bus.

- Attention module (CBAM): Tăng cường khả năng tập trung vào đặc trưng quan trọng của ảnh.

- Hỗ trợ real-time: Triển khai ứng dụng web nhận diện phương tiện theo thời gian thực.

**3. Requirements**

Cài đặt các thư viện cần thiết:
pip install -r requirements.txt

Các công nghệ chính:

- PyTorch

- OpenCV

- Flask (backend)

- React (frontend)

- MongoDB

**4. Dataset**

- Nguồn: COCO, Open Images

- Gán nhãn bằng LabelImg (định dạng YOLO).

- Số lượng ảnh: ~5,000 ảnh (sau xử lý).

- Kích thước chuẩn hóa: 640x640

- Chia dữ liệu:
Train: 80%
Validation: 20%

**5. Training**
Thông tin huấn luyện:

- Batch size: 16

- Epochs: 20

- Learning rate: 0.001

Tích hợp CBAM vào YOLOv8 để tăng độ chính xác.

Chạy huấn luyện:

- python train.py --img 640 --batch 16 --epochs 20 --data data.yaml --cfg yolo_cbam.yaml --weights yolov8n.pt --name yolo_cbam_traffic
Mô hình được lưu tại runs/train/yolo_cbam_traffic/weights/best.pt

**6. Inference**
Thực hiện dự đoán ảnh hoặc video:

- python detect.py --weights runs/train/yolo_cbam_traffic/weights/best.pt --source path_to_image_or_video
Kết quả sẽ hiển thị bounding boxes và nhãn phương tiện.

**7. Model Architecture**
- Backbone: YOLOv8 + CBAM

CBAM gồm:

- Channel Attention: tập trung vào kênh đặc trưng nổi bật.

- Spatial Attention: nhấn mạnh vùng ảnh chứa đối tượng.

- Head: YOLO detection head với các chỉ số loss và mAP được tính toán.

**8. Results**
- mAP@0.5: ~0.85

- mAP@0.5:0.95: >0.6

- Precision và Recall ổn định, không có hiện tượng overfitting.

- Mô hình hoạt động tốt với các ảnh giao thông thực tế.

**9. Deployment**
Triển khai dưới dạng ứng dụng web:

- Kiến trúc hệ thống:
Frontend (React) ←→ Backend (Flask) ←→ MongoDB
- Chức năng chính:
Xác thực người dùng (JWT).

- Phát hiện đối tượng từ ảnh/video upload.

- Lưu và hiển thị lịch sử kết quả theo user.

- Chạy backend:

cd backend
python app.py
- Chạy frontend:


cd frontend
npm install
npm start

**10. Troubleshooting**
- Không phát hiện ảnh: Kiểm tra format ảnh hoặc dữ liệu đầu vào.

- CUDA/PyTorch lỗi: Cài lại PyTorch phù hợp GPU.

- Ứng dụng web lỗi: Kiểm tra kết nối giữa Flask ↔ MongoDB ↔ React.

