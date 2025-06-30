"""
Module tính toán hệ số nội thất ảnh hưởng đến giá nhà
"""

class FurnitureScorer:
    """
    Lớp tính toán hệ số nội thất dựa trên số lượng thiết bị
    """
    
    def __init__(self):
        # Định nghĩa trọng số ảnh hưởng của từng thiết bị
        self.furniture_weights = {
            'air_conditioner': {
                'weight': 0.35,  # Ảnh hưởng cao nhất
                'max_count': 10,
                'description': 'Máy lạnh'
            },
            'kitchen': {
                'weight': 0.30,  # Ảnh hưởng cao
                'max_count': 5,
                'description': 'Bếp (gas/điện)'
            },
            'washing_machine': {
                'weight': 0.20,  # Ảnh hưởng vừa
                'max_count': 5,
                'description': 'Máy giặt'
            },
            'wardrobe': {
                'weight': 0.15,  # Ảnh hưởng thấp nhất
                'max_count': 10,
                'description': 'Tủ (âm tường)'
            }
        }
    
    def calculate_furniture_score(self, furniture_data: dict) -> dict:
        """
        Tính toán điểm số nội thất dựa trên số lượng thiết bị
        
        Args:
            furniture_data: Dict chứa số lượng từng thiết bị
                {
                    'air_conditioner': int,
                    'kitchen': int,
                    'washing_machine': int,
                    'wardrobe': int
                }
        
        Returns:
            Dict chứa kết quả tính toán
        """
        try:
            scores = {}
            total_score = 0
            total_weight = 0
            
            for furniture_type, config in self.furniture_weights.items():
                count = furniture_data.get(furniture_type, 0)
                max_count = config['max_count']
                weight = config['weight']
                
                # Tính điểm cho từng thiết bị (0-1)
                if max_count > 0:
                    # Điểm tăng theo số lượng nhưng có giới hạn
                    # Công thức: min(1.0, count / max_count * 1.5)
                    # Cho phép vượt quá 100% nếu có nhiều thiết bị
                    score = min(1.0, (count / max_count) * 1.5)
                else:
                    score = 0.0
                
                scores[furniture_type] = {
                    'count': count,
                    'score': score,
                    'weight': weight,
                    'weighted_score': score * weight,
                    'description': config['description'],
                    'max_count': max_count
                }
                
                total_score += score * weight
                total_weight += weight
            
            # Điểm tổng thể (0-1)
            overall_score = total_score / total_weight if total_weight > 0 else 0.0
            
            return {
                'overall_score': overall_score,
                'scores': scores,
                'total_weight': total_weight,
                'furniture_summary': self._generate_summary(scores)
            }
            
        except Exception as e:
            print(f"Lỗi khi tính điểm nội thất: {e}")
            return {
                'overall_score': 0.5,
                'scores': {},
                'total_weight': 1.0,
                'furniture_summary': 'Không thể tính toán',
                'error': str(e)
            }
    
    def adjust_price_with_furniture(self, base_price: float, furniture_score: float) -> dict:
        """
        Điều chỉnh giá dựa trên điểm số nội thất
        
        Args:
            base_price: Giá cơ bản (tỷ VND)
            furniture_score: Điểm số nội thất (0-1)
        
        Returns:
            Dict chứa thông tin điều chỉnh giá
        """
        try:
            # Công thức điều chỉnh:
            # - Nếu score = 0 (không có nội thất): giảm 15%
            # - Nếu score = 0.5 (nội thất trung bình): giữ nguyên
            # - Nếu score = 1.0 (nội thất đầy đủ): tăng 20%
            
            # Hệ số điều chỉnh từ 0.85 đến 1.20
            adjustment_factor = 0.85 + (furniture_score * 0.35)
            adjusted_price = base_price * adjustment_factor
            
            return {
                'base_price': base_price,
                'furniture_score': furniture_score,
                'adjustment_factor': adjustment_factor,
                'adjusted_price': adjusted_price,
                'price_change': adjusted_price - base_price,
                'price_change_percent': ((adjusted_price - base_price) / base_price) * 100
            }
            
        except Exception as e:
            print(f"Lỗi khi điều chỉnh giá theo nội thất: {e}")
            return {
                'base_price': base_price,
                'furniture_score': 0.5,
                'adjustment_factor': 1.0,
                'adjusted_price': base_price,
                'price_change': 0,
                'price_change_percent': 0,
                'error': str(e)
            }
    
    def _generate_summary(self, scores: dict) -> str:
        """
        Tạo tóm tắt về nội thất
        """
        summary_parts = []
        
        for furniture_type, data in scores.items():
            if data['count'] > 0:
                summary_parts.append(f"{data['description']}: {data['count']} cái")
        
        if summary_parts:
            return ", ".join(summary_parts)
        else:
            return "Không có nội thất"
    
    def get_furniture_recommendations(self, scores: dict) -> list:
        """
        Đưa ra khuyến nghị về nội thất
        """
        recommendations = []
        
        for furniture_type, data in scores.items():
            if data['count'] == 0:
                # Khuyến nghị thêm nếu chưa có
                if furniture_type == 'air_conditioner':
                    recommendations.append("Nên lắp đặt máy lạnh để tăng giá trị")
                elif furniture_type == 'kitchen':
                    recommendations.append("Nên trang bị bếp để tăng giá trị")
                elif furniture_type == 'washing_machine':
                    recommendations.append("Có thể thêm máy giặt để tăng tiện ích")
                elif furniture_type == 'wardrobe':
                    recommendations.append("Có thể thêm tủ âm tường để tăng giá trị")
            elif data['count'] < data['max_count'] * 0.5:
                # Khuyến nghị tăng số lượng nếu còn ít
                recommendations.append(f"Có thể tăng số lượng {data['description']} để tối ưu giá trị")
        
        return recommendations

# Hàm tiện ích để sử dụng
def get_furniture_adjusted_price(base_price: float, furniture_data: dict) -> dict:
    """
    Hàm tiện ích để lấy giá đã điều chỉnh theo nội thất
    
    Args:
        base_price: Giá cơ bản (tỷ VND)
        furniture_data: Dict chứa số lượng thiết bị
    
    Returns:
        Dict chứa kết quả phân tích và giá đã điều chỉnh
    """
    scorer = FurnitureScorer()
    
    # Tính điểm nội thất
    furniture_result = scorer.calculate_furniture_score(furniture_data)
    
    # Điều chỉnh giá
    price_result = scorer.adjust_price_with_furniture(base_price, furniture_result['overall_score'])
    
    # Kết hợp kết quả
    return {
        'furniture_analysis': furniture_result,
        'price_adjustment': price_result,
        'final_price': price_result['adjusted_price'],
        'recommendations': scorer.get_furniture_recommendations(furniture_result['scores'])
    }

# Test function
if __name__ == "__main__":
    # Test với dữ liệu mẫu
    test_furniture = {
        'air_conditioner': 2,
        'kitchen': 1,
        'washing_machine': 1,
        'wardrobe': 3
    }
    
    test_price = 10.0  # 10 tỷ VND
    
    print("=== Test Furniture Scorer ===")
    result = get_furniture_adjusted_price(test_price, test_furniture)
    
    print(f"Điểm nội thất tổng thể: {result['furniture_analysis']['overall_score']:.3f}")
    print(f"Tóm tắt nội thất: {result['furniture_analysis']['furniture_summary']}")
    print(f"Giá cơ bản: {result['price_adjustment']['base_price']} tỷ VND")
    print(f"Hệ số điều chỉnh: {result['price_adjustment']['adjustment_factor']:.3f}")
    print(f"Giá sau điều chỉnh: {result['price_adjustment']['adjusted_price']:.2f} tỷ VND")
    print(f"Thay đổi: {result['price_adjustment']['price_change_percent']:+.1f}%")
    
    if result['recommendations']:
        print("\nKhuyến nghị:")
        for rec in result['recommendations']:
            print(f"- {rec}") 