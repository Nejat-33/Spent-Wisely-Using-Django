import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
os.makedirs(MODEL_DIR, exist_ok=True)


def _model_path(user_id):
    return os.path.join(MODEL_DIR, f'anomaly_user_{user_id}.pkl')


def _build_features(df):
    """
    Engineer features from a cleaned expense DataFrame.
    Returns feature matrix X and the enriched df.
    """
    df = df.copy()
    df['date']         = pd.to_datetime(df['date'])
    df['day_of_week']  = df['date'].dt.dayofweek     
    df['day_of_month'] = df['date'].dt.day
    df['is_weekend']   = (df['day_of_week'] >= 5).astype(int)
    df['month']        = df['date'].dt.month

    cat_stats = (
        df.groupby('category')['amount']
          .agg(['mean', 'std'])
          .rename(columns={'mean': 'cat_mean', 'std': 'cat_std'})
          .reset_index()
    )
    df = df.merge(cat_stats, on='category', how='left')
    df['cat_std']      = df['cat_std'].fillna(1).replace(0, 1)
    df['amount'] = df['amount'].astype(float)
    df['amount_zscore'] = (df['amount'] - df['cat_mean']) / df['cat_std']

    feature_cols = [
        'amount',
        'day_of_week',
        'day_of_month',
        'is_weekend',
        'month',
        'cat_mean',
        'amount_zscore',
    ]
    return df, df[feature_cols]


def train_model(user_id, expenses_qs):
    
    df = pd.DataFrame(list(expenses_qs.values(
        'id', 'amount', 'category__name', 'date', 'description'
    )))
    df = df.rename(columns={'category__name': 'category'})

    if df.empty or len(df) < 10:
        return None, 'Need at least 10 expenses to detect anomalies'

    df, X = _build_features(df)

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', IsolationForest(
            n_estimators=100,
            contamination=0.05,  
            random_state=42
        ))
    ])
    pipeline.fit(X)

    joblib.dump(pipeline, _model_path(user_id))
    return pipeline, None


def _severity(zscore):
    if zscore >= 3.0:
        return 'high'
    elif zscore >= 2.0:
        return 'medium'
    return 'low'


def _build_reason(row):
    z = row['amount_zscore']
    cat = row['category']
    avg = round(row['cat_mean'], 2)

    if z >= 2:
        multiplier = round(row['amount'] / row['cat_mean'], 1)
        return (
            f"Amount is {multiplier}× higher than your usual "
            f"{cat} average of ${avg}"
        )
    elif row['is_weekend'] and row['amount'] > row['cat_mean'] * 1.5:
        return f"Unusually high {cat} expense on a weekend"
    elif row['day_of_week'] < 5 and row['amount'] > row['cat_mean'] * 1.5:
        return f"Unusually high {cat} expense on a weekday"
    return f"Unusual spending pattern detected in {cat}"


def detect_anomalies(user_id, expenses_qs):
    
    if not os.path.exists(_model_path(user_id)):
        pipeline, err = train_model(user_id, expenses_qs)
        if pipeline is None:
            return {'error': err, 'anomalies': [], 'summary': {}}
    else:
        pipeline = joblib.load(_model_path(user_id))

    df = pd.DataFrame(list(expenses_qs.values(
        'id', 'amount', 'category__name', 'date', 'description'
    )))
    df = df.rename(columns={'category__name': 'category'})

    if df.empty:
        return {'anomalies': [], 'summary': {}}

    df, X = _build_features(df)

    df['is_anomaly']     = pipeline.predict(X)
    df['anomaly_score']  = pipeline.score_samples(X)  
    df['amount_zscore']  = X['amount_zscore'].values

    anomalies_df = df[df['is_anomaly'] == -1].copy()
    anomalies_df = anomalies_df.sort_values('anomaly_score') 

    anomalies = []
    for _, row in anomalies_df.iterrows():
        anomalies.append({
            'id':          int(row['id']),
            'date':        str(row['date'].date()),
            'amount':      float(round(row['amount'], 2)),
            'category':    row['category'],
            'description': row.get('description', ''),
            'reason':      _build_reason(row),
            'severity':    _severity(row['amount_zscore']),
            'zscore':      float(round(row['amount_zscore'], 2)),
            'cat_avg':     float(round(row['cat_mean'], 2)),
        })

    total          = len(df)
    flagged_count  = len(anomalies_df)
    flagged_amount = float(round(anomalies_df['amount'].sum(), 2))
    normal_pct     = round((total - flagged_count) / total * 100) if total else 100
    max_z          = float(round(anomalies_df['amount_zscore'].max(), 1)) if flagged_count else 0

    return {
        'anomalies': anomalies,
        'summary': {
            'total_transactions': total,
            'flagged_count':      flagged_count,
            'flagged_amount':     flagged_amount,
            'normal_pct':         normal_pct,
            'highest_deviation':  max_z,
        }
    }