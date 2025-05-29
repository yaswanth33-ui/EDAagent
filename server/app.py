from flask import Flask, render_template, request, jsonify, send_file, make_response
import pandas as pd
import io
import os
import sqlite3
import atexit
import signal
from utils import (
    df_to_str, generate_visuals, get_statistical_summary,
    detect_anomalies, get_cleaning_suggestions, ai_text_analysis, chat_with_dataset
)
from database import Database

app = Flask(__name__)
db = Database()

# Handle graceful shutdown
def cleanup():
    """Clean up resources before shutdown"""
    print("Cleaning up resources...")
    try:
        # Clean up old files and database entries
        db.cleanup_old_files(days=7)
        
        # Close database connection
        if hasattr(db, 'conn') and db.conn:
            db.conn.close()
            
        # Clean up any temporary files
        temp_dir = os.path.join('server', 'static', 'plots')
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                if file.startswith('plot_'):
                    try:
                        os.remove(os.path.join(temp_dir, file))
                    except Exception as e:
                        print(f"Error removing file {file}: {str(e)}")
                        
        print("Cleanup completed successfully")
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

atexit.register(cleanup)

# Handle signals
def signal_handler(signum, frame):
    cleanup()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/chat', methods=['GET', 'POST'])
async def chat():
    if request.method == 'GET':
        return render_template('chat.html')
    
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message field'}), 400
            
        # Get or create chat session
        session_id = data.get('session_id')
        if not session_id:
            session_id = db.create_chat_session()
            
        # Get conversation history from database
        chat_history = db.get_chat_history(session_id)
        conversation_history = [
            {"role": role, "content": content}
            for role, content, _ in chat_history
        ]
        
        response = await chat_with_dataset(
            query=data['message'],
            df_context=data.get('df_context'),
            conversation_history=conversation_history
        )
        
        # Save both user message and assistant response
        db.save_chat_message(session_id, 'user', data['message'])
        db.save_chat_message(session_id, 'assistant', response)
            
        return jsonify({
            'response': response,
            'session_id': session_id
        })
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat/sessions', methods=['GET'])
def get_chat_sessions():
    """Get all chat sessions"""
    try:
        sessions = db.get_all_chat_sessions()
        return jsonify({
            'sessions': [
                {
                    'id': session[0],
                    'name': session[1],
                    'created_at': session[2]
                }
                for session in sessions
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat/sessions/<int:session_id>', methods=['GET', 'DELETE'])
def chat_session(session_id):
    if request.method == 'DELETE':
        try:
            success = db.delete_chat_session(session_id)
            if success:
                return jsonify({'message': 'Chat session deleted successfully'})
            else:
                return jsonify({'error': 'Failed to delete chat session'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    try:
        # Get chat history for the session
        messages = db.get_chat_history(session_id)
        return jsonify({
            'messages': [
                {
                    'role': role,
                    'content': content,
                    'created_at': created_at
                }
                for role, content, created_at in messages
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
async def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Read the file
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
            else:
                return jsonify({'error': 'Unsupported file format'}), 400
        except Exception as e:
            return jsonify({'error': f'Error reading file: {str(e)}'}), 400

        if df.empty:
            return jsonify({'error': 'The uploaded file is empty'}), 400
        
        # Generate comprehensive analysis
        df_context = df_to_str(df)
        analysis_plan = await ai_text_analysis("plan", df_context)
        visualizations = generate_visuals(df)
        stats_summary = get_statistical_summary(df)
        anomalies = detect_anomalies(df)
        cleaning_suggestions = get_cleaning_suggestions(df)
        final_analysis = await ai_text_analysis("final",df_context)
        
        # Save analysis results to database
        analysis_id = db.save_analysis(
            filename=file.filename,
            df_context=df_context,
            analysis_plan=analysis_plan,
            statistical_summary=stats_summary,
            anomalies=anomalies,
            cleaning_suggestions=cleaning_suggestions,
            visualizations=visualizations,
            final_analysis = final_analysis
        )
        
        return jsonify({
            'message': 'File uploaded successfully',
            'analysis_id': analysis_id,
            'analysis_plan': analysis_plan,
            'df_context': df_context,
            'visualizations': [{'id': i+1, 'type': v[0], 'title': v[1], 'path': v[2], 'image_data': v[3]} for i, v in enumerate(visualizations)],
            'statistical_summary': stats_summary,
            'anomalies': anomalies,
            'cleaning_suggestions': cleaning_suggestions,
            "final_analysis":final_analysis
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def history():
    try:
        recent_analyses = db.get_recent_analyses()
        
        # Check if the request wants JSON
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'analyses': [
                    {
                        'id': analysis[0],
                        'filename': analysis[1],
                        'created_at': analysis[2]
                    }
                    for analysis in recent_analyses
                ]
            })
            
        # Otherwise return HTML template
        return render_template('history.html', analyses=recent_analyses)
    except Exception as e:
        print(f"Error in history: {str(e)}")  # Add logging
        return jsonify({'error': str(e)}), 500

@app.route('/analysis/<int:analysis_id>', methods=['GET', 'DELETE'])
def view_analysis(analysis_id):
    if request.method == 'DELETE':
        try:
            # Delete the analysis and associated files
            success = db.delete_analysis(analysis_id)
            if success:
                return jsonify({'message': 'Analysis deleted successfully'})
            else:
                return jsonify({'error': 'Analysis not found'}), 404
        except Exception as e:
            print(f"Error deleting analysis: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    try:
        analysis = db.get_analysis(analysis_id)
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
            
        # Check if the request wants JSON
        if request.headers.get('Accept') == 'application/json':
            return jsonify(analysis)
            
        # Otherwise return HTML template
        return render_template('analysis.html', analysis=analysis)
    except Exception as e:
        print(f"Error in view_analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
async def analyze():
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        # If df_context is provided, use it for data analysis
        if 'df_context' in data and data['df_context']:
            response = await ai_text_analysis("final", f"Query: {data['query']}\nContext: {data['df_context']}")
        else:
            # Otherwise use general chat
            response = await chat_with_dataset(data['query'])
        
        # Save chat interaction to database if analysis_id is provided
        if 'analysis_id' in data:
            db.save_chat(data['analysis_id'], data['query'], response)
            
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error in analyze: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['POST'])
def get_stats():
    try:
        data = request.json
        if not data or 'df_context' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        df = pd.read_csv(io.StringIO(data['df_context']))
        stats = get_statistical_summary(df)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cleaning-suggestions', methods=['POST'])
def cleaning_suggestions():
    try:
        data = request.json
        if not data or 'df_context' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        df = pd.read_csv(io.StringIO(data['df_context']))
        suggestions = get_cleaning_suggestions(df)
        return jsonify({'suggestions': suggestions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/image/<int:analysis_id>/<int:viz_id>')
def serve_image(analysis_id, viz_id):
    try:
        # Get image data from database
        conn = sqlite3.connect('eda_agent.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT image_data FROM visualizations 
        WHERE analysis_id = ? AND id = ?
        ''', (analysis_id, viz_id))
        
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'Image not found'}), 404
            
        # The image data is already base64 encoded
        image_data = result[0]
        
        # Create response with base64 image data
        response = make_response(image_data)
        response.headers['Content-Type'] = 'image/png'
        response.headers['Content-Disposition'] = f'inline; filename=visualization_{viz_id}.png'
        
        conn.close()
        return response
        
    except Exception as e:
        print(f"Error serving image: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(debug=True, use_reloader=False)
    except OSError as e:
        if e.errno == 10038:  # Socket error
            print("Socket error occurred. Attempting to restart server...")
            cleanup()
            app.run(debug=True, use_reloader=False)
        else:
            raise