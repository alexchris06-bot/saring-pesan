import joblib
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Daftar domain & shortlink resmi terpercaya
DOMAIN_RESMI = [
    'tsel.me',
    'telkomsel.com',
    'telkomsel.co.id',
    'isat.me',
    'indosatooredoo.com',
    'xl.co.id',
    'axis.co.id',
    'tri.co.id',
    'smartfren.com',
    'bca.co.id',
    'bri.co.id',
    'mandiri.co.id',
    'bni.co.id',
    'cimbniaga.co.id',
    'gojek.com',
    'grab.com',
    'tokopedia.com',
    'shopee.co.id',
    'bukalapak.com',
]

# ==========================================
# 1. Buka Dataset CSV
# ==========================================
daftar_file_csv = [
    'combined_sms_spam_ham.csv',
    'sms_spam_indo_gevabriel.csv',
    'dataset_sms_spam_v1.csv',
]

list_dataframe = []

for file in daftar_file_csv:
  try:
    temp_df = pd.read_csv(file)
    temp_df = temp_df.rename(
        columns={
            'text': 'pesan',
            'teks': 'pesan',
            'Teks': 'pesan',
            'Pesan': 'pesan',
            'spam_ham_label': 'label',
            'Kategori': 'label',
            'Label': 'label',
            'kategori': 'label',
        }
    )

    if 'pesan' in temp_df.columns and 'label' in temp_df.columns:
      list_dataframe.append(temp_df[['pesan', 'label']])
      print(f'✅ Berhasil membaca {file} ({len(temp_df)} baris data)')

  except Exception as e:
    print(f'⚠️ Gagal/Lewati {file}: {e}')

if not list_dataframe:
  print('❌ Tidak ada dataset yang dibaca!')
  exit()

df = pd.concat(list_dataframe, ignore_index=True)

# ==========================================
# 2. Penyelarasan Label
# ==========================================
mapping_label = {
    0: 'aman',
    2: 'aman',
    1: 'penipuan',
    '0': 'aman',
    '2': 'aman',
    '1': 'penipuan',
    'ham': 'aman',
    'promo': 'aman',
    'spam': 'penipuan',
    'aman': 'aman',
    'penipuan': 'penipuan',
}

df['label'] = df['label'].map(mapping_label).fillna(df['label'])
df = df[df['label'].isin(['aman', 'penipuan'])].copy()
df = df.drop_duplicates(subset=['pesan'])


# ==========================================
# 3. Preprocessing Teks Pintar (Link & APK)
# ==========================================
def bersihkan_teks(teks):
  teks = str(teks).lower()

  # Deteksi file APK
  teks = re.sub(r'\b\S+\.apk\b', ' fileapk ', teks)

  # Deteksi & klasifikasi URL/Link
  urls = re.findall(
      r'https?://\S+|www\.\S+|\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/[^\s]*', teks
  )
  for url in urls:
    is_resmi = any(domain in url for domain in DOMAIN_RESMI)
    if is_resmi:
      teks = teks.replace(url, ' linkresmi ')
    else:
      teks = teks.replace(url, ' linkmencurigakan ')

  teks = re.sub(r'[^a-zA-Z\s]', ' ', teks)
  return re.sub(r'\s+', ' ', teks).strip()


# ==========================================
# 4. Tambahan Data Sintetis (Sangat Penting!)
# ==========================================
# A. Penipuan & Phishing
data_penipuan = [
    (
        'Pemberitahuan Coretax DJP NIK Anda belum terverifikasi klik'
        ' https://djp-pajak.com/login'
    ),
    'Unduh file Coretax.apk untuk konfirmasi data pajak anda',
    'Penting! Akun diblokir verifikasi di http://bit.ly/pajak-djp',
    'Tagihan membengkak cek rincian di www.pajak-online.site',
    'SDR/I NIK anda terdeteksi ganda verifikasi di www.djp-online.xyz',
    'Pemberitahuan dari bank akun anda dibatalkan klik http://bit.ly/bank',
]

# B. SMS Resmi Operator & Bank (Agar tidak terdeteksi penipuan)
data_resmi_aman = [
    (
        'Isi ulang pulsa Rp 100,000 telah berhasil dengan SN:04255200000288634622'
        ' pada 26/08/2026 08:06:48.Beli paket internet&nelpon'
        ' TERMURAH:https://tsel.me/PastiMurah'
    ),
    (
        'Isi ulang pulsa Rp 50,000 telah berhasil dengan SN:102938102938. Beli'
        ' paket promo di https://tsel.me/PastiMurah'
    ),
    (
        'Isi ulang pulsa Rp 20,000 berhasil. Cek sisa kuota dan promo paket'
        ' internet di https://telkomsel.com'
    ),
    (
        'Pengisian pulsa berhasil Rp 100000. Ref SN 0098123719283. Cek paket'
        ' murah di https://isat.me/promo'
    ),
    (
        'Sisa kuota internet Anda tinggal 500MB. Beli paket kuota ekstra di'
        ' https://tsel.me/app'
    ),
    (
        'Transfer berhasil sebesar Rp 500.000 ke rekening 1234567890. No Ref:'
        ' 9812371'
    ),
    (
        'Pembayaran di Tokopedia sebesar Rp 150.000 berhasil. Terima kasih'
        ' telah berbelanja.'
    ),
    (
        'Kode OTP transaksi Anda adalah 481920. JANGAN BERIKAN KODE INI KEPADA'
        ' SIAPAPUN.'
    ),
]

df_sintetis = pd.DataFrame({
    'pesan': data_penipuan + data_resmi_aman,
    'label': ['penipuan'] * len(data_penipuan) + ['aman'] * len(data_resmi_aman),
})

df = pd.concat([df, df_sintetis], ignore_index=True)
df['pesan_bersih'] = df['pesan'].apply(bersihkan_teks)

print(f'📊 Total data unik gabungan untuk training: {len(df)} baris.')

# ==========================================
# 5. Training & Simpan Model
# ==========================================
vectorizer = TfidfVectorizer(ngram_range=(1, 2))
X = vectorizer.fit_transform(df['pesan_bersih'])
y = df['label']

model = MultinomialNB(alpha=0.1)
model.fit(X, y)

joblib.dump(model, 'model_naive_bayes.pkl')
joblib.dump(vectorizer, 'vectorizer_tfidf.pkl')

print('🎉 SELESAI! Model baru berhasil dilatih dan dikalibrasi!')