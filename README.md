# mt2macro (Open Source Automation)

![Status](https://img.shields.io/badge/Status-Stable-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)
![Purpose](https://img.shields.io/badge/Purpose-Research%20Only-orange)

Bilgisayarlı görü (computer vision) destekli, açık kaynaklı bir masaüstü otomasyon aracı. Bu proje, Python, OpenCV ve WinAPI kullanarak nasıl sağlam otomasyon yazılımları (robust software) geliştirileceğini gösterir.

## ⚠️ Önemli Yasal Uyarı

Bu yazılım tamamen **EĞİTİM AMAÇLI** (educational purposes only) hazırlanmıştır. Aşağıdaki teknolojileri göstermek için tasarlanmıştır:
- `customtkinter` ile modern arayüz tasarımı.
- `mss` ile gerçek zamanlı ekran yakalama (real-time screen capture).
- `opencv` ile şablon eşleştirme (template matching).

**Bu yazılımı kullanarak şunları kabul etmiş sayılırsınız:**
1. Sadece kişisel araştırma veya çevrimdışı testler (offline testing) için kullanacaksınız.
2. Üçüncü taraf yazılımların Hizmet Koşullarını (ToS) ihlal etmeyeceksiniz.
3. Yazarların yanlış kullanımdan (misuse) sorumlu olmadığını kabul edersiniz.

Detaylar için `EDUCATIONAL_CERTIFICATE.md` dosyasına bakabilirsiniz.

## Özellikler

- **Gizlilik Odaklı (Stealth)**: Sistem süreçlerini taklit etmek için pencere başlığını rastgele değiştirir.
- **Modern Arayüz (GUI)**:
  - **RGB Efekti**: Profesyonel görünüm için renk değiştiren kenarlıklar.
  - **Açılış Ekranı (Splash Screen)**: Yumuşak geçişli (smooth transition) yükleme ekranı.
  - **Koyu Tema (Dark Mode)**: Göz yormayan tasarım.
- **Performans**: İşlemciyi yormaz, arkada sessizce çalışır (~1-2% CPU).
- **Esneklik**: Görsel şablonlar (templates) sayesinde her türlü masaüstü uygulamasında çalışır.
- **Güvenlik**: Takılma durumlarını algılar ve zaman aşımı (timeout) koruması içerir.

## Kurulum

1.  **Projeyi İndirin**
    ```bash
    git clone https://github.com/guvenada/mt2macro.git
    cd mt2macro
    ```

2.  **Gerekli Kütüphaneleri Yükleyin**
    ```bash
    pip install -r requirements.txt
    ```

## Kullanım

1.  **Aracı Başlatın**
    ```bash
    python external_gui.py
    ```

2.  **Hedefleri Belirleyin (Setup)**
    - **Capture Main**'e tıklayarak ana hedefin resmini alın.
    - **Capture Sub**'a tıklayarak yan hedefleri (elitler, butonlar vb.) kaydedin.
    - *Not: Resimler klasöre `target.png` ve `elite1.png` olarak kaydedilir.*

3.  **Ayarlar (Config)**
    - **Properties** sekmesine gelin.
    - **Threshold** (Hassasiyet): Genelde 0.55 - 0.75 arası iyidir.
    - **Action Delay** (Hız): İşlem aralığını belirleyin.

4.  **Servisi Başlatın**
    - **START SERVICE** butonuna basın. Bot arka planda çalışmaya başlar.
    - **F12** ile Durdur/Devam Et (Pause/Resume).
    - **ESC** ile Acil Çıkış (Emergency Exit).

## Proje Yapısı

- `external_gui.py`: Ana program (Arayüzlü).
- `external_bot.py`: Komut satırı sürümü (Headless).
- `requirements.txt`: Gerekli kütüphaneler.
- `LICENSE`: MIT Lisansı.
- `EDUCATIONAL_CERTIFICATE.md`: Eğitim amaçlı kullanım sertifikası.

## Lisans

MIT Lisansı ile dağıtılmaktadır. Daha fazla bilgi için `LICENSE` dosyasına bakın.
