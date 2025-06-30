# Hệ Số Địa Lý - Location Scorer

## 📍 Tổng Quan

Module `location_scorer.py` được thiết kế để cải thiện độ chính xác của dự đoán giá nhà bằng cách tích hợp thông tin địa lý từ Mapbox API. Hệ thống đánh giá vị trí dựa trên khoảng cách đến các tiện ích quan trọng và điều chỉnh giá dự đoán tương ứng.

## 🎯 Tính Năng Chính

### 1. **Phân Tích Vị Trí**
- **Trường học**: Đánh giá khoảng cách đến các trường học, đại học (tối đa 5km)
- **Bệnh viện**: Đánh giá khoảng cách đến bệnh viện, phòng khám (tối đa 10km)
- **Giao thông**: Đánh giá khoảng cách đến trạm xe buýt, giao thông công cộng (tối đa 2km)
- **Trung tâm thành phố**: Đánh giá khoảng cách đến trung tâm (tối đa 15km)

### 2. **Tính Toán Điểm Số**
- Mỗi tiện ích được đánh giá từ 0.1 đến 1.0
- Điểm tổng thể = trung bình của 4 tiện ích
- Càng gần tiện ích → điểm càng cao

### 3. **Điều Chỉnh Giá**
- Công thức: `final_price = predicted_price * (0.7 + 0.3 * location_score)`
- Nếu score = 1.0 → giữ nguyên giá (nhân 1.0)
- Nếu score = 0.0 → giảm 30% giá (nhân 0.7)

## 🔧 Cách Sử Dụng

### 1. **Import Module**
```python
from location_scorer import get_location_adjusted_price
```

### 2. **Sử Dụng Cơ Bản**
```python
# Token Mapbox
MAPBOX_TOKEN = "your_mapbox_token_here"

# Lấy giá đã điều chỉnh
result = get_location_adjusted_price(
    predicted_price=10.0,  # Giá dự đoán gốc (tỷ VND)
    address="123 Nguyễn Huệ",
    province="TP.HCM",
    district="Quận 1",
    mapbox_token=MAPBOX_TOKEN
)

# Kết quả
print(f"Giá cuối: {result['final_price']} tỷ VND")
print(f"Điểm vị trí: {result['location_analysis']['total_score']}")
```

### 3. **Kết Quả Chi Tiết**
```python
result = {
    'location_analysis': {
        'total_score': 0.75,  # Điểm tổng thể (0-1)
        'coordinates': {'lat': 10.7769, 'lng': 106.7009},
        'scores': {
            'school': 0.8,      # Điểm trường học
            'hospital': 0.7,    # Điểm bệnh viện
            'bus_station': 0.9, # Điểm giao thông
            'city_center': 0.6  # Điểm trung tâm
        }
    },
    'price_adjustment': {
        'original_price': 10.0,
        'adjusted_price': 9.25,
        'adjustment_factor': 0.925,
        'price_change_percent': -7.5
    },
    'final_price': 9.25
}
```

## 🧪 Test Module

### Chạy Test Cơ Bản
```bash
python test_location_scorer.py
```

### Test Trong Ứng Dụng
1. Chạy ứng dụng: `python app.py`
2. Truy cập: `http://localhost:5000`
3. Điền thông tin và dự đoán
4. Xem kết quả phân tích vị trí

## ⚙️ Cấu Hình

### Thay Đổi Trọng Số Tiện Ích
```python
# Trong location_scorer.py
self.amenity_types = {
    'school': {
        'weight': 0.3,        # Tăng trọng số trường học
        'max_distance': 3000  # Giảm khoảng cách tối đa
    },
    # ...
}
```

### Thay Đổi Công Thức Điều Chỉnh
```python
# Trong adjust_price_with_location()
adjustment_factor = 0.8 + 0.2 * location_score  # Thay đổi từ 0.7+0.3
```

## 🔍 API Endpoints

### Mapbox Geocoding
- **URL**: `https://api.mapbox.com/geocoding/v5/mapbox.places`
- **Chức năng**: Chuyển đổi địa chỉ thành tọa độ

### Mapbox Places
- **URL**: `https://api.mapbox.com/geocoding/v5/mapbox.places`
- **Chức năng**: Tìm kiếm tiện ích xung quanh

## 📊 Ví Dụ Kết Quả

### Vị Trí Tốt (Quận 1, TP.HCM)
```
Điểm vị trí: 85%
- Trường học: 90%
- Bệnh viện: 85%
- Giao thông: 95%
- Trung tâm: 70%
Giá điều chỉnh: +5.5%
```

### Vị Trí Xa Trung Tâm
```
Điểm vị trí: 45%
- Trường học: 60%
- Bệnh viện: 40%
- Giao thông: 30%
- Trung tâm: 50%
Giá điều chỉnh: -16.5%
```

## ⚠️ Lưu Ý

1. **Rate Limit**: Mapbox có giới hạn request, nên có delay 0.1s giữa các API call
2. **Độ Chính Xác**: Kết quả phụ thuộc vào chất lượng dữ liệu Mapbox tại Việt Nam
3. **Fallback**: Nếu API lỗi, hệ thống sẽ sử dụng giá gốc
4. **Token**: Cần có Mapbox token hợp lệ để sử dụng

## 🚀 Tích Hợp Vào Ứng Dụng

Module đã được tích hợp sẵn vào `app.py`:

1. **Import**: `from location_scorer import get_location_adjusted_price`
2. **Sử dụng**: Trong route `/predict`
3. **Hiển thị**: Kết quả phân tích trong giao diện web

## 📈 Cải Tiến Tương Lai

- [ ] Thêm đánh giá mật độ dân cư
- [ ] Tích hợp dữ liệu giao thông thời gian thực
- [ ] Thêm đánh giá môi trường (công viên, không khí)
- [ ] Machine learning cho trọng số tiện ích
- [ ] Cache kết quả để tăng tốc độ 