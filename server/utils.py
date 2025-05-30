import os, io
import numpy as np
import matplotlib.pyplot as plt 
import seaborn as sns
from PIL import Image
import matplotlib
import openrouter
import requests
import time
import base64
import logging

matplotlib.use('Agg')


MODEL = "deepseek/deepseek-chat-v3-0324:free"
MODEL_AVAILABLE = True

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

try:
    if api_key:= os.environ.get("OPENROUTER_API_KEY"):
        openrouter.api_key = api_key
        MODEL_AVAILABLE = True
except Exception as e:
    logger.error(f"Error configuring OpenRouter: {str(e)}")

def save_fig(fig):
    """Save matplotlib figure to a permanent location"""
    try:
        # Create a unique filename with timestamp
        timestamp = int(time.time() * 1000)
        filename = f'plot_{timestamp}.png'
        
        # Create plots directory if it doesn't exist
        plots_dir = os.path.join('server', 'static', 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        # Save the figure
        filepath = os.path.join(plots_dir, filename)
        fig.savefig(filepath, bbox_inches='tight', dpi=150, format='png')
        plt.close(fig)
        
        # Read the image data and encode as base64
        with open(filepath, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Return both the path and base64 encoded image data
        return os.path.join('plots', filename), image_data
    except Exception as e:
        logger.error(f"Error saving figure: {str(e)}")
        return None, None

def df_to_str(df, max_rows=5):
    """Convert dataframe to string representation"""
    try:
        buf = io.StringIO()
        df.info(buf=buf)
        schema = buf.getvalue()
        head = df.head(max_rows).to_markdown(index=False)
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        missing_info = "No missing values." if missing.empty else str(missing)
        return f"### Schema\n```\n{schema}```\n\n### Preview:\n{head}\n\n### Missing:\n{missing_info}"
    except Exception as e:
        logger.error(f"Error generating dataframe summary: {str(e)}")
        return f"Error generating dataframe summary: {str(e)}"

async def ai_text_analysis(prompt_type, df_context):
    """Perform AI text analysis using OpenRouter"""
    if not MODEL_AVAILABLE:
        return "Model is not available."
    
    prompts = {
        "plan": f"You are a senior data analyst. Suggest a concise data analysis plan:\n{df_context}",
        "final": f"Summarize insights from the following dataset:\n{df_context}"
    }
    
    try:
        headers = {
            "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompts[prompt_type]}],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('choices'):
                return result['choices'][0]['message']['content']
            else:
                return "No response generated from the model."
        else:
            return f"Error: {response.text}"
            
    except Exception as e:
        logger.error(f"Error analyzing data: {str(e)}")
        return f"Error analyzing data: {str(e)}"

async def ai_vision_analysis(img_paths):
    """Analyze images using OpenRouter vision model"""
    if not MODEL_AVAILABLE:
        return [("AI Vision", "Model is not available.")]
    
    results = []
    for title, path in img_paths:
        try:
            with Image.open(path) as img:
                # Convert image to base64
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                response = await openrouter.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"Analyze this visualization: {title}"},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                            ]
                        }
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                if response and hasattr(response, 'choices') and response.choices:
                    results.append((title, response.choices[0].message.content))
                else:
                    results.append((title, "No response generated from the model."))
                    
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            results.append((title, f"Error analyzing image: {str(e)}"))
    
    return results

def generate_visuals(df):
    """Generate visualizations for the dataframe"""
    if df.empty:
        return []
        
    visualizations = []
    try:
        # Set style for better-looking plots
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Configure plot aesthetics
        plt.rcParams.update({
            'figure.figsize': (10, 6),
            'figure.dpi': 100,
            'font.size': 12,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'figure.titlesize': 16
        })
        
        # Get column types with validation
        numeric_cols = [col for col in df.select_dtypes(include=np.number).columns if df[col].notna().any()]
        categorical_cols = [col for col in df.select_dtypes('object').columns 
                          if 1 < df[col].nunique() < 30 and df[col].notna().any()]
        
        if not numeric_cols and not categorical_cols:
            return []
        
        # Limit the number of plots for better performance
        max_numeric_cols = min(5, len(numeric_cols))
        max_categorical_cols = min(3, len(categorical_cols))
        
        # Select most important numeric columns (based on variance)
        if len(numeric_cols) > max_numeric_cols:
            variances = df[numeric_cols].var()
            numeric_cols = variances.nlargest(max_numeric_cols).index.tolist()
        
        # Select most important categorical columns (based on unique values)
        if len(categorical_cols) > max_categorical_cols:
            unique_counts = df[categorical_cols].nunique()
            categorical_cols = unique_counts.nlargest(max_categorical_cols).index.tolist()
        
        # 1. Basic Distribution Plots (only for top numeric columns)
        for col in numeric_cols:
            try:
                # 1.1 Histogram with KDE
                plt.figure()
                sns.histplot(data=df, x=col, kde=True, bins=20)
                plt.title(f'Distribution of {col}')
                plt.xlabel(col)
                plt.ylabel('Count')
                result = save_fig(plt.gcf())
                if result:
                    path, image_data = result
                    visualizations.append(('distribution', f'Histogram of {col}', path, image_data))
                plt.close()
                
                # 1.2 Box Plot
                plt.figure()
                sns.boxplot(data=df, y=col)
                plt.title(f'Box Plot of {col}')
                plt.ylabel(col)
                result = save_fig(plt.gcf())
                if result:
                    path, image_data = result
                    visualizations.append(('distribution', f'Box Plot of {col}', path, image_data))
                plt.close()
            except Exception as e:
                logger.error(f"Error generating distribution plots for {col}: {str(e)}")
                plt.close('all')

        # 2. Correlation Analysis (only if we have numeric columns)
        if len(numeric_cols) > 1:
            try:
                # 2.1 Correlation Heatmap
                plt.figure(figsize=(10, 8))
                corr_matrix = df[numeric_cols].corr()
                mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
                sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', center=0, fmt='.2f')
                plt.title('Correlation Heatmap')
                result = save_fig(plt.gcf())
                if result:
                    path, image_data = result
                    visualizations.append(('correlation', 'Correlation Heatmap', path, image_data))
                plt.close()
            except Exception as e:
                logger.error(f"Error generating correlation heatmap: {str(e)}")
                plt.close('all')

        # 3. Categorical Analysis (only for top categorical columns)
        for col in categorical_cols:
            try:
                # 3.1 Bar Plot
                plt.figure()
                value_counts = df[col].value_counts().head(10)
                if not value_counts.empty:
                    sns.barplot(x=value_counts.index, y=value_counts.values)
                    plt.title(f'Distribution of {col}')
                    plt.xlabel(col)
                    plt.ylabel('Count')
                    plt.xticks(rotation=45, ha='right')
                    result = save_fig(plt.gcf())
                    if result:
                        path, image_data = result
                        visualizations.append(('categorical', f'Bar Plot of {col}', path, image_data))
                plt.close()
            except Exception as e:
                logger.error(f"Error generating categorical plots for {col}: {str(e)}")
                plt.close('all')

        # 4. Relationship Analysis (only for top numeric columns)
        if len(numeric_cols) > 1:
            try:
                # 4.1 Scatter Plots (only for top 2 numeric columns)
                if len(numeric_cols) >= 2:
                    plt.figure()
                    sns.scatterplot(data=df, x=numeric_cols[0], y=numeric_cols[1])
                    plt.title(f'{numeric_cols[0]} vs {numeric_cols[1]}')
                    plt.xlabel(numeric_cols[0])
                    plt.ylabel(numeric_cols[1])
                    result = save_fig(plt.gcf())
                    if result:
                        path, image_data = result
                        visualizations.append(('relationship', f'Scatter Plot: {numeric_cols[0]} vs {numeric_cols[1]}', path, image_data))
                    plt.close()
            except Exception as e:
                logger.error(f"Error generating relationship plots: {str(e)}")
                plt.close('all')

        return visualizations
    except Exception as e:
        logger.error(f"Error generating visualizations: {str(e)}")
        plt.close('all')
        return []

def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj

def get_statistical_summary(df):
    """Generate statistical summary of the dataframe"""
    try:
        # Convert numpy types to Python native types
        numeric_summary = convert_numpy_types(df.describe().to_dict())
        categorical_summary = {
            col: {
                'unique_values': int(df[col].nunique()),
                'most_common': convert_numpy_types(df[col].value_counts().head(3).to_dict())
            }
            for col in df.select_dtypes(include=['object']).columns
        }
        return {
            'numeric': numeric_summary,
            'categorical': categorical_summary
        }
    except Exception as e:
        logger.error(f"Error generating statistical summary: {str(e)}")
        return {'error': str(e)}

def detect_anomalies(df):
    """Detect anomalies in numeric columns using IQR method"""
    try:
        anomalies = {}
        for col in df.select_dtypes(include=np.number).columns:
            Q1 = float(df[col].quantile(0.25))
            Q3 = float(df[col].quantile(0.75))
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            count = int(len(df[(df[col] < lower_bound) | (df[col] > upper_bound)]))
            anomalies[col] = {
                'count': count,
                'percentage': float(count / len(df) * 100)
            }
        return anomalies
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        return {'error': str(e)}

def get_cleaning_suggestions(df):
    """Generate data cleaning suggestions"""
    suggestions = []
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.any():
        suggestions.append({
            'type': 'missing_values',
            'message': f'Found {int(missing.sum())} missing values across {len(missing[missing > 0])} columns',
            'details': convert_numpy_types(missing[missing > 0].to_dict())
        })
    
    # Check for duplicates
    duplicates = int(df.duplicated().sum())
    if duplicates > 0:
        suggestions.append({
            'type': 'duplicates',
            'message': f'Found {duplicates} duplicate rows',
            'details': {'count': duplicates}
        })
    
    # Check for outliers
    for col in df.select_dtypes(include=np.number).columns:
        Q1 = float(df[col].quantile(0.25))
        Q3 = float(df[col].quantile(0.75))
        IQR = Q3 - Q1
        outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)][col]
        if len(outliers) > 0:
            suggestions.append({
                'type': 'outliers',
                'message': f'Found {int(len(outliers))} outliers in {col}',
                'details': {'column': col, 'count': int(len(outliers))}
            })
    
    return suggestions

async def cleanup(files):
    """Clean up temporary files"""
    for f in files:
        try:
            if os.path.exists(f):
                os.remove(f)
        except Exception as e:
            logger.error(f"Error cleaning up file {f}: {str(e)}")

async def chat_with_dataset(query, df_context=None, conversation_history=None):
    """General chat system using OpenRouter with conversation history support"""
    if not MODEL_AVAILABLE:
        return "Model is not available. Please check your OpenRouter API configuration."
    
    max_retries = 2
    retry_delay = 0.5
    
    for attempt in range(max_retries):
        try:
            # Construct messages array with conversation history
            messages = []
            
            # Add system message
            messages.append({
                "role": "system",
                "content": "You are a helpful AI assistant. Provide clear, accurate, and engaging responses. If you're not sure about something, say so."
            })
            
            # Add conversation history if available
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current query
            messages.append({
                "role": "user",
                "content": query
            })

            headers = {
                "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/your-repo",
                "X-Title": "Chat Assistant"
            }
            
            data = {
                "model": MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('choices'):
                    response_content = result['choices'][0]['message']['content']
                    return response_content.strip()
                else:
                    error_msg = result.get('error', {}).get('message', 'Unknown error')
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return "I apologize, but I couldn't generate a response. Please try again in a moment."
            else:
                error_msg = response.text
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return f"Error: Unable to process your request. Please try again later."
                
        except requests.exceptions.Timeout:
            pass
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return "Request timed out. Please try again."
            
        except Exception as e:
            pass
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return f"Error: {str(e)}"
    
    return "I apologize, but I couldn't generate a response after multiple attempts. Please try again later."

