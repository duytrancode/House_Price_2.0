# 🏠 Hệ Thống Dự Đoán Giá Nhà - AI

Ứng dụng web sử dụng học máy để dự đoán giá bất động sản dựa trên các đặc trưng của ngôi nhà.

## ✨ Tính Năng

- **Huấn luyện mô hình**: Sử dụng thuật toán Random Forest để huấn luyện mô hình dự đoán
- **Dự đoán giá nhà**: Nhập thông tin nhà và nhận dự đoán giá chính xác
- **Giao diện đẹp**: Thiết kế hiện đại, responsive và thân thiện người dùng
- **Thông tin mô hình**: Xem độ chính xác và độ quan trọng của các đặc trưng
- **Thống kê dữ liệu**: Hiển thị thông tin về dataset và khoảng giá

## 🚀 Cài Đặt và Chạy

### 1. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 2. Chạy ứng dụng

```bash
python app.py
```

### 3. Truy cập ứng dụng

Mở trình duyệt và truy cập: `http://localhost:5000`

## 📊 Dữ Liệu

Ứng dụng sử dụng dataset `Dataset_house.csv` với các cột:

- **TypeHouse**: Loại nhà (Apartment, Townhouse, Villa, Nha cap 4)
- **Area**: Diện tích (m²)
- **Frontage**: Mặt tiền (m)
- **Floors**: Số tầng
- **Bedrooms**: Số phòng ngủ
- **Bathrooms**: Số phòng tắm
- **YearBuilt**: Năm xây dựng
- **Legal_Status**: Tình trạng pháp lý
- **Road_Type**: Loại đường
- **Price**: Giá nhà (tỷ VND)
- **Gia_trung_binh**: Giá trung bình khu vực (triệu/m²)

## 🎯 Cách Sử Dụng

### Bước 1: Huấn luyện mô hình
1. Nhấn nút "Bắt Đầu Huấn Luyện"
2. Chờ quá trình huấn luyện hoàn tất
3. Xem độ chính xác và thông tin mô hình

### Bước 2: Dự đoán giá nhà
1. Điền đầy đủ thông tin nhà vào form
2. Nhấn "Dự Đoán Giá"
3. Xem kết quả dự đoán

### Bước 3: Xem thông tin chi tiết
- Nhấn "Xem Thông Tin" để xem thống kê dataset
- Xem độ quan trọng của các đặc trưng

## 🛠️ Công Nghệ Sử Dụng

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Machine Learning**: Scikit-learn (Random Forest)
- **Data Processing**: Pandas, NumPy
- **Model Persistence**: Joblib

## 📁 Cấu Trúc Dự Án

```
House_Price_2.0/
├── app.py                 # Ứng dụng Flask chính
├── training_modul.py      # Module huấn luyện mô hình
├── Dataset_house.csv      # Dataset huấn luyện
├── requirements.txt       # Thư viện cần thiết
├── README.md             # Hướng dẫn sử dụng
├── templates/
│   └── index.html        # Giao diện web
├── model.pkl             # Mô hình đã huấn luyện (tự động tạo)
└── feature_encoders.pkl  # Encoders cho biến phân loại (tự động tạo)
```

## 🎨 Giao Diện

- **Thiết kế hiện đại**: Gradient background, card layout
- **Responsive**: Tương thích với mọi thiết bị
- **Animation**: Hiệu ứng hover và transition mượt mà
- **Loading states**: Hiển thị trạng thái đang xử lý
- **Alert system**: Thông báo kết quả và lỗi

## 🔧 Tùy Chỉnh

### Thay đổi thuật toán
Chỉnh sửa file `training_modul.py` để thay đổi thuật toán học máy:

```python
# Thay đổi từ Random Forest sang XGBoost
from xgboost import XGBRegressor
model = XGBRegressor()
```

### Thêm đặc trưng mới
1. Cập nhật dataset với cột mới
2. Chỉnh sửa `feature_columns` trong `training_modul.py`
3. Cập nhật form trong `templates/index.html`

## 📈 Hiệu Suất

- **Độ chính xác**: Thường đạt 85-95% R² score
- **Thời gian huấn luyện**: ~10-30 giây tùy thuộc vào dataset
- **Thời gian dự đoán**: <1 giây

## 🤝 Đóng Góp

1. Fork dự án
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📄 Giấy Phép

Dự án này được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.

## 📞 Liên Hệ

Nếu có câu hỏi hoặc góp ý, vui lòng tạo issue trên GitHub.

---

**Lưu ý**: Đây là dự án demo cho mục đích học tập. Kết quả dự đoán chỉ mang tính chất tham khảo và không nên sử dụng cho mục đích thương mại mà không có đánh giá chuyên môn. 