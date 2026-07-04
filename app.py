from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from data_loader import DataLoader
from fuzzy_logic import FuzzyInfrastructure
import os
import math
import json

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float) and math.isnan(obj):
            return 0
        if isinstance(obj, float) and math.isinf(obj):
            return 0
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

print("\n" + "="*60)
print("🚀 SIPADU - Sistem Identifikasi Infrastruktur Jabar")
print("="*60)

data_loader = DataLoader()

def clean_for_json(obj):
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(v) for v in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0
        return obj
    else:
        return obj

@app.route('/')
def serve_frontend():
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except:
        return jsonify({'status': 'error', 'message': 'Frontend not found'})

@app.route('/<path:path>')
def serve_static(path):
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/test')
def test():
    kab_list = data_loader.get_all_kabupaten()
    return jsonify(clean_for_json({
        'status': 'success',
        'server_running': True,
        'data_loaded': len(kab_list) > 0,
        'total_kabupaten': len(kab_list),
        'kabupaten_list': kab_list[:5]
    }))

@app.route('/api/kabupaten', methods=['GET'])
def get_kabupaten_list():
    try:
        kabupaten_list = data_loader.get_all_kabupaten()
        return jsonify(clean_for_json({
            'status': 'success',
            'data': kabupaten_list,
            'total': len(kabupaten_list)
        }))
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/kabupaten/<kabupaten_name>', methods=['GET'])
def get_kabupaten_detail(kabupaten_name):
    try:
        data = data_loader.get_kabupaten_data(kabupaten_name)
        
        if data is None:
            available = data_loader.get_all_kabupaten()
            return jsonify({
                'status': 'error',
                'message': f'Kabupaten/Kota "{kabupaten_name}" tidak ditemukan',
                'available_kabupaten': available[:10]
            }), 404
        
        all_data = data_loader.get_all_data()
        fuzzy_calc = FuzzyInfrastructure(data, all_data)
        fuzzy_results = fuzzy_calc.calculate_all()
        
        response_data = {
            'kabupaten': str(data.get('kabupaten', '')),
            'jumlah_penduduk': int(data.get('jumlah_penduduk', 0)),
            'luas_wilayah': float(data.get('Luas Wilayah', 0)),
            'infrastruktur': fuzzy_results
        }
        
        return jsonify({
            'status': 'success',
            'data': clean_for_json(response_data)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_kabupaten():
    try:
        keyword = request.args.get('q', '').strip().upper()
        all_kabupaten = data_loader.get_all_kabupaten()
        
        filtered = [k for k in all_kabupaten if k.upper() == keyword]
        if not filtered:
            filtered = [k for k in all_kabupaten if keyword in k.upper()]
        if not filtered:
            simplified = keyword.replace('KABUPATEN ', '').replace('KOTA ', '')
            filtered = [k for k in all_kabupaten if simplified in k.upper()]
        
        return jsonify(clean_for_json({
            'status': 'success',
            'data': filtered,
            'keyword': keyword,
            'total': len(filtered)
        }))
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)