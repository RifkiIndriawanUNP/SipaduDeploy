import pandas as pd
import os
import math

class DataLoader:
    def __init__(self):
        self.data = None
        self.load_data()
    
    def load_data(self):
        """Load CSV data with comma separator"""
        # Path untuk Railway: cari di folder data/ di dalam backend
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'data', 'Infrastruktur_jabar.csv'),
            os.path.join(os.path.dirname(__file__), '..', 'data', 'Infrastruktur_jabar.csv'),
            os.path.join('data', 'Infrastruktur_jabar.csv'),
            'Infrastruktur_jabar.csv'
        ]
        
        csv_path = None
        for path in possible_paths:
            if os.path.exists(path):
                csv_path = path
                break
        
        if csv_path is None:
            print("="*60)
            print("ERROR: File CSV tidak ditemukan!")
            print("Lokasi yang dicari:")
            for path in possible_paths:
                print(f"  - {os.path.abspath(path)}")
            print("="*60)
            self.data = pd.DataFrame()
            return
        
        print(f"✅ File CSV ditemukan: {csv_path}")
        
        try:
            # Baca CSV dengan COMMA separator
            self.data = pd.read_csv(csv_path, sep=',', encoding='utf-8')
            
            print(f"✅ CSV berhasil dibaca")
            print(f"   - Jumlah baris: {len(self.data)}")
            print(f"   - Jumlah kolom: {len(self.data.columns)}")
            
            # Clean column names - remove whitespace
            self.data.columns = self.data.columns.str.strip()
            
            # List kolom yang perlu dibersihkan
            numeric_columns = [
                'Rumah Sakit', 'Puskesmas', 'SD', 'SMP', 'SMU', 
                'Pasar', 'Panjang Jalan', 'Luas Wilayah', 'Masjid',
                'Gereja Kristen', 'Gereja Katolik', 'Pura', 'Vihara/Klenteng',
                'Islam', 'Kristen', 'Katolik', 'Hindu', 'Budha', 'jumlah_penduduk',
                'Penduduk SD (7-12)', 'Penduduk SMP (13-15)', 'Penduduk SMU (16-18)'
            ]
            
            # Bersihkan setiap kolom numerik
            for col in numeric_columns:
                if col in self.data.columns:
                    # Convert to string dulu
                    self.data[col] = self.data[col].astype(str)
                    # Hapus spasi
                    self.data[col] = self.data[col].str.replace(' ', '')
                    # Ganti koma jadi titik (untuk desimal)
                    self.data[col] = self.data[col].str.replace(',', '.')
                    # Convert ke numeric, yang gagal jadi 0
                    self.data[col] = pd.to_numeric(self.data[col], errors='coerce').fillna(0)
            
            # Clean kabupaten names
            self.data['kabupaten'] = self.data['kabupaten'].str.strip()
            self.data['kabupaten_upper'] = self.data['kabupaten'].str.upper()
            
            # Debug: tampilkan sample data
            print(f"\n📊 Sample data ({len(self.data)} kabupaten):")
            for i in range(min(5, len(self.data))):
                row = self.data.iloc[i]
                print(f"   [{i}] '{row['kabupaten']}' -> penduduk={row['jumlah_penduduk']}")
            
            print(f"\n✅ Data siap!")
            
        except Exception as e:
            print(f"❌ Error membaca CSV: {e}")
            import traceback
            traceback.print_exc()
            self.data = pd.DataFrame()
    
    def get_all_kabupaten(self):
        """Get list of all kabupaten/kota (format asli dari CSV)"""
        if self.data is not None and not self.data.empty:
            return self.data['kabupaten'].tolist()
        return []
    
    def get_all_data(self):
        """Get all data as list of dictionaries (untuk perhitungan RDI global)"""
        if self.data is not None and not self.data.empty:
            return self.data.to_dict('records')
        return []
    
    def get_kabupaten_data(self, kabupaten_name):
        """Get data for specific kabupaten dengan multiple matching strategies"""
        if self.data is not None and not self.data.empty:
            search_name = kabupaten_name.strip()
            search_upper = search_name.upper()
            
            print(f"\n🔍 Mencari: '{search_name}'")
            
            # Strategy 1: Exact match (case insensitive)
            kabupaten_data = self.data[self.data['kabupaten_upper'] == search_upper]
            if not kabupaten_data.empty:
                print(f"   ✅ Exact match: '{kabupaten_data.iloc[0]['kabupaten']}'")
                return self.clean_data_dict(kabupaten_data.iloc[0].to_dict())
            
            # Strategy 2: Contains match
            kabupaten_data = self.data[self.data['kabupaten_upper'].str.contains(search_upper, na=False)]
            if not kabupaten_data.empty:
                print(f"   ✅ Contains match: '{kabupaten_data.iloc[0]['kabupaten']}'")
                return self.clean_data_dict(kabupaten_data.iloc[0].to_dict())
            
            # Strategy 3: Coba hapus "KABUPATEN " atau "KOTA " dari search
            simplified = search_upper.replace('KABUPATEN ', '').replace('KOTA ', '').strip()
            kabupaten_data = self.data[self.data['kabupaten_upper'].str.contains(simplified, na=False)]
            if not kabupaten_data.empty:
                print(f"   ✅ Simplified match: '{kabupaten_data.iloc[0]['kabupaten']}'")
                return self.clean_data_dict(kabupaten_data.iloc[0].to_dict())
            
            # Strategy 4: Coba dengan "KAB. " prefix
            with_kab = 'KAB. ' + simplified
            kabupaten_data = self.data[self.data['kabupaten_upper'].str.contains(with_kab, na=False)]
            if not kabupaten_data.empty:
                print(f"   ✅ KAB. match: '{kabupaten_data.iloc[0]['kabupaten']}'")
                return self.clean_data_dict(kabupaten_data.iloc[0].to_dict())
            
            print(f"   ❌ Tidak ditemukan!")
            print(f"   Available: {self.data['kabupaten'].tolist()}")
        
        return None
    
    def clean_data_dict(self, data_dict):
        """Clean NaN values from dictionary"""
        cleaned_data = {}
        for key, value in data_dict.items():
            if isinstance(value, float) and math.isnan(value):
                cleaned_data[key] = 0
            elif value is None:
                cleaned_data[key] = 0
            else:
                cleaned_data[key] = value
        return cleaned_data