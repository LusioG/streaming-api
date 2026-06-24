import requests
from app.database import SessionLocal, Base, engine
from app.models.user_model import User
from app.models.content_model import Content
from app.models.category_model import Category
from app.models.watch_history import History
from app.models.content_category import content_categories
from app.utils.security import hash_password
import time

API_KEY = "5229f630aff7fb8b3cba5993ed1fe7bd"
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/"

# Lista de categorías ordenada por ID del 1 al 15
categorias_definicion = [
    {"id": 1, "name": "Acción", "image": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=400&auto=format&fit=crop"},
    {"id": 2, "name": "Comedia", "image": "https://images.unsplash.com/photo-1514306191717-452ec28c7814?q=80&w=400&auto=format&fit=crop"},
    {"id": 3, "name": "Drama", "image": "https://images.unsplash.com/photo-1485846234645-a62644f84728?q=80&w=400&auto=format&fit=crop"},
    {"id": 4, "name": "Ciencia Ficción", "image": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?q=80&w=400&auto=format&fit=crop"},
    {"id": 5, "name": "Terror", "image": "https://images.unsplash.com/photo-1505635339347-29180c41e966?q=80&w=400&auto=format&fit=crop"},
    {"id": 6, "name": "Aventura", "image": "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?q=80&w=400&auto=format&fit=crop"},
    {"id": 7, "name": "Romance", "image": "https://images.unsplash.com/photo-1518199266791-5375a83190b7?q=80&w=400&auto=format&fit=crop"},
    {"id": 8, "name": "Familiar", "image": "https://images.unsplash.com/photo-1511895426328-dc8714191300?q=80&w=400&auto=format&fit=crop"},
    {"id": 9, "name": "Suspenso", "image": "https://images.unsplash.com/photo-1509114397022-ed747cca3f65?q=80&w=400&auto=format&fit=crop"},
    {"id": 10, "name": "Documental", "image": "https://images.unsplash.com/photo-1526470608268-f674ce90ebd4?q=80&w=400&auto=format&fit=crop"},
    {"id": 11, "name": "Anime", "image": "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?q=80&w=400&auto=format&fit=crop"},
    {"id": 12, "name": "Fantasía", "image": "https://images.unsplash.com/photo-1518156677180-95a2893f3e9f?q=80&w=400&auto=format&fit=crop"},
    {"id": 13, "name": "Musical", "image": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?q=80&w=400&auto=format&fit=crop"},
    {"id": 14, "name": "Historia / Bélico", "image": "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?q=80&w=400&auto=format&fit=crop"},
    {"id": 15, "name": "Misterio", "image": "https://images.unsplash.com/photo-1518049362265-d5b2a6467637?q=80&w=400&auto=format&fit=crop"}
]

peliculas = [
    {"name":"Back to the Future","categories":[1,4,6]},
    {"name":"Back to the Future Part II","categories":[1,4,6]},
    {"name":"Back to the Future Part III","categories":[1,4,6]},
    {"name":"JoJo's Bizarre Adventure","categories":[11,1,6]},
    {"name":"Your Name.","categories":[11,8,7]},
    {"name":"Thunderbolts*","categories":[1,6]},
    {"name":"The Avengers","categories":[1,4,6]},
    {"name":"Avengers: Age of Ultron","categories":[1,4,6]},
    {"name":"Avengers: Infinity War","categories":[1,4,6]},
    {"name":"Avengers: Endgame","categories":[1,4,6]},
    {"name":"Spider-Man","categories":[1,6]},
    {"name":"Spider-Man 2","categories":[1,6]},
    {"name":"Spider-Man 3","categories":[1,6]},
    {"name":"Guardians of the Galaxy","categories":[1,4,6]},
    {"name":"Guardians of the Galaxy Vol. 2","categories":[1,4,6]},
    {"name":"Jojo Rabbit","categories":[2,3,14]},
    {"name":"My Neighbor Totoro","categories":[11,8,12]},
    {"name":"Grave of the Fireflies","categories":[3,8,14]},
    {"name":"The Greatest Showman","categories":[3,13,7]},
    {"name":"Star Wars","categories":[1,4,6,12]},
    {"name":"Star Wars: Episode I - The Phantom Menace","categories":[1,4,6,12]},
    {"name":"Star Wars: Episode II - Attack of the Clones","categories":[1,4,6,12]},
    {"name":"Star Wars: Episode III - Revenge of the Sith","categories":[1,4,6,12]},
    {"name":"Rogue One: A Star Wars Story","categories":[1,4,6]},
    {"name":"It","categories":[5,9]},
    {"name":"Demon Slayer: Kimetsu no Yaiba Infinity Castle","categories":[11,1,12]},
    {"name":"Chucky","categories":[5,9]},
    {"name":"Annabelle","categories":[5,9]},
    {"name":"Dead Silence","categories":[5,9]},
    {"name":"A Quiet Place","categories":[5,9]},
    {"name":"A Quiet Place Part II","categories":[5,9]},
    {"name":"Ben 10: Secret of the Omnitrix","categories":[8,1,6]},
    {"name":"Avatar","categories":[1,4,6,12]},
    {"name":"Avatar: The Way of Water","categories":[1,4,6,12]},
    {"name":"Avatar: Fire and Ash","categories":[1,4,6,12]},
    {"name":"The Midnight Sky","categories":[3,4]},
    {"name":"Interstellar","categories":[3,4,6]},
    {"name":"The Martian","categories":[3,4]},
    {"name":"The Revenant","categories":[3,1]},
    {"name":"Dragon Ball Z: Broly - The Legendary Super Saiyan","categories":[11,1,12]},
    {"name":"Hercules","categories":[8,12,6]},
    {"name":"The Princess and the Frog","categories":[8,7,12]},
    {"name":"WALL·E","categories":[8,4,7]},
    {"name":"Ratatouille","categories":[8,2]},
    {"name":"Oxygen","categories":[4,9]},
    {"name":"Archive","categories":[4,3]},
    {"name":"Cloverfield","categories":[4,5,9]},
    {"name":"The Cloverfield Paradox","categories":[4,5]},
    {"name":"Alien","categories":[4,5]},
    {"name":"Predator","categories":[1,4,5]},
    {"name":"AVP: Alien vs. Predator","categories":[1,4,5]},
    {"name":"Rocky","categories":[3]},
    {"name":"Rocky II","categories":[3]},
    {"name":"Rocky III","categories":[3]},
    {"name":"Rocky IV","categories":[3]},
    {"name":"Rocky V","categories":[3]},
    {"name":"Batman v Superman: Dawn of Justice","categories":[1,4,6]},
    {"name":"Venom","categories":[1,4]},
    {"name":"Anaconda","categories":[5,1]},
    {"name":"White Chicks","categories":[2]},
    {"name":"Scary Movie","categories":[2,5]},
    {"name":"Scary Movie 2","categories":[2,5]},
    {"name":"Jeepers Creepers","categories":[5]},
    {"name":"Slither","categories":[5,2]},
    {"name":"A Nightmare on Elm Street","categories":[5]},
    {"name":"Friday the 13th","categories":[5]},
    {"name":"If I Stay","categories":[3,7]},
    {"name":"The Devil Wears Prada","categories":[2,3]},
    {"name":"Teen Beach Movie","categories":[2,7,13]},
    {"name":"The Lord of the Rings: The Fellowship of the Ring","categories":[1,6,12]},
    {"name":"The Hobbit: An Unexpected Journey","categories":[1,6,12]},
    {"name":"The Hobbit: The Battle of the Five Armies","categories":[1,6,12]},
    {"name":"The Hobbit: The Desolation of Smaug","categories":[1,6,12]},
    {"name":"The Lord of the Rings: The Return of the King","categories":[1,6,12]},
    {"name":"The Lord of the Rings: The Two Towers","categories":[1,6,12]},
    {"name":"Pulp Fiction","categories":[3,9]},
    {"name":"The Truman Show","categories":[3,2]},
    {"name":"The Mask","categories":[2,12]},
    {"name":"How the Grinch Stole Christmas","categories":[2,12]},
    {"name":"Home on the Range","categories":[8,2]},
    {"name":"Dune","categories":[1,4,6]},
    {"name":"Dune: Part Two","categories":[1,4,6]},
    {"name":"Armageddon","categories":[1,4]},
    {"name":"Taken","categories":[1,9]},
    {"name":"Superbad","categories":[2]},
    {"name":"Spider-Man: Into the Spider-Verse","categories":[8,1,6]},
    {"name":"The Dark Knight","categories":[1,9]},
    {"name":"Spirited Away","categories":[11,8,12]},
    {"name":"The Matrix","categories":[1,4]},
    {"name":"Logan","categories":[1,3]},
    {"name":"Shrek","categories":[8,2,12]},
    {"name":"Shrek 2","categories":[8,2,12]},
    {"name":"Ice Age","categories":[8,2]},
    {"name":"The Godfather","categories":[3]},
    {"name":"Blade Runner 2049","categories":[4,3]},
    {"name":"The Lego Batman Movie","categories":[8,1,2]},
    {"name":"The Spiderwick Chronicles","categories":[6,12]},
    {"name":"Rush Hour","categories":[1,2]},
    {"name":"The Chronicles of Narnia: The Lion, the Witch and the Wardrobe","categories":[6,12]},
    {"name":"Cool Runnings","categories":[2,3]},
    {"name":"Journey to the Center of the Earth","categories":[6,4]},
    {"name":"Looney Tunes: Back in Action","categories":[2,8]},
    {"name":"Going in Style","categories":[2]},
    {"name":"Now You See Me","categories":[9,15]}
]

def get_movie_details(movie_name):
    # Buscar película
    search_url = f"{BASE_URL}/search/movie?api_key={API_KEY}&query={movie_name}"
    try:
        resp = requests.get(search_url, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not data.get('results'):
            return None
            
        movie = data['results'][0]
        movie_id = movie.get('id')
        
        poster_path = movie.get('poster_path')
        backdrop_path = movie.get('backdrop_path')
        
        poster_url = f"{IMAGE_BASE}w500{poster_path}" if poster_path else "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?q=80&w=400&auto=format&fit=crop"
        banner_url = f"{IMAGE_BASE}w780{backdrop_path}" if backdrop_path else "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=1200&auto=format&fit=crop"
        
        release_year = movie.get('release_date', '')[:4]
        release_year = int(release_year) if release_year.isdigit() else 2020
        description = movie.get('overview', 'Sin descripción.')
        
        # Obtener detalle para la duración
        duration = 120 # default
        if movie_id:
            detail_url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}"
            detail_resp = requests.get(detail_url, timeout=10)
            if detail_resp.status_code == 200:
                detail_data = detail_resp.json()
                runtime = detail_data.get('runtime')
                if runtime:
                    duration = runtime
                    
        return {
            "name": movie_name,
            "description": description,
            "image_url": poster_url,
            "banner_url": banner_url,
            "duration_minutes": duration,
            "release_year": release_year
        }
    except Exception as e:
        print(f"Error buscando {movie_name}: {e}")
        return None

def seed_database():
    print("Iniciando la carga de datos TMDB...")
    
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Limpiar datos anteriores
        print("Limpiando tablas de base de datos...")
        db.query(History).delete()
        db.execute(content_categories.delete())
        db.query(Content).delete()
        db.query(Category).delete()
        db.query(User).delete()
        db.commit()
        
        # 1. Crear Categorías en orden de ID
        print("Creando categorías (1 a 15)...")
        cat_map = {}
        for cat_def in categorias_definicion:
            cat = Category(
                id=cat_def["id"],
                name=cat_def["name"],
                image_url=cat_def["image"]
            )
            db.add(cat)
            cat_map[cat_def["id"]] = cat
        db.commit()
        
        # 2. Consultar TMDB y Crear Contenido
        total = len(peliculas)
        print(f"Buscando e insertando {total} películas/series desde TMDb...")
        
        added_count = 0
        for index, peli in enumerate(peliculas, 1):
            movie_name = peli["name"]
            category_ids = peli["categories"]
            
            print(f"[{index}/{total}] Procesando: {movie_name}...")
            
            # Intentar buscar en TMDb
            movie_data = get_movie_details(movie_name)
            if not movie_data:
                # Crear datos mock de fallback si falla la conexión o no se encuentra
                print(f"   [Fallback] Usando fallback para: {movie_name}")
                movie_data = {
                    "name": movie_name,
                    "description": f"Una gran película de prueba sobre {movie_name}.",
                    "image_url": "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?q=80&w=400&auto=format&fit=crop",
                    "banner_url": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=1200&auto=format&fit=crop",
                    "duration_minutes": 120,
                    "release_year": 2020
                }
            
            # Crear película
            nuevo_contenido = Content(
                name=movie_data["name"],
                description=movie_data["description"],
                image_url=movie_data["image_url"],
                banner_url=movie_data["banner_url"],
                duration_minutes=movie_data["duration_minutes"],
                release_year=movie_data["release_year"],
                is_active=True
            )
            
            # Asociar categorías
            associated_cats = []
            for cid in category_ids:
                if cid in cat_map:
                    associated_cats.append(cat_map[cid])
            nuevo_contenido.categories = associated_cats
            
            db.add(nuevo_contenido)
            added_count += 1
            
            # Commit parcial cada 10 items para no perder progreso y evitar transacciones enormes
            if index % 10 == 0:
                db.commit()
                print("   [Parcial] Guardado parcial completado.")
                
            # Pequeño delay respetuoso para no saturar la API de TMDB
            time.sleep(0.1)
            
        db.commit()
        print(f"Carga de contenidos completa! {added_count} peliculas agregadas.")
        
        # 3. Crear usuario de prueba por defecto
        print("Creando usuario de prueba...")
        user_test = User(
            email="test@streaming.com",
            username="luchodev",
            password_hash=hash_password("admin123"),
            is_active=True
        )
        db.add(user_test)
        db.commit()
        
        print("\nBase de datos inicializada exitosamente!")
        print("------------------------------------------")
        print("Credenciales de usuario de prueba:")
        print("Email: test@streaming.com")
        print("Usuario: luchodev")
        print("Contrasena: admin123")
        print("------------------------------------------")
        
    except Exception as e:
        print(f"Error al sembrar la base de datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
