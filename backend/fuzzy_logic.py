import math

class FuzzyInfrastructure:
    def __init__(self, data, all_data=None):
        self.data = data
        self.all_data = all_data
        self.results = {}
    
    def safe_divide(self, a, b):
        """Safe division yang menghindari NaN dan infinity"""
        try:
            if b == 0 or b is None:
                return 0
            result = float(a) / float(b)
            if math.isnan(result) or math.isinf(result):
                return 0
            return result
        except:
            return 0
    
    def safe_value(self, value, default=0):
        """Mengembalikan nilai yang aman"""
        if value is None:
            return default
        try:
            val = float(value)
            if math.isnan(val) or math.isinf(val):
                return default
            return val
        except:
            return default
    
    def calculate_all(self):
        """Calculate all fuzzy values"""
        if not self.data:
            return {}
        
        self.calculate_rumah_sakit()
        self.calculate_puskesmas()
        self.calculate_sd()
        self.calculate_smp()
        self.calculate_smu()
        self.calculate_jalan()
        self.calculate_pasar()
        self.calculate_tempat_ibadah()
        
        return self.results
    
    def calculate_rumah_sakit(self):
        """Fuzzy calculation for Rumah Sakit"""
        jumlah_penduduk = self.safe_value(self.data.get('jumlah_penduduk', 0))
        jumlah_ideal = jumlah_penduduk / 120000 if jumlah_penduduk > 0 else 0
        data_asli = self.safe_value(self.data.get('Rumah Sakit', 0))
        
        fuzzy_value = self.safe_divide(data_asli, jumlah_ideal)
        
        self.results['rumah_sakit'] = {
            'data_asli': int(data_asli),
            'jumlah_ideal': round(jumlah_ideal, 2),
            'fuzzy_value': round(fuzzy_value, 4),
            'status': self.get_status(fuzzy_value)
        }
    
    def calculate_puskesmas(self):
        """Fuzzy calculation for Puskesmas"""
        jumlah_penduduk = self.safe_value(self.data.get('jumlah_penduduk', 0))
        jumlah_ideal = jumlah_penduduk / 120000 if jumlah_penduduk > 0 else 0
        data_asli = self.safe_value(self.data.get('Puskesmas', 0))
        
        fuzzy_value = self.safe_divide(data_asli, jumlah_ideal)
        
        self.results['puskesmas'] = {
            'data_asli': int(data_asli),
            'jumlah_ideal': round(jumlah_ideal, 2),
            'fuzzy_value': round(fuzzy_value, 4),
            'status': self.get_status(fuzzy_value)
        }
    
    def calculate_sd(self):
        """Fuzzy calculation for SD"""
        penduduk_sd = self.safe_value(self.data.get('Penduduk SD (7-12)', 0))
        jumlah_ideal = penduduk_sd / 1600 if penduduk_sd > 0 else 0
        data_asli = self.safe_value(self.data.get('SD', 0))
        
        fuzzy_value = self.safe_divide(data_asli, jumlah_ideal)
        
        self.results['sd'] = {
            'data_asli': int(data_asli),
            'jumlah_ideal': round(jumlah_ideal, 2),
            'fuzzy_value': round(fuzzy_value, 4),
            'status': self.get_status(fuzzy_value),
            'penduduk_usia_sd': int(penduduk_sd)
        }
    
    def calculate_smp(self):
        """Fuzzy calculation for SMP"""
        penduduk_smp = self.safe_value(self.data.get('Penduduk SMP (13-15)', 0))
        jumlah_ideal = penduduk_smp / 4800 if penduduk_smp > 0 else 0
        data_asli = self.safe_value(self.data.get('SMP', 0))
        
        fuzzy_value = self.safe_divide(data_asli, jumlah_ideal)
        
        self.results['smp'] = {
            'data_asli': int(data_asli),
            'jumlah_ideal': round(jumlah_ideal, 2),
            'fuzzy_value': round(fuzzy_value, 4),
            'status': self.get_status(fuzzy_value),
            'penduduk_usia_smp': int(penduduk_smp)
        }
    
    def calculate_smu(self):
        """Fuzzy calculation for SMU"""
        penduduk_smu = self.safe_value(self.data.get('Penduduk SMU (16-18)', 0))
        jumlah_ideal = penduduk_smu / 4800 if penduduk_smu > 0 else 0
        data_asli = self.safe_value(self.data.get('SMU', 0))
        
        fuzzy_value = self.safe_divide(data_asli, jumlah_ideal)
        
        self.results['smu'] = {
            'data_asli': int(data_asli),
            'jumlah_ideal': round(jumlah_ideal, 2),
            'fuzzy_value': round(fuzzy_value, 4),
            'status': self.get_status(fuzzy_value),
            'penduduk_usia_smu': int(penduduk_smu)
        }
    
    def calculate_jalan(self):
        """
        Fuzzy calculation for Jalan dengan aturan:
        - RDI = Panjang Jalan / Luas Wilayah
        - Jika RDI <= 1: Fuzzy = RDI (nilai langsung)
        - Jika RDI > 1: Fuzzy = (RDI - RDImin) / (RDImax - RDImin) (normalisasi)
        """
        panjang_jalan = self.safe_value(self.data.get('Panjang Jalan', 0))
        luas_wilayah = self.safe_value(self.data.get('Luas Wilayah', 1))
        
        # Hitung RDI
        rdi = self.safe_divide(panjang_jalan, luas_wilayah)
        
        # Tentukan fuzzy value berdasarkan aturan
        if rdi <= 1.0:
            # RDI <= 1, gunakan langsung
            fuzzy_value = rdi
            metode = "RDI langsung (RDI ≤ 1)"
        else:
            # RDI > 1, normalisasi dengan min-max
            rdi_min = 0.1
            rdi_max = 2.0
            
            # Hitung RDI min/max dari semua data jika tersedia
            if self.all_data is not None and len(self.all_data) > 0:
                all_rdi = []
                for d in self.all_data:
                    pj = self.safe_value(d.get('Panjang Jalan', 0))
                    lw = self.safe_value(d.get('Luas Wilayah', 1))
                    r = self.safe_divide(pj, lw)
                    if r > 0:
                        all_rdi.append(r)
                
                if all_rdi:
                    rdi_min = min(all_rdi)
                    rdi_max = max(all_rdi)
            
            # Normalisasi min-max
            if rdi_max - rdi_min > 0:
                fuzzy_value = (rdi - rdi_min) / (rdi_max - rdi_min)
                fuzzy_value = max(0.0, min(1.0, fuzzy_value))
            else:
                fuzzy_value = 0
            
            metode = f"Normalisasi min-max (RDI > 1)"
        
        self.results['jalan'] = {
            'panjang_jalan': round(panjang_jalan, 2),
            'luas_wilayah': round(luas_wilayah, 2),
            'rdi': round(rdi, 4),
            'fuzzy_value': round(fuzzy_value, 4),
            'status': self.get_status(fuzzy_value),
            'metode': metode,
            'rdi_min': round(rdi_min if rdi > 1.0 else 0, 4),
            'rdi_max': round(rdi_max if rdi > 1.0 else 0, 4)
        }
    
    def calculate_pasar(self):
        """Fuzzy calculation for Pasar"""
        jumlah_pasar = self.safe_value(self.data.get('Pasar', 0))
        jumlah_penduduk = self.safe_value(self.data.get('jumlah_penduduk', 1))
        
        pkp = self.safe_divide(jumlah_pasar * 100, jumlah_penduduk)
        
        # Convert PKP to fuzzy value
        pkp_ideal = 0.001
        fuzzy_value = min(self.safe_divide(pkp, pkp_ideal), 1)
        
        self.results['pasar'] = {
            'jumlah_pasar': int(jumlah_pasar),
            'pkp': round(pkp, 6),
            'fuzzy_value': round(fuzzy_value, 4),
            'status': self.get_status(fuzzy_value)
        }
    
    def calculate_tempat_ibadah(self):
        """Fuzzy calculation for Tempat Ibadah per agama"""
        ibadah_data = {
            'islam': {
                'tempat_ibadah': self.safe_value(self.data.get('Masjid', 0)),
                'jumlah_pemeluk': self.safe_value(self.data.get('Islam', 0))
            },
            'kristen': {
                'tempat_ibadah': self.safe_value(self.data.get('Gereja Kristen', 0)),
                'jumlah_pemeluk': self.safe_value(self.data.get('Kristen', 0))
            },
            'katolik': {
                'tempat_ibadah': self.safe_value(self.data.get('Gereja Katolik', 0)),
                'jumlah_pemeluk': self.safe_value(self.data.get('Katolik', 0))
            },
            'hindu': {
                'tempat_ibadah': self.safe_value(self.data.get('Pura', 0)),
                'jumlah_pemeluk': self.safe_value(self.data.get('Hindu', 0))
            },
            'budha': {
                'tempat_ibadah': self.safe_value(self.data.get('Vihara/Klenteng', 0)),
                'jumlah_pemeluk': self.safe_value(self.data.get('Budha', 0))
            }
        }
        
        tempat_ibadah_results = {}
        for agama, data_ibadah in ibadah_data.items():
            jumlah_pemeluk = data_ibadah['jumlah_pemeluk'] if data_ibadah['jumlah_pemeluk'] > 0 else 1
            rasio = self.safe_divide(data_ibadah['tempat_ibadah'] * 1000, jumlah_pemeluk)
            
            # Normalize to fuzzy value
            rasio_ideal = 0.5
            fuzzy_value = min(self.safe_divide(rasio, rasio_ideal), 1)
            
            tempat_ibadah_results[agama] = {
                'tempat_ibadah': int(data_ibadah['tempat_ibadah']),
                'jumlah_pemeluk': int(data_ibadah['jumlah_pemeluk']),
                'rasio': round(rasio, 4),
                'fuzzy_value': round(fuzzy_value, 4),
                'status': self.get_status(fuzzy_value)
            }
        
        self.results['tempat_ibadah'] = tempat_ibadah_results
    
    def get_status(self, fuzzy_value):
        """Determine status based on fuzzy value"""
        if fuzzy_value >= 1.0:
            return "Sangat Layak"
        elif fuzzy_value >= 0.8:
            return "Layak"
        elif fuzzy_value >= 0.6:
            return "Cukup Layak"
        elif fuzzy_value >= 0.4:
            return "Kurang Layak"
        elif fuzzy_value >= 0.2:
            return "Tidak Layak"
        else:
            return "Sangat Tidak Layak"