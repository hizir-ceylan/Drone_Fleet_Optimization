"""
Drone Filo Optimizasyonu: Ana Modül
Bu modül, drone filo optimizasyonu projesinin ana giriş noktasıdır.
"""

import os
import argparse
import time as zaman_modulu
from datetime import time

from models import Drone, TeslimatNoktasi, UcusYasakBolgesi
from data_generator import VeriUreteci
from astar import AStar
from csp import KisitCozucu
from genetic import GenetikAlgoritma
from visualization import Gorselleştirici
from test_scenarios import testleri_calistir


def main():
    """
    Ana fonksiyon.
    """
    # Komut satırı argümanlarını ayarla
    parser = argparse.ArgumentParser(description='Drone Filo Optimizasyonu')
    
    # Test senaryoları
    parser.add_argument('--test', action='store_true', help='Test senaryolarını çalıştır')
    
    # Veri üretimi
    parser.add_argument('--uret', action='store_true', help='Rastgele senaryo üret')
    parser.add_argument('--dron_sayisi', type=int, default=5, help='Drone sayısı')
    parser.add_argument('--teslimat_sayisi', type=int, default=20, help='Teslimat noktası sayısı')
    parser.add_argument('--ucus_yasak_bolge_sayisi', type=int, default=2, help='Uçuşa yasak bölge sayısı')
    
    # Senaryo yükleme ve çözme
    parser.add_argument('--senaryo', type=str, help='Senaryo dosyası')
    parser.add_argument('--coz', type=str, choices=['a_yildiz', 'kisit', 'genetik', 'hepsi'], 
                        help='Çözüm algoritması')
    
    # Görselleştirme
    parser.add_argument('--gorselleştir', action='store_true', help='Sonuçları görselleştir')
    parser.add_argument('--cikti_dizini', type=str, default='cikti', help='Çıktı dizini')
    
    args = parser.parse_args()
    
    # Çıktı dizinini oluştur
    os.makedirs(args.cikti_dizini, exist_ok=True)
    
    # Test senaryolarını çalıştır
    if args.test:
        testleri_calistir(args.cikti_dizini)
        return
    
    # Rastgele senaryo üret
    if args.uret:
        print(f"Rastgele senaryo üretiliyor: {args.dron_sayisi} drone, {args.teslimat_sayisi} teslimat, "
              f"{args.ucus_yasak_bolge_sayisi} uçuş yasak bölgesi")
        
        veri_ureteci = VeriUreteci()
        dronlar, teslimat_noktalari, ucus_yasak_bolgeleri = veri_ureteci.senaryo_uret(
            args.dron_sayisi,
            args.teslimat_sayisi,
            args.ucus_yasak_bolge_sayisi
        )
        
        # Senaryoyu kaydet
        senaryo_dosyasi = os.path.join(args.cikti_dizini, "senaryo_uretilen.txt")
        veri_ureteci.senaryoyu_dosyaya_kaydet(
            senaryo_dosyasi, 
            dronlar, 
            teslimat_noktalari, 
            ucus_yasak_bolgeleri
        )
        print(f"Senaryo kaydedildi: {senaryo_dosyasi}")
        
        # Görselleştir
        if args.gorselleştir:
            mevcut_zaman = time(10, 0)  # 10:00
            gorselleştirici = Gorselleştirici(
                dronlar, 
                teslimat_noktalari, 
                ucus_yasak_bolgeleri,
                mevcut_zaman
            )
            
            senaryo_gorselleştirme = gorselleştirici.senaryoyu_gorselleştir(
                baslik=f"Üretilen Senaryo: {args.dron_sayisi} Drone, {args.teslimat_sayisi} Teslimat, "
                      f"{args.ucus_yasak_bolge_sayisi} Uçuş Yasak Bölgesi"
            )
            
            gorselleştirici.gorselleştirmeyi_kaydet(
                senaryo_gorselleştirme, 
                os.path.join(args.cikti_dizini, "senaryo_uretilen.png")
            )
            print(f"Senaryo görselleştirmesi kaydedildi: {os.path.join(args.cikti_dizini, 'senaryo_uretilen.png')}")
        
        return
    
    # Senaryo yükle ve çöz
    if args.senaryo and args.coz:
        print(f"Senaryo yükleniyor: {args.senaryo}")
        
        # Senaryoyu yükle
        veri_ureteci = VeriUreteci()
        dronlar, teslimat_noktalari, ucus_yasak_bolgeleri = veri_ureteci.senaryoyu_dosyadan_yukle(args.senaryo)
        
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
        if args.gorselleştir:
            senaryo_gorselleştirme = gorselleştirici.senaryoyu_gorselleştir(
                baslik=f"Yüklenen Senaryo: {len(dronlar)} Drone, {len(teslimat_noktalari)} Teslimat, "
                      f"{len(ucus_yasak_bolgeleri)} Uçuş Yasak Bölgesi"
            )
            
            gorselleştirici.gorselleştirmeyi_kaydet(
                senaryo_gorselleştirme, 
                os.path.join(args.cikti_dizini, "senaryo_yuklenen.png")
            )
            print(f"Senaryo görselleştirmesi kaydedildi: {os.path.join(args.cikti_dizini, 'senaryo_yuklenen.png')}")
        
        # A* algoritması
        if args.coz in ['a_yildiz', 'hepsi']:
            print("A* algoritması çalıştırılıyor...")
            baslangic_zamani = zaman_modulu.time()
            
            a_yildiz = AStar(dronlar[0], teslimat_noktalari, ucus_yasak_bolgeleri, mevcut_zaman)
            optimal_rota = a_yildiz.tum_teslimatlar_icin_optimal_rotalar_bul()
            
            bitis_zamani = zaman_modulu.time()
            print(f"A* algoritması çalışma süresi: {bitis_zamani - baslangic_zamani:.4f} saniye")
            print(f"Bulunan rota sayısı: {len(optimal_rota)}")
            
            # A* sonuçlarını görselleştir
            if args.gorselleştir:
                a_yildiz_rotalari = {}
                for i, rota in enumerate(optimal_rota):
                    a_yildiz_rotalari[dronlar[0].id] = [dronlar[0].baslangic_poz] + [nokta.poz for nokta in rota]
                
                a_yildiz_gorselleştirme = gorselleştirici.rotalari_gorselleştir(
                    a_yildiz_rotalari,
                    baslik="A* Algoritması Sonuçları"
                )
                
                gorselleştirici.gorselleştirmeyi_kaydet(
                    a_yildiz_gorselleştirme, 
                    os.path.join(args.cikti_dizini, "sonuc_a_yildiz.png")
                )
                print(f"A* sonuçları görselleştirmesi kaydedildi: {os.path.join(args.cikti_dizini, 'sonuc_a_yildiz.png')}")
        
        # CSP algoritması
        if args.coz in ['kisit', 'hepsi']:
            print("CSP algoritması çalıştırılıyor...")
            baslangic_zamani = zaman_modulu.time()
            
            kisit_cozucu = KisitCozucu(dronlar, teslimat_noktalari, ucus_yasak_bolgeleri, mevcut_zaman)
            kisit_cozucu.coz()
            
            bitis_zamani = zaman_modulu.time()
            print(f"CSP algoritması çalışma süresi: {bitis_zamani - baslangic_zamani:.4f} saniye")
            
            # CSP istatistiklerini al
            kisit_istatistikleri = kisit_cozucu.teslimat_istatistiklerini_al()
            print(f"Tamamlanan teslimat yüzdesi: {kisit_istatistikleri['tamamlanma_orani']:.2f}%")
            print(f"Ortalama enerji tüketimi: {kisit_istatistikleri['ortalama_enerji_tuketimi']:.2f} mAh")
            
            # CSP sonuçlarını görselleştir
            if args.gorselleştir:
                kisit_rotalari = kisit_cozucu.dron_rotalarini_al()
                
                kisit_gorselleştirme = gorselleştirici.rotalari_gorselleştir(
                    kisit_rotalari,
                    baslik="CSP Algoritması Sonuçları"
                )
                
                gorselleştirici.gorselleştirmeyi_kaydet(
                    kisit_gorselleştirme, 
                    os.path.join(args.cikti_dizini, "sonuc_kisit.png")
                )
                print(f"CSP sonuçları görselleştirmesi kaydedildi: {os.path.join(args.cikti_dizini, 'sonuc_kisit.png')}")
        
        # Genetik Algoritma
        if args.coz in ['genetik', 'hepsi']:
            print("Genetik Algoritma çalıştırılıyor...")
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
            print(f"Genetik Algoritma çalışma süresi: {bitis_zamani - baslangic_zamani:.4f} saniye")
            
            # GA istatistiklerini al
            ga_istatistikleri = genetik_algoritma.istatistikleri_al()
            print(f"Toplam teslimat sayısı: {ga_istatistikleri['toplam_teslimatlar']}")
            print(f"Toplam enerji tüketimi: {ga_istatistikleri['toplam_enerji']:.2f} mAh")
            print(f"Toplam kural ihlali sayısı: {ga_istatistikleri['toplam_ihlaller']}")
            print(f"Uygunluk değeri: {ga_istatistikleri['uygunluk']:.2f}")
            
            # GA sonuçlarını görselleştir
            if args.gorselleştir:
                genetik_rotalari = genetik_algoritma.dron_rotalarini_al()
                
                genetik_gorselleştirme = gorselleştirici.rotalari_gorselleştir(
                    genetik_rotalari,
                    baslik="Genetik Algoritma Sonuçları"
                )
                
                gorselleştirici.gorselleştirmeyi_kaydet(
                    genetik_gorselleştirme, 
                    os.path.join(args.cikti_dizini, "sonuc_genetik.png")
                )
                print(f"GA sonuçları görselleştirmesi kaydedildi: {os.path.join(args.cikti_dizini, 'sonuc_genetik.png')}")
                
                # Animasyon oluştur
                animasyon_dosyasi = os.path.join(args.cikti_dizini, "sonuc_animasyon.gif")
                gorselleştirici.animasyon_olustur(genetik_rotalari, animasyon_dosyasi)
                print(f"Animasyon kaydedildi: {animasyon_dosyasi}")
        
        return
    
    # Hiçbir argüman verilmemişse yardım mesajını göster
    parser.print_help()


if __name__ == "__main__":
    main()
