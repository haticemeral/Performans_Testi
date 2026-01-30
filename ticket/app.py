import time
import random
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Veritabanı Ayarları
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "super_secret_key"  
db = SQLAlchemy(app)


# -----------------------------
#       VERİTABANI MODELLERİ
# -----------------------------

class Event(db.Model): #etkinlikleri tutan tablo
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    location = db.Column(db.String(120))
    date = db.Column(db.String(50))
    stock = db.Column(db.Integer)


class User(db.Model): #kullanıcıları tutan tablo
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(200))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Favorite(db.Model): #favori etkinlikleri tutan tablo
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))


# --------------------------------
#       SAYFA (HTML) ROUTELARI
# --------------------------------
#sadece sayfaları getiriyor api işlemi yok
@app.route('/') #ana sayfa
def index():
    return render_template("index.html")


@app.route('/login') #giriş sayfası
def login_page():
    return render_template("login.html")


@app.route('/register') #kayıt sayfası
def register_page():
    return render_template("register.html")


@app.route('/favorites') #favori etkinlikler sayfası
def favorites_page():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return render_template("favorites.html")


@app.route('/event/<int:event_id>') #etkinlik detay sayfası
def event_detail(event_id):
    event = Event.query.get(event_id)
    if not event:
        return "Etkinlik bulunamadı", 404

    posters = {
        "Duman": "/static/images/duman.jpg",
        "Adamlar": "/static/images/adamlar.jpg",
        "Yüzyüzeyken Konuşuruz": "/static/images/yyk.jpg",
        "Manifest": "/static/images/manifest.jpg",
        "Dedublüman": "/static/images/dedubluman.jpg",
        "Göksel": "/static/images/goksel.jpg"
    }

    poster = posters.get(event.name, "/static/images/dedubluman.jpg")#etkinlik adına göre poster seçimi eğer yoksa dedüblüman default

    return render_template("event_detail.html", event=event, poster=poster)


@app.route('/logout') #çıkış yapma sayfası
def logout_page():
    session.pop("user_id", None)
    return redirect(url_for("index"))


# --------------------------------
#             API
# --------------------------------
#api işlemleri burada yapılıyor
@app.route('/api/events') #etkinlik listesini döndüren api
def list_events():
    events = Event.query.all()
    result = []
    for e in events:
        result.append({
            "id": e.id,
            "name": e.name,
            "location": e.location,
            "date": e.date,
            "stock": e.stock
        })
    return jsonify(result) #json formatında döndürüyor


@app.route('/api/register', methods=['POST']) #yeni kullanıcı kaydı api
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Kullanıcı adı ve şifre gerekli"}), 400 #hatalı istek

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Bu kullanıcı adı zaten alınmış"}), 400 #hatalı istek
    
    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user) #yeni kullanıcıyı sessiona ekliyoruz
    db.session.commit() #sessiona eklenen kullanıcıyı veritabanına kaydediyoruz

    return jsonify({"message": "Kayıt başarılı!"})


@app.route('/api/login', methods=['POST']) #kullanıcı girişi api
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first() #kullanıcıları filtrelerdik first ile  sorgudaki ilk kaydı alıyoruz

    if user and user.check_password(data.get("password")): #kullanıcı var mı ve şifre doğru mu kontrolü
        session['user_id'] = user.id
        return jsonify({"message": "Giriş başarılı!"})
    
    return jsonify({"error": "Hatalı kullanıcı adı veya şifre"}), 401 #kullanıcı giriş yapmamış veya yetkisi yok


@app.route('/api/logout') #çıkış yapma api
def logout_api():
    session.pop('user_id', None) #kullancı idye göre sessiondan çıkarma
    return jsonify({"message": "Çıkış yapıldı"})


@app.route('/api/favorites/add', methods=['POST']) #favori etkinlik ekleme api
def add_favorite():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Giriş yapmanız gerekiyor"}), 401 #kullanıcı giriş yapmamış veya yetkisi yok

    event_id = request.json.get("event_id")
    if not event_id:
        return jsonify({"error": "event_id gerekli"}), 400 #hatalı istek

    if Favorite.query.filter_by(user_id=user_id, event_id=event_id).first():
        return jsonify({"error": "Bu etkinlik zaten favorilerde"}), 400 #hatalı istek

    fav = Favorite(user_id=user_id, event_id=event_id)
    db.session.add(fav)
    db.session.commit()

    return jsonify({"message": "Etkinlik favorilere eklendi!"})


@app.route('/api/favorites') #favori etkinlikleri listeleme api
def list_favorites():
    user_id = session.get('user_id')
    if not user_id: #kullanıcı giriş yapmamışsa hata döndürüyor
        return jsonify({"error": "Giriş yapmanız gerekiyor"}), 401 #kullanıcı giriş yapmamış veya yetkisi yok

    favorites = Favorite.query.filter_by(user_id=user_id).all() #kullanıcının favori etkinliklerini alıyoruz
    result = []

    for f in favorites: #favori etkinlikleri dönüyoruz
        event = Event.query.get(f.event_id)
        if event:
            result.append({
                "id": event.id,
                "name": event.name,
                "location": event.location,
                "date": event.date,
                "stock": event.stock
            })

    return jsonify(result)


# -----------------------------
#        BİLET SATIN ALMA
# -----------------------------

@app.route('/api/buy/<int:event_id>', methods=['POST']) #bilet satın alma api
def buy_ticket(event_id): #etkinlik idye göre bilet satın alma
    time.sleep(random.uniform(0.1, 0.2)) #rastgele gecikme ekliyoruz

    event = Event.query.get(event_id) #etkinlik idye göre etkinliği alıyoruz
    if event and event.stock > 0: #etkinlik var mı ve stokta bilet var mı kontrolü
        event.stock -= 1 #stoktan 1 bilet eksiltiyoruz
        try:
            db.session.commit() #değişiklikleri veritabanına kaydediyoruz
            return jsonify({"message": "Satın alma başarılı!", "kalan": event.stock})
        except:
            db.session.rollback() #hata olursa değişiklikleri geri alıyoruz
            return jsonify({"error": "Veritabanı hatası"}), 500 #sunucu hatası
    else:
        return jsonify({"error": "Stok tükendi!"}), 400 #hatalı istek


# -----------------------------
#   DOLDURMA / TEST İÇİN INIT
# -----------------------------

@app.route('/api/init') #veritabanını doldurma api
def init_db():
    with app.app_context():
        db.create_all()
        Event.query.delete()
        #örnek etkinlikler
        events = [ 
            Event(name="Duman", location="İstanbul", date="2025-06-10", stock=300),
            Event(name="Adamlar", location="Ankara", date="2025-07-01", stock=400),
            Event(name="Yüzyüzeyken Konuşuruz", location="İzmir", date="2025-07-12", stock=500),
            Event(name="Manifest", location="Antalya", date="2025-08-05", stock=350),
            Event(name="Dedublüman", location="Bursa", date="2025-09-15", stock=420),
            Event(name="Göksel", location="Muğla", date="2025-10-20", stock=390),
        ]

        for e in events:
            db.session.add(e)

        db.session.commit()

    return jsonify({"status": "Hazır", "message": "Etkinlikler oluşturuldu!"})


# -----------------------------
#            RUN
# -----------------------------

if __name__ == '__main__': #uygulamayı çalıştırma
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000, threaded=True)