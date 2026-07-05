import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import confusion_matrix, roc_curve, auc, precision_recall_curve

def plot_confusion_matrix(y_true, y_pred, labels=None):
    """Generates a Plotly confusion matrix."""
    cm = confusion_matrix(y_true, y_pred)
    if labels is None:
        labels = [str(i) for i in range(cm.shape[0])]
    
    fig = px.imshow(cm, text_auto=True, color_continuous_scale='Blues',
                    labels=dict(x="Predicted", y="Actual", color="Count"),
                    x=labels, y=labels, title="Confusion Matrix")
    fig.update_layout(xaxis_title="Predicted Label", yaxis_title="True Label")
    return fig

def plot_roc_curve(y_true, y_prob):
    """Generates a Plotly ROC curve for binary classification."""
    if len(np.unique(y_true)) > 2:
        return None # Multi-class ROC requires binarization, skip for simplicity unless needed
        
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fpr, y=tpr, name=f'ROC Curve (AUC = {roc_auc:.3f})', mode='lines', line=dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', line=dict(color='gray', dash='dash'), name='Random Classifier'))
    fig.update_layout(title="Receiver Operating Characteristic (ROC)", xaxis_title="False Positive Rate", yaxis_title="True Positive Rate")
    return fig

def plot_precision_recall_curve(y_true, y_prob):
    """Generates a Plotly Precision-Recall curve."""
    if len(np.unique(y_true)) > 2:
        return None
        
    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=recall, y=precision, mode='lines', line=dict(color='green', width=2), name="PR Curve"))
    fig.update_layout(title="Precision-Recall Curve", xaxis_title="Recall", yaxis_title="Precision")
    return fig
