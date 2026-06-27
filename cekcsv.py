import pandas as pd

print("="*60)
print("Mengecek file CSV...")
print("="*60)

# Baca CSV dengan koma
df = pd.read_csv('data/Infrastruktur_jabar.csv', sep=',')
print(f"\n✅ CSV berhasil dibaca!")
print(f"Jumlah baris: {len(df)}")
print(f"Jumlah kolom: {len(df.columns)}")
print(f"\nNama kolom:")
for i, col in enumerate(df.columns):
    print(f"  {i+1}. '{col}'")

print(f"\n5 baris pertama:")
print(df.head())

print(f"\nSample data kabupaten:")
for i, row in df.iterrows():
    print(f"  - {row['kabupaten']}: {row['jumlah_penduduk']} penduduk")

print("\n✅ CSV OK!")