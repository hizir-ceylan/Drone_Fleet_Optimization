"""
Drone Filo Optimizasyonu: Veri Yapıları Modülü
Bu modül, drone filo optimizasyonu projesinde kullanılan temel veri yapılarını içerir.
"""

from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass
from datetime import time


@dataclass
class Drone:
    """
    Drone sınıfı, bir drone'un özelliklerini temsil eder.
    
    Attributes:
        id (int): Drone'un benzersiz kimlik numarası
        maksimum_agirlik (float): Drone'un taşıyabileceği maksimum ağırlık (kg)
        batarya (int): Drone'un batarya kapasitesi (mAh)
        hiz (float): Drone'un hızı (m/s)
        baslangic_poz (Tuple[float, float]): Drone'un başlangıç koordinatları (x, y) metre cinsinden
        mevcut_poz (Tuple[float, float]): Drone'un mevcut koordinatları
        mevcut_batarya (int): Drone'un mevcut batarya durumu
        mevcut_yuk (float): Drone'un mevcut yükü
        musait_mi (bool): Drone'un müsait olup olmadığı
    """
    id: int
    maksimum_agirlik: float
    batarya: int
    hiz: float
    baslangic_poz: Tuple[float, float]
    mevcut_poz: Optional[Tuple[float, float]] = None
    mevcut_batarya: Optional[int] = None
    mevcut_yuk: float = 0.0
    musait_mi: bool = True
    
    def __post_init__(self):
        """Başlangıç değerlerini ayarlar."""
        if self.mevcut_poz is None:
            self.mevcut_poz = self.baslangic_poz
        if self.mevcut_batarya is None:
            self.mevcut_batarya = self.batarya
    
    def tasiyabilir_mi(self, agirlik: float) -> bool:
        """Drone'un belirli bir ağırlığı taşıyıp taşıyamayacağını kontrol eder."""
        return agirlik <= self.maksimum_agirlik
    
    def enerji_tuketimi_hesapla(self, mesafe: float, agirlik: float) -> int:
        """
        Belirli bir mesafe ve ağırlık için enerji tüketimini hesaplar.
        Basit bir model: Enerji = Mesafe * (1 + Ağırlık/10) * 10 mAh
        """
        return int(mesafe * (1 + agirlik/10) * 10)
    
    def yeterli_batarya_var_mi(self, mesafe: float, agirlik: float) -> bool:
        """Belirli bir mesafe ve ağırlık için yeterli batarya olup olmadığını kontrol eder."""
        gereken_enerji = self.enerji_tuketimi_hesapla(mesafe, agirlik)
        return self.mevcut_batarya >= gereken_enerji
    
    def pozisyon_guncelle(self, yeni_poz: Tuple[float, float], mesafe: float, agirlik: float):
        """Drone'un pozisyonunu ve batarya durumunu günceller."""
        self.mevcut_poz = yeni_poz
        tuketilen_enerji = self.enerji_tuketimi_hesapla(mesafe, agirlik)
        self.mevcut_batarya -= tuketilen_enerji
    
    def sifirla(self):
        """Drone'u başlangıç durumuna sıfırlar."""
        self.mevcut_poz = self.baslangic_poz
        self.mevcut_batarya = self.batarya
        self.mevcut_yuk = 0.0
        self.musait_mi = True


@dataclass
class TeslimatNoktasi:
    """
    Teslimat Noktası sınıfı, bir teslimat noktasının özelliklerini temsil eder.
    
    Attributes:
        id (int): Teslimat noktasının benzersiz kimlik numarası
        poz (Tuple[float, float]): Teslimatın yapılacağı koordinatlar (x, y) metre cinsinden
        agirlik (float): Paketin ağırlığı (kg)
        oncelik (int): Teslimatın öncelik seviyesi (1: düşük, 5: yüksek)
        zaman_araligi (Tuple[time, time]): Teslimatın kabul edilebilir zaman aralığı
        teslim_edildi_mi (bool): Teslimatın yapılıp yapılmadığı
    """
    id: int
    poz: Tuple[float, float]
    agirlik: float
    oncelik: int
    zaman_araligi: Tuple[time, time]
    teslim_edildi_mi: bool = False
    
    def __post_init__(self):
        """Öncelik değerinin geçerli olup olmadığını kontrol eder."""
        if not 1 <= self.oncelik <= 5:
            raise ValueError("Öncelik değeri 1 ile 5 arasında olmalıdır.")
    
    def zaman_araliginda_mi(self, mevcut_zaman: time) -> bool:
        """Mevcut zamanın teslimat zaman aralığında olup olmadığını kontrol eder."""
        return self.zaman_araligi[0] <= mevcut_zaman <= self.zaman_araligi[1]


@dataclass
class UcusYasakBolgesi:
    """
    Uçuşa Yasak Bölge sınıfı, bir uçuşa yasak bölgenin özelliklerini temsil eder.
    
    Attributes:
        id (int): Bölgenin benzersiz kimlik numarası
        koordinatlar (List[Tuple[float, float]]): Bölgenin köşe noktaları
        aktif_zaman (Tuple[time, time]): Bölgenin aktif olduğu zaman aralığı
    """
    id: int
    koordinatlar: List[Tuple[float, float]]
    aktif_zaman: Tuple[time, time]
    
    def aktif_mi(self, mevcut_zaman: time) -> bool:
        """Bölgenin belirli bir zamanda aktif olup olmadığını kontrol eder."""
        return self.aktif_zaman[0] <= mevcut_zaman <= self.aktif_zaman[1]
    
    def nokta_iceriyor_mu(self, nokta: Tuple[float, float]) -> bool:
        """
        Bir noktanın bölge içinde olup olmadığını kontrol eder.
        Ray casting algoritması kullanılır.
        """
        x, y = nokta
        n = len(self.koordinatlar)
        icinde = False
        
        p1x, p1y = self.koordinatlar[0]
        for i in range(1, n + 1):
            p2x, p2y = self.koordinatlar[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            icinde = not icinde
            p1x, p1y = p2x, p2y
        
        return icinde
    
    def cizgi_kesisiyor_mu(self, baslangic: Tuple[float, float], bitis: Tuple[float, float]) -> bool:
        """
        Bir çizginin bölgeyle kesişip kesişmediğini kontrol eder.
        Çizgi segmenti ile poligonun her bir kenarı arasında kesişim kontrolü yapılır.
        """
        # Çizgi segmenti ile poligonun her bir kenarı arasında kesişim kontrolü
        n = len(self.koordinatlar)
        for i in range(n):
            kenar_baslangic = self.koordinatlar[i]
            kenar_bitis = self.koordinatlar[(i + 1) % n]
            
            if self._cizgi_segmentleri_kesisiyor_mu(baslangic, bitis, kenar_baslangic, kenar_bitis):
                return True
        
        # Eğer başlangıç veya bitiş noktası poligon içindeyse
        if self.nokta_iceriyor_mu(baslangic) or self.nokta_iceriyor_mu(bitis):
            return True
        
        return False
    
    def _cizgi_segmentleri_kesisiyor_mu(
        self, 
        cizgi1_baslangic: Tuple[float, float], 
        cizgi1_bitis: Tuple[float, float],
        cizgi2_baslangic: Tuple[float, float], 
        cizgi2_bitis: Tuple[float, float]
    ) -> bool:
        """İki çizgi segmentinin kesişip kesişmediğini kontrol eder."""
        def yonelim(p, q, r):
            val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
            if val == 0:
                return 0  # Doğrusal
            return 1 if val > 0 else 2  # Saat yönünde veya Saat yönünün tersine
        
        def segment_uzerinde(p, q, r):
            return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
                    q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))
        
        p1, q1 = cizgi1_baslangic, cizgi1_bitis
        p2, q2 = cizgi2_baslangic, cizgi2_bitis
        
        o1 = yonelim(p1, q1, p2)
        o2 = yonelim(p1, q1, q2)
        o3 = yonelim(p2, q2, p1)
        o4 = yonelim(p2, q2, q1)
        
        # Genel durum
        if o1 != o2 and o3 != o4:
            return True
        
        # Özel durumlar
        if o1 == 0 and segment_uzerinde(p1, p2, q1):
            return True
        if o2 == 0 and segment_uzerinde(p1, q2, q1):
            return True
        if o3 == 0 and segment_uzerinde(p2, p1, q2):
            return True
        if o4 == 0 and segment_uzerinde(p2, q1, q2):
            return True
        
        return False
