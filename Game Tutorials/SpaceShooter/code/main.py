import pygame                           # Oyun yapmak için gereken büyük araç kutusunu getir.
from os.path import join                # Dosya yollarını birleştirmek için.
from random import randint, uniform     # Rastgele sayı üretecler.
                                            # randint(0, 100) tam sayı verir, uniform(-0.5, 0.5) ondalıklı sayı verir.

class Player(pygame.sprite.Sprite):     # pygame.sprite.Sprite'tan miras alıyor, Pygame'in hazır oyuncu sistemi kullanılıyor.
    def __init__(self, groups):         # __init__ her yeni Player oluşturulduğunda bir kez çalışır (kurucu metot).
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()        # Resmi diskten yükler. convert_alpha() → şeffaflığı (PNG'nin arka planı) düzgün işlemesi için.
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))    # Resmin çarpışma kutusunu (rect) alır ve ekranın tam ortasına yerleştirir. frect ondalıklı koordinat kullanımı için.
        self.direction =pygame.Vector2()    # direction, gidiş yönü. Vector2, x ve y yönünü tutan iki sayılık kutu. 
        self.speed = 300                # saniyede 300 piksel hız.

        # cooldown
        self.can_shoot = True           # ateş edebilir.
        self.laser_shoot_time = 0       # ateş edilen en son zamananı tutar.
        self.cooldown_duration = 400    # 400 milisaniye geçmeden tekrar ateş edemez.

        # mask
        self.mask = pygame.mask.from_surface(self.image)    # mask, resmin şeffaf olmayan piksellerinin haritası. rect yerine gemiyle çarpışma olsun diye.

    def laser_timer(self):
        if not self.can_shoot:                  # Ateş edemiyorsa, ne kadar zaman geçti bak. 400ms geçtiyse, tekrar ateş etmeye izin ver.
            current_time = pygame.time.get_ticks()                              # oyun başladığından bu yana geçen milisaniyeyi döndürüyor.
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()         # klavyede basılan tuşu atıyor.
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])             # Sağ ve sol ok tuşlarına göre x yönünü belirler.
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])                # Sağ ve sol ok tuşlarına göre y yönünü belirler.
        self.direction = self.direction.normalize() if self.direction else self.direction   # çapraz hareketin hızını düzeltmek için vektör normalize ediliyor. Edilmez ise çapraz giderken daha hızlı olur.
        self.rect.center += self.direction * self.speed * dt   # Karakterin konumunu günceller.      # if self.direction, sıfır vektörünü (Vector2(0,0)) normalize etmeye çalışıp hata alınmasını engeller.

        # if self.direction:
        #     self.direction = self.direction.normalize()
        # else:
        #     self.direction = self.direction

        recent_keys = pygame.key.get_just_pressed()                             # get_just_pressed(), bu kareye özel yeni basışları yakalar 
        if recent_keys[pygame.K_SPACE] and self.can_shoot:                      # Space basıldı ve ateş edebiliyorsa: lazer oluştur, ateş etmeyi kapat, zamanı kaydet, sesi çal.
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))   # Lazer Oluştur: lazerin resmi, Playerın üst orta noktası, lazerin ekleneceği gruplar.
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()

            # pygame.key.get_pressed() : Tuş basılı tutulduğu sürece True döner.
            # pygame.key.get_just_pressed() : Sadece tuşa ilk basıldığı karede True döner.

        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH),randint(0, WINDOW_HEIGHT)))     # Ekranda rastgele bir yere yıldız koy. Hareket etmiyor, sadece arka planı dolduruyor.

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)       # midbottom = pos , lazerin altı geminin tepesine denk gelsin.

    def update(self, dt):
        self.rect.centery -= 400 * dt   # Her kare 400px/sn hızla yukarı gider.
        if self.rect.bottom < 0:        # Ekrandan çıktıysa kill(), kendini sil, bellekten temizle.
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)          # Meteorun merkezi pos koordinatına yerleştirilir.
        self.start_time = pygame.time.get_ticks()               # Meteorun oluşturulduğu zamanı kaydeder.
        self.lifetime = 3000                                    # 3000 ms = 3 saniye
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)   # uniform(-0.5, 0.5) rastgele sayı üretir. Meteorlar rastgele gider.
        self.speed = randint(400, 500)                          # Meteorun hızı rastgele seçiliyor.
        self.rotation_speed = randint(40,80)                    # Dönme hızı
        self.rotation = 0                                       # Başlangıçta dönmemiş.

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt    # Meteorun mevcut konumuna, meteorun gideceği yön * hızı * dt eklenir.
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:      # Eğer yaşam süresi (3000 ms) dolmuşsa meteoru oyundan siliyoruz.
            self.kill()

        self.rotation += self.rotation_speed * dt               # Meteorun dönüş açısını her karede biraz artırıyoruz.
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)    # rotozoom, resmi döndürür ve boyutlandırır. rotozoom(kaynak, derece, boyut).  kaynak → hangi resmi döndüreceğiz, derece → kaç derece döndür, boyut → ne kadar büyüt/küçült (1 = aynı boyut, 2 = iki katı).
        self.rect = self.image.get_frect(center = self.rect.center)                     # Döndürülünce resmin boyutu değişir

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames                            # 21 resimlik liste geldi
        self.frame_index = 0                            # 0. resimden başla
        self.image = self.frames[self.frame_index]      # ilk resmi göster
        self.rect = self.image.get_frect(center = pos)  # lazerin çarptığı yere koy
        explosion_sound.play()                          # sesi çal

    def update(self, dt):                                       # her kare çalışır
        self.frame_index += 20 * dt                             # Frame ilerletme
        if self.frame_index < len(self.frames):                 # frame_index 21'e ulaştı mı? Daha gösterecek resim yok. kill() → sprite'ı tüm gruplardan çıkar, bellekten temizle.
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill( )

def collision():
    global running

    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)       # player ile meteor_sprites grubundaki meteorlardan herhangi biri çarpıştı mı?
    if collision_sprites:
        running = False

    for  laser in laser_sprites:    # Ekrandaki her lazeri tek tek ele alıyoruz.
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)     # bu lazer herhangi bir meteora çarptı mı?
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)     # Çarpışmanın olduğu yere patlama animasyonu oluştur. 

def display_score():                                                                                # ekranda skor/süre göstergesi çiziyor.
    current_time = pygame.time.get_ticks() // 100                                                   # Geçen süreyi al
    text_surf = font.render(str(current_time), True, (240,240,240))                                 # Yazıyı oluştur
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))             # Yazının konumunu belirle
    display_surface.blit(text_surf, text_rect)                                                      # Yazıyı çiz
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5, 10)    # azının etrafına çerçeve çiz


# general setup
pygame.init()                                                               # Pygame'in modüllerini başlatır:
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720                                     # Pencere boyutu
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))    # Ekranı oluşturur.
pygame.display.set_caption('Space shooter')                                 # Pencere başlığı
running = True
clock = pygame.time.Clock()                                                 # FPS ve dt hesaplamak için kullanılır.


# import
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]


# sounds
laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.4)
game_music.play(loops= -1)


# sprites
all_sprites = pygame.sprite.Group()             # all_sprites, Ekrana çizilecek her şey
meteor_sprites = pygame.sprite.Group()          # meteor_sprites, Sadece meteorlar
laser_sprites = pygame.sprite.Group()           # laser_sprites, Sadece lazerler
for i in range(20):                             # 20 adet yıldız oluşturur.
    Star(all_sprites, star_surf)
player = Player(all_sprites)                    # Oyuncuyu oluşturuyorsun.


# custom events -> meteor event                 # her 500 ms'de bir meteor oluşturma olayı üretmek için kullanılıyor.
meteor_event = pygame.event.custom_type()       # Yeni bir event türü oluştur
pygame.time.set_timer(meteor_event, 500)        # Her 500 milisaniyede bir meteor_event event kuyruğuna eklensin.


while running:
    dt = clock.tick() / 1000                                                # kaç saniye geçtiğini alır

    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))

    # update
    all_sprites.update(dt)
    collision()


    # draw the game
    display_surface.fill('#3a2e3f')         # get_ticks() ile süre/skor gösterir
    display_score()
    all_sprites.draw(display_surface)         # Tüm sprite’ları ekrana basar.


    pygame.display.update()                   # Ekranı güncelle, Çizilen her şeyi ekrana yansıtır.

pygame.quit()                                 # Pygame’i kapatır, temizler.

