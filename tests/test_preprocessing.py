import pandas as pd
import pytest
from sklearn.pipeline import Pipeline
from src.preprocessing.detector import detect_features
from src.preprocessing.pipeline import build_preprocessor

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'num1': [1, 2, 3, 4, None],
        'num2': [10.5, 20.1, 30.2, 40.8, 50.9],
        'cat1': ['A', 'B', 'A', 'C', 'B'],
        'bool1': [True, False, True, False, True],
        'target': [0, 1, 0, 1, 0],
        'id_col': ['id1', 'id2', 'id3', 'id4', 'id5']
    })

def test_feature_detection(sample_data):
    features = detect_features(sample_data, target_col='target', drop_cols=['id_col'])
    
    assert 'num1' in features['numeric']
    assert 'num2' in features['numeric']
    assert 'cat1' in features['categorical']
    assert 'bool1' in features['boolean']
    
    # Target and IDs should be excluded
    assert 'target' not in features['numeric']
    assert 'id_col' not in features['categorical']

def test_preprocessing_pipeline(sample_data):
    features = detect_features(sample_data, target_col='target', drop_cols=['id_col'])
    
    X = sample_data.drop(columns=['target', 'id_col'])
    y = sample_data['target']
    
    preprocessor = build_preprocessor(features)
    
    # Pipeline should fit and transform without error
    preprocessor.fit(X, y)
    X_transformed = preprocessor.transform(X)
    
    # Check that transformation occurred (shape should change due to one-hot encoding cat1)
    # 2 numeric, 1 boolean, 3 categories for cat1 = 6 features expected
    # VarianceThreshold should keep all of them unless a column has 0 variance
    assert X_transformed.shape[1] > X.shape[1]
