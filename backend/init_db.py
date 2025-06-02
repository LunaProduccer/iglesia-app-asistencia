print("DEBUG: Iniciando init_db.py...")
import sqlite3
import os

# Determinar la ruta de la base de datos dentro de la carpeta 'instance'
# que estará al mismo nivel que este script si 'backend' es el directorio de trabajo.
# Si ejecutas desde la raíz del proyecto, necesitará ajustarse o ser absoluta.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'iglesia.db')
INSTANCE_FOLDER_PATH = os.path.join(BASE_DIR, 'instance')

def init_db():
    # Crear la carpeta 'instance' si no existe
    if not os.path.exists(INSTANCE_FOLDER_PATH):
        os.makedirs(INSTANCE_FOLDER_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crear tabla 'hermanos'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hermanos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            sexo TEXT,
            otros_campos TEXT
        )
    ''')

    # Crear tabla 'asistencias'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS asistencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hermano_id INTEGER NOT NULL,
            fecha_sunday DATE NOT NULL,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hermano_id) REFERENCES hermanos (id),
            UNIQUE (hermano_id, fecha_sunday)
        )
    ''')

    # Crear tabla 'visitas'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitante_id INTEGER NOT NULL,
            visitado_id INTEGER NOT NULL,
            fecha DATE NOT NULL,
            mes TEXT NOT NULL, -- ej. "junio"
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (visitante_id) REFERENCES hermanos (id),
            FOREIGN KEY (visitado_id) REFERENCES hermanos (id)
        )
    ''')

    # Poblar tabla 'hermanos' con datos iniciales si está vacía
    cursor.execute("SELECT COUNT(*) FROM hermanos")
    if cursor.fetchone()[0] == 0:
        hermanos_iniciales = [
            ("Aburto Amaya, Jhonatan Efraín", "M", None),
            ("Acero Renteria, Adolfo Alonso", "M", None),
            ("Acosta Mantilla, Sergio Steven", "M", None),
            ("Aguirre Perez, Christian Harold", "M", None),
            ("Aguirre Perez, Jeffrey Spencer", "M", None),
            ("Aguirre Toribio, Santos Andres", "M", None),
            ("Altamirano Hidalgo, Jhonatan Aldair", "M", None),
            ("Alvarez Espinola, Jimmy Edgar", "M", None),
            ("Alvarez Huaman, Braulio Omar", "M", None),
            ("Alvarez Salazar, Stefano Omar", "M", None),
            ("Alvarez Torres, Angel David", "M", None), # Añadido de 'Visitados'
            ("Alzamora Aragon, Guillermo Hugo", "M", None),
            ("Amoroto Castro, Enrique", "M", None),
            ("Aquino Coronado, Jhonatan Deiby", "M", None), # De 'Asistencia'
            ("Aquino Coronado, Manuel Jesus", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Aquino Coronado, Victor Andres", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Aranda Risco, Henry Edwin", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Armas Villanueva, Victor Manuel", "M", None),
            ("Asto Rojas, Ramon", "M", None),
            ("Atoche Lozada, Fernando Manuel", "M", None),
            ("Avalos Campos, Jorge Luis", "M", None),
            ("Avalos Peralta, Lorenzo", "M", None),
            ("Bejar Nieto, William Manuel", "M", None),
            ("Bermudes Bracamonte, Brian Joel", "M", None),
            ("Bermudez Diaz, Pedro Jesus Alonso", "M", None),
            ("Bocanegra Baca, Andair Alfredo", "M", None),
            ("Bocanegra Baca, Ricdson Jair", "M", None),
            ("Bocanegra Marquina, Alfredo Richard", "M", None),
            ("Briceño Burillo, Jesus Elias", "M", None),
            ("Cadenillas Preciado, Gregorio Manuel", "M", None),
            ("Calderon Tafur, Jose Warren", "M", None),
            ("Calderón Chávez, Sixto Arturo", "M", None),
            ("Camacho Chavez, Christhian Enrique", "M", None),
            ("Camacho Galarza, Victor Enrique", "M", None),
            ("Cano Bazan, Gerald Philips", "M", None),
            ("Carbajal Valdivia, Ary Daniel", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Carpio de la Cruz, Demetrio Henry", "M", None),
            ("Carvajal Valdivia, Danny Jairo", "M", None),
            ("Castillo Barahona, Francisco Antonio", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Castillo Jara, Daniel", "M", None),
            ("Castro Chavez, Fredes Vindo", "M", None),
            ("Castro Diaz, Lay Franklin", "M", None),
            ("Castro Villalva, Marco Antonio", "M", None),
            ("Cerdan Bazan, Grimaldo", "M", None),
            ("Cerna Izaguirre, Julio Cesar", "M", None),
            ("Chamochumbi Villanueva, Jilmer Roy", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Chauca Barreto, Luis Alberto", "M", None),
            ("Chavez Rengifo, Jorge", "M", None),
            ("Chinchay Amparado, Renzo Eduardo", "M", None),
            ("Chinchay Burillo, Jorge Segundo", "M", None),
            ("Cholan Quezada, Alejandro Manuel", "M", None),
            ("Cholan Quezada, Jhon Carlos", "M", None),
            ("Cholan Quezada, Juan Antonio", "M", None),
            ("Cholan Saucedo, Pedro Alexis", "M", None),
            ("Cobeñas Correa, Lennyn Smith", "M", None),
            ("Coronado Ortega, Nelson Edgardo", "M", None),
            ("Criollo Condoy, Eder Amadeo", "M", None),
            ("Cruzado Allemant, Jean Pierre", "M", None), # De 'Que Visitan'
            ("Cruzado Allemant, Jean Pol", "M", None), # De 'Que Visitan'
            ("Cruzado Cervera, Cesar Augusto", "M", None),
            ("Cruzado Cevallos, Carlos Yraldo", "M", None),
            ("Davalos Cano, Dick Denis", "M", None),
            ("De la Cruz Chanamé, Carlos Miguel", "M", None), # Añadido de 'Visitados' (de pareja)
            ("De La Cruz Mejia, Carlos Humberto", "M", None),
            ("De la Cuz Villanueva, Yefferson Mathias", "M", None),
            ("De La Guarda Budinich, Gino Aldo", "M", None),
            ("Devoto Durand, Juan Carlos", "M", None),
            ("Deza Rodriguez, Carlos Manuel", "M", None),
            ("Diaz Caballero, Jesus Alberto", "M", None),
            ("Dominguez Castillo, Rafael Wilfredo", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Dominguez Gudeño, Anthony Obed", "M", None),
            ("Elguera Montero, Juan Julio", "M", None),
            ("Escobar Silva, Arturo Alejandro", "M", None),
            ("Escobar Silva, Mario Francisco", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Escobar Silva, Martin Francisco", "M", None),
            ("Espinoza Ronceros, Irvin Marcos", "M", None),
            ("Farro Lozada, Arturo Meliton", "M", None),
            ("Farro Vera, Edwardo Arturo", "M", None),
            ("Fasshauer Mejia, Guillermo Franco", "M", None),
            ("Fasshauer Torres, Guillermo Otto", "M", None),
            ("Fernandez Molina, Renzo Miguel Angel", "M", None),
            ("Ferrer Chinchay, Jairo Antonio", "M", None),
            ("Flores Campos, Manuel Humberto", "M", None),
            ("Granados Arias, Victor Yahir", "M", None),
            ("Gutierrez Lopez, Giorgio Andre", "M", None),
            ("Gutierrez Mamani de Valeriano, Taylor Guillermo", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Gutierrez Molina, Alejandro", "M", None),
            ("Gutiérrez López, Anthony Giordano", "M", None),
            ("Guzman Leon, Ulices Ivan", "M", None),
            ("Guzman Minchola, David Wilman", "M", None),
            ("Guzman Minchola, Mario Arturo", "M", None),
            ("Guzman Polo, Raul Francisco", "M", None),
            ("Guzman Rosillo, Victor Manuel", "M", None),
            ("Hernandez Estrada, Nelson Eduardo", "M", None),
            ("Huacacolqui Minaya, Armando Eleazar", "M", None),
            ("Huaman Medina, Adriano Ashley", "M", None), # Ya estaba en Asistencia, también en Que Visitan
            ("Huaman Mera, Adriano Jesús Francisco", "M", None), # De 'Que Visitan'
            ("Huaman Montero, Randy Jesus", "M", None),
            ("Huaman Rodriguez, Adriano Antero", "M", None),
            ("Huaman Rodriguez, Nelson Alberto", "M", None),
            ("Huaman Rodriguez, Nelson Isaias", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Huaman Torres, Segundo Nicanor", "M", None),
            ("Huamanchumo Ortiz, Max Enrique", "M", None),
            ("Huamanchumo Ortiz, Yull Nestor", "M", None),
            ("Huamanchumo Pelaez, Nestor Enrique", "M", None),
            ("Huaraz Salinas, David Alexander", "M", None),
            ("Idelfonso Lopez, Lorezo", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Iparraguirre Yarleque, Cesar Augusto", "M", None),
            ("Iparraquirre Aacosta, Danny Bricenio", "M", None), # Nota: typo "Aacosta"
            ("Jaramillo Mendoza, Luis Rafael", "M", None),
            ("Jaramillo Oropeza, Luis Angel", "M", None),
            ("Jaramillo Oropeza, Rafael Daniel", "M", None),
            ("Jimenez Rodriguez, Hector Manuel", "M", None),
            ("Jiron Inilupu, Anyelo Clifor", "M", None),
            ("Jiron Yovera, Eulogio Ramiro", "M", None),
            ("Laguerre Gallardo, Helder Darcell", "M", None),
            ("Lazaro Morán de, Saneo Rafael", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Linares Melo, Jesus Martíner", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Linares Rojas, Juan Manuel", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Lopez Cerna, Miguel Angel", "M", None), # Añadido de 'Visitados'
            ("Lopez Lozano, Ernesto", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Lopez Sanchez, Emmel Eddy Gabriel", "M", None), # Añadido de 'Visitados'
            ("Lujan Haro, Marciano Celestino", "M", None), # Añadido de 'Visitados'
            ("Mariños Estrada, Patrick Adonis", "M", None), # Añadido de 'Visitados'
            ("Marin Rosales, Jaime Gonzalo", "M", None), # Añadido de 'Visitados'
            ("Martinez Pinedo, Carl Steveen", "M", None), # De 'Que Visitan'
            ("Matheus Medina, Edu Helmer", "M", None), # De 'Que Visitan' / 'Visitados' (de pareja)
            ("Maza Riofrio, Ailton Manuel", "M", None), # De 'Que Visitan'
            ("Medina Garcia, Apolinario Manuel", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Medina Gonzales, Erick Andres", "M", None), # De 'Que Visitan'
            ("Medina Ruiz, Andres Edgardo", "M", None), # De 'Que Visitan' / 'Visitados' (de pareja)
            ("Mera Vargas, Raul Renato", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Meza Bolaños, Fernando Nicolas", "M", None), # De 'Que Visitan'
            ("Meza Perez, Amador Livorio", "M", None), # De 'Que Visitan' / 'Visitados' (de pareja)
            ("Millones Tisnado, Francisco Alberto", "M", None), # De 'Que Visitan' / 'Visitados' (de pareja)
            ("Millones Vega, Albert Jhon", "M", None), # De 'Que Visitan'
            ("Montoya Otiniano, Juan Armando", "M", None), # De 'Que Visitan' / 'Visitados' (de pareja)
            ("Monzón Pinedo, Luis Fabrizzio", "M", None), # De 'Que Visitan'
            ("Morales Castro, Edgar Percy", "M", None), # Añadido de 'Visitados'
            ("Morales Valdiviezo, Frank Wuesly Wilkinson", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Morán Guerrero, Rosario Hernán", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Moretti Rivas, Franco Luis", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Mutto Gabriel, Carlos Alberto", "M", None), # De 'Que Visitan'
            ("Nazario Flores, Fisher Fernando James", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Neira Chavez, Roberto Carlos", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Neira Flores, Angel Patricio", "M", None), # Añadido de 'Visitados'
            ("Nieto Rivasplata, Jose Wilfredo", "M", None), # Añadido de 'Visitados'
            ("Ortega Contreras, Gustavo Adolfo", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Osorio Estefo, Leoncio Pedro", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Oyangure Rodriguez, Carlos Edinson", "M", None), # Añadido de 'Visitados'
            ("Palacios Ruiz, José Aimar", "M", None), # De 'Que Visitan'
            ("Palomino Depaz, Eduardo Daniel", "M", None), # De 'Que Visitan' / 'Visitados' (de pareja)
            ("Palomino Reyes, Jhonatan", "M", None), # De 'Que Visitan'
            ("Pastor Lozada, Adriano Ashley", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Pastor Medina, Dallin Antonio", "M", None), # De 'Que Visitan'
            ("Perez Tafur, Marco Antonio", "M", None), # Añadido de 'Visitados'
            ("Pinedo Farfan, Adolfo Nicolas", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Pinedo Flores, Willian Richard", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Pinedo Sarmiento, Nataniel Adolfo", "M", None), # De 'Que Visitan'
            ("Polo Campos, Christian Guillermo", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Polo Verastegui, Christian Eduardo", "M", None), # De 'Que Visitan'
            ("Portocarrero Sandy, Jorge Elias", "M", None), # Añadido de 'Visitados'
            ("Prieto Reyes, Paolo Josue", "M", None), # Añadido de 'Visitados'
            ("Prieto Tarma, Cesar Gregorio", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Pumarica Tafur, Dennis Guillermo", "M", None), # De 'Que Visitan'
            ("Ramirez Mejia, Armando Benjamin", "M", None), # De 'Que Visitan'
            ("Ramirez Reyes, Luis Alfredo", "M", None), # Añadido de 'Visitados'
            ("Ramirez Zapata, Dennis Lehi", "M", None), # De 'Que Visitan' / 'Visitados' (de pareja)
            ("Ramos Aguilar, Enrique", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Reyes Polo, Marco Antonio", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Rimache Ordinola, Victoriano", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Rios Barrera, Yul Milton", "M", None), # De 'Que Visitan' / 'Visitados' (de pareja)
            ("Rivera Matos, Roberto", "M", None), # De 'Que Visitan'
            ("Rivera Matos, Wilson Bladimir", "M", None), # De 'Que Visitan'
            ("Rodriguez Bernabe, Julio Cesar", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Rodriguez Blas, Anselmo", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Rodriguez Chuquino, Isidro", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Rodriguez Huaripata, Jose Luis", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Rodriguez Mendoza, Han Jefferson", "M", None), # Añadido de 'Visitados'
            ("Rodriguez Sanchez, Henry Jhon", "M", None), # De 'Que Visitan' / 'Visitados' (de pareja)
            ("Rodriguez Sanchez, Raul Walther", "M", None), # De 'Que Visitan' / 'Visitados' (de pareja)
            ("Rojas Cadenillas, Percy Smith", "M", None), # De 'Que Visitan'
            ("Romero Saldaña, Jeanpiere Del Piero", "M", None), # Añadido de 'Visitados'
            ("Ronceros Aquino, Brajean Andres", "M", None), # De 'Que Visitan'
            ("Ronceros Aquino, Franco Gabriel", "M", None), # Añadido de 'Visitados'
            ("Ronceros Aquino, Manuel Jesus", "M", None), # De 'Que Visitan'
            ("Ronceros Arcos, Carlos Antonio", "M", None), # Añadido de 'Visitados'
            ("Roque de la Cruz, Jose Alonso", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Saldaña Gusman, Roberto", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Salinas Alayo, Jeferson Andres", "M", None), # Añadido de 'Visitados'
            ("Sanchez Miranda, Isabel", "M", None), # Añadido de 'Visitados' - OJO: "Isabel" es nombre femenino. Lo incluyo como pediste nombres de las 3 listas, pero si es error, quítalo.
            ("Sanchez Rodriguez, Alex Paul", "M", None), # De 'Que Visitan' / 'Visitados' (de pareja)
            ("Sanchez Saldaña, Andres", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Sandoval Salcedo, Lucas Jhoao", "M", None), # Añadido de 'Visitados'
            ("Santillan Urquiza, Jaime Pedro", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Sarmiento Bustamante, Raul Alberto", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Savana Villena, Wolfan Nelson", "M", None), # Añadido de 'Visitados'
            ("Seclen Echeandia, Alex Ronaldinho", "M", None), # Añadido de 'Visitados'
            ("Segura Castro, David Eduardo", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Segura Vasquez, Luis Guillermo", "M", None), # De 'Que Visitan' / 'Visitados' (de pareja)
            ("Silva Chavez, John williams", "M", None), # De 'Que Visitan'
            ("Silva Chavez, Roger Arturo", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Silva Dominguez, Kurt Michael Steven", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Solon Quispe, Segundo Raul", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Tafur Carlos, Roberto", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Tafur Moreno, Vicente", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Tavera Ventura, Jorge Moises", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Timoteo Samamé, Elard Howend", "M", None), # De 'Que Visitan'
            ("Trejo Flores, Jhunior Erasmo", "M", None), # Añadido de 'Visitados'
            ("Trujillo del Castillo, Cristian Efrain", "M", None), # De 'Que Visitan' / 'Visitados' (de pareja)
            ("Valeriano Gutierrez, Taylor Guillermo", "M", None), # De 'Que Visitan'
            ("Valle Cuestas, Jesús Orlando", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Vargas Cam, Elizardo Oscar", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Vasquez Camilo, Luis Miguel", "M", None), # De 'Que Visitan'
            ("Vasquez Lopez, Saul Moises", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Vasquez Pajuelo, Luis Daniel", "M", None), # Añadido de 'Visitados'
            ("Vassallo Rodriguez, Marco Antonio", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Velarde Adrianzen, Manuel Eduardo", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Velasquez Estrada, Jimmy Cesar", "M", None), # Añadido de 'Visitados'
            ("Venegas de Oliveira, Thiago Franshesco", "M", None), # Añadido de 'Visitados'
            ("Verastegui Villalobos, Alcidez Nicolas", "M", None), # Añadido de 'Visitados' (de pareja)
            ("Villanueva Aguilar, Cesar Armando", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Villanueva Calderon, Brando Raúl", "M", None), # Añadido de 'Visitados'
            ("Villanueva Calderon, Mauro Alexander", "M", None), # De 'Que Visitan' / 'Visitados'
            ("Villanueva Millones, Walter Omar", "M", None), # Añadido de 'Visitados'
            ("Villanueva Miranda, Alex Gabriel", "M", None), # De 'Que Visitan'
            ("Yovera Romero, Jesus Narcizo", "M", None), # Añadido de 'Visitados'
            ("Zapata Chero, Jose Angel", "M", None), # De 'Que Visitan' / 'Visitados' (de pareja)
            ("Zumaran Juarez, Richar Efrain", "M", None) # Añadido de 'Visitados'
        ]
        cursor.executemany("INSERT INTO hermanos (nombre, sexo, otros_campos) VALUES (?, ?, ?)", hermanos_iniciales)
        print(f"Tabla 'hermanos' poblada con {len(hermanos_iniciales)} registros.")

    conn.commit()
    conn.close()
    print(f"Base de datos inicializada en {DB_PATH}")

if __name__ == '__main__':
    init_db()
print("DEBUG: Finalizando init_db.py...")