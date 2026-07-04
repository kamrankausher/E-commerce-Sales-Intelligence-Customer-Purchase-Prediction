"""
utils.py — Plotting helpers and common utility functions.

WHY THIS EXISTS:
    Reusable visualization functions used across notebooks and the Streamlit
    dashboard. Keeps plotting code DRY and consistent.

INTERVIEW EXPLANATION:
    "I created a utils module for consistent, publication-quality charts.
    Rather than repeating matplotlib boilerplate in every notebook, I have
    reusable functions for bar charts, heatmaps, and confusion matrices
    with a consistent dark theme."
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, roc_curve, auc


# ─── Global Plotting Theme ──────────────────────────────────────────────────
COLORS = {
    "primary": "#6366f1",
    "secondary": "#06b6d4",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "purple": "#a78bfa",
    "pink": "#ec4899",
    "slate": "#64748b",
}

PALETTE = list(COLORS.values())


def set_plot_style():
    """Set a clean, modern plotting style for all visualizations."""
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": True,
        "grid.alpha": 0.3,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "figure.dpi": 100,
    })
    sns.set_palette(PALETTE)


def plot_bar(data, x, y, title, xlabel="", ylabel="", figsize=(10, 6),
             color=None, horizontal=False):
    """Create a clean bar chart."""
    set_plot_style()
    fig, ax = plt.subplots(figsize=figsize)

    if horizontal:
        bars = ax.barh(data[x], data[y], color=color or COLORS["primary"],
                       edgecolor="none", height=0.6)
        ax.set_xlabel(ylabel or y)
        ax.set_ylabel(xlabel or x)
        ax.invert_yaxis()
    else:
        bars = ax.bar(data[x], data[y], color=color or COLORS["primary"],
                      edgecolor="none", width=0.6)
        ax.set_xlabel(xlabel or x)
        ax.set_ylabel(ylabel or y)
        plt.xticks(rotation=45, ha="right")

    ax.set_title(title, pad=15)
    plt.tight_layout()
    return fig, ax


def plot_confusion_matrix(y_true, y_pred, title="Confusion Matrix", figsize=(6, 5)):
    """Plot a styled confusion matrix heatmap."""
    set_plot_style()
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues", ax=ax,
        xticklabels=["Active", "Churned"],
        yticklabels=["Active", "Churned"],
        linewidths=0.5, linecolor="white",
    )
    ax.set_xlabel("Predicted", fontsize=12)
    ax.set_ylabel("Actual", fontsize=12)
    ax.set_title(title, pad=15, fontsize=14, fontweight="bold")
    plt.tight_layout()
    return fig


def plot_roc_curves(models_dict, X_test, y_test, figsize=(8, 6)):
    """
    Plot ROC curves for multiple models on the same axes.

    Args:
        models_dict: dict of {model_name: trained_model}
        X_test: test features
        y_test: test labels
    """
    set_plot_style()
    fig, ax = plt.subplots(figsize=figsize)

    colors = list(COLORS.values())
    for i, (name, model) in enumerate(models_dict.items()):
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_test)[:, 1]
        else:
            y_proba = model.predict(X_test)
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, color=colors[i % len(colors)], lw=2,
                label=f"{name} (AUC = {roc_auc:.3f})")

    ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5, label="Random (AUC = 0.500)")
    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title("ROC Curve Comparison", pad=15, fontsize=14, fontweight="bold")
    ax.legend(loc="lower right", fontsize=10)
    plt.tight_layout()
    return fig


def plot_feature_importance(fi_df, top_n=12, title="Feature Importance", figsize=(10, 6)):
    """
    Plot horizontal bar chart of feature importance.

    Args:
        fi_df: DataFrame with 'feature' and 'importance' columns
        top_n: number of top features to show
    """
    set_plot_style()
    top = fi_df.head(top_n)
    fig, ax = plt.subplots(figsize=figsize)

    colors = [COLORS["primary"] if i > 2 else COLORS["success"] for i in range(len(top))]
    colors = colors[::-1]  # reverse for horizontal bar

    ax.barh(top["feature"][::-1], top["importance"][::-1],
            color=colors, edgecolor="none", height=0.6)
    ax.set_xlabel("Importance", fontsize=12)
    ax.set_title(title, pad=15, fontsize=14, fontweight="bold")

    # Add value labels
    for i, (val, name) in enumerate(zip(top["importance"][::-1], top["feature"][::-1])):
        ax.text(val + max(top["importance"]) * 0.01, i, f"{val:.3f}",
                va="center", fontsize=10, color=COLORS["slate"])

    plt.tight_layout()
    return fig


def plot_correlation_heatmap(df, figsize=(10, 8), title="Feature Correlation Matrix"):
    """Plot a correlation heatmap for numeric features."""
    set_plot_style()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    corr = df[numeric_cols].corr()

    fig, ax = plt.subplots(figsize=figsize)
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(
        corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
        center=0, ax=ax, linewidths=0.5, linecolor="white",
        vmin=-1, vmax=1, square=True
    )
    ax.set_title(title, pad=15, fontsize=14, fontweight="bold")
    plt.tight_layout()
    return fig


def format_number(n):
    """Format large numbers with K/M suffixes for display."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def format_currency(n, currency="R$"):
    """Format numbers as currency."""
    return f"{currency} {n:,.2f}"
