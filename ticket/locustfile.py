# from locust import HttpUser, task, between

# class BiletAliciKullanici(HttpUser):
#     # Kullanıcılar işlemler arasında 1-3 saniye bekler (İnsani davranış)
#     wait_time = between(1, 3)

#     # %80 Olasılıkla sadece stok durumuna bakar (Sistemi yormaz)
#     @task(4)
#     def stok_kontrol(self):
#         self.client.get("/api/status")

#     # %20 Olasılıkla bilet almaya çalışır (Sistemi yorar - YAZMA işlemi)
#     @task(1)
#     def bilet_al(self):
#         self.client.post("/api/buy")


from locust import HttpUser, task, between

class BiletAliciKullanici(HttpUser): #httpuser dan kalıtım alıyoruz->client nesnesi(bu nesneye client adında bir HTTP oturumu)
    """
    Performans Testi Senaryosu:
    - Servisin maksimum istek kapasitesini belirlemek
    - 50/100/200 kullanıcı ile yük testi
    - Darboğaz analizi
    """
    # Kullanıcılar işlemler arasında 1-3 saniye bekler (insani davranış simülasyonu)
    wait_time = between(1, 3)

    # Kullanıcı kaydı ve login (her kullanıcı için ayrı oturum)
    def on_start(self):
        username = f"user_{self.environment.runner.user_count}"
        self.client.post("/api/register", json={"username": username, "password": "123"}) #post isteği ile kullanıcı kaydı
        self.client.post("/api/login", json={"username": username, "password": "123"})

    # % 
    @task(4)
    def stok_kontrol(self):
        self.client.get("/api/status") #get isteği ile stok durumunu kontrol ediyor

    # %20 olasılıkla bilet alma (DB write, kritik endpoint)
    @task(1)
    def bilet_al(self):
        event_id = 2  # Sabit event üzerinden yük bindiriyoruz
        self.client.post(f"/api/buy/{event_id}") #post isteği ile bilet satın alıyor

    # Opsiyonel: Favorilere ekleme (DB yazma testi)
    @task(1)
    def favorilere_ekle(self):
        self.client.post("/api/favorites/add", json={"event_id": 2}) #post isteği ile favorilere etkinlik ekliyor
 