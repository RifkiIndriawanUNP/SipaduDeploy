from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from data_loader import DataLoader
from fuzzy_logic import FuzzyInfrastructure
import os
import math
import json

# Untuk Railway: static_folder mengarah ke folder frontend di dalam backend
app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# Custom JSON encoder untuk handle NaN
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float) and math.isnan(obj):
            return 0
        if isinstance(obj, float) and math.isinf(obj):
            return 0
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

# Initialize data loader
print("\n" + "="*60)
print("🚀 MEMULAI SISTEM IDENTIFIKASI INFRASTRUKTUR JABAR")
print("="*60)
data_loader = DataLoader()

def clean_for_json(obj):
    """Rekursif membersihkan nilai NaN dari dictionary/list"""
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
    """Serve frontend"""
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except:
        return jsonify({'status': 'error', 'message': 'Frontend not found'})

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/test')
def test():
    """Test endpoint"""
    kab_list = data_loader.get_all_kabupaten()
    return jsonify(clean_for_json({
        'status': 'success',
        'server_running': True,
        'data_loaded': len(kab_list) > 0,
        'total_kabupaten': len(kab_list),
        'kabupaten_list': kab_list[:5],
        'sample_search': {
            'try_these': [
                'KABUPATEN BANDUNG',
                'KABUPATEN CIAMIS',
                'KOTA BANDUNG'
            ]
        }
    }))

@app.route('/api/kabupaten', methods=['GET'])
def get_kabupaten_list():
    """Get list of all kabupaten/kota"""
    try:
        kabupaten_list = data_loader.get_all_kabupaten()
        print(f"📋 Returning {len(kabupaten_list)} kabupaten")
        return jsonify(clean_for_json({
            'status': 'success',
            'data': kabupaten_list,
            'total': len(kabupaten_list)
        }))
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/kabupaten/<kabupaten_name>', methods=['GET'])
def get_kabupaten_detail(kabupaten_name):
    """Get detailed analysis for specific kabupaten"""
    try:
        print(f"\n{'='*50}")
        print(f"🔍 Request untuk: '{kabupaten_name}'")
        
        data = data_loader.get_kabupaten_data(kabupaten_name)
        
        if data is None:
            available = data_loader.get_all_kabupaten()
            print(f"❌ Tidak ditemukan. Tersedia: {len(available)} kabupaten")
            return jsonify({
                'status': 'error',
                'message': f'Kabupaten/Kota "{kabupaten_name}" tidak ditemukan',
                'available_kabupaten': available[:10],
                'hint': 'Gunakan nama lengkap seperti "KABUPATEN BANDUNG" atau "KOTA BANDUNG"'
            }), 404
        
        print(f"✅ Data ditemukan untuk: {data.get('kabupaten', 'Unknown')}")
        print(f"   Penduduk: {data.get('jumlah_penduduk', 0)}")
        print(f"   Panjang Jalan: {data.get('Panjang Jalan', 0)}")
        print(f"   Luas Wilayah: {data.get('Luas Wilayah', 0)}")
        
        # Dapatkan semua data untuk perhitungan RDI min/max
        all_data = data_loader.get_all_data()
        
        # Calculate fuzzy logic dengan all_data
        fuzzy_calc = FuzzyInfrastructure(data, all_data)
        fuzzy_results = fuzzy_calc.calculate_all()
        
        # Log hasil perhitungan jalan
        if 'jalan' in fuzzy_results:
            j = fuzzy_results['jalan']
            print(f"   RDI: {j['rdi']}")
            print(f"   Metode: {j['metode']}")
            print(f"   Fuzzy Value: {j['fuzzy_value']}")
            print(f"   Status: {j['status']}")
        
        # Prepare response dengan nilai yang aman
        response_data = {
            'kabupaten': str(data.get('kabupaten', '')),
            'jumlah_penduduk': int(data.get('jumlah_penduduk', 0)),
            'luas_wilayah': float(data.get('Luas Wilayah', 0)),
            'infrastruktur': fuzzy_results
        }
        
        # Clean semua nilai
        cleaned_response = clean_for_json(response_data)
        
        print(f"✅ Perhitungan selesai")
        
        return jsonify({
            'status': 'success',
            'data': cleaned_response
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/search', methods=['GET'])
def search_kabupaten():
    """Search kabupaten by keyword"""
    try:
        keyword = request.args.get('q', '').strip()
        print(f"\n🔍 Pencarian: '{keyword}'")
        
        all_kabupaten = data_loader.get_all_kabupaten()
        
        # Multiple search strategies
        keyword_upper = keyword.upper()
        
        # Strategy 1: Exact match
        filtered = [kab for kab in all_kabupaten if kab.upper() == keyword_upper]
        
        # Strategy 2: Contains
        if not filtered:
            filtered = [kab for kab in all_kabupaten if keyword_upper in kab.upper()]
        
        # Strategy 3: Simplified (without KABUPATEN/KOTA prefix)
        if not filtered:
            simplified = keyword_upper.replace('KABUPATEN ', '').replace('KOTA ', '').replace('KAB. ', '')
            filtered = [kab for kab in all_kabupaten if simplified in kab.upper()]
        
        print(f"✅ Ditemukan: {len(filtered)} hasil")
        if filtered:
            print(f"   Hasil: {filtered}")
        
        return jsonify(clean_for_json({
            'status': 'success',
            'data': filtered,
            'keyword': keyword,
            'total': len(filtered)
        }))
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/debug/names')
def debug_names():
    """Debug endpoint to see exact names in database"""
    all_names = data_loader.get_all_kabupaten()
    return jsonify({
        'total': len(all_names),
        'names': all_names,
        'sample_request_urls': [
            f'/api/kabupaten/{name}' for name in all_names[:5]
        ]
    })

# Untuk Railway: gunakan PORT dari environment variable
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*60)
    print(f"🌐 Server berjalan di port {port}")
    print("📝 API Test: /api/test")
    print("📋 List: /api/kabupaten")
    print("="*60 + "\n")
    app.run(debug=False, host='0.0.0.0', port=port)