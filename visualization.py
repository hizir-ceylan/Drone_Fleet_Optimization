"""
Drone Filo Optimizasyonu: Görselleştirme Modülü
Bu modül, drone teslimat rotalarının ve uçuşa yasak bölgelerin görselleştirilmesini sağlar.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import List, Dict, Tuple, Optional
import random
from datetime import time
from matplotlib.colors import to_rgba

from models import Drone, TeslimatNoktasi, UcusYasakBolgesi


class Gorselleştirici:
    """
    Görselleştirme sınıfı.
    
    Bu sınıf, drone teslimat rotalarının ve uçuşa yasak bölgelerin görselleştirilmesini sağlar.
    """
    def __init__(
        self, 
        dronlar: List[Drone], 
        teslimat_noktalari: List[TeslimatNoktasi], 
        ucus_yasak_bolgeleri: List[UcusYasakBolgesi],
        mevcut_zaman: time,
        sekil_boyutu: Tuple[int, int] = (12, 10),
        cozunurluk: int = 100
    ):
        """
        Args:
            dronlar (List[Drone]): Drone'ların listesi
            teslimat_noktalari (List[TeslimatNoktasi]): Teslimat noktalarının listesi
            ucus_yasak_bolgeleri (List[UcusYasakBolgesi]): Uçuşa yasak bölgelerin listesi
            mevcut_zaman (time): Mevcut zaman
            sekil_boyutu (Tuple[int, int]): Figür boyutu
            cozunurluk (int): Figür çözünürlüğü
        """
        self.dronlar = dronlar
        self.teslimat_noktalari = teslimat_noktalari
        self.ucus_yasak_bolgeleri = ucus_yasak_bolgeleri
        self.mevcut_zaman = mevcut_zaman
        self.sekil_boyutu = sekil_boyutu
        self.cozunurluk = cozunurluk
        
        # Aktif uçuşa yasak bölgeleri filtrele
        self.aktif_ucus_yasak_bolgeleri = [
            bolge for bolge in ucus_yasak_bolgeleri if bolge.aktif_mi(mevcut_zaman)
        ]
        
        # Drone ve teslimat noktalarını ID'lerine göre eşle
        self.dron_sozlugu = {dron.id: dron for dron in dronlar}
        self.teslimat_sozlugu = {nokta.id: nokta for nokta in teslimat_noktalari}
        
        # Renk paleti oluştur
        self.dron_renkleri = self._renkleri_olustur(len(dronlar))
    
    def _renkleri_olustur(self, n: int) -> List[Tuple[float, float, float, float]]:
        """
        Belirli sayıda ayırt edilebilir renk üretir.
        
        Args:
            n (int): Renk sayısı
            
        Returns:
            List[Tuple[float, float, float, float]]: RGBA renk listesi
        """
        renkler = []
        for i in range(n):
            ton = i / n
            doygunluk = 0.7 + 0.3 * random.random()
            deger = 0.7 + 0.3 * random.random()
            
            # HSV'den RGB'ye dönüşüm
            h = ton * 6
            c = deger * doygunluk
            x = c * (1 - abs(h % 2 - 1))
            m = deger - c
            
            if h < 1:
                r, g, b = c, x, 0
            elif h < 2:
                r, g, b = x, c, 0
            elif h < 3:
                r, g, b = 0, c, x
            elif h < 4:
                r, g, b = 0, x, c
            elif h < 5:
                r, g, b = x, 0, c
            else:
                r, g, b = c, 0, x
            
            renkler.append((r + m, g + m, b + m, 0.8))
        
        return renkler
    
    def _harita_sinirlarini_al(self) -> Tuple[float, float, float, float]:
        """
        Harita sınırlarını hesaplar.
        
        Returns:
            Tuple[float, float, float, float]: (min_x, max_x, min_y, max_y)
        """
        tum_noktalar = []
        
        # Drone başlangıç noktaları
        for dron in self.dronlar:
            tum_noktalar.append(dron.baslangic_poz)
        
        # Teslimat noktaları
        for nokta in self.teslimat_noktalari:
            tum_noktalar.append(nokta.poz)
        
        # Uçuşa yasak bölge köşeleri
        for bolge in self.ucus_yasak_bolgeleri:
            tum_noktalar.extend(bolge.koordinatlar)
        
        if not tum_noktalar:
            return (-10, 10, -10, 10)
        
        # Sınırları hesapla
        x_koordinatlari = [p[0] for p in tum_noktalar]
        y_koordinatlari = [p[1] for p in tum_noktalar]
        
        min_x, max_x = min(x_koordinatlari), max(x_koordinatlari)
        min_y, max_y = min(y_koordinatlari), max(y_koordinatlari)
        
        # Sınırlara marj ekle
        marj = max(max_x - min_x, max_y - min_y) * 0.1
        
        return (min_x - marj, max_x + marj, min_y - marj, max_y + marj)
    
    def _ucus_yasak_bolgelerini_ciz(self, eksen: plt.Axes):
        """
        Uçuşa yasak bölgeleri çizer.
        
        Args:
            eksen (plt.Axes): Matplotlib ekseni
        """
        for bolge in self.ucus_yasak_bolgeleri:
            # Bölge aktif mi?
            aktif_mi = bolge.aktif_mi(self.mevcut_zaman)
            
            # Koordinatları numpy dizisine dönüştür
            koordinatlar = np.array(bolge.koordinatlar)
            
            # Poligon çiz
            poligon = patches.Polygon(
                koordinatlar, 
                closed=True, 
                fill=True, 
                alpha=0.4 if aktif_mi else 0.2,
                color='red' if aktif_mi else 'orange',
                edgecolor='darkred' if aktif_mi else 'darkorange',
                linewidth=2,
                label=f"Uçuş Yasak Bölgesi {bolge.id}" + (" (Aktif)" if aktif_mi else " (Pasif)")
            )
            eksen.add_patch(poligon)
            
            # Bölge ID'sini ekle
            merkez = np.mean(koordinatlar, axis=0)
            eksen.text(
                merkez[0], 
                merkez[1], 
                f"UYB-{bolge.id}", 
                ha='center', 
                va='center', 
                color='white',
                fontweight='bold',
                fontsize=10
            )
    
    def _teslimat_noktalarini_ciz(self, eksen: plt.Axes):
        """
        Teslimat noktalarını çizer.
        
        Args:
            eksen (plt.Axes): Matplotlib ekseni
        """
        for nokta in self.teslimat_noktalari:
            # Önceliğe göre boyut belirle
            boyut = 100 + nokta.oncelik * 20
            
            # Teslimat noktasını çiz
            eksen.scatter(
                nokta.poz[0], 
                nokta.poz[1], 
                s=boyut, 
                color='blue', 
                marker='o', 
                edgecolor='darkblue',
                linewidth=1.5,
                alpha=0.7,
                zorder=3
            )
            
            # Teslimat ID'sini ve ağırlığını ekle
            eksen.text(
                nokta.poz[0], 
                nokta.poz[1] + 0.5, 
                f"T-{nokta.id}\n{nokta.agirlik}kg\nÖ:{nokta.oncelik}", 
                ha='center', 
                va='bottom', 
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7)
            )
    
    def _dronlari_ciz(self, eksen: plt.Axes):
        """
        Drone'ları çizer.
        
        Args:
            eksen (plt.Axes): Matplotlib ekseni
        """
        for i, dron in enumerate(self.dronlar):
            # Drone'u çiz
            eksen.scatter(
                dron.baslangic_poz[0], 
                dron.baslangic_poz[1], 
                s=200, 
                color=self.dron_renkleri[i], 
                marker='^', 
                edgecolor='black',
                linewidth=1.5,
                zorder=4,
                label=f"Dron {dron.id}"
            )
            
            # Drone bilgilerini ekle
            eksen.text(
                dron.baslangic_poz[0], 
                dron.baslangic_poz[1] - 0.5, 
                f"Dron-{dron.id}\n{dron.maksimum_agirlik}kg\n{dron.batarya}mAh", 
                ha='center', 
                va='top', 
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7)
            )
    
    def _rotalari_ciz(self, eksen: plt.Axes, rotalar: Dict[int, List[Tuple[float, float]]]):
        """
        Drone rotalarını çizer.
        
        Args:
            eksen (plt.Axes): Matplotlib ekseni
            rotalar (Dict[int, List[Tuple[float, float]]]): Her drone için rota koordinatları
        """
        for i, (dron_id, rota) in enumerate(rotalar.items()):
            if len(rota) < 2:
                continue
            
            # Rota çizgilerini çiz
            for j in range(len(rota) - 1):
                baslangic = rota[j]
                bitis = rota[j + 1]
                
                # Ok başı boyutu ve pozisyonu
                ok_boyutu = 15
                ok_pozisyonu = 0.6  # Çizginin %60'ında
                
                # Çizgiyi çiz
                eksen.annotate(
                    '', 
                    xy=bitis, 
                    xytext=baslangic,
                    arrowprops=dict(
                        arrowstyle='->', 
                        color=self.dron_renkleri[i], 
                        lw=2,
                        shrinkA=5, 
                        shrinkB=5,
                        mutation_scale=ok_boyutu
                    ),
                    zorder=2
                )
                
                # Rota sırasını göster
                orta_x = baslangic[0] + (bitis[0] - baslangic[0]) * ok_pozisyonu
                orta_y = baslangic[1] + (bitis[1] - baslangic[1]) * ok_pozisyonu
                
                eksen.text(
                    orta_x, 
                    orta_y, 
                    f"{j+1}", 
                    ha='center', 
                    va='center', 
                    fontsize=10,
                    fontweight='bold',
                    bbox=dict(boxstyle="circle,pad=0.3", fc=to_rgba(self.dron_renkleri[i], 0.8), ec="black")
                )
    
    def senaryoyu_gorselleştir(self, baslik: str = "Drone Filo Optimizasyonu"):
        """
        Senaryo görselleştirmesi oluşturur.
        
        Args:
            baslik (str): Görselleştirme başlığı
            
        Returns:
            plt.Figure: Matplotlib figürü
        """
        sekil, eksen = plt.subplots(figsize=self.sekil_boyutu, dpi=self.cozunurluk)
        
        # Harita sınırlarını ayarla
        sinirlar = self._harita_sinirlarini_al()
        eksen.set_xlim(sinirlar[0], sinirlar[1])
        eksen.set_ylim(sinirlar[2], sinirlar[3])
        
        # Uçuşa yasak bölgeleri çiz
        self._ucus_yasak_bolgelerini_ciz(eksen)
        
        # Teslimat noktalarını çiz
        self._teslimat_noktalarini_ciz(eksen)
        
        # Drone'ları çiz
        self._dronlari_ciz(eksen)
        
        # Izgara ve etiketler
        eksen.grid(True, linestyle='--', alpha=0.7)
        eksen.set_xlabel('X Koordinatı (m)')
        eksen.set_ylabel('Y Koordinatı (m)')
        eksen.set_title(baslik)
        
        # Lejant
        eksen.legend(loc='upper right')
        
        plt.tight_layout()
        return sekil
    
    def rotalari_gorselleştir(
        self, 
        rotalar: Dict[int, List[Tuple[float, float]]], 
        baslik: str = "Drone Teslimat Rotaları"
    ):
        """
        Drone rotalarını görselleştirir.
        
        Args:
            rotalar (Dict[int, List[Tuple[float, float]]]): Her drone için rota koordinatları
            baslik (str): Görselleştirme başlığı
            
        Returns:
            plt.Figure: Matplotlib figürü
        """
        sekil, eksen = plt.subplots(figsize=self.sekil_boyutu, dpi=self.cozunurluk)
        
        # Harita sınırlarını ayarla
        sinirlar = self._harita_sinirlarini_al()
        eksen.set_xlim(sinirlar[0], sinirlar[1])
        eksen.set_ylim(sinirlar[2], sinirlar[3])
        
        # Uçuşa yasak bölgeleri çiz
        self._ucus_yasak_bolgelerini_ciz(eksen)
        
        # Teslimat noktalarını çiz
        self._teslimat_noktalarini_ciz(eksen)
        
        # Drone'ları çiz
        self._dronlari_ciz(eksen)
        
        # Rotaları çiz
        self._rotalari_ciz(eksen, rotalar)
        
        # Izgara ve etiketler
        eksen.grid(True, linestyle='--', alpha=0.7)
        eksen.set_xlabel('X Koordinatı (m)')
        eksen.set_ylabel('Y Koordinatı (m)')
        eksen.set_title(baslik)
        
        # Lejant
        eksen.legend(loc='upper right')
        
        plt.tight_layout()
        return sekil
    
    def gorselleştirmeyi_kaydet(self, sekil: plt.Figure, dosya_adi: str):
        """
        Görselleştirmeyi dosyaya kaydeder.
        
        Args:
            sekil (plt.Figure): Matplotlib figürü
            dosya_adi (str): Dosya adı
        """
        sekil.savefig(dosya_adi, bbox_inches='tight')
        plt.close(sekil)
    
    def gorselleştirmeyi_goster(self, sekil: plt.Figure):
        """
        Görselleştirmeyi gösterir.
        
        Args:
            sekil (plt.Figure): Matplotlib figürü
        """
        plt.show()
    
    def animasyon_olustur(
        self, 
        rotalar: Dict[int, List[Tuple[float, float]]], 
        cikti_dosyasi: str,
        fps: int = 10
    ):
        """
        Drone rotalarının animasyonunu oluşturur.
        
        Args:
            rotalar (Dict[int, List[Tuple[float, float]]]): Her drone için rota koordinatları
            cikti_dosyasi (str): Çıktı dosyası
            fps (int): Saniyedeki kare sayısı
        """
        import matplotlib.animation as animation
        
        # Tüm rotaların maksimum uzunluğunu bul
        max_rota_uzunlugu = max([len(rota) for rota in rotalar.values()], default=0)
        
        if max_rota_uzunlugu <= 1:
            print("Animasyon oluşturmak için yeterli rota noktası yok.")
            return
        
        # Figür ve eksen oluştur
        sekil, eksen = plt.subplots(figsize=self.sekil_boyutu, dpi=self.cozunurluk)
        
        # Harita sınırlarını ayarla
        sinirlar = self._harita_sinirlarini_al()
        eksen.set_xlim(sinirlar[0], sinirlar[1])
        eksen.set_ylim(sinirlar[2], sinirlar[3])
        
        # Uçuşa yasak bölgeleri çiz
        self._ucus_yasak_bolgelerini_ciz(eksen)
        
        # Teslimat noktalarını çiz
        self._teslimat_noktalarini_ciz(eksen)
        
        # Drone'ları çiz (başlangıç pozisyonları)
        dron_isaretcileri = {}
        for i, dron in enumerate(self.dronlar):
            isaretci = eksen.scatter(
                dron.baslangic_poz[0], 
                dron.baslangic_poz[1], 
                s=200, 
                color=self.dron_renkleri[i], 
                marker='^', 
                edgecolor='black',
                linewidth=1.5,
                zorder=4,
                label=f"Dron {dron.id}"
            )
            dron_isaretcileri[dron.id] = isaretci
        
        # Rota çizgileri için boş listeler
        rota_cizgileri = {dron_id: [] for dron_id in rotalar.keys()}
        
        # Izgara ve etiketler
        eksen.grid(True, linestyle='--', alpha=0.7)
        eksen.set_xlabel('X Koordinatı (m)')
        eksen.set_ylabel('Y Koordinatı (m)')
        eksen.set_title("Drone Teslimat Rotaları Animasyonu")
        
        # Lejant
        eksen.legend(loc='upper right')
        
        # Zaman göstergesi
        zaman_metni = eksen.text(
            0.02, 
            0.98, 
            "Adım: 0", 
            transform=eksen.transAxes, 
            fontsize=12,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.7)
        )
        
        def baslat():
            """Animasyon başlangıç durumu."""
            for dron_id in rotalar.keys():
                if dron_id in dron_isaretcileri:
                    dron_isaretcileri[dron_id].set_offsets(
                        np.array([self.dron_sozlugu[dron_id].baslangic_poz])
                    )
            
            zaman_metni.set_text("Adım: 0")
            return list(dron_isaretcileri.values()) + [zaman_metni]
        
        def animasyon_yap(kare):
            """Her karedeki animasyon durumu."""
            # Drone pozisyonlarını güncelle
            for dron_id, rota in rotalar.items():
                if dron_id in dron_isaretcileri and kare < len(rota):
                    dron_isaretcileri[dron_id].set_offsets(np.array([rota[kare]]))
                    
                    # Rota çizgisini güncelle
                    if kare > 0:
                        # Önceki çizgileri kaldır
                        for cizgi in rota_cizgileri[dron_id]:
                            cizgi.remove()
                        
                        rota_cizgileri[dron_id] = []
                        
                        # Yeni çizgiyi ekle
                        for j in range(kare):
                            cizgi = eksen.plot(
                                [rota[j][0], rota[j+1][0]], 
                                [rota[j][1], rota[j+1][1]],
                                color=self.dron_renkleri[list(rotalar.keys()).index(dron_id)],
                                linewidth=2,
                                alpha=0.7,
                                zorder=2
                            )[0]
                            rota_cizgileri[dron_id].append(cizgi)
            
            zaman_metni.set_text(f"Adım: {kare}")
            
            return list(dron_isaretcileri.values()) + [zaman_metni] + [
                cizgi for cizgiler in rota_cizgileri.values() for cizgi in cizgiler
            ]
        
        # Animasyonu oluştur
        anim = animation.FuncAnimation(
            sekil, 
            animasyon_yap, 
            init_func=baslat,
            frames=max_rota_uzunlugu,
            interval=1000/fps,  # ms cinsinden
            blit=True
        )
        
        # Animasyonu kaydet
        anim.save(cikti_dosyasi, writer='pillow', fps=fps)
        plt.close(sekil)
