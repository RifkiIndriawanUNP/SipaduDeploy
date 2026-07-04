import pandas as pd
import os
import math

class DataLoader:
    def __init__(self):
        self.data = None
        self.load_data()
    
    def load_data(self):
        possible_paths = [
            os.path.join('data', 'Infrastruktur_jabar.csv'),
            os.path.join(os.path.dirname(__file__), 'data', 'Infrastruktur_jabar.csv'),
            'Infrastruktur_jabar.csv'
        ]
        
        csv_path = None
        for path in possible_paths:
            if os.path.exists(path):
                csv_path = path
                break
        
        if csv_path is None:
            print("ERROR: File CSV tidak ditemukan!")
            self.data = pd.DataFrame()
            return
        
        print(f"✅ CSV: {csv_path}")
        
        try:
            self.data = pd.read_csv(csv_path, sep=',', encoding='utf-8')
            self.data.columns = self.data.columns.str.strip()
            
            numeric_columns = [
                'Rumah Sakit', 'Puskesmas', 'SD', 'SMP', 'SMU', 
                'Pasar', 'Panjang Jalan', 'Luas Wilayah', 'Masjid',
                'Gereja Kristen', 'Gereja Katolik', 'Pura', 'Vihara/Klenteng',
                'Islam', 'Kristen', 'Katolik', 'Hindu', 'Budha', 'jumlah_penduduk',
                'Penduduk SD (7-12)', 'Penduduk SMP (13-15)', 'Penduduk SMU (16-18)'
            ]
            
            for col in numeric_columns:
                if col in self.data.columns:
                    self.data[col] = self.data[col].astype(str).str.replace(' ', '').str.replace(',', '.')
                    self.data[col] = pd.to_numeric(self.data[col], errors='coerce').fillna(0)
            
            self.data['kabupaten'] = self.data['kabupaten'].str.strip()
            self.data['kabupaten_upper'] = self.data['kabupaten'].str.upper()
            
            print(f"✅ Data siap: {len(self.data)} kabupaten")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.data = pd.DataFrame()
    
    def get_all_kabupaten(self):
        if self.data is not None and not self.data.empty:
            return self.data['kabupaten'].tolist()
        return []
    
    def get_all_data(self):
        if self.data is not None and not self.data.empty:
            return self.data.to_dict('records')
        return []
    
    def get_kabupaten_data(self, kabupaten_name):
        if self.data is not None and not self.data.empty:
            search_upper = kabupaten_name.strip().upper()
            
            kabupaten_data = self.data[self.data['kabupaten_upper'] == search_upper]
            if not kabupaten_data.empty:
                return self.clean_data_dict(kabupaten_data.iloc[0].to_dict())
            
            kabupaten_data = self.data[self.data['kabupaten_upper'].str.contains(search_upper, na=False)]
            if not kabupaten_data.empty:
                return self.clean_data_dict(kabupaten_data.iloc[0].to_dict())
            
            simplified = search_upper.replace('KABUPATEN ', '').replace('KOTA ', '').strip()
            kabupaten_data = self.data[self.data['kabupaten_upper'].str.contains(simplified, na=False)]
            if not kabupaten_data.empty:
                return self.clean_data_dict(kabupaten_data.iloc[0].to_dict())
        
        return None
    
    def clean_data_dict(self, data_dict):
        cleaned_data = {}
        for key, value in data_dict.items():
            if isinstance(value, float) and math.isnan(value):
                cleaned_data[key] = 0
            elif value is None:
                cleaned_data[key] = 0
            else:
                cleaned_data[key] = value
        return cleaned_data