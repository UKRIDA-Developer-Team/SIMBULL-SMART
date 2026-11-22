| Metode | Cakupan | Pertanyaan yang dijawab | Di aplikasi |
|---|---|---|---|
| **Nilai Shapley eksak** (SHAP intervensional) | lokal, tahap RF | Faktor mana yang menaikkan atau menurunkan prediksi kecemasan siswa ini, dan seberapa besar? | Rekomendasi → Penjelasan AI → Prediksi kecemasan |
| **Kontribusi SMART** (bobot × utilitas) | lokal, tahap SMART | Kriteria mana yang membuat alternatif terpilih unggul? | Rekomendasi → Dari prediksi ke rekomendasi |
| **Kontrafaktual "bagaimana jika"** | lokal, RF + SMART | Apa yang berubah bila satu faktor diperbaiki ke tingkat siswa tipikal? | Rekomendasi → Bagaimana jika? |
| **Kepentingan permutasi** | global, RF | Seberapa besar galat naik bila informasi satu fitur dihilangkan? | bab ini |
| **PDP dan ICE** | global, RF | Bagaimana prediksi berubah mengikuti satu faktor, rata-rata dan per siswa? | bab ini |
| **Kepentingan Gini** | global, RF | Fitur mana yang paling banyak dipakai pohon untuk memecah data? | Bab 2 Model |

**Nilai Shapley.** Untuk prediksi *f(x)* dan himpunan fitur *F* (11 fitur), nilai fitur *i* adalah

$$
\phi_i = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!\,(|F|-|S|-1)!}{|F|!}\,\bigl[v(S \cup \{i\}) - v(S)\bigr],
$$

dengan *v(S)* = rata-rata prediksi ketika fitur dalam *S* memakai nilai siswa dan fitur lain memakai nilai siswa pembanding. Karena hanya ada 2¹¹ = 2.048 koalisi, semuanya dihitung (tanpa pendekatan sampling). Sifat yang diuji otomatis: jumlah φ = prediksi − rata-rata (*efisiensi*), fitur yang tidak dipakai model bernilai 0 (*dummy*), dan pada model linear φᵢ = βᵢ(xᵢ − x̄ᵢ).

**Batasan.** SHAP intervensional mengganti nilai fitur secara independen, sehingga dapat membuat kombinasi yang jarang terjadi bila fitur saling berkorelasi (misalnya stres dan kelelahan). Kontrafaktual adalah simulasi model, **bukan** bukti sebab-akibat. Semua penjelasan menerangkan perilaku model, bukan kondisi klinis siswa.
