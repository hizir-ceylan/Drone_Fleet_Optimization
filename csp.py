"""
Drone Filo Optimizasyonu: Kısıt Tatmin Problemi (CSP) Modülü
Bu modül, drone teslimat rotalarının optimizasyonu için CSP kısıtlarını uygular.
"""

from typing import List, Dict, Tuple, Set, Optional
from datetime import time, datetime, timedelta
import copy

from models import Drone, TeslimatNoktasi, UcusYasakBolgesi


class KisitCozucu:
    """
    CSP çözücü sınıfı.
    
    Bu sınıf, drone teslimat rotalarının optimizasyonu için CSP kısıtlarını uygular.
    """
    def __init__(
        self, 
        dronlar: List[Drone], 
        teslimat_noktalari: List[TeslimatNoktasi], 
        ucus_yasak_bolgeleri: List[UcusYasakBolgesi],
        baslangic_zamani: time
    ):
        """
        Args:
            dronlar (List[Drone]): Kullanılabilir drone'ların listesi
            teslimat_noktalari (List[TeslimatNoktasi]): Teslimat noktalarının listesi
            ucus_yasak_bolgeleri (List[UcusYasakBolgesi]): Uçuşa yasak bölgelerin listesi
            baslangic_zamani (time): Başlangıç zamanı
        """
        self.dronlar = dronlar
        self.teslimat_noktalari = teslimat_noktalari
        self.ucus_yasak_bolgeleri = ucus_yasak_bolgeleri
        self.baslangic_zamani = baslangic_zamani
        
        # Drone'ların mevcut durumlarını takip et
        self.dron_durumlari = {dron.id: copy.deepcopy(dron) for dron in dronlar}
        
        # Teslimat noktalarının durumlarını takip et
        self.teslimat_durumlari = {nokta.id: copy.deepcopy(nokta) for nokta in teslimat_noktalari}
        
        # Drone'lara atanmış teslimatları takip et
        self.atamalar: Dict[int, List[int]] = {dron.id: [] for dron in dronlar}
        
        # Drone'ların tahmini varış zamanlarını takip et
        self.tahmini_varis_zamanlari: Dict[int, Dict[int, time]] = {
            dron.id: {} for dron in dronlar
        }
    
    def _mesafe_hesapla(self, poz1: Tuple[float, float], poz2: Tuple[float, float]) -> float:
        """İki nokta arasındaki Öklid mesafesini hesaplar."""
        return ((poz2[0] - poz1[0])**2 + (poz2[1] - poz1[1])**2)**0.5
    
    def _seyahat_suresi_hesapla(
        self, 
        dron: Drone, 
        baslangic_poz: Tuple[float, float], 
        bitis_poz: Tuple[float, float]
    ) -> float:
        """
        İki nokta arasındaki seyahat süresini hesaplar (saniye cinsinden).
        
        Args:
            dron (Drone): Drone
            baslangic_poz (Tuple[float, float]): Başlangıç pozisyonu
            bitis_poz (Tuple[float, float]): Bitiş pozisyonu
            
        Returns:
            float: Seyahat süresi (saniye cinsinden)
        """
        mesafe = self._mesafe_hesapla(baslangic_poz, bitis_poz)
        return mesafe / dron.hiz
    
    def _zaman_ekle(self, t: time, saniyeler: float) -> time:
        """
        Bir zaman nesnesine belirli saniye ekler.
        
        Args:
            t (time): Zaman nesnesi
            saniyeler (float): Eklenecek saniye
            
        Returns:
            time: Yeni zaman nesnesi
        """
        dt = datetime.combine(datetime.today(), t)
        dt = dt + timedelta(seconds=saniyeler)
        return dt.time()
    
    def _yol_gecerli_mi(
        self, 
        baslangic_poz: Tuple[float, float], 
        bitis_poz: Tuple[float, float], 
        mevcut_zaman: time
    ) -> bool:
        """
        İki nokta arasındaki yolun geçerli olup olmadığını kontrol eder.
        
        Args:
            baslangic_poz (Tuple[float, float]): Başlangıç pozisyonu
            bitis_poz (Tuple[float, float]): Bitiş pozisyonu
            mevcut_zaman (time): Mevcut zaman
            
        Returns:
            bool: Yol geçerliyse True, değilse False
        """
        # Aktif uçuşa yasak bölgeleri kontrol et
        for bolge in self.ucus_yasak_bolgeleri:
            if bolge.aktif_mi(mevcut_zaman) and bolge.cizgi_kesisiyor_mu(baslangic_poz, bitis_poz):
                return False
        return True
    
    def _dron_teslimat_yapabilir_mi(
        self, 
        dron_id: int, 
        teslimat_id: int, 
        mevcut_zaman: time
    ) -> bool:
        """
        Bir drone'un belirli bir teslimatı yapıp yapamayacağını kontrol eder.
        
        Args:
            dron_id (int): Drone ID
            teslimat_id (int): Teslimat noktası ID
            mevcut_zaman (time): Mevcut zaman
            
        Returns:
            bool: Drone teslimatı yapabilirse True, değilse False
        """
        dron = self.dron_durumlari[dron_id]
        teslimat = self.teslimat_durumlari[teslimat_id]
        
        # Drone'un taşıma kapasitesini kontrol et
        if not dron.tasiyabilir_mi(teslimat.agirlik):
            return False
        
        # Drone'un mevcut pozisyonundan teslimat noktasına olan yolu kontrol et
        if not self._yol_gecerli_mi(dron.mevcut_poz, teslimat.poz, mevcut_zaman):
            return False
        
        # Drone'un batarya durumunu kontrol et
        mesafe = self._mesafe_hesapla(dron.mevcut_poz, teslimat.poz)
        if not dron.yeterli_batarya_var_mi(mesafe, teslimat.agirlik):
            return False
        
        # Teslimat zaman aralığını kontrol et
        seyahat_suresi = self._seyahat_suresi_hesapla(dron, dron.mevcut_poz, teslimat.poz)
        tahmini_varis = self._zaman_ekle(mevcut_zaman, seyahat_suresi)
        
        if not (teslimat.zaman_araligi[0] <= tahmini_varis <= teslimat.zaman_araligi[1]):
            return False
        
        return True
    
    def _dron_durumunu_guncelle(
        self, 
        dron_id: int, 
        teslimat_id: int, 
        mevcut_zaman: time
    ) -> time:
        """
        Bir drone'un durumunu günceller ve tahmini varış zamanını döndürür.
        
        Args:
            dron_id (int): Drone ID
            teslimat_id (int): Teslimat noktası ID
            mevcut_zaman (time): Mevcut zaman
            
        Returns:
            time: Tahmini varış zamanı
        """
        dron = self.dron_durumlari[dron_id]
        teslimat = self.teslimat_durumlari[teslimat_id]
        
        # Mesafeyi hesapla
        mesafe = self._mesafe_hesapla(dron.mevcut_poz, teslimat.poz)
        
        # Seyahat süresini hesapla
        seyahat_suresi = self._seyahat_suresi_hesapla(dron, dron.mevcut_poz, teslimat.poz)
        
        # Tahmini varış zamanını hesapla
        varis_zamani = self._zaman_ekle(mevcut_zaman, seyahat_suresi)
        
        # Drone'un pozisyonunu güncelle
        dron.pozisyon_guncelle(teslimat.poz, mesafe, teslimat.agirlik)
        
        # Drone'un yükünü güncelle (teslimat yapıldıktan sonra yük sıfırlanır)
        dron.mevcut_yuk = 0.0
        
        # Teslimat durumunu güncelle
        teslimat.teslim_edildi_mi = True
        
        return varis_zamani
    
    def _teslimat_icin_en_iyi_dronu_sec(
        self, 
        teslimat_id: int, 
        mevcut_zaman: time
    ) -> Optional[int]:
        """
        Belirli bir teslimat için en uygun drone'u seçer.
        
        Args:
            teslimat_id (int): Teslimat noktası ID
            mevcut_zaman (time): Mevcut zaman
            
        Returns:
            Optional[int]: En uygun drone'un ID'si, uygun drone yoksa None
        """
        teslimat = self.teslimat_durumlari[teslimat_id]
        en_iyi_dron_id = None
        en_iyi_skor = float('inf')
        
        for dron_id, dron in self.dron_durumlari.items():
            # Drone müsait değilse atla
            if not dron.musait_mi:
                continue
            
            # Drone teslimatı yapabilir mi?
            if not self._dron_teslimat_yapabilir_mi(dron_id, teslimat_id, mevcut_zaman):
                continue
            
            # Mesafeyi hesapla
            mesafe = self._mesafe_hesapla(dron.mevcut_poz, teslimat.poz)
            
            # Skor hesapla (mesafe ve öncelik faktörü)
            # Düşük mesafe ve yüksek öncelik daha iyi
            oncelik_faktoru = (6 - teslimat.oncelik) * 100  # 5 için 100, 1 için 500
            skor = mesafe + oncelik_faktoru
            
            if skor < en_iyi_skor:
                en_iyi_skor = skor
                en_iyi_dron_id = dron_id
        
        return en_iyi_dron_id
    
    def coz(self) -> Dict[int, List[Tuple[int, time]]]:
        """
        CSP problemini çözer ve her drone için teslimat planını döndürür.
        
        Returns:
            Dict[int, List[Tuple[int, time]]]: Her drone için (teslimat ID, tahmini varış zamanı) çiftlerinin listesi
        """
        # Teslimat noktalarını önceliğe göre sırala (yüksek öncelik önce)
        siralanmis_teslimatlar = sorted(
            self.teslimat_noktalari, 
            key=lambda x: x.oncelik, 
            reverse=True
        )
        
        mevcut_zaman = self.baslangic_zamani
        sonuc: Dict[int, List[Tuple[int, time]]] = {dron.id: [] for dron in self.dronlar}
        
        # Her teslimat için en uygun drone'u seç
        for teslimat in siralanmis_teslimatlar:
            en_iyi_dron_id = self._teslimat_icin_en_iyi_dronu_sec(teslimat.id, mevcut_zaman)
            
            if en_iyi_dron_id is not None:
                # Drone'u teslimat noktasına ata
                self.atamalar[en_iyi_dron_id].append(teslimat.id)
                
                # Drone'un durumunu güncelle ve tahmini varış zamanını al
                varis_zamani = self._dron_durumunu_guncelle(en_iyi_dron_id, teslimat.id, mevcut_zaman)
                
                # Sonuçları kaydet
                sonuc[en_iyi_dron_id].append((teslimat.id, varis_zamani))
                
                # Tahmini varış zamanını kaydet
                self.tahmini_varis_zamanlari[en_iyi_dron_id][teslimat.id] = varis_zamani
        
        return sonuc
    
    def atanmamis_teslimatlari_al(self) -> List[int]:
        """
        Atanmamış teslimatların ID'lerini döndürür.
        
        Returns:
            List[int]: Atanmamış teslimat ID'lerinin listesi
        """
        atanmis_teslimatlar = set()
        for dron_id, teslimatlar in self.atamalar.items():
            atanmis_teslimatlar.update(teslimatlar)
        
        tum_teslimatlar = {teslimat.id for teslimat in self.teslimat_noktalari}
        return list(tum_teslimatlar - atanmis_teslimatlar)
    
    def dron_rotalarini_al(self) -> Dict[int, List[Tuple[float, float]]]:
        """
        Her drone için rota koordinatlarını döndürür.
        
        Returns:
            Dict[int, List[Tuple[float, float]]]: Her drone için koordinat listesi
        """
        rotalar = {}
        
        for dron in self.dronlar:
            dron_id = dron.id
            rota = [dron.baslangic_poz]
            
            for teslimat_id in self.atamalar.get(dron_id, []):
                teslimat = next(d for d in self.teslimat_noktalari if d.id == teslimat_id)
                rota.append(teslimat.poz)
            
            rotalar[dron_id] = rota
        
        return rotalar
    
    def teslimat_istatistiklerini_al(self) -> Dict[str, float]:
        """
        Teslimat istatistiklerini döndürür.
        
        Returns:
            Dict[str, float]: İstatistikler
        """
        toplam_teslimatlar = len(self.teslimat_noktalari)
        atanmis_teslimatlar = sum(len(teslimatlar) for teslimatlar in self.atamalar.values())
        tamamlanma_orani = atanmis_teslimatlar / toplam_teslimatlar if toplam_teslimatlar > 0 else 0
        
        # Toplam enerji tüketimini hesapla
        toplam_enerji = 0
        for dron_id, dron in self.dron_durumlari.items():
            toplam_enerji += (self.dronlar[dron_id].batarya - dron.mevcut_batarya)
        
        ortalama_enerji = toplam_enerji / len(self.dronlar) if self.dronlar else 0
        
        return {
            "tamamlanma_orani": tamamlanma_orani * 100,  # Yüzde olarak
            "ortalama_enerji_tuketimi": ortalama_enerji
        }
