import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import csv
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalyticsConfig:
    """Configuration class for analytics engine"""
    output_dir: str = "analytics_output"
    cache_enabled: bool = True
    max_memory_usage: int = 1024  # MB
    parallel_processing: bool = True
    default_chart_theme: str = "plotly_white"
    export_formats: List[str] = None
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ["csv", "json", "html"]

class DataProcessor:
    """Handles data cleaning, transformation, and preprocessing"""
    
    def __init__(self, config: AnalyticsConfig):
        self.config = config
        self.data_cache = {}
        
    def load_data(self, source: str, data_type: str = "csv") -> pd.DataFrame:
        """Load data from various sources"""
        try:
            if data_type == "csv":
                df = pd.read_csv(source)
            elif data_type == "json":
                df = pd.read_json(source)
            elif data_type == "sqlite":
                conn = sqlite3.connect(source)
                df = pd.read_sql_query("SELECT * FROM data", conn)
                conn.close()
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
            
            logger.info(f"Loaded {len(df)} rows from {source}")
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess data"""
        if df.empty:
            return df
            
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        categorical_columns = df.select_dtypes(include=['object']).columns
        
        # Fill numeric missing values with median
        for col in numeric_columns:
            if df[col].isnull().sum() > 0:
                df[col].fillna(df[col].median(), inplace=True)
        
        # Fill categorical missing values with mode
        for col in categorical_columns:
            if df[col].isnull().sum() > 0:
                df[col].fillna(df[col].mode()[0], inplace=True)
        
        # Remove outliers using IQR method for numeric columns
        for col in numeric_columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        
        logger.info(f"Cleaned data: {len(df)} rows remaining")
        return df
    
    def transform_data(self, df: pd.DataFrame, transformations: List[Dict]) -> pd.DataFrame:
        """Apply various data transformations"""
        for transform in transformations:
            transform_type = transform.get('type')
            
            if transform_type == 'normalize':
                column = transform['column']
                df[column] = (df[column] - df[column].mean()) / df[column].std()
                
            elif transform_type == 'log':
                column = transform['column']
                df[column] = np.log1p(df[column])
                
            elif transform_type == 'bin':
                column = transform['column']
                bins = transform.get('bins', 10)
                df[f"{column}_binned"] = pd.cut(df[column], bins=bins, labels=False)
                
            elif transform_type == 'encode':
                column = transform['column']
                df[f"{column}_encoded"] = pd.Categorical(df[column]).codes
                
            elif transform_type == 'aggregate':
                group_by = transform['group_by']
                agg_column = transform['agg_column']
                agg_func = transform['agg_func']
                df = df.groupby(group_by)[agg_column].agg(agg_func).reset_index()
        
        return df
    
    def feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create new features from existing data"""
        # Date features if datetime columns exist
        datetime_columns = df.select_dtypes(include=['datetime64']).columns
        for col in datetime_columns:
            df[f"{col}_year"] = df[col].dt.year
            df[f"{col}_month"] = df[col].dt.month
            df[f"{col}_day"] = df[col].dt.day
            df[f"{col}_dayofweek"] = df[col].dt.dayofweek
            df[f"{col}_quarter"] = df[col].dt.quarter
        
        # Interaction features for numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) >= 2:
            for i, col1 in enumerate(numeric_columns):
                for col2 in numeric_columns[i+1:]:
                    df[f"{col1}_{col2}_product"] = df[col1] * df[col2]
                    df[f"{col1}_{col2}_ratio"] = df[col1] / (df[col2] + 1e-8)
        
        return df

class StatisticalAnalyzer:
    """Performs statistical analysis on data"""
    
    def __init__(self):
        self.analysis_results = {}
    
    def descriptive_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate descriptive statistics"""
        stats = {
            'count': df.count().to_dict(),
            'mean': df.mean().to_dict(),
            'std': df.std().to_dict(),
            'min': df.min().to_dict(),
            'max': df.max().to_dict(),
            'median': df.median().to_dict(),
            'skewness': df.skew().to_dict(),
            'kurtosis': df.kurtosis().to_dict()
        }
        
        self.analysis_results['descriptive_stats'] = stats
        return stats
    
    def correlation_analysis(self, df: pd.DataFrame) -> Dict:
        """Analyze correlations between variables"""
        numeric_df = df.select_dtypes(include=[np.number])
        correlation_matrix = numeric_df.corr()
        
        # Find highly correlated pairs
        high_corr_pairs = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    high_corr_pairs.append({
                        'var1': correlation_matrix.columns[i],
                        'var2': correlation_matrix.columns[j],
                        'correlation': corr_value
                    })
        
        results = {
            'correlation_matrix': correlation_matrix.to_dict(),
            'high_correlations': high_corr_pairs
        }
        
        self.analysis_results['correlation_analysis'] = results
        return results
    
    def outlier_detection(self, df: pd.DataFrame, method: str = "iqr") -> Dict:
        """Detect outliers using various methods"""
        outliers = {}
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_indices = df[(df[col] < lower_bound) | (df[col] > upper_bound)].index
                
            elif method == "zscore":
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outlier_indices = df[z_scores > 3].index
                
            outliers[col] = {
                'count': len(outlier_indices),
                'percentage': len(outlier_indices) / len(df) * 100,
                'indices': outlier_indices.tolist()
            }
        
        self.analysis_results['outlier_detection'] = outliers
        return outliers
    
    def trend_analysis(self, df: pd.DataFrame, time_column: str, value_column: str) -> Dict:
        """Analyze trends in time series data"""
        if time_column not in df.columns or value_column not in df.columns:
            return {}
        
        # Sort by time
        df_sorted = df.sort_values(time_column)
        
        # Calculate moving averages
        df_sorted['ma_7'] = df_sorted[value_column].rolling(window=7).mean()
        df_sorted['ma_30'] = df_sorted[value_column].rolling(window=30).mean()
        
        # Calculate trend using linear regression
        x = np.arange(len(df_sorted))
        y = df_sorted[value_column].values
        slope, intercept = np.polyfit(x, y, 1)
        
        # Calculate seasonality (if enough data)
        seasonality = {}
        if len(df_sorted) >= 365:
            df_sorted['month'] = pd.to_datetime(df_sorted[time_column]).dt.month
            monthly_avg = df_sorted.groupby('month')[value_column].mean()
            seasonality = monthly_avg.to_dict()
        
        results = {
            'trend_slope': slope,
            'trend_intercept': intercept,
            'moving_averages': {
                'ma_7': df_sorted['ma_7'].tolist(),
                'ma_30': df_sorted['ma_30'].tolist()
            },
            'seasonality': seasonality,
            'total_periods': len(df_sorted)
        }
        
        self.analysis_results['trend_analysis'] = results
        return results

class VisualizationEngine:
    """Creates various types of visualizations"""
    
    def __init__(self, config: AnalyticsConfig):
        self.config = config
        self.chart_theme = config.default_chart_theme
        
    def create_distribution_plot(self, df: pd.DataFrame, column: str, plot_type: str = "histogram") -> go.Figure:
        """Create distribution plots"""
        if plot_type == "histogram":
            fig = px.histogram(df, x=column, title=f"Distribution of {column}")
        elif plot_type == "box":
            fig = px.box(df, y=column, title=f"Box Plot of {column}")
        elif plot_type == "violin":
            fig = px.violin(df, y=column, title=f"Violin Plot of {column}")
        
        fig.update_layout(template=self.chart_theme)
        return fig
    
    def create_correlation_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """Create correlation heatmap"""
        numeric_df = df.select_dtypes(include=[np.number])
        correlation_matrix = numeric_df.corr()
        
        fig = px.imshow(
            correlation_matrix,
            title="Correlation Heatmap",
            color_continuous_scale="RdBu",
            aspect="auto"
        )
        fig.update_layout(template=self.chart_theme)
        return fig
    
    def create_time_series_plot(self, df: pd.DataFrame, time_column: str, value_column: str) -> go.Figure:
        """Create time series plot"""
        fig = px.line(
            df, 
            x=time_column, 
            y=value_column,
            title=f"Time Series: {value_column} over time"
        )
        fig.update_layout(template=self.chart_theme)
        return fig
    
    def create_scatter_plot(self, df: pd.DataFrame, x_column: str, y_column: str, color_column: str = None) -> go.Figure:
        """Create scatter plot"""
        if color_column:
            fig = px.scatter(df, x=x_column, y=y_column, color=color_column)
        else:
            fig = px.scatter(df, x=x_column, y=y_column)
        
        fig.update_layout(template=self.chart_theme)
        return fig
    
    def create_subplot_dashboard(self, df: pd.DataFrame, columns: List[str]) -> go.Figure:
        """Create a dashboard with multiple subplots"""
        fig = make_subplots(
            rows=len(columns), 
            cols=1,
            subplot_titles=[f"Distribution of {col}" for col in columns]
        )
        
        for i, col in enumerate(columns, 1):
            fig.add_trace(
                go.Histogram(x=df[col], name=col),
                row=i, col=1
            )
        
        fig.update_layout(
            height=300 * len(columns),
            title_text="Data Distribution Dashboard",
            template=self.chart_theme
        )
        return fig
    
    def export_chart(self, fig: go.Figure, filename: str, format: str = "html"):
        """Export chart to various formats"""
        if format == "html":
            fig.write_html(f"{self.config.output_dir}/{filename}.html")
        elif format == "png":
            fig.write_image(f"{self.config.output_dir}/{filename}.png")
        elif format == "pdf":
            fig.write_image(f"{self.config.output_dir}/{filename}.pdf")

class ReportGenerator:
    """Generates comprehensive analytics reports"""
    
    def __init__(self, config: AnalyticsConfig):
        self.config = config
    
    def generate_summary_report(self, df: pd.DataFrame, analysis_results: Dict) -> str:
        """Generate a comprehensive summary report"""
        report = []
        report.append("# Data Analytics Report")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Dataset size: {len(df)} rows, {len(df.columns)} columns")
        report.append("")
        
        # Data quality summary
        report.append("## Data Quality Summary")
        missing_data = df.isnull().sum()
        report.append(f"Missing values: {missing_data.sum()} total")
        for col, missing in missing_data.items():
            if missing > 0:
                report.append(f"- {col}: {missing} ({missing/len(df)*100:.1f}%)")
        report.append("")
        
        # Statistical summary
        if 'descriptive_stats' in analysis_results:
            report.append("## Statistical Summary")
            stats = analysis_results['descriptive_stats']
            for col in df.select_dtypes(include=[np.number]).columns:
                report.append(f"### {col}")
                report.append(f"- Mean: {stats['mean'].get(col, 'N/A'):.2f}")
                report.append(f"- Median: {stats['median'].get(col, 'N/A'):.2f}")
                report.append(f"- Std Dev: {stats['std'].get(col, 'N/A'):.2f}")
                report.append("")
        
        # Correlation insights
        if 'correlation_analysis' in analysis_results:
            report.append("## Correlation Insights")
            high_corr = analysis_results['correlation_analysis']['high_correlations']
            if high_corr:
                report.append("Highly correlated variables (|r| > 0.7):")
                for pair in high_corr:
                    report.append(f"- {pair['var1']} & {pair['var2']}: {pair['correlation']:.3f}")
            else:
                report.append("No highly correlated variables found.")
            report.append("")
        
        # Outlier summary
        if 'outlier_detection' in analysis_results:
            report.append("## Outlier Analysis")
            outliers = analysis_results['outlier_detection']
            total_outliers = sum(outlier['count'] for outlier in outliers.values())
            report.append(f"Total outliers detected: {total_outliers}")
            for col, outlier_info in outliers.items():
                if outlier_info['count'] > 0:
                    report.append(f"- {col}: {outlier_info['count']} ({outlier_info['percentage']:.1f}%)")
            report.append("")
        
        return "\n".join(report)
    
    def export_report(self, report: str, filename: str):
        """Export report to file"""
        with open(f"{self.config.output_dir}/{filename}.md", 'w') as f:
            f.write(report)
        logger.info(f"Report exported to {filename}.md")

class AnalyticsEngine:
    """Main analytics engine that orchestrates all components"""
    
    def __init__(self, config: AnalyticsConfig = None):
        self.config = config or AnalyticsConfig()
        self.processor = DataProcessor(self.config)
        self.analyzer = StatisticalAnalyzer()
        self.visualizer = VisualizationEngine(self.config)
        self.report_generator = ReportGenerator(self.config)
        
        # Create output directory
        import os
        os.makedirs(self.config.output_dir, exist_ok=True)
    
    def run_full_analysis(self, data_source: str, data_type: str = "csv") -> Dict:
        """Run complete analytics pipeline"""
        logger.info("Starting full analytics pipeline")
        
        # Load and clean data
        df = self.processor.load_data(data_source, data_type)
        if df.empty:
            logger.error("Failed to load data")
            return {}
        
        df = self.processor.clean_data(df)
        df = self.processor.feature_engineering(df)
        
        # Perform analyses
        descriptive_stats = self.analyzer.descriptive_statistics(df)
        correlation_analysis = self.analyzer.correlation_analysis(df)
        outlier_analysis = self.analyzer.outlier_detection(df)
        
        # Create visualizations
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            # Distribution plots
            for col in numeric_columns[:5]:  # Limit to first 5 columns
                fig = self.visualizer.create_distribution_plot(df, col)
                self.visualizer.export_chart(fig, f"distribution_{col}", "html")
            
            # Correlation heatmap
            if len(numeric_columns) > 1:
                fig = self.visualizer.create_correlation_heatmap(df)
                self.visualizer.export_chart(fig, "correlation_heatmap", "html")
        
        # Generate report
        analysis_results = self.analyzer.analysis_results
        report = self.report_generator.generate_summary_report(df, analysis_results)
        self.report_generator.export_report(report, "analytics_report")
        
        logger.info("Analytics pipeline completed successfully")
        
        return {
            'data_shape': df.shape,
            'analysis_results': analysis_results,
            'report_generated': True
        }

# Example usage and testing
if __name__ == "__main__":
    # Create sample data for testing
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'user_id': range(1000),
        'age': np.random.normal(35, 10, 1000),
        'income': np.random.lognormal(10, 0.5, 1000),
        'satisfaction_score': np.random.uniform(1, 10, 1000),
        'purchase_amount': np.random.exponential(100, 1000),
        'category': np.random.choice(['A', 'B', 'C'], 1000),
        'date': pd.date_range('2023-01-01', periods=1000, freq='D')
    })
    
    # Save sample data
    sample_data.to_csv('sample_data.csv', index=False)
    
    # Initialize and run analytics engine
    config = AnalyticsConfig(output_dir="analytics_output")
    engine = AnalyticsEngine(config)
    
    # Run analysis
    results = engine.run_full_analysis('sample_data.csv')
    print("Analytics completed!")
    print(f"Results: {results}") 