# Analysis Mode Training - Session 1: Fundamentals

## Data Analysis Fundamentals

### Statistical Analysis Concepts

#### Descriptive Statistics
**Measures of Central Tendency**:
- **Mean**: Average value of a dataset
- **Median**: Middle value when data is ordered
- **Mode**: Most frequently occurring value

**Measures of Variability**:
- **Range**: Difference between max and min values
- **Variance**: Average of squared differences from mean
- **Standard Deviation**: Square root of variance
- **Interquartile Range (IQR)**: Range of middle 50% of data

**Python Implementation**:
```python
import numpy as np
import pandas as pd
from scipy import stats

def descriptive_analysis(data):
    """Comprehensive descriptive statistics analysis"""
    results = {
        'count': len(data),
        'mean': np.mean(data),
        'median': np.median(data),
        'mode': stats.mode(data)[0][0] if len(stats.mode(data)[0]) > 0 else None,
        'std': np.std(data, ddof=1),
        'variance': np.var(data, ddof=1),
        'min': np.min(data),
        'max': np.max(data),
        'range': np.max(data) - np.min(data),
        'q1': np.percentile(data, 25),
        'q3': np.percentile(data, 75),
        'iqr': np.percentile(data, 75) - np.percentile(data, 25),
        'skewness': stats.skew(data),
        'kurtosis': stats.kurtosis(data)
    }
    return results

# Example usage
sales_data = [100, 150, 200, 175, 300, 250, 180, 220, 190, 160]
analysis = descriptive_analysis(sales_data)
print(f"Mean: {analysis['mean']:.2f}")
print(f"Median: {analysis['median']:.2f}")
print(f"Standard Deviation: {analysis['std']:.2f}")
```

#### Inferential Statistics
**Hypothesis Testing**:
```python
from scipy.stats import ttest_1samp, ttest_ind, chi2_contingency

def perform_t_test(sample_data, population_mean=None, sample2=None):
    """Perform appropriate t-test based on input"""
    
    if population_mean is not None:
        # One-sample t-test
        t_stat, p_value = ttest_1samp(sample_data, population_mean)
        test_type = "One-sample t-test"
        
    elif sample2 is not None:
        # Two-sample t-test
        t_stat, p_value = ttest_ind(sample_data, sample2)
        test_type = "Two-sample t-test"
        
    else:
        raise ValueError("Must provide either population_mean or sample2")
    
    # Interpret results
    alpha = 0.05
    significant = p_value < alpha
    
    return {
        'test_type': test_type,
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': significant,
        'alpha': alpha,
        'interpretation': f"{'Reject' if significant else 'Fail to reject'} null hypothesis"
    }

# Chi-square test for categorical data
def chi_square_test(contingency_table):
    """Perform chi-square test of independence"""
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
    
    return {
        'chi2_statistic': chi2,
        'p_value': p_value,
        'degrees_of_freedom': dof,
        'expected_frequencies': expected,
        'significant': p_value < 0.05
    }
```

### Data Visualization and Exploration

#### Exploratory Data Analysis (EDA)
```python
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

class DataExplorer:
    def __init__(self, data):
        self.data = data
        
    def univariate_analysis(self, column):
        """Analyze single variable"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Histogram
        axes[0, 0].hist(self.data[column], bins=30, alpha=0.7)
        axes[0, 0].set_title(f'Histogram of {column}')
        axes[0, 0].set_xlabel(column)
        axes[0, 0].set_ylabel('Frequency')
        
        # Box plot
        axes[0, 1].boxplot(self.data[column])
        axes[0, 1].set_title(f'Box Plot of {column}')
        axes[0, 1].set_ylabel(column)
        
        # Q-Q plot
        stats.probplot(self.data[column], dist="norm", plot=axes[1, 0])
        axes[1, 0].set_title(f'Q-Q Plot of {column}')
        
        # Density plot
        self.data[column].plot(kind='density', ax=axes[1, 1])
        axes[1, 1].set_title(f'Density Plot of {column}')
        axes[1, 1].set_xlabel(column)
        
        plt.tight_layout()
        return fig
    
    def bivariate_analysis(self, x_col, y_col):
        """Analyze relationship between two variables"""
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Scatter plot
        axes[0].scatter(self.data[x_col], self.data[y_col], alpha=0.6)
        axes[0].set_xlabel(x_col)
        axes[0].set_ylabel(y_col)
        axes[0].set_title(f'{y_col} vs {x_col}')
        
        # Add correlation coefficient
        correlation = self.data[x_col].corr(self.data[y_col])
        axes[0].text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                    transform=axes[0].transAxes, verticalalignment='top')
        
        # Regression line
        z = np.polyfit(self.data[x_col], self.data[y_col], 1)
        p = np.poly1d(z)
        axes[0].plot(self.data[x_col], p(self.data[x_col]), "r--", alpha=0.8)
        
        # Correlation heatmap for context
        corr_matrix = self.data[[x_col, y_col]].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=axes[1])
        axes[1].set_title('Correlation Matrix')
        
        plt.tight_layout()
        return fig, correlation
    
    def correlation_analysis(self):
        """Comprehensive correlation analysis"""
        # Calculate correlation matrix
        corr_matrix = self.data.corr()
        
        # Create interactive heatmap
        fig = px.imshow(corr_matrix, 
                       text_auto=True, 
                       aspect="auto",
                       title="Correlation Matrix Heatmap")
        
        # Find strong correlations
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:  # Strong correlation threshold
                    strong_correlations.append({
                        'var1': corr_matrix.columns[i],
                        'var2': corr_matrix.columns[j],
                        'correlation': corr_val
                    })
        
        return fig, strong_correlations
```

#### Advanced Visualization Techniques
```python
def create_dashboard_visualizations(data):
    """Create comprehensive dashboard visualizations"""
    
    # Time series analysis
    def plot_time_series(df, date_col, value_col):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df[date_col], 
            y=df[value_col],
            mode='lines+markers',
            name=value_col,
            line=dict(width=2)
        ))
        
        # Add trend line
        z = np.polyfit(range(len(df)), df[value_col], 1)
        trend_line = np.poly1d(z)(range(len(df)))
        
        fig.add_trace(go.Scatter(
            x=df[date_col],
            y=trend_line,
            mode='lines',
            name='Trend',
            line=dict(dash='dash', color='red')
        ))
        
        fig.update_layout(
            title=f'{value_col} Over Time',
            xaxis_title=date_col,
            yaxis_title=value_col,
            hovermode='x unified'
        )
        
        return fig
    
    # Distribution comparison
    def plot_distribution_comparison(df, group_col, value_col):
        fig = go.Figure()
        
        for group in df[group_col].unique():
            group_data = df[df[group_col] == group][value_col]
            fig.add_trace(go.Histogram(
                x=group_data,
                name=str(group),
                opacity=0.7,
                nbinsx=30
            ))
        
        fig.update_layout(
            title=f'Distribution of {value_col} by {group_col}',
            xaxis_title=value_col,
            yaxis_title='Frequency',
            barmode='overlay'
        )
        
        return fig
    
    # Funnel analysis
    def create_funnel_chart(stages, values):
        fig = go.Figure(go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial+percent previous",
            texttemplate='%{label}: %{value} (%{percentInitial} of total, %{percentPrevious} of previous)',
            connector={"line": {"color": "royalblue", "dash": "solid", "width": 3}}
        ))
        
        fig.update_layout(
            title="Conversion Funnel Analysis",
            font_size=12
        )
        
        return fig
    
    return {
        'time_series': plot_time_series,
        'distribution_comparison': plot_distribution_comparison,
        'funnel_chart': create_funnel_chart
    }
```

### Business Intelligence and KPI Analysis

#### Key Performance Indicators (KPIs)
```python
class KPIAnalyzer:
    def __init__(self, data):
        self.data = data
    
    def calculate_business_metrics(self):
        """Calculate common business KPIs"""
        metrics = {}
        
        # Revenue metrics
        if 'revenue' in self.data.columns:
            metrics['total_revenue'] = self.data['revenue'].sum()
            metrics['avg_revenue'] = self.data['revenue'].mean()
            metrics['revenue_growth'] = self.calculate_growth_rate('revenue')
        
        # Customer metrics
        if 'customer_id' in self.data.columns:
            metrics['total_customers'] = self.data['customer_id'].nunique()
            metrics['avg_order_value'] = self.data.groupby('customer_id')['revenue'].sum().mean()
            metrics['customer_retention_rate'] = self.calculate_retention_rate()
        
        # Conversion metrics
        if all(col in self.data.columns for col in ['visitors', 'conversions']):
            metrics['conversion_rate'] = (self.data['conversions'].sum() / 
                                        self.data['visitors'].sum()) * 100
        
        return metrics
    
    def calculate_growth_rate(self, column, period='month'):
        """Calculate period-over-period growth rate"""
        if 'date' not in self.data.columns:
            return None
        
        # Group by period
        if period == 'month':
            grouped = self.data.groupby(self.data['date'].dt.to_period('M'))[column].sum()
        elif period == 'quarter':
            grouped = self.data.groupby(self.data['date'].dt.to_period('Q'))[column].sum()
        else:
            grouped = self.data.groupby(self.data['date'].dt.to_period('Y'))[column].sum()
        
        # Calculate growth rate
        growth_rates = grouped.pct_change() * 100
        return growth_rates.dropna()
    
    def cohort_analysis(self):
        """Perform customer cohort analysis"""
        if not all(col in self.data.columns for col in ['customer_id', 'date', 'revenue']):
            return None
        
        # Define cohorts by first purchase month
        self.data['order_period'] = self.data['date'].dt.to_period('M')
        
        cohort_data = self.data.groupby('customer_id')['date'].min().reset_index()
        cohort_data.columns = ['customer_id', 'cohort_group']
        cohort_data['cohort_group'] = cohort_data['cohort_group'].dt.to_period('M')
        
        # Merge back to main data
        df_cohort = self.data.merge(cohort_data, on='customer_id')
        df_cohort['period_number'] = (df_cohort['order_period'] - df_cohort['cohort_group']).apply(attrgetter('n'))
        
        # Create cohort table
        cohort_table = df_cohort.groupby(['cohort_group', 'period_number'])['customer_id'].nunique().reset_index()
        cohort_sizes = df_cohort.groupby('cohort_group')['customer_id'].nunique()
        
        cohort_table = cohort_table.pivot(index='cohort_group', 
                                         columns='period_number', 
                                         values='customer_id')
        
        # Calculate retention rates
        cohort_table = cohort_table.divide(cohort_sizes, axis=0)
        
        return cohort_table
    
    def rfi_analysis(self):
        """RFM (Recency, Frequency, Monetary) Analysis"""
        if not all(col in self.data.columns for col in ['customer_id', 'date', 'revenue']):
            return None
        
        # Calculate RFM metrics
        current_date = self.data['date'].max()
        
        rfm = self.data.groupby('customer_id').agg({
            'date': lambda x: (current_date - x.max()).days,  # Recency
            'customer_id': 'count',  # Frequency
            'revenue': 'sum'  # Monetary
        })
        
        rfm.columns = ['recency', 'frequency', 'monetary']
        
        # Create RFM scores (1-5 scale)
        rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5,4,3,2,1])
        rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
        rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1,2,3,4,5])
        
        # Combine scores
        rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
        
        # Customer segmentation
        def segment_customers(row):
            if row['rfm_score'] in ['555', '554', '544', '545', '454', '455', '445']:
                return 'Champions'
            elif row['rfm_score'] in ['543', '444', '435', '355', '354', '345', '344', '335']:
                return 'Loyal Customers'
            elif row['rfm_score'] in ['553', '551', '552', '541', '542', '533', '532', '531', '452', '451']:
                return 'Potential Loyalists'
            elif row['rfm_score'] in ['512', '511', '422', '421', '412', '411', '311']:
                return 'New Customers'
            elif row['rfm_score'] in ['155', '154', '144', '214', '215', '115', '114']:
                return 'At Risk'
            elif row['rfm_score'] in ['155', '254', '245']:
                return "Can't Lose Them"
            else:
                return 'Others'
        
        rfm['segment'] = rfm.apply(segment_customers, axis=1)
        
        return rfm
```

### Predictive Analytics

#### Machine Learning for Business Analysis
```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder

class PredictiveAnalyzer:
    def __init__(self, data):
        self.data = data
        self.models = {}
        self.scalers = {}
    
    def sales_forecasting(self, target_col='sales', feature_cols=None):
        """Build sales forecasting model"""
        if feature_cols is None:
            feature_cols = [col for col in self.data.columns if col != target_col and self.data[col].dtype in ['int64', 'float64']]
        
        X = self.data[feature_cols]
        y = self.data[target_col]
        
        # Handle missing values
        X = X.fillna(X.mean())
        y = y.fillna(y.mean())
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train models
        models = {
            'linear_regression': LinearRegression(),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        
        results = {}
        for name, model in models.items():
            # Train model
            if name == 'linear_regression':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            # Evaluate
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            results[name] = {
                'model': model,
                'mse': mse,
                'r2': r2,
                'predictions': y_pred
            }
        
        self.models['sales_forecast'] = results
        self.scalers['sales_forecast'] = scaler
        
        return results
    
    def customer_churn_prediction(self, target_col='churn', feature_cols=None):
        """Build customer churn prediction model"""
        if feature_cols is None:
            feature_cols = [col for col in self.data.columns if col != target_col]
        
        X = self.data[feature_cols]
        y = self.data[target_col]
        
        # Encode categorical variables
        le = LabelEncoder()
        for col in X.select_dtypes(include=['object']).columns:
            X[col] = le.fit_transform(X[col].astype(str))
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train models
        models = {
            'logistic_regression': LogisticRegression(random_state=42),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42)
        }
        
        results = {}
        for name, model in models.items():
            # Train model
            if name == 'logistic_regression':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # Evaluate
            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred, output_dict=True)
            
            results[name] = {
                'model': model,
                'accuracy': accuracy,
                'classification_report': report,
                'predictions': y_pred,
                'probabilities': y_pred_proba
            }
        
        self.models['churn_prediction'] = results
        self.scalers['churn_prediction'] = scaler
        
        return results
    
    def feature_importance_analysis(self, model_type='sales_forecast'):
        """Analyze feature importance from trained models"""
        if model_type not in self.models:
            return None
        
        results = {}
        for name, model_info in self.models[model_type].items():
            model = model_info['model']
            
            if hasattr(model, 'feature_importances_'):
                # Tree-based models
                importances = model.feature_importances_
                feature_names = self.data.columns[:-1]  # Assuming last column is target
                
                importance_df = pd.DataFrame({
                    'feature': feature_names,
                    'importance': importances
                }).sort_values('importance', ascending=False)
                
                results[name] = importance_df
            
            elif hasattr(model, 'coef_'):
                # Linear models
                coefficients = model.coef_
                feature_names = self.data.columns[:-1]
                
                coef_df = pd.DataFrame({
                    'feature': feature_names,
                    'coefficient': coefficients
                }).sort_values('coefficient', key=abs, ascending=False)
                
                results[name] = coef_df
        
        return results
```

### Statistical Process Control

#### Control Charts and Quality Analysis
```python
import matplotlib.pyplot as plt
import numpy as np

class QualityAnalyzer:
    def __init__(self, data):
        self.data = data
    
    def create_control_chart(self, column, chart_type='xbar'):
        """Create statistical process control charts"""
        values = self.data[column].values
        
        if chart_type == 'xbar':
            # X-bar chart for continuous data
            mean = np.mean(values)
            std = np.std(values, ddof=1)
            
            ucl = mean + 3 * std  # Upper Control Limit
            lcl = mean - 3 * std  # Lower Control Limit
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Plot data points
            ax.plot(range(len(values)), values, 'bo-', markersize=4, linewidth=1)
            
            # Plot control limits
            ax.axhline(y=mean, color='green', linestyle='-', linewidth=2, label='Center Line')
            ax.axhline(y=ucl, color='red', linestyle='--', linewidth=2, label='UCL')
            ax.axhline(y=lcl, color='red', linestyle='--', linewidth=2, label='LCL')
            
            # Identify out-of-control points
            out_of_control = (values > ucl) | (values < lcl)
            if np.any(out_of_control):
                out_points = np.where(out_of_control)[0]
                ax.scatter(out_points, values[out_points], color='red', s=100, marker='x', linewidth=3)
            
            ax.set_title(f'X-bar Control Chart for {column}')
            ax.set_xlabel('Sample Number')
            ax.set_ylabel(column)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            return fig, {
                'mean': mean,
                'ucl': ucl,
                'lcl': lcl,
                'out_of_control_points': out_of_control.sum(),
                'process_capability': self.calculate_process_capability(values, mean, std)
            }
    
    def calculate_process_capability(self, values, mean, std, usl=None, lsl=None):
        """Calculate process capability indices"""
        if usl is None:
            usl = mean + 3 * std
        if lsl is None:
            lsl = mean - 3 * std
        
        # Cp: Process capability
        cp = (usl - lsl) / (6 * std)
        
        # Cpk: Process capability index
        cpu = (usl - mean) / (3 * std)
        cpl = (mean - lsl) / (3 * std)
        cpk = min(cpu, cpl)
        
        return {
            'cp': cp,
            'cpk': cpk,
            'cpu': cpu,
            'cpl': cpl
        }
```

## Training Exercises

### Exercise 1: E-commerce Analytics Dashboard
**Task**: Build comprehensive analytics for an e-commerce platform
**Requirements**:
- Sales performance analysis with trends and seasonality
- Customer segmentation using RFM analysis
- Product performance and inventory optimization
- Marketing campaign effectiveness measurement
- Predictive models for sales forecasting and churn

### Exercise 2: Financial Risk Analysis
**Task**: Develop risk assessment models for financial data
**Requirements**:
- Portfolio risk analysis and optimization
- Credit risk modeling and scoring
- Market risk assessment using VaR calculations
- Stress testing and scenario analysis
- Regulatory compliance reporting

### Exercise 3: Operational Excellence Analysis
**Task**: Analyze operational processes for improvement opportunities
**Requirements**:
- Process capability analysis using control charts
- Root cause analysis for quality issues
- Efficiency metrics and benchmarking
- Resource utilization optimization
- Performance improvement recommendations

## Assessment Criteria

### Analytical Skills
- Proper statistical method selection and application
- Accurate interpretation of results and findings
- Identification of patterns and insights in data
- Understanding of data limitations and assumptions

### Technical Proficiency
- Proficiency in Python/R for data analysis
- Effective use of visualization tools and libraries
- Database querying and data manipulation skills
- Machine learning model development and evaluation

### Business Acumen
- Translation of analytical findings to business insights
- Understanding of business context and objectives
- Recommendation development and prioritization
- Communication of complex findings to stakeholders
