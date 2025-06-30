import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import warnings
warnings.filterwarnings('ignore')

# ===== BƯỚC 1: TẢI VÀ TIỀN XỬ LÝ DỮ LIỆU =====
def load_and_preprocess_data():
    try:
        # Đọc dữ liệu dùng phân tách dấu ';'
        df = pd.read_csv("Dataset_house.csv", encoding='utf-8', sep=';')
        print("✅ Đã tải dữ liệu thành công")
        print(f"Số lượng mẫu: {len(df)}")

        # Loại bỏ cột 'Address' nếu không dùng
        df = df.drop(columns=['Address'], errors='ignore')

        # Đảm bảo cột YearBuilt là số nguyên
        df['YearBuilt'] = pd.to_numeric(df['YearBuilt'], errors='coerce')
        df['YearBuilt'] = df['YearBuilt'].fillna(df['YearBuilt'].mode()[0]).astype(int)

        # Các cột số và phân loại
        numeric_columns = ['Area', 'Frontage', 'Floors', 'Bedrooms', 'Bathrooms', 'YearBuilt', 'Gia_trung_binh', 'Price']
        categorical_columns = ['TypeHouse', 'Legal_Status', 'Road_Type']

        # Xử lý cột số
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(df[col].mean())

        # Xử lý cột phân loại
        for col in categorical_columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].fillna('Unknown')

        # Mã hóa các biến phân loại bằng LabelEncoder
        encoders = {}
        for col in categorical_columns:
            le = LabelEncoder()
            df[f'{col}_encoded'] = le.fit_transform(df[col])
            encoders[col] = le

        # Lưu encoders
        joblib.dump(encoders, 'feature_encoders.pkl')

        return df

    except Exception as e:
        print(f"❌ Lỗi khi xử lý dữ liệu: {str(e)}")
        raise

# ===== BƯỚC 2: CHUẨN BỊ DỮ LIỆU =====
def prepare_features(df):
    feature_columns = [
        'Area', 'Frontage', 'Floors', 'Bedrooms', 'Bathrooms', 'YearBuilt', 'Gia_trung_binh',
        'TypeHouse_encoded', 'Legal_Status_encoded', 'Road_Type_encoded'
    ]
    X = df[feature_columns]
    y = df['Price']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test

# ===== BƯỚC 3: HUẤN LUYỆN MÔ HÌNH =====
def train_model(X_train, y_train):
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    print("\n🔄 Đang huấn luyện mô hình...")
    model.fit(X_train, y_train)
    return model

# ===== BƯỚC 4: ĐÁNH GIÁ MÔ HÌNH =====
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    print("\n===== ĐÁNH GIÁ MÔ HÌNH =====")
    print(f"Root Mean Squared Error: {rmse:.2f}")
    print(f"R² Score: {r2:.2f}")

    # In độ quan trọng đặc trưng
    feature_importance = pd.DataFrame({
        'Feature': X_test.columns,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    print("\n🎯 Độ quan trọng các đặc trưng:")
    print(feature_importance)

# ===== BƯỚC 5: LƯU MÔ HÌNH =====
def save_model(model):
    try:
        joblib.dump(model, 'model.pkl')
        print("\n✅ Đã lưu mô hình thành công")
    except Exception as e:
        print(f"❌ Lỗi khi lưu mô hình: {str(e)}")

# ===== QUY TRÌNH CHÍNH =====
def main():
    try:
        df = load_and_preprocess_data()
        X_train, X_test, y_train, y_test = prepare_features(df)
        model = train_model(X_train, y_train)
        evaluate_model(model, X_test, y_test)
        save_model(model)
    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình huấn luyện: {str(e)}")

if __name__ == '__main__':
    main()
