import requests
import json
import time
from typing import Dict, List, Tuple, Optional
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocationScorer:
    """
    Lớp tính toán hệ số địa lý dựa trên Mapbox API
    Đánh giá vị trí dựa trên khoảng cách đến các tiện ích quan trọng
    """
    
    def __init__(self, mapbox_token: str):
        self.mapbox_token = mapbox_token
        self.base_url = "https://api.mapbox.com/geocoding/v5/mapbox.places"
        self.directions_url = "https://api.mapbox.com/directions/v5/mapbox/driving"
        
        # Định nghĩa các loại tiện ích và trọng số
        self.amenity_types = {
            'school': {
                'keywords': ['school', 'university', 'college', 'education'],
                'weight': 0.25,
                'max_distance': 5000  # 5km
            },
            'hospital': {
                'keywords': ['hospital', 'clinic', 'medical', 'health'],
                'weight': 0.25,
                'max_distance': 10000  # 10km
            },
            'bus_station': {
                'keywords': ['bus', 'transit', 'transportation'],
                'weight': 0.25,
                'max_distance': 2000  # 2km
            },
            'city_center': {
                'keywords': ['city center', 'downtown', 'central'],
                'weight': 0.25,
                'max_distance': 15000  # 15km
            }
        }
    
    def geocode_address(self, address: str, province: str, district: str) -> Optional[Tuple[float, float]]:
        """
        Chuyển đổi địa chỉ thành tọa độ (latitude, longitude)
        """
        try:
            # Tạo query string với địa chỉ đầy đủ
            full_address = f"{address}, {district}, {province}, Vietnam"
            
            params = {
                'access_token': self.mapbox_token,
                'query': full_address,
                'country': 'vn',
                'limit': 1
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['features']:
                coordinates = data['features'][0]['center']
                # Mapbox trả về [longitude, latitude], chuyển thành [latitude, longitude]
                return coordinates[1], coordinates[0]
            else:
                logger.warning(f"Không tìm thấy tọa độ cho địa chỉ: {full_address}")
                return self.get_fallback_coordinates(province, district)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi kết nối Mapbox API: {e}")
            # Fallback: sử dụng tọa độ mặc định cho các thành phố lớn
            return self.get_fallback_coordinates(province, district)
        except Exception as e:
            logger.error(f"Lỗi khi geocode địa chỉ: {e}")
            return self.get_fallback_coordinates(province, district)
    
    def get_fallback_coordinates(self, province: str, district: str) -> Optional[Tuple[float, float]]:
        """
        Lấy tọa độ mặc định cho các thành phố lớn khi API không hoạt động
        """
        fallback_coords = {
            'TP.HCM': {
                'Quận 1': (10.7769, 106.7009),
                'Quận 3': (10.7829, 106.6889),
                'Quận 4': (10.7663, 106.7054),
                'Quận 5': (10.7540, 106.6634),
                'Quận 6': (10.7465, 106.6492),
                'Quận 7': (10.7323, 106.7265),
                'Quận 8': (10.7243, 106.6286),
                'Quận 10': (10.7626, 106.6602),
                'Quận 11': (10.7639, 106.6434),
                'Quận 12': (10.8633, 106.6544),
                'Bình Tân': (10.7656, 106.6033),
                'Bình Thạnh': (10.8014, 106.7148),
                'Gò Vấp': (10.8385, 106.6650),
                'Phú Nhuận': (10.7948, 106.6752),
                'Tân Bình': (10.8011, 106.6526),
                'Tân Phú': (10.7905, 106.6282),
                'Thủ Đức': (10.8494, 106.7537),
                'Bình Chánh': (10.6874, 106.5967),
                'Cần Giờ': (10.5083, 106.8638),
                'Củ Chi': (11.0065, 106.5142),
                'Hóc Môn': (10.8845, 106.5952),
                'Nhà Bè': (10.6952, 106.7292)
            },
            'Hà Nội': {
                'Ba Đình': (21.0352, 105.8342),
                'Hoàn Kiếm': (21.0278, 105.8342),
                'Tây Hồ': (21.0781, 105.8184),
                'Long Biên': (21.0388, 105.8834),
                'Cầu Giấy': (21.0367, 105.7896),
                'Đống Đa': (21.0198, 105.8154),
                'Hai Bà Trưng': (21.0160, 105.8412),
                'Hoàng Mai': (20.9831, 105.8444),
                'Thanh Xuân': (21.0031, 105.8012),
                'Hà Đông': (20.9714, 105.7787),
                'Bắc Từ Liêm': (21.0781, 105.7733),
                'Nam Từ Liêm': (21.0031, 105.7733)
            },
            'Đà Nẵng': {
                'Hải Châu': (16.0544, 108.2022),
                'Thanh Khê': (16.0665, 108.1911),
                'Sơn Trà': (16.1061, 108.2411),
                'Ngũ Hành Sơn': (15.9850, 108.2545),
                'Liên Chiểu': (16.1392, 108.1506),
                'Cẩm Lệ': (16.0167, 108.2167),
                'Hòa Vang': (16.0167, 108.0167)
            }
        }
        
        if province in fallback_coords:
            if district in fallback_coords[province]:
                logger.info(f"Sử dụng tọa độ fallback cho {district}, {province}")
                return fallback_coords[province][district]
            else:
                # Lấy tọa độ đầu tiên của tỉnh
                first_district = list(fallback_coords[province].keys())[0]
                logger.info(f"Sử dụng tọa độ fallback cho {first_district}, {province}")
                return fallback_coords[province][first_district]
        
        # Tọa độ mặc định cho Việt Nam
        logger.info("Sử dụng tọa độ mặc định cho Việt Nam")
        return (16.0544, 108.2022)  # Đà Nẵng
    
    def find_nearby_amenities(self, lat: float, lng: float, amenity_type: str) -> float:
        """
        Tìm kiếm tiện ích gần nhất và tính điểm dựa trên khoảng cách
        """
        try:
            amenity_config = self.amenity_types[amenity_type]
            
            # Tạo query để tìm kiếm tiện ích
            query = f"{amenity_type} near {lat},{lng}"
            
            params = {
                'access_token': self.mapbox_token,
                'query': query,
                'proximity': f"{lng},{lat}",
                'limit': 5,
                'types': 'poi'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data['features']:
                return self.get_fallback_amenity_score(amenity_type, lat, lng)
            
            # Tính khoảng cách đến tiện ích gần nhất
            min_distance = float('inf')
            
            for feature in data['features']:
                if 'center' in feature:
                    poi_lng, poi_lat = feature['center']
                    
                    # Tính khoảng cách Euclidean (đơn giản)
                    distance = self.calculate_distance(lat, lng, poi_lat, poi_lng)
                    
                    if distance < min_distance:
                        min_distance = distance
            
            # Tính điểm dựa trên khoảng cách
            max_distance = amenity_config['max_distance']
            if min_distance <= max_distance:
                # Điểm từ 1.0 (rất gần) đến 0.1 (xa nhất)
                score = 1.0 - (min_distance / max_distance) * 0.9
                return max(0.1, score)
            else:
                return 0.1
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi kết nối khi tìm tiện ích {amenity_type}: {e}")
            return self.get_fallback_amenity_score(amenity_type, lat, lng)
        except Exception as e:
            logger.error(f"Lỗi khi tìm tiện ích {amenity_type}: {e}")
            return self.get_fallback_amenity_score(amenity_type, lat, lng)
    
    def get_fallback_amenity_score(self, amenity_type: str, lat: float, lng: float) -> float:
        """
        Tính điểm fallback cho tiện ích dựa trên vị trí địa lý
        """
        # Điểm mặc định dựa trên loại tiện ích và vị trí
        base_scores = {
            'school': 0.7,      # Trường học thường có nhiều
            'hospital': 0.6,    # Bệnh viện ít hơn
            'bus_station': 0.8, # Giao thông công cộng phổ biến
            'city_center': 0.5  # Trung tâm tùy thuộc vào vị trí
        }
        
        base_score = base_scores.get(amenity_type, 0.5)
        
        # Điều chỉnh dựa trên vị trí (ví dụ: TP.HCM có nhiều tiện ích hơn)
        if lat > 10 and lat < 11 and lng > 106 and lng < 107:  # Khu vực TP.HCM
            if amenity_type == 'city_center':
                return 0.8  # TP.HCM có nhiều trung tâm
            elif amenity_type == 'bus_station':
                return 0.9  # Giao thông công cộng tốt
            else:
                return min(1.0, base_score + 0.2)
        
        elif lat > 20 and lat < 21 and lng > 105 and lng < 106:  # Khu vực Hà Nội
            if amenity_type == 'city_center':
                return 0.7  # Hà Nội có trung tâm
            elif amenity_type == 'bus_station':
                return 0.8  # Giao thông công cộng khá
            else:
                return min(1.0, base_score + 0.1)
        
        else:  # Các tỉnh khác
            return base_score
    
    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Tính khoảng cách Euclidean giữa hai điểm (đơn giản)
        Trong thực tế nên dùng Haversine formula cho khoảng cách thực tế
        """
        import math
        
        # Chuyển đổi sang mét (ước tính)
        lat_diff = (lat2 - lat1) * 111000  # 1 độ lat ≈ 111km
        lng_diff = (lng2 - lng1) * 111000 * math.cos(math.radians(lat1))
        
        return math.sqrt(lat_diff**2 + lng_diff**2)
    
    def calculate_location_score(self, address: str, province: str, district: str) -> Dict:
        """
        Tính toán điểm số tổng thể cho vị trí
        """
        try:
            # Geocode địa chỉ
            coordinates = self.geocode_address(address, province, district)
            
            if not coordinates:
                logger.warning("Không thể lấy tọa độ, trả về điểm mặc định")
                return {
                    'total_score': 0.5,
                    'coordinates': None,
                    'scores': {
                        'school': 0.5,
                        'hospital': 0.5,
                        'bus_station': 0.5,
                        'city_center': 0.5
                    },
                    'error': 'Không thể lấy tọa độ',
                    'using_fallback': True
                }
            
            lat, lng = coordinates
            
            # Tính điểm cho từng loại tiện ích
            scores = {}
            for amenity_type in self.amenity_types.keys():
                score = self.find_nearby_amenities(lat, lng, amenity_type)
                scores[amenity_type] = score
                
                # Delay nhỏ để tránh rate limit
                time.sleep(0.1)
            
            # Tính điểm tổng thể (trung bình có trọng số)
            total_score = sum(scores.values()) / len(scores)
            
            return {
                'total_score': total_score,
                'coordinates': {'lat': lat, 'lng': lng},
                'scores': scores,
                'error': None,
                'using_fallback': False
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi tính điểm vị trí: {e}")
            return {
                'total_score': 0.5,
                'coordinates': None,
                'scores': {
                    'school': 0.5,
                    'hospital': 0.5,
                    'bus_station': 0.5,
                    'city_center': 0.5
                },
                'error': str(e),
                'using_fallback': True
            }
    
    def adjust_price_with_location(self, predicted_price: float, location_score: float) -> Dict:
        """
        Điều chỉnh giá dự đoán dựa trên điểm số vị trí
        """
        try:
            # Công thức: final_price = predicted_price * (0.7 + 0.3 * score)
            adjustment_factor = 0.7 + 0.3 * location_score
            adjusted_price = predicted_price * adjustment_factor
            
            return {
                'original_price': predicted_price,
                'location_score': location_score,
                'adjustment_factor': adjustment_factor,
                'adjusted_price': adjusted_price,
                'price_change': adjusted_price - predicted_price,
                'price_change_percent': ((adjusted_price - predicted_price) / predicted_price) * 100
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi điều chỉnh giá: {e}")
            return {
                'original_price': predicted_price,
                'location_score': 0.5,
                'adjustment_factor': 1.0,
                'adjusted_price': predicted_price,
                'price_change': 0,
                'price_change_percent': 0,
                'error': str(e)
            }

# Hàm tiện ích để sử dụng
def get_location_adjusted_price(predicted_price: float, address: str, province: str, district: str, mapbox_token: str) -> Dict:
    """
    Hàm tiện ích để lấy giá đã điều chỉnh theo vị trí
    """
    scorer = LocationScorer(mapbox_token)
    
    # Tính điểm vị trí
    location_result = scorer.calculate_location_score(address, province, district)
    
    # Điều chỉnh giá
    price_result = scorer.adjust_price_with_location(predicted_price, location_result['total_score'])
    
    # Kết hợp kết quả
    return {
        'location_analysis': location_result,
        'price_adjustment': price_result,
        'final_price': price_result['adjusted_price']
    }

# Test function
if __name__ == "__main__":
    # Token Mapbox
    MAPBOX_TOKEN = "pk.eyJ1Ijoia2hkdXktejUiLCJhIjoiY21iNnQwN3NiMDByNjJrcHR0cGowbHRsaCJ9.jhNI4EwNZZin9d2STOdCOQ"
    
    # Test với một địa chỉ mẫu
    test_address = "123 Nguyễn Huệ"
    test_province = "TP.HCM"
    test_district = "Quận 1"
    test_price = 10.0  # 10 tỷ VND
    
    print("Đang test hệ số địa lý...")
    result = get_location_adjusted_price(test_price, test_address, test_province, test_district, MAPBOX_TOKEN)
    
    print(f"Kết quả phân tích:")
    print(f"- Điểm vị trí tổng thể: {result['location_analysis']['total_score']:.3f}")
    print(f"- Tọa độ: {result['location_analysis']['coordinates']}")
    print(f"- Điểm chi tiết: {result['location_analysis']['scores']}")
    print(f"- Giá gốc: {result['price_adjustment']['original_price']} tỷ VND")
    print(f"- Hệ số điều chỉnh: {result['price_adjustment']['adjustment_factor']:.3f}")
    print(f"- Giá sau điều chỉnh: {result['price_adjustment']['adjusted_price']:.2f} tỷ VND")
    print(f"- Thay đổi: {result['price_adjustment']['price_change_percent']:+.1f}%") 