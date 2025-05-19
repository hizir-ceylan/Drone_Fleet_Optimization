"""
Drone Filo Optimizasyonu: Genetik Algoritma Modülü
Bu modül, drone teslimat rotalarının optimizasyonu için Genetik Algoritma uygular.
"""

import random
import copy
from typing import List, Dict, Tuple, Set, Optional, Callable
from datetime import time

from models import Drone, TeslimatNoktasi, UcusYasakBolgesi


class Birey:
    """
    Genetik Algoritma için birey sınıfı.
    
    Attributes:
        kromozom (Dict[int, List[int]]): Her drone için teslimat noktalarının sıralı listesi
        uygunluk (float): Bireyin uygunluk değeri
    """
    def __init__(self, kromozom: Dict[int, List[int]], uygunluk: float = 0.0):
        self.kromozom = kromozom
        self.uygunluk = uygunluk
    
    def __lt__(self, other: 'Birey') -> bool:
        """Karşılaştırma operatörü (sıralama için)."""
        return self.uygunluk > other.uygunluk  # Yüksek uygunluk değeri daha iyidir


class GenetikAlgoritma:
    """
    Genetik Algoritma sınıfı.
    
    Bu sınıf, drone teslimat rotalarının optimizasyonu için Genetik Algoritma uygular.
    """
    def __init__(
        self, 
        dronlar: List[Drone], 
        teslimat_noktalari: List[TeslimatNoktasi], 
        ucus_yasak_bolgeleri: List[UcusYasakBolgesi],
        mevcut_zaman: time,
        populasyon_boyutu: int = 50,
        nesil_sayisi: int = 100,
        caprazlama_orani: float = 0.8,
        mutasyon_orani: float = 0.2
    ):
        """
        Args:
            dronlar (List[Drone]): Kullanılabilir drone'ların listesi
            teslimat_noktalari (List[TeslimatNoktasi]): Teslimat noktalarının listesi
            ucus_yasak_bolgeleri (List[UcusYasakBolgesi]): Uçuşa yasak bölgelerin listesi
            mevcut_zaman (time): Mevcut zaman
            populasyon_boyutu (int): Popülasyon büyüklüğü
            nesil_sayisi (int): Maksimum nesil sayısı
            caprazlama_orani (float): Çaprazlama oranı
            mutasyon_orani (float): Mutasyon oranı
        """
        self.dronlar = dronlar
        self.teslimat_noktalari = teslimat_noktalari
        self.ucus_yasak_bolgeleri = ucus_yasak_bolgeleri
        self.mevcut_zaman = mevcut_zaman
        
        self.populasyon_boyutu = populasyon_boyutu
        self.nesil_sayisi = nesil_sayisi
        self.caprazlama_orani = caprazlama_orani
        self.mutasyon_orani = mutasyon_orani
        
        # Aktif uçuşa yasak bölgeleri filtrele
        self.aktif_ucus_yasak_bolgeleri = [
            bolge for bolge in ucus_yasak_bolgeleri if bolge.aktif_mi(mevcut_zaman)
        ]
        
        # Drone ve teslimat noktalarının ID'lerini al
        self.dron_idleri = [dron.id for dron in dronlar]
        self.teslimat_idleri = [nokta.id for nokta in teslimat_noktalari]
        
        # Drone ve teslimat noktalarını ID'lerine göre eşle
        self.dron_sozlugu = {dron.id: dron for dron in dronlar}
        self.teslimat_sozlugu = {nokta.id: nokta for nokta in teslimat_noktalari}
        
        # En iyi bireyi sakla
        self.en_iyi_birey: Optional[Birey] = None
    
    def _mesafe_hesapla(self, poz1: Tuple[float, float], poz2: Tuple[float, float]) -> float:
        """İki nokta arasındaki Öklid mesafesini hesaplar."""
        return ((poz2[0] - poz1[0])**2 + (poz2[1] - poz1[1])**2)**0.5
    
    def _yol_gecerli_mi(
        self, 
        baslangic_poz: Tuple[float, float], 
        bitis_poz: Tuple[float, float]
    ) -> bool:
        """
        İki nokta arasındaki yolun geçerli olup olmadığını kontrol eder.
        
        Args:
            baslangic_poz (Tuple[float, float]): Başlangıç pozisyonu
            bitis_poz (Tuple[float, float]): Bitiş pozisyonu
            
        Returns:
            bool: Yol geçerliyse True, değilse False
        """
        # Aktif uçuşa yasak bölgeleri kontrol et
        for bolge in self.aktif_ucus_yasak_bolgeleri:
            if bolge.cizgi_kesisiyor_mu(baslangic_poz, bitis_poz):
                return False
        return True
    
    def _rota_enerji_hesapla(
        self, 
        dron: Drone, 
        rota: List[int]
    ) -> float:
        """
        Bir drone'un belirli bir rota için enerji tüketimini hesaplar.
        
        Args:
            dron (Drone): Drone
            rota (List[int]): Teslimat noktalarının ID'lerinin listesi
            
        Returns:
            float: Toplam enerji tüketimi
        """
        if not rota:
            return 0.0
        
        toplam_enerji = 0.0
        mevcut_poz = dron.baslangic_poz
        
        for teslimat_id in rota:
            teslimat = self.teslimat_sozlugu[teslimat_id]
            mesafe = self._mesafe_hesapla(mevcut_poz, teslimat.poz)
            enerji = dron.enerji_tuketimi_hesapla(mesafe, teslimat.agirlik)
            toplam_enerji += enerji
            mevcut_poz = teslimat.poz
        
        return toplam_enerji
    
    def _kural_ihlallerini_say(
        self, 
        dron: Drone, 
        rota: List[int]
    ) -> int:
        """
        Bir drone'un belirli bir rota için kural ihlallerini sayar.
        
        Args:
            dron (Drone): Drone
            rota (List[int]): Teslimat noktalarının ID'lerinin listesi
            
        Returns:
            int: Toplam kural ihlali sayısı
        """
        if not rota:
            return 0
        
        ihlaller = 0
        mevcut_poz = dron.baslangic_poz
        mevcut_batarya = dron.batarya
        
        for teslimat_id in rota:
            teslimat = self.teslimat_sozlugu[teslimat_id]
            
            # Taşıma kapasitesi kontrolü
            if teslimat.agirlik > dron.maksimum_agirlik:
                ihlaller += 1
            
            # Yol geçerliliği kontrolü
            if not self._yol_gecerli_mi(mevcut_poz, teslimat.poz):
                ihlaller += 1
            
            # Batarya kontrolü
            mesafe = self._mesafe_hesapla(mevcut_poz, teslimat.poz)
            enerji = dron.enerji_tuketimi_hesapla(mesafe, teslimat.agirlik)
            
            if enerji > mevcut_batarya:
                ihlaller += 1
            
            mevcut_batarya -= enerji
            mevcut_poz = teslimat.poz
        
        return ihlaller
    
    def _uygunluk_hesapla(self, birey: Birey) -> float:
        """
        Bir bireyin uygunluk değerini hesaplar.
        
        uygunluk = teslimat sayısı × 100 - (enerji tüketimi × 0.5) - (kural ihlali sayısı × 2000)
        
        Args:
            birey (Birey): Birey
            
        Returns:
            float: Uygunluk değeri
        """
        toplam_teslimatlar = 0
        toplam_enerji = 0.0
        toplam_ihlaller = 0
        
        for dron_id, rota in birey.kromozom.items():
            dron = self.dron_sozlugu[dron_id]
            toplam_teslimatlar += len(rota)
            toplam_enerji += self._rota_enerji_hesapla(dron, rota)
            toplam_ihlaller += self._kural_ihlallerini_say(dron, rota)
        
        uygunluk = (toplam_teslimatlar * 100) - (toplam_enerji * 0.5) - (toplam_ihlaller * 2000)
        return uygunluk
    
    def _populasyonu_baslat(self) -> List[Birey]:
        """
        Başlangıç popülasyonunu oluşturur.
        
        Returns:
            List[Birey]: Başlangıç popülasyonu
        """
        populasyon = []
        
        for _ in range(self.populasyon_boyutu):
            # Rastgele bir birey oluştur
            kromozom = {dron_id: [] for dron_id in self.dron_idleri}
            
            # Teslimat noktalarını rastgele drone'lara ata
            teslimat_idleri = self.teslimat_idleri.copy()
            random.shuffle(teslimat_idleri)
            
            for teslimat_id in teslimat_idleri:
                # Rastgele bir drone seç
                dron_id = random.choice(self.dron_idleri)
                kromozom[dron_id].append(teslimat_id)
            
            # Her drone için teslimat sırasını rastgele karıştır
            for dron_id in self.dron_idleri:
                random.shuffle(kromozom[dron_id])
            
            birey = Birey(kromozom)
            birey.uygunluk = self._uygunluk_hesapla(birey)
            populasyon.append(birey)
        
        return populasyon
    
    def _ebeveynleri_sec(self, populasyon: List[Birey]) -> Tuple[Birey, Birey]:
        """
        Turnuva seçimi ile ebeveynleri seçer.
        
        Args:
            populasyon (List[Birey]): Popülasyon
            
        Returns:
            Tuple[Birey, Birey]: Seçilen ebeveynler
        """
        # Turnuva büyüklüğü
        turnuva_boyutu = max(2, len(populasyon) // 5)
        
        # İlk ebeveyn için turnuva
        turnuva1 = random.sample(populasyon, turnuva_boyutu)
        ebeveyn1 = max(turnuva1, key=lambda ind: ind.uygunluk)
        
        # İkinci ebeveyn için turnuva
        turnuva2 = random.sample(populasyon, turnuva_boyutu)
        ebeveyn2 = max(turnuva2, key=lambda ind: ind.uygunluk)
        
        return ebeveyn1, ebeveyn2
    
    def _caprazla(
        self, 
        ebeveyn1: Birey, 
        ebeveyn2: Birey
    ) -> Tuple[Birey, Birey]:
        """
        İki ebeveyn arasında çaprazlama yapar.
        
        Args:
            ebeveyn1 (Birey): Birinci ebeveyn
            ebeveyn2 (Birey): İkinci ebeveyn
            
        Returns:
            Tuple[Birey, Birey]: Oluşan çocuklar
        """
        if random.random() > self.caprazlama_orani:
            return copy.deepcopy(ebeveyn1), copy.deepcopy(ebeveyn2)
        
        cocuk1_kromozom = {dron_id: [] for dron_id in self.dron_idleri}
        cocuk2_kromozom = {dron_id: [] for dron_id in self.dron_idleri}
        
        # Her drone için ayrı çaprazlama yap
        for dron_id in self.dron_idleri:
            rota1 = ebeveyn1.kromozom[dron_id]
            rota2 = ebeveyn2.kromozom[dron_id]
            
            if not rota1 or not rota2:
                cocuk1_kromozom[dron_id] = rota1.copy()
                cocuk2_kromozom[dron_id] = rota2.copy()
                continue
            
            # Çaprazlama noktası seç
            caprazlama_noktasi = random.randint(1, min(len(rota1), len(rota2)))
            
            # Çocukları oluştur
            cocuk1_kromozom[dron_id] = rota1[:caprazlama_noktasi] + [
                gen for gen in rota2 if gen not in rota1[:caprazlama_noktasi]
            ]
            
            cocuk2_kromozom[dron_id] = rota2[:caprazlama_noktasi] + [
                gen for gen in rota1 if gen not in rota2[:caprazlama_noktasi]
            ]
        
        # Teslimat noktalarının tekrarlanmadığından emin ol
        self._kromozomu_duzelt(cocuk1_kromozom)
        self._kromozomu_duzelt(cocuk2_kromozom)
        
        cocuk1 = Birey(cocuk1_kromozom)
        cocuk2 = Birey(cocuk2_kromozom)
        
        cocuk1.uygunluk = self._uygunluk_hesapla(cocuk1)
        cocuk2.uygunluk = self._uygunluk_hesapla(cocuk2)
        
        return cocuk1, cocuk2
    
    def _kromozomu_duzelt(self, kromozom: Dict[int, List[int]]):
        """
        Kromozomdaki tekrarlanan teslimat noktalarını düzeltir.
        
        Args:
            kromozom (Dict[int, List[int]]): Düzeltilecek kromozom
        """
        # Tüm teslimat noktalarını topla
        tum_teslimatlar = []
        for dron_id in self.dron_idleri:
            tum_teslimatlar.extend(kromozom[dron_id])
        
        # Tekrarlanan ve eksik teslimat noktalarını bul
        teslimat_sayilari = {}
        for teslimat_id in tum_teslimatlar:
            teslimat_sayilari[teslimat_id] = teslimat_sayilari.get(teslimat_id, 0) + 1
        
        tekrarlar = [
            teslimat_id for teslimat_id, sayi in teslimat_sayilari.items() if sayi > 1
        ]
        eksikler = [
            teslimat_id for teslimat_id in self.teslimat_idleri 
            if teslimat_id not in teslimat_sayilari
        ]
        
        # Tekrarlanan teslimat noktalarını kaldır
        for dron_id in self.dron_idleri:
            for teslimat_id in tekrarlar:
                # İlk bulunduğu yer hariç hepsini kaldır
                bulundu = False
                i = 0
                while i < len(kromozom[dron_id]):
                    if kromozom[dron_id][i] == teslimat_id:
                        if bulundu:
                            kromozom[dron_id].pop(i)
                            continue
                        bulundu = True
                    i += 1
        
        # Eksik teslimat noktalarını rastgele drone'lara ekle
        for teslimat_id in eksikler:
            dron_id = random.choice(self.dron_idleri)
            kromozom[dron_id].append(teslimat_id)
    
    def _mutasyon_yap(self, birey: Birey) -> Birey:
        """
        Bireyde mutasyon yapar.
        
        Args:
            birey (Birey): Mutasyon yapılacak birey
            
        Returns:
            Birey: Mutasyon yapılmış birey
        """
        if random.random() > self.mutasyon_orani:
            return birey
        
        mutasyonlu = copy.deepcopy(birey)
        
        # Mutasyon tipi: Teslimat noktasını başka bir drone'a taşı
        if random.random() < 0.5 and len(self.dron_idleri) > 1:
            # Rastgele bir kaynak drone seç
            kaynak_dron_id = random.choice(self.dron_idleri)
            
            # Kaynak drone'da teslimat varsa
            if mutasyonlu.kromozom[kaynak_dron_id]:
                # Rastgele bir teslimat noktası seç
                teslimat_indeksi = random.randint(0, len(mutasyonlu.kromozom[kaynak_dron_id]) - 1)
                teslimat_id = mutasyonlu.kromozom[kaynak_dron_id][teslimat_indeksi]
                
                # Rastgele bir hedef drone seç (kaynak drone'dan farklı)
                hedef_dron_id = random.choice([
                    dron_id for dron_id in self.dron_idleri if dron_id != kaynak_dron_id
                ])
                
                # Teslimat noktasını taşı
                mutasyonlu.kromozom[kaynak_dron_id].pop(teslimat_indeksi)
                mutasyonlu.kromozom[hedef_dron_id].append(teslimat_id)
        
        # Mutasyon tipi: Teslimat sırasını değiştir
        else:
            # Rastgele bir drone seç
            dron_id = random.choice(self.dron_idleri)
            
            # Drone'da en az 2 teslimat varsa
            if len(mutasyonlu.kromozom[dron_id]) >= 2:
                # Rastgele iki indeks seç
                idx1, idx2 = random.sample(range(len(mutasyonlu.kromozom[dron_id])), 2)
                
                # Teslimat noktalarını değiştir
                mutasyonlu.kromozom[dron_id][idx1], mutasyonlu.kromozom[dron_id][idx2] = (
                    mutasyonlu.kromozom[dron_id][idx2], mutasyonlu.kromozom[dron_id][idx1]
                )
        
        # Uygunluk değerini güncelle
        mutasyonlu.uygunluk = self._uygunluk_hesapla(mutasyonlu)
        
        return mutasyonlu
    
    def evrimles(self) -> Dict[int, List[int]]:
        """
        Genetik Algoritma'yı çalıştırır ve en iyi çözümü döndürür.
        
        Returns:
            Dict[int, List[int]]: Her drone için en iyi teslimat rotası
        """
        # Başlangıç popülasyonunu oluştur
        populasyon = self._populasyonu_baslat()
        
        # En iyi bireyi bul
        self.en_iyi_birey = max(populasyon, key=lambda ind: ind.uygunluk)
        
        # Nesiller boyunca evrimleş
        for nesil in range(self.nesil_sayisi):
            yeni_populasyon = []
            
            # Elitizm: En iyi bireyi doğrudan yeni nesle aktar
            yeni_populasyon.append(copy.deepcopy(self.en_iyi_birey))
            
            # Yeni nesli oluştur
            while len(yeni_populasyon) < self.populasyon_boyutu:
                # Ebeveynleri seç
                ebeveyn1, ebeveyn2 = self._ebeveynleri_sec(populasyon)
                
                # Çaprazlama
                cocuk1, cocuk2 = self._caprazla(ebeveyn1, ebeveyn2)
                
                # Mutasyon
                cocuk1 = self._mutasyon_yap(cocuk1)
                cocuk2 = self._mutasyon_yap(cocuk2)
                
                yeni_populasyon.append(cocuk1)
                yeni_populasyon.append(cocuk2)
            
            # Popülasyon boyutunu ayarla
            populasyon = yeni_populasyon[:self.populasyon_boyutu]
            
            # En iyi bireyi güncelle
            mevcut_en_iyi = max(populasyon, key=lambda ind: ind.uygunluk)
            if mevcut_en_iyi.uygunluk > self.en_iyi_birey.uygunluk:
                self.en_iyi_birey = copy.deepcopy(mevcut_en_iyi)
        
        return self.en_iyi_birey.kromozom
    
    def en_iyi_uygunluk_al(self) -> float:
        """
        En iyi bireyin uygunluk değerini döndürür.
        
        Returns:
            float: En iyi uygunluk değeri
        """
        return self.en_iyi_birey.uygunluk if self.en_iyi_birey else 0.0
    
    def istatistikleri_al(self) -> Dict[str, float]:
        """
        Algoritma istatistiklerini döndürür.
        
        Returns:
            Dict[str, float]: İstatistikler
        """
        if not self.en_iyi_birey:
            return {
                "toplam_teslimatlar": 0,
                "toplam_enerji": 0.0,
                "toplam_ihlaller": 0,
                "uygunluk": 0.0
            }
        
        toplam_teslimatlar = 0
        toplam_enerji = 0.0
        toplam_ihlaller = 0
        
        for dron_id, rota in self.en_iyi_birey.kromozom.items():
            dron = self.dron_sozlugu[dron_id]
            toplam_teslimatlar += len(rota)
            toplam_enerji += self._rota_enerji_hesapla(dron, rota)
            toplam_ihlaller += self._kural_ihlallerini_say(dron, rota)
        
        return {
            "toplam_teslimatlar": toplam_teslimatlar,
            "toplam_enerji": toplam_enerji,
            "toplam_ihlaller": toplam_ihlaller,
            "uygunluk": self.en_iyi_birey.uygunluk
        }
    
    def dron_rotalarini_al(self) -> Dict[int, List[Tuple[float, float]]]:
        """
        Her drone için rota koordinatlarını döndürür.
        
        Returns:
            Dict[int, List[Tuple[float, float]]]: Her drone için koordinat listesi
        """
        if not self.en_iyi_birey:
            return {dron_id: [dron.baslangic_poz] for dron_id, dron in self.dron_sozlugu.items()}
        
        rotalar = {}
        
        for dron_id, dron in self.dron_sozlugu.items():
            rota = [dron.baslangic_poz]
            
            for teslimat_id in self.en_iyi_birey.kromozom.get(dron_id, []):
                teslimat = self.teslimat_sozlugu[teslimat_id]
                rota.append(teslimat.poz)
            
            rotalar[dron_id] = rota
        
        return rotalar
