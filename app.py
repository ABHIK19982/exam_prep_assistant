from dotenv  import load_dotenv
import os
if os.environ.get('env_name') == 'LOCAL':
    load_dotenv('config/local.env', verbose = True, override = True)
else:
    load_dotenv('config/.env', verbose = True ,override = True)
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from metaagent import get_AI_response, AVAILABLE_MODELS, DEFAULT_MODEL
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = lambda: os.urandom(24).hex()

messages_store = [{'role':'ai','content':'Hello Aspirant! How may i help you with your preparation today ?'}]
MODEL_IDS = {model["id"] for model in AVAILABLE_MODELS}

@app.route('/')
def index():
    return render_template(
        'index.html',
        available_models=AVAILABLE_MODELS,
        default_model=DEFAULT_MODEL
    )

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        selected_model = data.get('model') or DEFAULT_MODEL
        if selected_model not in MODEL_IDS:
            selected_model = DEFAULT_MODEL
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        user_msg = {
            'sender': 'user',
            'message': user_message,
            'timestamp': datetime.now().isoformat()
        }
        messages_store.append({"role":'human', "content":user_message})
        
        ai_response = get_AI_response(
            messages_store,
            debug = True if os.getenv('AI_DEBUG') == 'Y' else False,
            model_name=selected_model
        )
        ai_msg = {
            'sender': 'ai',
            'message': '\n'.join([i['text'] for i in ai_response if isinstance(i,dict) and i['type'] == 'text']) if isinstance(ai_response,list) else ai_response,
            'timestamp': datetime.now().isoformat()
        }
        messages_store.append({"role":'ai', "content":ai_response})
        
        return jsonify({
            'user_message': user_msg,
            'ai_response': ai_msg,
            'model': selected_model
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages', methods=['GET'])
def get_messages():
    return jsonify({'messages': messages_store})

if __name__ == '__main__':
    app.run(host = '0.0.0.0',
            port = os.environ['PORT'] if os.getenv('PORT') is not None else 4000, debug=True)
