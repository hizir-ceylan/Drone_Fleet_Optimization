"""
Drone Filo Optimizasyonu: A* Algoritması Modülü
Bu modül, drone teslimat rotalarının optimizasyonu için A* algoritmasını uygular.
"""

import heapq
import math
from typing import Dict, List, Tuple, Set, Optional, Callable
from datetime import time

from models import Drone, TeslimatNoktasi, UcusYasakBolgesi


class Dugum:
    """
    A* algoritması için düğüm sınıfı.
    
    Attributes:
        teslimat_noktasi (TeslimatNoktasi): Teslimat noktası
        g_skor (float): Başlangıç noktasından bu düğüme kadar olan maliyet
        h_skor (float): Bu düğümden hedefe olan tahmini maliyet (sezgisel)
        f_skor (float): Toplam maliyet (g_skor + h_skor)
        ebeveyn (Dugum): Bu düğüme ulaşmak için kullanılan önceki düğüm
    """
    def __init__(
        self, 
        teslimat_noktasi: TeslimatNoktasi, 
        g_skor: float = float('inf'), 
        h_skor: float = 0.0,
        ebeveyn: Optional['Dugum'] = None
    ):
        self.teslimat_noktasi = teslimat_noktasi
        self.g_skor = g_skor
        self.h_skor = h_skor
        self.f_skor = g_skor + h_skor
        self.ebeveyn = ebeveyn
    
    def __lt__(self, other: 'Dugum') -> bool:
        """Öncelik kuyruğu için karşılaştırma operatörü."""
        # Önce f_skor'a göre sırala
        if self.f_skor != other.f_skor:
            return self.f_skor < other.f_skor
        # f_skor eşitse, önceliği yüksek olan teslimatı tercih et
        return self.teslimat_noktasi.oncelik > other.teslimat_noktasi.oncelik
    
    def __eq__(self, other: object) -> bool:
        """Eşitlik kontrolü."""
        if not isinstance(other, Dugum):
            return False
        return self.teslimat_noktasi.id == other.teslimat_noktasi.id
    
    def __hash__(self) -> int:
        """Hash fonksiyonu."""
        return hash(self.teslimat_noktasi.id)


class AStar:
    """
    A* algoritması sınıfı.
    
    Bu sınıf, drone teslimat rotalarının optimizasyonu için A* algoritmasını uygular.
    """
    def __init__(
        self, 
        drone: Drone, 
        teslimat_noktalari: List[TeslimatNoktasi], 
        ucus_yasak_bolgeleri: List[UcusYasakBolgesi],
        mevcut_zaman: time
    ):
        """
        Args:
            drone (Drone): Rota planlaması yapılacak drone
            teslimat_noktalari (List[TeslimatNoktasi]): Teslimat noktaları listesi
            ucus_yasak_bolgeleri (List[UcusYasakBolgesi]): Uçuşa yasak bölgeler listesi
            mevcut_zaman (time): Mevcut zaman
        """
        self.drone = drone
        self.teslimat_noktalari = teslimat_noktalari
        self.ucus_yasak_bolgeleri = ucus_yasak_bolgeleri
        self.mevcut_zaman = mevcut_zaman
        
        # Aktif uçuşa yasak bölgeleri filtrele
        self.aktif_ucus_yasak_bolgeleri = [
            bolge for bolge in ucus_yasak_bolgeleri if bolge.aktif_mi(mevcut_zaman)
        ]
    
    def mesafe_hesapla(self, poz1: Tuple[float, float], poz2: Tuple[float, float]) -> float:
        """İki nokta arasındaki Öklid mesafesini hesaplar."""
        return math.sqrt((poz2[0] - poz1[0])**2 + (poz2[1] - poz1[1])**2)
    
    def kenar_maliyeti_hesapla(
        self, 
        baslangic_poz: Tuple[float, float], 
        hedef_nokta: TeslimatNoktasi
    ) -> float:
        """
        İki nokta arasındaki kenar maliyetini hesaplar.
        Maliyet = Mesafe × Ağırlık + (Öncelik × 100)
        """
        mesafe = self.mesafe_hesapla(baslangic_poz, hedef_nokta.poz)
        # Öncelik ters orantılı olarak etki eder (1: düşük, 5: yüksek)
        # Yüksek öncelikli teslimatlar daha düşük maliyet almalı
        oncelik_faktoru = (6 - hedef_nokta.oncelik) * 100  # 5 için 100, 1 için 500
        return mesafe * hedef_nokta.agirlik + oncelik_faktoru
    
    def sezgisel_hesapla(
        self, 
        poz: Tuple[float, float], 
        hedef_poz: Tuple[float, float]
    ) -> float:
        """
        A* algoritması için sezgisel fonksiyon.
        h(n) = Hedefe olan mesafe + Uçuş yasağı bölgelerine girme cezası
        """
        # Temel sezgisel: Hedefe olan direkt mesafe
        temel_sezgisel = self.mesafe_hesapla(poz, hedef_poz)
        
        # Uçuş yasağı bölgelerine girme cezası
        ucus_yasak_cezasi = 0.0
        for bolge in self.aktif_ucus_yasak_bolgeleri:
            if bolge.cizgi_kesisiyor_mu(poz, hedef_poz):
                ucus_yasak_cezasi += 1000.0  # Büyük bir ceza
        
        return temel_sezgisel + ucus_yasak_cezasi
    
    def yol_gecerli_mi(
        self, 
        baslangic_poz: Tuple[float, float], 
        bitis_poz: Tuple[float, float]
    ) -> bool:
        """
        İki nokta arasındaki yolun geçerli olup olmadığını kontrol eder.
        Uçuş yasağı bölgelerini ihlal etmemeli.
        """
        for bolge in self.aktif_ucus_yasak_bolgeleri:
            if bolge.cizgi_kesisiyor_mu(baslangic_poz, bitis_poz):
                return False
        return True
    
    def komsulari_al(
        self, 
        mevcut_dugum: Dugum, 
        ziyaret_edilmis: Set[int]
    ) -> List[Tuple[Dugum, float]]:
        """
        Bir düğümün komşularını döndürür.
        
        Args:
            mevcut_dugum (Dugum): Mevcut düğüm
            ziyaret_edilmis (Set[int]): Ziyaret edilmiş düğümlerin ID'leri
            
        Returns:
            List[Tuple[Dugum, float]]: (Komşu düğüm, kenar maliyeti) çiftlerinin listesi
        """
        komsular = []
        mevcut_poz = mevcut_dugum.teslimat_noktasi.poz
        
        for nokta in self.teslimat_noktalari:
            # Ziyaret edilmiş noktaları veya mevcut noktayı atla
            if nokta.id in ziyaret_edilmis or nokta.id == mevcut_dugum.teslimat_noktasi.id:
                continue
            
            # Drone'un taşıma kapasitesini kontrol et
            if not self.drone.tasiyabilir_mi(nokta.agirlik):
                continue
            
            # Yolun geçerli olup olmadığını kontrol et
            if not self.yol_gecerli_mi(mevcut_poz, nokta.poz):
                continue
            
            # Mesafeyi hesapla
            mesafe = self.mesafe_hesapla(mevcut_poz, nokta.poz)
            
            # Drone'un batarya durumunu kontrol et
            if not self.drone.yeterli_batarya_var_mi(mesafe, nokta.agirlik):
                continue
            
            # Kenar maliyetini hesapla
            kenar_maliyeti = self.kenar_maliyeti_hesapla(mevcut_poz, nokta)
            
            # Komşu düğümü oluştur
            komsu_dugum = Dugum(nokta)
            
            komsular.append((komsu_dugum, kenar_maliyeti))
        
        return komsular
    
    def yolu_yeniden_olustur(self, son_dugum: Dugum) -> List[TeslimatNoktasi]:
        """
        Son düğümden başlayarak yolu yeniden oluşturur.
        
        Args:
            son_dugum (Dugum): Son düğüm
            
        Returns:
            List[TeslimatNoktasi]: Teslimat noktalarının sıralı listesi
        """
        yol = []
        mevcut = son_dugum
        
        while mevcut:
            yol.append(mevcut.teslimat_noktasi)
            mevcut = mevcut.ebeveyn
        
        # Yolu tersine çevir (başlangıçtan sona)
        yol.reverse()
        
        return yol
    
    def optimal_rota_bul(
        self, 
        baslangic_noktasi: TeslimatNoktasi, 
        bitis_noktasi: Optional[TeslimatNoktasi] = None
    ) -> List[TeslimatNoktasi]:
        """
        Başlangıç noktasından bitiş noktasına (veya tüm noktalara) en uygun rotayı bulur.
        
        Args:
            baslangic_noktasi (TeslimatNoktasi): Başlangıç noktası
            bitis_noktasi (Optional[TeslimatNoktasi]): Bitiş noktası (None ise tüm noktaları ziyaret et)
            
        Returns:
            List[TeslimatNoktasi]: En uygun rota (teslimat noktalarının sıralı listesi)
        """
        # Başlangıç düğümünü oluştur
        baslangic_dugumu = Dugum(
            baslangic_noktasi, 
            g_skor=0.0, 
            h_skor=0.0 if bitis_noktasi is None else self.sezgisel_hesapla(
                baslangic_noktasi.poz, bitis_noktasi.poz
            )
        )
        
        # Açık ve kapalı setleri oluştur
        acik_set = []
        heapq.heappush(acik_set, baslangic_dugumu)
        acik_set_hash = {baslangic_dugumu.teslimat_noktasi.id: baslangic_dugumu}
        
        kapali_set = set()
        
        while acik_set:
            # En düşük f_skor'a sahip düğümü al
            mevcut_dugum = heapq.heappop(acik_set)
            mevcut_id = mevcut_dugum.teslimat_noktasi.id
            
            # Düğümü açık setten çıkar
            if mevcut_id in acik_set_hash:
                del acik_set_hash[mevcut_id]
            
            # Düğümü kapalı sete ekle
            kapali_set.add(mevcut_id)
            
            # Hedef kontrolü
            if bitis_noktasi and mevcut_dugum.teslimat_noktasi.id == bitis_noktasi.id:
                return self.yolu_yeniden_olustur(mevcut_dugum)
            
            # Tüm noktaları ziyaret ettik mi?
            if bitis_noktasi is None and len(kapali_set) == len(self.teslimat_noktalari):
                return self.yolu_yeniden_olustur(mevcut_dugum)
            
            # Komşuları kontrol et
            for komsu, kenar_maliyeti in self.komsulari_al(mevcut_dugum, kapali_set):
                # Yeni g_skor hesapla
                gecici_g_skor = mevcut_dugum.g_skor + kenar_maliyeti
                
                # Komşu açık sette mi?
                if komsu.teslimat_noktasi.id in acik_set_hash:
                    # Daha iyi bir yol bulduk mu?
                    if gecici_g_skor < acik_set_hash[komsu.teslimat_noktasi.id].g_skor:
                        # g_skor'u güncelle
                        acik_set_hash[komsu.teslimat_noktasi.id].g_skor = gecici_g_skor
                        acik_set_hash[komsu.teslimat_noktasi.id].f_skor = (
                            gecici_g_skor + acik_set_hash[komsu.teslimat_noktasi.id].h_skor
                        )
                        acik_set_hash[komsu.teslimat_noktasi.id].ebeveyn = mevcut_dugum
                else:
                    # Yeni bir düğüm ekle
                    komsu.g_skor = gecici_g_skor
                    komsu.h_skor = 0.0 if bitis_noktasi is None else self.sezgisel_hesapla(
                        komsu.teslimat_noktasi.poz, bitis_noktasi.poz
                    )
                    komsu.f_skor = komsu.g_skor + komsu.h_skor
                    komsu.ebeveyn = mevcut_dugum
                    
                    heapq.heappush(acik_set, komsu)
                    acik_set_hash[komsu.teslimat_noktasi.id] = komsu
        
        # Yol bulunamadı
        return []
    
    def tum_teslimatlar_icin_optimal_rotalar_bul(self) -> List[List[TeslimatNoktasi]]:
        """
        Tüm teslimatlar için en uygun rotaları bulur.
        
        Returns:
            List[List[TeslimatNoktasi]]: Her bir teslimat için en uygun rotaların listesi
        """
        # Teslimat noktalarını önceliğe göre sırala (yüksek öncelik önce)
        siralanmis_teslimatlar = sorted(
            self.teslimat_noktalari, 
            key=lambda x: x.oncelik, 
            reverse=True
        )
        
        rotalar = []
        ziyaret_edilmis = set()
        
        # Drone'un başlangıç noktasını temsil eden sanal bir teslimat noktası oluştur
        baslangic_teslimati = TeslimatNoktasi(
            id=-1,  # Özel ID
            poz=self.drone.baslangic_poz,
            agirlik=0.0,
            oncelik=1,  # En düşük öncelik değeri
            zaman_araligi=(time(0, 0), time(23, 59))  # Tüm gün
        )
        
        mevcut_teslimat = baslangic_teslimati
        
        # Tüm teslimatları ziyaret et
        while len(ziyaret_edilmis) < len(siralanmis_teslimatlar):
            en_iyi_rota = []
            en_iyi_skor = float('inf')
            
            for teslimat in siralanmis_teslimatlar:
                if teslimat.id in ziyaret_edilmis:
                    continue
                
                # Bu teslimat için en uygun rotayı bul
                rota = self.optimal_rota_bul(mevcut_teslimat, teslimat)
                
                if not rota:
                    continue
                
                # Rotanın toplam maliyetini hesapla
                toplam_maliyet = 0.0
                onceki_poz = mevcut_teslimat.poz
                
                for nokta in rota:
                    mesafe = self.mesafe_hesapla(onceki_poz, nokta.poz)
                    kenar_maliyeti = self.kenar_maliyeti_hesapla(onceki_poz, nokta)
                    toplam_maliyet += kenar_maliyeti
                    onceki_poz = nokta.poz
                
                # Öncelik faktörünü ekle
                oncelik_faktoru = (6 - teslimat.oncelik) * 100
                skor = toplam_maliyet - oncelik_faktoru
                
                if skor < en_iyi_skor:
                    en_iyi_skor = skor
                    en_iyi_rota = rota
            
            if not en_iyi_rota:
                break
            
            rotalar.append(en_iyi_rota)
            mevcut_teslimat = en_iyi_rota[-1]
            ziyaret_edilmis.add(mevcut_teslimat.id)
        
        return rotalar
