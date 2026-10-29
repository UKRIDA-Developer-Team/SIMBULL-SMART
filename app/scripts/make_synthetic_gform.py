"""Generate a SYNTHETIC Google Form export with the questionnaire's columns.

No real respondent is in this file. It exists so the real-data pipeline, the
tests and the app demo can run before the confidential export is dropped in.

The form was revised (context_ori.pdf -> context_new.pdf, minus the removed items).
Both versions are one Google Form, so a real export mixes rows answered before and
after the revision: headers carry the current titles, and the added questions are
empty for the older rows. --revised-share sets the share of rows answered on the
revised form; --legacy writes an export taken before the revision (original titles,
no added columns).

    python scripts/make_synthetic_gform.py                       # -> data/sample_gform.csv (250 rows)
    python scripts/make_synthetic_gform.py --n 60 --seed 7 --out data/private/gform_synthetic.csv
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from spk import config, gform  # noqa: E402

STUDY_TITLE = "Rata-Rata Jam Belajar Per Hari (Study Hours) di luar jam sekolah"
TASK_TITLE = "Target pengumpulan tugas"
ESSAY_TITLE = ("Ketika Anda terbangun dari tidur, baik di tengah malam maupun pada pagi hari, ceritakan apa "
               "yang biasanya Anda rasakan, pikirkan, atau alami pada saat tersebut.")

# Titles the revision renamed. Google keeps the column, so an export shows the current title;
# an export taken before the revision shows the old one.
LEGACY_TITLES = {
    "Jenis Kelamin (Gender)": "Jenis Kelamin",
    "Nama teman pemberi informasi": "Teman (Word of Mouth)",
    "Pada hari sekolah, biasanya pukul berapa Anda tidur?": "Kebiasaan tidur di hari sekolah",
    "Aktivitas harian di sekolah": "Aktivitas harian",
}

# Grid questions export as "Grid title [row text]".
GRIDS = {
    "Aktivitas harian di sekolah": {
        "lack_sleep": "Seberapa sering Anda merasa kurang tidur pada hari sekolah?",
        "sleepy_class": "Seberapa sering Anda merasa mengantuk saat mengikuti pelajaran?",
    },
    "Kualitas tidur": {
        "sleep_onset": "Seberapa sering kamu sulit tertidur dalam 30 menit setelah berbaring?",
        "night_waking": "Seberapa sering kamu terbangun di tengah malam lalu sulit tidur kembali?",
        "sleep_restless": "Seberapa sering kamu bermimpi buruk atau tidurmu terasa gelisah?",
    },
    "Interaksi dengan media sosial": {
        "socmed_study": "Seberapa sering Anda menggunakan media sosial ketika seharusnya sedang belajar?",
        "socmed_bed": "Seberapa sering Anda menggunakan media sosial sebelum tidur?",
    },
    "Tuntutan dan tekanan": {
        "many_tasks": "Seberapa sering Anda merasa memiliki terlalu banyak tugas sekolah pada waktu yang bersamaan?",
        "exam_stress": "Seberapa sering Anda merasa tertekan karena ujian, nilai, atau tuntutan akademik?",
        "fear_parents": "Saya merasa takut mengecewakan orang tua jika prestasi sekolah saya tidak sesuai dengan harapan mereka",
        "family_demand": "Keluarga saya menuntut saya untuk mendapatkan nilai akademik yang sangat tinggi.",
    },
    "Komunikasi dengan Keluarga": {
        "family_talk": "Saya mampu membicarakan kesulitanku di sekolah dengan keluarga tanpa takut dimarahi",
    },
    "Pernyataan mengenai kebiasaan fisik harian:": {
        "light_activity": "Seberapa sering Anda melakukan aktivitas fisik ringan-sedang (jalan kaki, naik tangga, bersepeda) .",
        "exercise_stress": "Seberapa sering Anda melakukan aktivitas fisik untuk menjaga kebugaran atau mengurangi rasa stres?",
    },
    "Kelelahan fisik dan emosional akibat rutinitas sekolah/belajar.": {
        "time_split": "Saya kesulitan membagi waktu antara kegiatan sekolah dan belajar.",
        "exhausted": "Saya merasa kelelahan karena banyaknya kegiatan sekolah yang saya ikuti.",
        "confidence": "Kegiatan sekolah yang saya ikuti membuat saya merasa lebih percaya diri dan memiliki tujuan.",
        "lost_interest": "Saya merasa kehilangan minat dan motivasi terhadap kegiatan belajar maupun sekolah",
    },
    "Lingkungan Pertemanan": {
        "peer_accepted": "Saya merasa diterima oleh teman-teman di sekolah.",
        "peer_trust": "Saya memiliki teman yang dapat saya percaya untuk bercerita ketika sedang menghadapi masalah.",
        "peer_support": "Saya merasa mendapat dukungan dari teman ketika menghadapi masalah sekolah.",
        "peer_pressure": "Saya pernah merasa tertekan untuk mengikuti apa yang dilakukan teman-teman saya.",
        "peer_conflict": "Konflik dengan teman membuat saya sulit berkonsentrasi pada kegiatan sekolah.",
    },
    "Psikologis:": {
        "p1_nervous": "Seberapa sering Anda merasakan gugup, cemas, atau gelisah saat menghadapi tugas/ujian/lomba/event penting?",
        "p2_worry": "Seberapa sering Anda merasakan kesulitan mengatasi rasa khawatir atau mengendalikan rasa khawatir?",
        "p3_focus": "Seberapa sering Anda berkonsentrasi ketika mengikuti pelajaran?",
        "p4_distracted": "Seberapa sering pikiran Anda terganggu oleh masalah pribadi ketika sedang belajar?",
        "p5_hard_finish": "Seberapa sering Anda merasa kesulitan menyelesaikan tugas karena sulit berkonsentrasi?",
        "p6_irritable": "Seberapa sering kamu merasa mudah tersinggung atau mudah marah?",
        "p7_avoid": "Seberapa sering kecemasan membuatmu menghindari kegiatan di sekolah (misalnya maju presentasi atau bertanya di kelas)?",
    },
    "Kebiasaan makan/jajan": {
        "pocket_money": "Saya memiliki uang saku yang cukup untuk memenuhi kebutuhan harian saya di sekolah.",
        "buy_food": "Saya sering membeli makanan atau minuman saat berada di sekolah.",
        "buy_sweet": "Saya sering membeli makanan/minuman manis saat di sekolah.",
        "buy_caffeine": "Saya sering membeli minuman berkafein (misalnya kopi, teh, minuman energi) saat sekolah.",
        "stress_food": "Saya memilih makanan/minuman tertentu ketika sedang merasa tertekan atau banyak tugas.",
        "calm_food": "Saya merasa lebih tenang setelah membeli atau mengonsumsi makanan/minuman yang saya sukai.",
        "skip_meal": "Seberapa sering Anda melewatkan waktu makan karena kegiatan sekolah atau belajar?",
    },
}

WAKE_NOTES = [
    "Biasanya masih mengantuk dan badan terasa lelah.",
    "Merasa cukup segar.",
    "Kadang jantung berdebar karena memikirkan ujian.",
    "Pusing dan sulit konsentrasi di pagi hari.",
]


def hours_label(h: float) -> str:
    if h < 0.5:
        return "Dibawah 30 menit"
    whole, half = int(h), (h - int(h)) >= 0.5
    if whole == 0:
        return "30 menit"
    return f"{whole} jam 30 menit" if half else f"{whole} jam"


def legacy_title(header: str) -> str:
    for new, old in LEGACY_TITLES.items():
        if header == new or header.startswith(new + " ["):
            return old + header[len(new):]
    return header


def generate(n: int = 250, seed: int = 42, reference_date: str = "2026-09-01",
             revised_share: float = 0.6, legacy: bool = False) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    m = gform.load_mapping()
    scales = m["scales"]
    added = {name for name, spec in m["fields"].items() if spec.get("new_form")}
    revised = np.zeros(n, dtype=bool) if legacy else rng.random(n) < revised_share
    z = rng.normal(size=n)                       # latent anxiety
    load = 0.6 * z + 0.8 * rng.normal(size=n)    # academic load, correlated with anxiety

    def likert(options, signal, noise=0.9, shift=0.0):
        labels = gform.scale_labels(options)
        k = len(labels)
        raw = (k + 1) / 2 + shift + signal * (k - 1) / 4 + rng.normal(scale=noise, size=n)
        idx = np.clip(np.rint(raw), 1, k).astype(int) - 1
        return [labels[i] for i in idx]

    def revised_only(values):
        return [v if r else None for v, r in zip(values, revised)]

    def capped(options, signal, shift=0.0):
        """The top option was added in the revision; earlier rows could only pick the one below."""
        labels = gform.scale_labels(options)
        return [labels[-2] if (v == labels[-1] and not r) else v
                for v, r in zip(likert(options, signal, shift=shift), revised)]

    ref = pd.Timestamp(reference_date)
    ages_days = rng.integers(int(15 * 365.25), int(18.9 * 365.25), size=n)
    birth = [(ref - pd.Timedelta(days=int(d))).strftime("%d/%m/%Y") for d in ages_days]
    # Original-form rows come in the first two weeks, revised rows a month later.
    minutes = rng.integers(0, 60 * 24 * 14, size=n) + np.where(revised, 60 * 24 * 30, 0)
    stamp = [(ref + pd.Timedelta(minutes=int(x))).strftime("%d/%m/%Y %H:%M:%S") for x in minutes]

    study = np.clip(2.5 + 1.2 * load + rng.normal(scale=1.2, size=n), 0, 11.5)
    sleep = np.clip(7.2 - 0.7 * z - 0.4 * load + rng.normal(scale=0.8, size=n), 4, 12)
    days_opts = list(m["value_maps"]["exercise_days"])
    days_idx = np.clip(np.rint(2 - 0.5 * z + rng.normal(scale=1.0, size=n)), 0, 4).astype(int)

    cols: dict[str, list] = {
        "Timestamp": stamp,
        "Jenis Kelamin (Gender)": rng.choice(["Laki-laki (Male)", "Perempuan (Female)"], size=n).tolist(),
        "Tanggal Lahir (Birth Date)": birth,
        "Nama Sekolah": [f"SMA SINTETIS {i % 7 + 1}" for i in range(n)],
        "Sumber Informasi Kuesioner": rng.choice(
            ["Teman / Mulut ke Mulut (Word of mouth)", "Social Media (Instagram, Tiktok, lainnya)",
             "Pengumuman Sekolah / Guru", "Poster / Mading"], size=n).tolist(),
        "Nama teman pemberi informasi": ["" for _ in range(n)],
    }
    frame = pd.DataFrame(cols)
    if not legacy:
        frame["Asal SMA teman pemberi informasi"] = ["" for _ in range(n)]
    # Two questions share each of these titles in the form -> duplicate headers in the export.
    frame[STUDY_TITLE] = [hours_label(h) for h in study]
    frame[STUDY_TITLE + " "] = capped(scales["late_night5"], load)
    frame[TASK_TITLE] = likert(scales["insufficient4"], load)
    frame[TASK_TITLE + " "] = capped(scales["late_tasks5"], load, shift=-0.8)
    frame["Nilai Rata-Rata Rapor Terakhir (Academic Performance)"] = np.round(
        np.clip(84 - 2.0 * z + rng.normal(scale=5, size=n), 60, 100), 1)
    if not legacy:
        frame["Seberapa sering kamu mendapat nilai di bawah yang kamu targetkan?"] = revised_only(
            likert(scales["freq5a"], 0.5 * z + 0.3 * load))
    frame["Berapa persentase kehadiran Anda dalam satu semester terakhir?"] = likert(
        scales["attendance5"], -0.3 * z, shift=1.2)
    frame["Rata-Rata Jam Tidur setiap malam (Sleep Hours)"] = [hours_label(round(h * 2) / 2) for h in sleep]
    frame["Pada hari sekolah, biasanya pukul berapa Anda tidur?"] = likert(scales["bedtime5"], 0.5 * z + 0.5 * load)
    if not legacy:
        frame[ESSAY_TITLE] = revised_only([WAKE_NOTES[i] if rng.random() < 0.5 else None
                                           for i in rng.integers(0, len(WAKE_NOTES), size=n)])
        frame["Berapa jam per hari kamu punya waktu bebas untuk bermain, hobi, atau bersantai "
              "(tidak menggunakan media sosial)?"] = revised_only(likert(scales["socmed5"], -0.4 * load))
    frame["Rata-rata berapa jam per hari Anda menggunakan media sosial?"] = likert(scales["socmed5"], 0.4 * z)
    frame["Dalam satu minggu terakhir, berapa hari Anda melakukan aktivitas fisik/olahraga "
          "(misal: lari, berenang, gym, olahraga tim) minimal 20–30 menit?"] = [days_opts[i] for i in days_idx]
    frame["Rata-rata berapa menit Anda melakukan aktivitas fisik setiap kali berolahraga?"] = rng.choice(
        [15, 20, 30, 45, 60, 90], size=n)
    frame["Berapa banyak kegiatan organisasi/ekstrakurikuler yang Anda ikuti?"] = rng.choice(
        ["0", "1", "2", "3"], size=n, p=[0.2, 0.4, 0.3, 0.1])
    frame["Rata-rata berapa jam per minggu yang Anda gunakan untuk kegiatan organisasi, "
          "ekstrakurikuler, atau kegiatan sekolah lainnya?"] = rng.integers(0, 12, size=n)
    frame["Dalam satu tahun terakhir, seberapa sering Anda mengikuti lomba/kompetisi?"] = rng.choice(
        list(m["value_maps"]["competitions"]), size=n, p=[0.5, 0.25, 0.2, 0.05])

    signal = {
        "many_tasks": load, "exam_stress": 0.6 * z + 0.4 * load, "fear_parents": 0.5 * z,
        "family_demand": 0.4 * z, "family_talk": -0.4 * z, "time_split": load,
        "exhausted": 0.5 * load + 0.4 * z, "lost_interest": 0.6 * z, "confidence": -0.3 * z,
        "lack_sleep": 0.6 * z + 0.3 * load, "sleepy_class": 0.5 * z, "sleep_onset": 0.6 * z,
        "night_waking": 0.5 * z, "sleep_restless": 0.5 * z, "socmed_study": 0.4 * z, "socmed_bed": 0.4 * z,
        "light_activity": -0.2 * z, "exercise_stress": -0.3 * z, "peer_accepted": -0.4 * z,
        "peer_trust": -0.4 * z, "peer_support": -0.4 * z, "peer_pressure": 0.4 * z,
        "peer_conflict": 0.5 * z, "pocket_money": -0.3 * z, "buy_food": 0 * z,
        "buy_sweet": 0.2 * z, "buy_caffeine": 0.3 * z, "stress_food": 0.4 * z,
        "calm_food": 0.3 * z, "skip_meal": 0.4 * z,
        "p1_nervous": 1.2 * z, "p2_worry": 1.2 * z, "p3_focus": -0.9 * z,
        "p4_distracted": 1.0 * z, "p5_hard_finish": 1.0 * z, "p6_irritable": 0.9 * z, "p7_avoid": 1.0 * z,
    }
    for grid, rows in GRIDS.items():
        for name, text in rows.items():
            if legacy and name in added:
                continue
            values = likert(scales[m["fields"][name]["scale"]], signal[name], noise=0.8)
            frame[f"{grid} [{text}]"] = revised_only(values) if name in added else values

    # Mimic the real export: the duplicated titles have identical header text.
    headers = [h.rstrip() if h.rstrip() in (STUDY_TITLE, TASK_TITLE) else h for h in frame.columns]
    frame.columns = [legacy_title(h) for h in headers] if legacy else headers
    return frame


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=250)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--revised-share", type=float, default=0.6,
                   help="share of rows answered on the revised form (the rest on the original)")
    p.add_argument("--legacy", action="store_true", help="export taken before the revision")
    p.add_argument("--out", default=str(config.APP_DIR / "data" / "sample_gform.csv"))
    args = p.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    generate(args.n, args.seed, revised_share=args.revised_share, legacy=args.legacy).to_csv(out, index=False)
    print(f"SYNTHETIC export: {args.n} rows -> {out}")


if __name__ == "__main__":
    main()
