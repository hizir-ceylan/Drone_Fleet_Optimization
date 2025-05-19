"""
Drone Filo Optimizasyonu: Veri Üreteci Modülü
Bu modül, test senaryoları için örnek veri üretir.
"""

import random
import math
from typing import List, Tuple
from datetime import time

from models import Drone, TeslimatNoktasi, UcusYasakBolgesi


class VeriUreteci:
    """
    Örnek veri üreteci sınıfı.
    
    Bu sınıf, test senaryoları için rastgele drone'lar, teslimat noktaları ve
    uçuşa yasak bölgeler üretir.
    """
    def __init__(
        self, 
        alan_boyutu: Tuple[float, float] = (100.0, 100.0),
        tohum: int = None
    ):
        """
        Args:
            alan_boyutu (Tuple[float, float]): Harita boyutu (genişlik, yükseklik)
            tohum (int): Rastgele sayı üreteci için tohum değeri
        """
        self.alan_genisligi, self.alan_yuksekligi = alan_boyutu
        
        if tohum is not None:
            random.seed(tohum)
    
    def dronlari_uret(
        self, 
        adet: int, 
        baslangic_poz: Tuple[float, float] = None
    ) -> List[Drone]:
        """
        Rastgele drone'lar üretir.
        
        Args:
            adet (int): Üretilecek drone sayısı
            baslangic_poz (Tuple[float, float]): Tüm drone'ların başlangıç pozisyonu
                                               (None ise rastgele üretilir)
            
        Returns:
            List[Drone]: Üretilen drone'ların listesi
        """
        dronlar = []
        
        for i in range(adet):
            # Rastgele başlangıç pozisyonu
            if baslangic_poz is None:
                poz_x = random.uniform(0, self.alan_genisligi)
                poz_y = random.uniform(0, self.alan_yuksekligi)
                dron_baslangic_poz = (poz_x, poz_y)
            else:
                dron_baslangic_poz = baslangic_poz
            
            # Rastgele drone özellikleri
            maksimum_agirlik = random.uniform(1.0, 5.0)  # 1-5 kg
            batarya = random.randint(5000, 10000)  # 5000-10000 mAh
            hiz = random.uniform(5.0, 15.0)  # 5-15 m/s
            
            dron = Drone(
                id=i,
                maksimum_agirlik=maksimum_agirlik,
                batarya=batarya,
                hiz=hiz,
                baslangic_poz=dron_baslangic_poz
            )
            
            dronlar.append(dron)
        
        return dronlar
    
    def teslimat_noktalari_uret(self, adet: int) -> List[TeslimatNoktasi]:
        """
        Rastgele teslimat noktaları üretir.
        
        Args:
            adet (int): Üretilecek teslimat noktası sayısı
            
        Returns:
            List[TeslimatNoktasi]: Üretilen teslimat noktalarının listesi
        """
        teslimat_noktalari = []
        
        for i in range(adet):
            # Rastgele pozisyon
            poz_x = random.uniform(0, self.alan_genisligi)
            poz_y = random.uniform(0, self.alan_yuksekligi)
            poz = (poz_x, poz_y)
            
            # Rastgele ağırlık
            agirlik = random.uniform(0.5, 4.0)  # 0.5-4 kg
            
            # Rastgele öncelik
            oncelik = random.randint(1, 5)  # 1-5
            
            # Rastgele zaman aralığı
            baslangic_saat = random.randint(8, 16)
            baslangic_dakika = random.choice([0, 15, 30, 45])
            
            bitis_saat = baslangic_saat + random.randint(1, 3)
            if bitis_saat > 18:
                bitis_saat = 18
            bitis_dakika = random.choice([0, 15, 30, 45])
            
            zaman_araligi = (
                time(baslangic_saat, baslangic_dakika),
                time(bitis_saat, bitis_dakika)
            )
            
            teslimat_noktasi = TeslimatNoktasi(
                id=i,
                poz=poz,
                agirlik=agirlik,
                oncelik=oncelik,
                zaman_araligi=zaman_araligi
            )
            
            teslimat_noktalari.append(teslimat_noktasi)
        
        return teslimat_noktalari
    
    def ucus_yasak_bolgeleri_uret(self, adet: int) -> List[UcusYasakBolgesi]:
        """
        Rastgele uçuşa yasak bölgeler üretir.
        
        Args:
            adet (int): Üretilecek uçuşa yasak bölge sayısı
            
        Returns:
            List[UcusYasakBolgesi]: Üretilen uçuşa yasak bölgelerin listesi
        """
        ucus_yasak_bolgeleri = []
        
        for i in range(adet):
            # Rastgele merkez
            merkez_x = random.uniform(0, self.alan_genisligi)
            merkez_y = random.uniform(0, self.alan_yuksekligi)
            
            # Rastgele boyut
            yaricap = random.uniform(5.0, 15.0)
            
            # Rastgele köşe sayısı
            kose_sayisi = random.randint(3, 6)
            
            # Poligon köşelerini oluştur
            koordinatlar = []
            for j in range(kose_sayisi):
                aci = 2 * math.pi * j / kose_sayisi
                
                # Düzensizlik ekle
                aci += random.uniform(-0.2, 0.2)
                
                # Yarıçapı değiştir
                r = yaricap * random.uniform(0.8, 1.2)
                
                x = merkez_x + r * math.cos(aci)
                y = merkez_y + r * math.sin(aci)
                
                # Harita sınırları içinde kal
                x = max(0, min(x, self.alan_genisligi))
                y = max(0, min(y, self.alan_yuksekligi))
                
                koordinatlar.append((x, y))
            
            # Rastgele zaman aralığı
            baslangic_saat = random.randint(8, 14)
            baslangic_dakika = random.choice([0, 15, 30, 45])
            
            sure = random.randint(2, 6)  # 2-6 saat
            bitis_saat = baslangic_saat + sure
            if bitis_saat > 18:
                bitis_saat = 18
            bitis_dakika = random.choice([0, 15, 30, 45])
            
            aktif_zaman = (
                time(baslangic_saat, baslangic_dakika),
                time(bitis_saat, bitis_dakika)
            )
            
            ucus_yasak_bolgesi = UcusYasakBolgesi(
                id=i,
                koordinatlar=koordinatlar,
                aktif_zaman=aktif_zaman
            )
            
            ucus_yasak_bolgeleri.append(ucus_yasak_bolgesi)
        
        return ucus_yasak_bolgeleri
    
    def senaryo_uret(
        self, 
        dron_sayisi: int, 
        teslimat_sayisi: int, 
        ucus_yasak_bolge_sayisi: int,
        dron_baslangic_poz: Tuple[float, float] = None
    ) -> Tuple[List[Drone], List[TeslimatNoktasi], List[UcusYasakBolgesi]]:
        """
        Tam bir senaryo üretir.
        
        Args:
            dron_sayisi (int): Drone sayısı
            teslimat_sayisi (int): Teslimat noktası sayısı
            ucus_yasak_bolge_sayisi (int): Uçuşa yasak bölge sayısı
            dron_baslangic_poz (Tuple[float, float]): Tüm drone'ların başlangıç pozisyonu
                                                   (None ise rastgele üretilir)
            
        Returns:
            Tuple[List[Drone], List[TeslimatNoktasi], List[UcusYasakBolgesi]]: Üretilen senaryo
        """
        dronlar = self.dronlari_uret(dron_sayisi, dron_baslangic_poz)
        teslimat_noktalari = self.teslimat_noktalari_uret(teslimat_sayisi)
        ucus_yasak_bolgeleri = self.ucus_yasak_bolgeleri_uret(ucus_yasak_bolge_sayisi)
        
        return dronlar, teslimat_noktalari, ucus_yasak_bolgeleri
    
    def senaryoyu_dosyaya_kaydet(
        self, 
        dosya_adi: str, 
        dronlar: List[Drone], 
        teslimat_noktalari: List[TeslimatNoktasi], 
        ucus_yasak_bolgeleri: List[UcusYasakBolgesi]
    ):
        """
        Senaryoyu dosyaya kaydeder.
        
        Args:
            dosya_adi (str): Dosya adı
            dronlar (List[Drone]): Drone'ların listesi
            teslimat_noktalari (List[TeslimatNoktasi]): Teslimat noktalarının listesi
            ucus_yasak_bolgeleri (List[UcusYasakBolgesi]): Uçuşa yasak bölgelerin listesi
        """
        with open(dosya_adi, 'w') as f:
            # Başlık
            f.write("# Drone Filo Optimizasyonu Senaryo Dosyası\n\n")
            
            # Drone'lar
            f.write("## DRONLAR\n")
            f.write("# id,maksimum_agirlik,batarya,hiz,baslangic_poz_x,baslangic_poz_y\n")
            for dron in dronlar:
                f.write(f"{dron.id},{dron.maksimum_agirlik},{dron.batarya},{dron.hiz},{dron.baslangic_poz[0]},{dron.baslangic_poz[1]}\n")
            
            f.write("\n")
            
            # Teslimat noktaları
            f.write("## TESLIMAT_NOKTALARI\n")
            f.write("# id,poz_x,poz_y,agirlik,oncelik,zaman_araligi_baslangic,zaman_araligi_bitis\n")
            for nokta in teslimat_noktalari:
                f.write(f"{nokta.id},{nokta.poz[0]},{nokta.poz[1]},{nokta.agirlik},{nokta.oncelik},{nokta.zaman_araligi[0]},{nokta.zaman_araligi[1]}\n")
            
            f.write("\n")
            
            # Uçuşa yasak bölgeler
            f.write("## UCUS_YASAK_BOLGELERI\n")
            f.write("# id,aktif_zaman_baslangic,aktif_zaman_bitis,kose_sayisi,koordinatlar\n")
            for bolge in ucus_yasak_bolgeleri:
                koordinat_str = ";".join([f"{x},{y}" for x, y in bolge.koordinatlar])
                f.write(f"{bolge.id},{bolge.aktif_zaman[0]},{bolge.aktif_zaman[1]},{len(bolge.koordinatlar)},{koordinat_str}\n")
    
    def senaryoyu_dosyadan_yukle(self, dosya_adi: str) -> Tuple[List[Drone], List[TeslimatNoktasi], List[UcusYasakBolgesi]]:
        """
        Senaryoyu dosyadan yükler.
        
        Args:
            dosya_adi (str): Dosya adı
            
        Returns:
            Tuple[List[Drone], List[TeslimatNoktasi], List[UcusYasakBolgesi]]: Yüklenen senaryo
        """
        dronlar = []
        teslimat_noktalari = []
        ucus_yasak_bolgeleri = []
        
        mevcut_bolum = None
        
        with open(dosya_adi, 'r') as f:
            for satir in f:
                satir = satir.strip()
                
                # Boş satırları ve yorumları atla
                if not satir or satir.startswith('#'):
                    continue
                
                # Bölüm başlıklarını kontrol et
                if satir.startswith('## '):
                    mevcut_bolum = satir[3:]
                    continue
                
                # Bölüme göre veri işle
                if mevcut_bolum == 'DRONLAR':
                    parcalar = satir.split(',')
                    dron = Drone(
                        id=int(parcalar[0]),
                        maksimum_agirlik=float(parcalar[1]),
                        batarya=int(parcalar[2]),
                        hiz=float(parcalar[3]),
                        baslangic_poz=(float(parcalar[4]), float(parcalar[5]))
                    )
                    dronlar.append(dron)
                
                elif mevcut_bolum == 'TESLIMAT_NOKTALARI':
                    parcalar = satir.split(',')
                    
                    # Zaman aralığını parse et
                    baslangic_zaman_parcalari = parcalar[5].split(':')
                    bitis_zaman_parcalari = parcalar[6].split(':')
                    
                    zaman_araligi = (
                        time(int(baslangic_zaman_parcalari[0]), int(baslangic_zaman_parcalari[1])),
                        time(int(bitis_zaman_parcalari[0]), int(bitis_zaman_parcalari[1]))
                    )
                    
                    nokta = TeslimatNoktasi(
                        id=int(parcalar[0]),
                        poz=(float(parcalar[1]), float(parcalar[2])),
                        agirlik=float(parcalar[3]),
                        oncelik=int(parcalar[4]),
                        zaman_araligi=zaman_araligi
                    )
                    teslimat_noktalari.append(nokta)
                
                elif mevcut_bolum == 'UCUS_YASAK_BOLGELERI':
                    parcalar = satir.split(',')
                    
                    # Zaman aralığını parse et
                    baslangic_zaman_parcalari = parcalar[1].split(':')
                    bitis_zaman_parcalari = parcalar[2].split(':')
                    
                    aktif_zaman = (
                        time(int(baslangic_zaman_parcalari[0]), int(baslangic_zaman_parcalari[1])),
                        time(int(bitis_zaman_parcalari[0]), int(bitis_zaman_parcalari[1]))
                    )
                    
                    # Koordinatları parse et
                    kose_sayisi = int(parcalar[3])
                    koordinat_str = ','.join(parcalar[4:])
                    koordinat_parcalari = koordinat_str.split(';')
                    
                    koordinatlar = []
                    for i in range(kose_sayisi):
                        koordinat_parcalari_i = koordinat_parcalari[i].split(',')
                        koordinatlar.append((float(koordinat_parcalari_i[0]), float(koordinat_parcalari_i[1])))
                    
                    bolge = UcusYasakBolgesi(
                        id=int(parcalar[0]),
                        koordinatlar=koordinatlar,
                        aktif_zaman=aktif_zaman
                    )
                    ucus_yasak_bolgeleri.append(bolge)
        
        return dronlar, teslimat_noktalari, ucus_yasak_bolgeleri
