from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import pandas as pd
import numpy as np
import joblib
import os
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Hàm chuyển đổi tên loại nhà
def convert_house_type(type_name, to_vietnamese=True):
    mapping = {
        'Apartment': 'Căn Hộ',
        'Villa': 'Biệt Thự',
        'Townhouse': 'Nhà Phố',
        'Nha cap 4': 'Nhà Cấp 4'
    }
    if to_vietnamese:
        return mapping.get(type_name, type_name)
    else:
        reverse_mapping = {v: k for k, v in mapping.items()}
        return reverse_mapping.get(type_name, type_name)

# Import module hệ số địa lý
from location_scorer import get_location_adjusted_price

# Import module hệ số nội thất
from furniture_scorer import get_furniture_adjusted_price

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Token Mapbox
MAPBOX_TOKEN = "pk.eyJ1Ijoia2hkdXktejUiLCJhIjoiY21iNnQwN3NiMDByNjJrcHR0cGowbHRsaCJ9.jhNI4EwNZZin9d2STOdCOQ"

# Biến global để lưu trạng thái mô hình
model_status = {
    'is_trained': False,
    'training_date': None,
    'model_accuracy': None,
    'feature_importance': None
}

def load_model_and_encoders():
    """Tải mô hình và encoders nếu có"""
    try:
        if os.path.exists('model.pkl') and os.path.exists('feature_encoders.pkl'):
            model = joblib.load('model.pkl')
            encoders = joblib.load('feature_encoders.pkl')
            return model, encoders
        return None, None
    except Exception as e:
        print(f"Lỗi khi tải mô hình: {e}")
        return None, None

def get_unique_values():
    """Lấy các giá trị duy nhất cho dropdown"""
    try:
        df = pd.read_csv("Dataset_house.csv", encoding='utf-8', sep=';')
        # Chuyển đổi các giá trị TypeHouse sang tiếng Việt
        type_house_values = [convert_house_type(t) for t in df['TypeHouse'].unique()]
        return {
            'type_house': sorted(type_house_values),
            'legal_status': sorted(df['Legal_Status'].unique().tolist()),
            'road_type': sorted(df['Road_Type'].unique().tolist())
        }
    except Exception as e:
        print(f"Lỗi khi đọc dữ liệu: {e}")
        return {
            'type_house': ['Căn Hộ', 'Nhà Phố', 'Biệt Thự', 'Nhà Cấp 4'],
            'legal_status': ['Đã có Sổ Hồng/Sổ Đỏ', 'Đang chờ Sổ / Đang làm thủ tục cấp sổ', 'Đang thế chấp ngân hàng', 'Nằm trong diện quy hoạch', 'Sở hữu theo hợp đồng mua bán/giấy tờ viết tay'],
            'road_type': ['Đường chính', 'Đường nhánh', 'Ngõ rộng', 'Ngõ nhỏ', 'Đường cao tốc']
        }

def load_location_data():
    """Tải dữ liệu địa điểm từ file CSV"""
    try:
        df = pd.read_csv("huyen_tinh_gia.csv", encoding='utf-8')
        return df
    except Exception as e:
        print(f"Lỗi khi đọc file địa điểm: {e}")
        return pd.DataFrame()

def get_provinces():
    """Lấy danh sách các tỉnh/thành phố"""
    try:
        df = load_location_data()
        if not df.empty:
            provinces = sorted(df['Tỉnh'].unique().tolist())
            return provinces
        return []
    except Exception as e:
        print(f"Lỗi khi lấy danh sách tỉnh: {e}")
        return []

def get_districts(province):
    """Lấy danh sách quận/huyện theo tỉnh/thành phố"""
    try:
        df = load_location_data()
        if not df.empty:
            districts = df[df['Tỉnh'] == province]['Huyện'].unique().tolist()
            return sorted(districts)
        return []
    except Exception as e:
        print(f"Lỗi khi lấy danh sách huyện: {e}")
        return []

def get_average_price(province, district):
    """Lấy giá trung bình theo tỉnh và huyện"""
    try:
        df = load_location_data()
        if not df.empty:
            price_data = df[(df['Tỉnh'] == province) & (df['Huyện'] == district)]
            if not price_data.empty:
                return float(price_data['Giá trung bình (triệu đồng/m2)'].iloc[0])
        return None
    except Exception as e:
        print(f"Lỗi khi lấy giá trung bình: {e}")
        return None

@app.route('/')
def index():
    """Trang chủ"""
    model, encoders = load_model_and_encoders()
    model_status['is_trained'] = model is not None
    
    unique_values = get_unique_values()
    provinces = get_provinces()
    
    return render_template('index.html', 
                         model_status=model_status,
                         unique_values=unique_values,
                         provinces=provinces)

@app.route('/predict', methods=['POST'])
def predict():
    """Dự đoán giá nhà"""
    try:
        # Tải mô hình và encoders
        model, encoders = load_model_and_encoders()
        if model is None or encoders is None:
            return jsonify({'success': False, 'message': 'Mô hình chưa được huấn luyện. Vui lòng huấn luyện mô hình trước.'})
        
        # Lấy dữ liệu từ form
        data = request.get_json()
        
        # Chuẩn bị dữ liệu đầu vào
        input_data = {
            'Province': data.get('province', ''),
            'District': data.get('district', ''),
            'Address': data.get('address', ''),
            'TypeHouse': convert_house_type(data['type_house'], to_vietnamese=False),
            'Legal_Status': data['legal_status'],
            'Road_Type': data['road_type'],
            'Area': float(data['area']),
            'Frontage': float(data['frontage']),
            'Floors': int(data['floors']),
            'Bedrooms': int(data['bedrooms']),
            'Bathrooms': int(data['bathrooms']),
            'YearBuilt': int(data['year_built']),
            'Gia_trung_binh': float(data['gia_trung_binh'])
        }
        
        # Dữ liệu nội thất
        furniture_data = {
            'air_conditioner': int(data.get('air_conditioner', 0)),
            'kitchen': int(data.get('kitchen', 0)),
            'washing_machine': int(data.get('washing_machine', 0)),
            'wardrobe': int(data.get('wardrobe', 0))
        }
        
        # Mã hóa các biến phân loại
        encoded_data = {}
        for col in ['TypeHouse', 'Legal_Status', 'Road_Type']:
            if col in encoders:
                encoded_data[f'{col}_encoded'] = encoders[col].transform([input_data[col]])[0]
        
        # Tạo feature vector
        features = [
            input_data['Area'],
            input_data['Frontage'],
            input_data['Floors'],
            input_data['Bedrooms'],
            input_data['Bathrooms'],
            input_data['YearBuilt'],
            input_data['Gia_trung_binh'],
            encoded_data['TypeHouse_encoded'],
            encoded_data['Legal_Status_encoded'],
            encoded_data['Road_Type_encoded']
        ]
        
        # Dự đoán
        prediction = model.predict([features])[0]
        
        # Format kết quả với địa chỉ
        formatted_prediction = f"{prediction:.2f} tỷ VND"
        
        # Tạo thông tin chi tiết
        details = {
            'address': input_data['Address'],
            'district': input_data['District'],
            'province': input_data['Province'],
            'type_house': input_data['TypeHouse'],
            'area': input_data['Area'],
            'prediction': formatted_prediction,
            'raw_prediction': round(prediction, 2),
            'furniture_data': furniture_data
        }
        
        # Tích hợp hệ số địa lý
        try:
            location_result = get_location_adjusted_price(
                predicted_price=prediction,
                address=input_data['Address'],
                province=input_data['Province'],
                district=input_data['District'],
                mapbox_token=MAPBOX_TOKEN
            )
            
            # Cập nhật thông tin chi tiết với kết quả phân tích vị trí
            details['location_analysis'] = location_result['location_analysis']
            details['price_adjustment_location'] = location_result['price_adjustment']
            
            # Lấy giá sau điều chỉnh vị trí
            location_adjusted_price = location_result['final_price']
            
        except Exception as e:
            # Nếu có lỗi, sử dụng giá gốc
            details['location_analysis'] = {'error': str(e)}
            details['price_adjustment_location'] = {
                'original_price': prediction,
                'adjusted_price': prediction,
                'price_change_percent': 0
            }
            location_adjusted_price = prediction
        
        # Tích hợp hệ số nội thất
        try:
            furniture_result = get_furniture_adjusted_price(
                base_price=location_adjusted_price,
                furniture_data=furniture_data
            )
            
            # Cập nhật thông tin chi tiết với kết quả phân tích nội thất
            details['furniture_analysis'] = furniture_result['furniture_analysis']
            details['price_adjustment_furniture'] = furniture_result['price_adjustment']
            details['furniture_recommendations'] = furniture_result['recommendations']
            
            # Giá cuối cùng sau cả hai điều chỉnh
            final_price = furniture_result['final_price']
            
        except Exception as e:
            # Nếu có lỗi, sử dụng giá sau điều chỉnh vị trí
            details['furniture_analysis'] = {'error': str(e)}
            details['price_adjustment_furniture'] = {
                'base_price': location_adjusted_price,
                'adjusted_price': location_adjusted_price,
                'price_change_percent': 0
            }
            details['furniture_recommendations'] = []
            final_price = location_adjusted_price
        
        # Format giá cuối cùng
        final_formatted_price = f"{final_price:.2f} tỷ VND"
        
        return jsonify({
            'success': True,
            'prediction': formatted_prediction,
            'final_prediction': final_formatted_price,
            'raw_prediction': round(prediction, 2),
            'details': details
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi khi dự đoán: {str(e)}'})

@app.route('/api/districts/<province>')
def get_districts_api(province):
    """API lấy danh sách quận/huyện theo tỉnh/thành phố"""
    try:
        districts = get_districts(province)
        return jsonify({
            'success': True,
            'districts': districts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })

@app.route('/api/price/<province>/<district>')
def get_price_api(province, district):
    """API lấy giá trung bình theo tỉnh và huyện"""
    try:
        price = get_average_price(province, district)
        if price is not None:
            return jsonify({
                'success': True,
                'price': price
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Không tìm thấy dữ liệu giá cho địa điểm này'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
