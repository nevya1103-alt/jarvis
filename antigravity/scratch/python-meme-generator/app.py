from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

IMGFLIP_API_URL = "https://api.imgflip.com/get_memes"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/memes')
def get_memes():
    try:
        response = requests.get(IMGFLIP_API_URL)
        response.raise_for_status()
        data = response.json()
        if data.get('success'):
            return jsonify({'success': True, 'memes': data['data']['memes']})
        else:
            return jsonify({'success': False, 'error': 'Failed to fetch from Imgflip API'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
