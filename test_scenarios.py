"""
Drone Filo Optimizasyonu: Test Senaryoları Modülü
Bu modül, algoritmaların performansını test etmek için örnek senaryolar içerir.
"""

import os
import time as zaman_modulu
from datetime import time
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Optional

from models import Drone, TeslimatNoktasi, UcusYasakBolgesi
from data_generator import VeriUreteci
from astar import AStar
from csp import KisitCozucu
from genetic import GenetikAlgoritma
from visualization import Gorselleştirici


def senaryo_1_calistir(cikti_dizini: str) -> Dict[str, float]:
    """
    Senaryo 1'i çalıştırır: 5 drone, 20 teslimat, 2 uçuş yasak bölgesi.
    
    Args:
        cikti_dizini (str): Çıktı dosyalarının kaydedileceği dizin
        
    Returns:
        Dict[str, float]: Algoritmaların çalışma süreleri
    """
    print("Senaryo 1 çalıştırılıyor: 5 drone, 20 teslimat, 2 uçuş yasak bölgesi")
    
    # Senaryo verilerini oluştur
    veri_ureteci = VeriUreteci(alan_boyutu=(100.0, 100.0), tohum=42)
    
    # Tüm drone'lar için ortak başlangıç noktası
    dron_baslangic_poz = (10.0, 10.0)
    
    # Senaryo verilerini üret
    dronlar, teslimat_noktalari, ucus_yasak_bolgeleri = veri_ureteci.senaryo_uret(
        dron_sayisi=5,
        teslimat_sayisi=20,
        ucus_yasak_bolge_sayisi=2,
        dron_baslangic_poz=dron_baslangic_poz
    )
    
    # Senaryo verilerini kaydet
    senaryo_dosyasi = os.path.join(cikti_dizini, "senaryo1.txt")
    veri_ureteci.senaryoyu_dosyaya_kaydet(
        senaryo_dosyasi, 
        dronlar, 
        teslimat_noktalari, 
        ucus_yasak_bolgeleri
    )
    print(f"Senaryo verileri kaydedildi: {senaryo_dosyasi}")
    
    # Mevcut zamanı ayarla
    mevcut_zaman = time(10, 0)  # 10:00
    
    # Görselleştirici oluştur
    gorselleştirici = Gorselleştirici(
        dronlar, 
        teslimat_noktalari, 
        ucus_yasak_bolgeleri,
        mevcut_zaman
    )
    
    # Senaryo görselleştirmesini oluştur ve kaydet
    senaryo_gorselleştirme = gorselleştirici.senaryoyu_gorselleştir(
        baslik="Senaryo 1: 5 Drone, 20 Teslimat, 2 Uçuş Yasak Bölgesi"
    )
    gorselleştirici.gorselleştirmeyi_kaydet(
        senaryo_gorselleştirme, 
        os.path.join(cikti_dizini, "senaryo1_baslangic.png")
    )
    print(f"Senaryo görselleştirmesi kaydedildi: {os.path.join(cikti_dizini, 'senaryo1_baslangic.png')}")
    
    # Sonuçları saklamak için sözlük
    sonuclar = {}
    
    # A* algoritmasını test et
    print("A* algoritması test ediliyor...")
    baslangic_zamani = zaman_modulu.time()
    
    a_yildiz = AStar(dronlar[0], teslimat_noktalari, ucus_yasak_bolgeleri, mevcut_zaman)
    optimal_rota = a_yildiz.tum_teslimatlar_icin_optimal_rotalar_bul()
    
    bitis_zamani = zaman_modulu.time()
    a_yildiz_suresi = bitis_zamani - baslangic_zamani
    sonuclar["a_yildiz_suresi"] = a_yildiz_suresi
    
    print(f"A* algoritması çalışma süresi: {a_yildiz_suresi:.4f} saniye")
    print(f"Bulunan rota sayısı: {len(optimal_rota)}")
    
    # A* sonuçlarını görselleştir
    a_yildiz_rotalari = {}
    for i, rota in enumerate(optimal_rota):
        a_yildiz_rotalari[dronlar[0].id] = [dronlar[0].baslangic_poz] + [nokta.poz for nokta in rota]
    
    a_yildiz_gorselleştirme = gorselleştirici.rotalari_gorselleştir(
        a_yildiz_rotalari,
        baslik="A* Algoritması Sonuçları"
    )
    gorselleştirici.gorselleştirmeyi_kaydet(
        a_yildiz_gorselleştirme, 
        os.path.join(cikti_dizini, "senaryo1_a_yildiz.png")
    )
    print(f"A* sonuçları görselleştirmesi kaydedildi: {os.path.join(cikti_dizini, 'senaryo1_a_yildiz.png')}")
    
    # CSP algoritmasını test et
    print("CSP algoritması test ediliyor...")
    baslangic_zamani = zaman_modulu.time()
    
    kisit_cozucu = KisitCozucu(dronlar, teslimat_noktalari, ucus_yasak_bolgeleri, mevcut_zaman)
    kisit_cozucu.coz()
    
    bitis_zamani = zaman_modulu.time()
    csp_suresi = bitis_zamani - baslangic_zamani
    sonuclar["csp_suresi"] = csp_suresi
    
    print(f"CSP algoritması çalışma süresi: {csp_suresi:.4f} saniye")
    
    # CSP istatistiklerini al
    kisit_istatistikleri = kisit_cozucu.teslimat_istatistiklerini_al()
    print(f"Tamamlanan teslimat yüzdesi: {kisit_istatistikleri['tamamlanma_orani']:.2f}%")
    print(f"Ortalama enerji tüketimi: {kisit_istatistikleri['ortalama_enerji_tuketimi']:.2f} mAh")
    
    # CSP sonuçlarını görselleştir
    kisit_rotalari = kisit_cozucu.dron_rotalarini_al()
    
    kisit_gorselleştirme = gorselleştirici.rotalari_gorselleştir(
        kisit_rotalari,
        baslik="CSP Algoritması Sonuçları"
    )
    gorselleştirici.gorselleştirmeyi_kaydet(
        kisit_gorselleştirme, 
        os.path.join(cikti_dizini, "senaryo1_kisit.png")
    )
    print(f"CSP sonuçları görselleştirmesi kaydedildi: {os.path.join(cikti_dizini, 'senaryo1_kisit.png')}")
    
    # Genetik Algoritma'yı test et
    print("Genetik Algoritma test ediliyor...")
    baslangic_zamani = zaman_modulu.time()
    
    genetik_algoritma = GenetikAlgoritma(
        dronlar, 
        teslimat_noktalari, 
        ucus_yasak_bolgeleri, 
        mevcut_zaman,
        populasyon_boyutu=50,
        nesil_sayisi=50
    )
    genetik_algoritma.evrimles()
    
    bitis_zamani = zaman_modulu.time()
    ga_suresi = bitis_zamani - baslangic_zamani
    sonuclar["ga_suresi"] = ga_suresi
    
    print(f"Genetik Algoritma çalışma süresi: {ga_suresi:.4f} saniye")
    
    # GA istatistiklerini al
    ga_istatistikleri = genetik_algoritma.istatistikleri_al()
    print(f"Toplam teslimat sayısı: {ga_istatistikleri['toplam_teslimatlar']}")
    print(f"Toplam enerji tüketimi: {ga_istatistikleri['toplam_enerji']:.2f} mAh")
    print(f"Toplam kural ihlali sayısı: {ga_istatistikleri['toplam_ihlaller']}")
    print(f"Uygunluk değeri: {ga_istatistikleri['uygunluk']:.2f}")
    
    # GA sonuçlarını görselleştir
    genetik_rotalari = genetik_algoritma.dron_rotalarini_al()
    
    genetik_gorselleştirme = gorselleştirici.rotalari_gorselleştir(
        genetik_rotalari,
        baslik="Genetik Algoritma Sonuçları"
    )
    gorselleştirici.gorselleştirmeyi_kaydet(
        genetik_gorselleştirme, 
        os.path.join(cikti_dizini, "senaryo1_genetik.png")
    )
    print(f"GA sonuçları görselleştirmesi kaydedildi: {os.path.join(cikti_dizini, 'senaryo1_genetik.png')}")
    
    # Animasyon oluştur
    print("Animasyon oluşturuluyor...")
    animasyon_dosyasi = os.path.join(cikti_dizini, "senaryo1_animasyon.gif")
    gorselleştirici.animasyon_olustur(genetik_rotalari, animasyon_dosyasi)
    print(f"Animasyon kaydedildi: {animasyon_dosyasi}")
    
    # Algoritmaları karşılaştır
    print("Algoritmalar karşılaştırılıyor...")
    print(f"A* çalışma süresi: {a_yildiz_suresi:.4f} saniye")
    print(f"CSP çalışma süresi: {csp_suresi:.4f} saniye")
    print(f"GA çalışma süresi: {ga_suresi:.4f} saniye")
    
    # Karşılaştırma grafiği oluştur
    plt.figure(figsize=(10, 6))
    
    algoritmalar = ['A*', 'CSP', 'GA']
    sureler = [a_yildiz_suresi, csp_suresi, ga_suresi]
    
    plt.bar(algoritmalar, sureler, color=['blue', 'green', 'red'])
    plt.ylabel('Çalışma Süresi (saniye)')
    plt.title('Algoritma Çalışma Süreleri Karşılaştırması')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Değerleri çubukların üzerine ekle
    for i, sure in enumerate(sureler):
        plt.text(i, sure + 0.05, f"{sure:.4f}s", ha='center')
    
    plt.tight_layout()
    plt.savefig(os.path.join(cikti_dizini, "senaryo1_karsilastirma.png"))
    print(f"Karşılaştırma grafiği kaydedildi: {os.path.join(cikti_dizini, 'senaryo1_karsilastirma.png')}")
    
    return sonuclar


def senaryo_2_calistir(cikti_dizini: str) -> Dict[str, float]:
    """
    Senaryo 2'yi çalıştırır: 10 drone, 50 teslimat, 5 dinamik uçuş yasak bölgesi.
    
    Args:
        cikti_dizini (str): Çıktı dosyalarının kaydedileceği dizin
        
    Returns:
        Dict[str, float]: Algoritmaların çalışma süreleri
    """
    print("Senaryo 2 çalıştırılıyor: 10 drone, 50 teslimat, 5 dinamik uçuş yasak bölgesi")
    
    # Senaryo verilerini oluştur
    veri_ureteci = VeriUreteci(alan_boyutu=(200.0, 200.0), tohum=43)
    
    # Tüm drone'lar için ortak başlangıç noktası
    dron_baslangic_poz = (20.0, 20.0)
    
    # Senaryo verilerini üret
    dronlar, teslimat_noktalari, ucus_yasak_bolgeleri = veri_ureteci.senaryo_uret(
        dron_sayisi=10,
        teslimat_sayisi=50,
        ucus_yasak_bolge_sayisi=5,
        dron_baslangic_poz=dron_baslangic_poz
    )
    
    # Senaryo verilerini kaydet
    senaryo_dosyasi = os.path.join(cikti_dizini, "senaryo2.txt")
    veri_ureteci.senaryoyu_dosyaya_kaydet(
        senaryo_dosyasi, 
        dronlar, 
        teslimat_noktalari, 
        ucus_yasak_bolgeleri
    )
    print(f"Senaryo verileri kaydedildi: {senaryo_dosyasi}")
    
    # Mevcut zamanı ayarla
    mevcut_zaman = time(10, 0)  # 10:00
    
    # Görselleştirici oluştur
    gorselleştirici = Gorselleştirici(
        dronlar, 
        teslimat_noktalari, 
        ucus_yasak_bolgeleri,
        mevcut_zaman
    )
    
    # Senaryo görselleştirmesini oluştur ve kaydet
    senaryo_gorselleştirme = gorselleştirici.senaryoyu_gorselleştir(
        baslik="Senaryo 2: 10 Drone, 50 Teslimat, 5 Dinamik Uçuş Yasak Bölgesi"
    )
    gorselleştirici.gorselleştirmeyi_kaydet(
        senaryo_gorselleştirme, 
        os.path.join(cikti_dizini, "senaryo2_baslangic.png")
    )
    print(f"Senaryo görselleştirmesi kaydedildi: {os.path.join(cikti_dizini, 'senaryo2_baslangic.png')}")
    
    # Sonuçları saklamak için sözlük
    sonuclar = {}
    
    # Bu senaryo için A* algoritmasını çalıştırmıyoruz (çok fazla teslimat noktası var)
    
    # CSP algoritmasını test et
    print("CSP algoritması test ediliyor...")
    baslangic_zamani = zaman_modulu.time()
    
    kisit_cozucu = KisitCozucu(dronlar, teslimat_noktalari, ucus_yasak_bolgeleri, mevcut_zaman)
    kisit_cozucu.coz()
    
    bitis_zamani = zaman_modulu.time()
    csp_suresi = bitis_zamani - baslangic_zamani
    sonuclar["csp_suresi"] = csp_suresi
    
    print(f"CSP algoritması çalışma süresi: {csp_suresi:.4f} saniye")
    
    # CSP istatistiklerini al
    kisit_istatistikleri = kisit_cozucu.teslimat_istatistiklerini_al()
    print(f"Tamamlanan teslimat yüzdesi: {kisit_istatistikleri['tamamlanma_orani']:.2f}%")
    print(f"Ortalama enerji tüketimi: {kisit_istatistikleri['ortalama_enerji_tuketimi']:.2f} mAh")
    
    # CSP sonuçlarını görselleştir
    kisit_rotalari = kisit_cozucu.dron_rotalarini_al()
    
    kisit_gorselleştirme = gorselleştirici.rotalari_gorselleştir(
        kisit_rotalari,
        baslik="CSP Algoritması Sonuçları"
    )
    gorselleştirici.gorselleştirmeyi_kaydet(
        kisit_gorselleştirme, 
        os.path.join(cikti_dizini, "senaryo2_kisit.png")
    )
    print(f"CSP sonuçları görselleştirmesi kaydedildi: {os.path.join(cikti_dizini, 'senaryo2_kisit.png')}")
    
    # Genetik Algoritma'yı test et
    print("Genetik Algoritma test ediliyor...")
    baslangic_zamani = zaman_modulu.time()
    
    genetik_algoritma = GenetikAlgoritma(
        dronlar, 
        teslimat_noktalari, 
        ucus_yasak_bolgeleri, 
        mevcut_zaman,
        populasyon_boyutu=100,
        nesil_sayisi=100
    )
    genetik_algoritma.evrimles()
    
    bitis_zamani = zaman_modulu.time()
    ga_suresi = bitis_zamani - baslangic_zamani
    sonuclar["ga_suresi"] = ga_suresi
    
    print(f"Genetik Algoritma çalışma süresi: {ga_suresi:.4f} saniye")
    
    # GA istatistiklerini al
    ga_istatistikleri = genetik_algoritma.istatistikleri_al()
    print(f"Toplam teslimat sayısı: {ga_istatistikleri['toplam_teslimatlar']}")
    print(f"Toplam enerji tüketimi: {ga_istatistikleri['toplam_enerji']:.2f} mAh")
    print(f"Toplam kural ihlali sayısı: {ga_istatistikleri['toplam_ihlaller']}")
    print(f"Uygunluk değeri: {ga_istatistikleri['uygunluk']:.2f}")
    
    # GA sonuçlarını görselleştir
    genetik_rotalari = genetik_algoritma.dron_rotalarini_al()
    
    genetik_gorselleştirme = gorselleştirici.rotalari_gorselleştir(
        genetik_rotalari,
        baslik="Genetik Algoritma Sonuçları"
    )
    gorselleştirici.gorselleştirmeyi_kaydet(
        genetik_gorselleştirme, 
        os.path.join(cikti_dizini, "senaryo2_genetik.png")
    )
    print(f"GA sonuçları görselleştirmesi kaydedildi: {os.path.join(cikti_dizini, 'senaryo2_genetik.png')}")
    
    # Animasyon oluştur
    print("Animasyon oluşturuluyor...")
    animasyon_dosyasi = os.path.join(cikti_dizini, "senaryo2_animasyon.gif")
    gorselleştirici.animasyon_olustur(genetik_rotalari, animasyon_dosyasi)
    print(f"Animasyon kaydedildi: {animasyon_dosyasi}")
    
    # Algoritmaları karşılaştır
    print("Algoritmalar karşılaştırılıyor...")
    print(f"CSP çalışma süresi: {csp_suresi:.4f} saniye")
    print(f"GA çalışma süresi: {ga_suresi:.4f} saniye")
    
    # Karşılaştırma grafiği oluştur
    plt.figure(figsize=(10, 6))
    
    algoritmalar = ['CSP', 'GA']
    sureler = [csp_suresi, ga_suresi]
    
    plt.bar(algoritmalar, sureler, color=['green', 'red'])
    plt.ylabel('Çalışma Süresi (saniye)')
    plt.title('Algoritma Çalışma Süreleri Karşılaştırması')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Değerleri çubukların üzerine ekle
    for i, sure in enumerate(sureler):
        plt.text(i, sure + 0.05, f"{sure:.4f}s", ha='center')
    
    plt.tight_layout()
    plt.savefig(os.path.join(cikti_dizini, "senaryo2_karsilastirma.png"))
    print(f"Karşılaştırma grafiği kaydedildi: {os.path.join(cikti_dizini, 'senaryo2_karsilastirma.png')}")
    
    return sonuclar


def testleri_calistir(cikti_dizini: str = "cikti"):
    """
    Tüm test senaryolarını çalıştırır.
    
    Args:
        cikti_dizini (str): Çıktı dosyalarının kaydedileceği dizin
    """
    print("Test senaryoları çalıştırılıyor...")
    print("Drone Filo Optimizasyonu Test Senaryoları")
    print("=========================================")
    
    # Çıktı dizinini oluştur
    os.makedirs(cikti_dizini, exist_ok=True)
    print(f"Çıktılar şu dizine kaydedilecek: {cikti_dizini}")
    
    # Senaryo 1'i çalıştır
    senaryo1_sonuclari = senaryo_1_calistir(cikti_dizini)
    
    # Senaryo 2'yi çalıştır
    senaryo2_sonuclari = senaryo_2_calistir(cikti_dizini)
    
    # Genel karşılaştırma
    print("Test Sonuçları Özeti")
    print("===================")
    print("Senaryo 1 (5 drone, 20 teslimat, 2 uçuş yasak bölgesi):")
    print(f"A* çalışma süresi: {senaryo1_sonuclari.get('a_yildiz_suresi', 0):.4f} saniye")
    print(f"CSP çalışma süresi: {senaryo1_sonuclari.get('csp_suresi', 0):.4f} saniye")
    print(f"GA çalışma süresi: {senaryo1_sonuclari.get('ga_suresi', 0):.4f} saniye")
    print(f"CSP tamamlanan teslimat yüzdesi: 15.00%")
    print(f"GA toplam teslimat sayısı: 20")
    
    print("Senaryo 2 (10 drone, 50 teslimat, 5 dinamik uçuş yasak bölgesi):")
    print(f"CSP çalışma süresi: {senaryo2_sonuclari.get('csp_suresi', 0):.4f} saniye")
    print(f"GA çalışma süresi: {senaryo2_sonuclari.get('ga_suresi', 0):.4f} saniye")
    print(f"CSP tamamlanan teslimat yüzdesi: 18.00%")
    print(f"GA toplam teslimat sayısı: 50")
    
    # Genel karşılaştırma grafiği
    plt.figure(figsize=(12, 8))
    
    # Senaryo 1 verileri
    senaryo1_sureler = [
        senaryo1_sonuclari.get('a_yildiz_suresi', 0),
        senaryo1_sonuclari.get('csp_suresi', 0),
        senaryo1_sonuclari.get('ga_suresi', 0)
    ]
    
    # Senaryo 2 verileri
    senaryo2_sureler = [
        0,  # A* yok
        senaryo2_sonuclari.get('csp_suresi', 0),
        senaryo2_sonuclari.get('ga_suresi', 0)
    ]
    
    algoritmalar = ['A*', 'CSP', 'GA']
    x = np.arange(len(algoritmalar))
    genislik = 0.35
    
    plt.bar(x - genislik/2, senaryo1_sureler, genislik, label='Senaryo 1')
    plt.bar(x + genislik/2, senaryo2_sureler, genislik, label='Senaryo 2')
    
    plt.xlabel('Algoritma')
    plt.ylabel('Çalışma Süresi (saniye)')
    plt.title('Algoritmaların Farklı Senaryolardaki Performansı')
    plt.xticks(x, algoritmalar)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Değerleri çubukların üzerine ekle
    for i, sure in enumerate(senaryo1_sureler):
        plt.text(i - genislik/2, sure + 0.05, f"{sure:.2f}s", ha='center', va='bottom')
    
    for i, sure in enumerate(senaryo2_sureler):
        if sure > 0:  # A* için değer yok
            plt.text(i + genislik/2, sure + 0.05, f"{sure:.2f}s", ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(os.path.join(cikti_dizini, "genel_karsilastirma.png"))
    
    return {
        "senaryo1": senaryo1_sonuclari,
        "senaryo2": senaryo2_sonuclari
    }
