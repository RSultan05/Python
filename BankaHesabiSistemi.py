#🏦 Banka Hesabı Sistemi
#Bir bankanın müşteri hesap yönetim sistemini kodlayacaksın.

class BankaHesabi:                              #Ana sınıf
    def __init__(self, sahibi):                 # sahip → dışarıdan gelen parametre.
        self.sahibi = sahibi                    # parametreyi değişkene atar.
        self.__bakiye = 0                       # dışarıdan gelmiyor, direkt 0 olarak tanımlanıyor. -  Dışarıdan doğrudan değiştirilmesini önlemek için saklıyoruz.

    def para_yatir(self, miktar):
        self.__bakiye += miktar
        print(f"{miktar} TL yatırıldı")

    def para_cek(self, miktar):
        if miktar <= self.__bakiye:
            self.__bakiye -= miktar
            print(f"{miktar} TL çekildi")
        else:
            print("Yetersiz bakiye!")

    def bakiye_goster(self):
        return self.__bakiye

    def hesap_bilgisi(self):
        print(f"Hesap Sahibi: {self.sahibi} | Bakiye: {self.__bakiye} TL")



class VadesizHesap(BankaHesabi):                #Alt Sınıf
    def __init__(self, sahibi, faiz_orani):
        super().__init__(sahibi)
        self.faiz_orani = faiz_orani

    def faiz_ekle(self):
        faiz = self.bakiye_goster() * self.faiz_orani                  #__bakiye sadece BankaHesabi class ında olduğundan bakiye_goster() ile erişiyoruz.
        self.para_yatir(faiz)
        print(f"{faiz} TL faiz eklendi")

    def hesap_bilgisi(self):                                           #override
        super().hesap_bilgisi()
        print(f"Faiz Oranı: %{int(self.faiz_orani * 100)}")



class KrediHesabi(BankaHesabi):                  #Alt Sınıf
    def __init__(self, sahibi, kredi_limiti):
        super().__init__(sahibi)
        self.kredi_limiti = kredi_limiti

    def para_cek(self, miktar):                                        #override
        if miktar <= self.bakiye_goster() + self.kredi_limiti:
            fark = miktar - self.bakiye_goster()
            if fark > 0:
                super().para_cek(self.bakiye_goster())                 # bakiyeyi sıfırla, geri kalanı eksi yap
                self._BankaHesabi__bakiye -= fark                      # eksi bakiyeyi simüle etmek için özel bir yol:
            else:
                super().para_cek(miktar)
            print(f"{miktar} TL çekildi")
        else:
            print("Kredi limiti aşıldı!")

    def hesap_bilgisi(self):
        super().hesap_bilgisi()
        print(f"Kredi Limiti: {self.kredi_limiti} TL")


# Test
v = VadesizHesap("Ayşe", 0.05)
v.para_yatir(1000)
v.faiz_ekle()
v.hesap_bilgisi()

print("---")

k = KrediHesabi("Mehmet", 3000)
k.para_yatir(500)
k.para_cek(3000)
k.para_cek(1000)
k.hesap_bilgisi()