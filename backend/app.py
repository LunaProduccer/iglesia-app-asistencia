import sqlite3
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from datetime import datetime, timedelta, date
import os

# Configuración de la App
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'iglesia.db')
INSTANCE_FOLDER_PATH = os.path.join(BASE_DIR, 'instance')

app = Flask(__name__) # No se necesita static_folder si el frontend se sirve por separado
CORS(app) # Habilitar CORS para todas las rutas

# --- Configuración de la Base de Datos ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        if not os.path.exists(INSTANCE_FOLDER_PATH):
            os.makedirs(INSTANCE_FOLDER_PATH)
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row # Permite acceder a las columnas por nombre
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Funciones Auxiliares ---
def get_previous_or_current_sunday(input_date_str):
    """
    Dada una fecha en formato YYYY-MM-DD, devuelve la fecha del domingo
    correspondiente (si es domingo) o el domingo anterior.
    """
    dt = datetime.strptime(input_date_str, '%Y-%m-%d').date()
    # weekday() devuelve Lunes=0, ..., Domingo=6
    if dt.weekday() == 6: # Si es domingo
        return dt
    else: # Si no es domingo, encontrar el domingo anterior
        return dt - timedelta(days=(dt.weekday() + 1) % 7)

# --- API Endpoints ---

@app.route('/api/hermanos', methods=['GET'])
def get_hermanos():
    try:
        db = get_db()
        cursor = db.execute("SELECT id, nombre, sexo, otros_campos FROM hermanos ORDER BY nombre")
        hermanos = [dict(row) for row in cursor.fetchall()]
        return jsonify(hermanos)
    except Exception as e:
        app.logger.error(f"Error en /api/hermanos: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/asistencias', methods=['GET'])
def get_asistencias():
    mes = request.args.get('mes') # ej. "junio"
    year = request.args.get('year') # ej. "2025"

    if not mes or not year:
        return jsonify({"error": "Parámetros 'mes' y 'year' son requeridos"}), 400

    # Convertir nombre del mes a número de mes
    nombres_meses_es = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
        "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
    }
    month_number = nombres_meses_es.get(mes.lower())

    if not month_number:
        return jsonify({"error": "Nombre de mes inválido"}), 400

    try:
        year_int = int(year)
        # Primer día del mes y último día del mes
        start_date = date(year_int, month_number, 1)
        if month_number == 12:
            end_date = date(year_int + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year_int, month_number + 1, 1) - timedelta(days=1)

        db = get_db()
        # Filtrar asistencias por el rango de fechas del mes, específicamente los domingos
        query = """
            SELECT hermano_id, fecha_sunday
            FROM asistencias
            WHERE fecha_sunday >= ? AND fecha_sunday <= ?
        """
        cursor = db.execute(query, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        asistencias_raw = cursor.fetchall()

        # Agrupar asistencias por hermano_id y luego por fecha_sunday
        asistencias_agrupadas = {}
        for row in asistencias_raw:
            hermano_id_str = str(row['hermano_id'])
            fecha_str = row['fecha_sunday'] # Ya está en formato YYYY-MM-DD
            if hermano_id_str not in asistencias_agrupadas:
                asistencias_agrupadas[hermano_id_str] = []
            asistencias_agrupadas[hermano_id_str].append(fecha_str)

        return jsonify(asistencias_agrupadas)

    except ValueError:
        return jsonify({"error": "Año inválido"}), 400
    except Exception as e:
        app.logger.error(f"Error en /api/asistencias: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/asistencia', methods=['POST'])
def add_asistencia():
    data = request.get_json()
    hermano_id = data.get('hermano_id')
    fecha_str = data.get('fecha') # Espera "YYYY-MM-DD"

    if not hermano_id or not fecha_str:
        return jsonify({"error": "hermano_id y fecha son requeridos"}), 400

    try:
        fecha_domingo_correspondiente = get_previous_or_current_sunday(fecha_str)
        fecha_domingo_str = fecha_domingo_correspondiente.strftime('%Y-%m-%d')

        db = get_db()
        cursor = db.cursor()

        # Verificar si ya existe
        cursor.execute("SELECT id FROM asistencias WHERE hermano_id = ? AND fecha_sunday = ?",
                       (hermano_id, fecha_domingo_str))
        existente = cursor.fetchone()

        if existente:
            return jsonify({"mensaje": "ya registrado", "id_existente": existente['id'], "fecha_registrada": fecha_domingo_str}), 200
        else:
            cursor.execute("INSERT INTO asistencias (hermano_id, fecha_sunday) VALUES (?, ?)",
                           (hermano_id, fecha_domingo_str))
            db.commit()
            nuevo_id = cursor.lastrowid
            return jsonify({"mensaje": "guardado", "id": nuevo_id, "hermano_id": hermano_id, "fecha_sunday": fecha_domingo_str}), 201

    except ValueError:
        return jsonify({"error": "Formato de fecha inválido. Usar YYYY-MM-DD"}), 400
    except sqlite3.IntegrityError as e: # Podría ser por FK constraint si el hermano_id no existe
        app.logger.error(f"Error de integridad en /api/asistencia: {e}")
        return jsonify({"error": "Error de integridad en la base de datos. ¿El hermano_id es válido?"}), 400
    except Exception as e:
        app.logger.error(f"Error en /api/asistencia: {e}")
        db.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/visitas', methods=['GET'])
def get_visitas():
    mes_param = request.args.get('mes') # ej. "junio"
    year_param = request.args.get('year') # ej. "2025"

    if not mes_param or not year_param:
        return jsonify({"error": "Parámetros 'mes' y 'year' son requeridos"}), 400
    
    try:
        # No necesitamos convertir el año a int si solo lo usamos para filtrar texto en la DB
        # pero es bueno validar que sea un número potencialmente.
        int(year_param) # Valida que sea un número
    except ValueError:
        return jsonify({"error": "Parámetro 'year' debe ser un número."}), 400


    try:
        db = get_db()
        query = """
            SELECT
                v.id,
                v.fecha,
                v.mes,
                v.creado_en,
                visitante.nombre as nombre_visitante,
                visitado.nombre as nombre_visitado,
                v.visitante_id,
                v.visitado_id
            FROM visitas v
            JOIN hermanos visitante ON v.visitante_id = visitante.id
            JOIN hermanos visitado ON v.visitado_id = visitado.id
            WHERE v.mes = ? AND strftime('%Y', v.fecha) = ?
            ORDER BY v.fecha DESC
        """
        cursor = db.execute(query, (mes_param.lower(), year_param))
        visitas = [dict(row) for row in cursor.fetchall()]
        return jsonify(visitas)
    except Exception as e:
        app.logger.error(f"Error en /api/visitas: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/visita', methods=['POST'])
def add_visita():
    data = request.get_json()
    visitante_id = data.get('visitante_id')
    visitado_id = data.get('visitado_id')

    if not visitante_id or not visitado_id:
        return jsonify({"error": "visitante_id y visitado_id son requeridos"}), 400
    
    if visitante_id == visitado_id:
        return jsonify({"error": "Un hermano no puede visitarse a sí mismo de esta manera."}), 400

    try:
        fecha_actual = date.today()
        mes_actual_texto = fecha_actual.strftime("%B").lower() # Nombre del mes en inglés por defecto
        # Para español, necesitaríamos un mapeo si el sistema está en inglés
        nombres_meses_es = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
            7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
        }
        mes_actual_texto_es = nombres_meses_es[fecha_actual.month]

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO visitas (visitante_id, visitado_id, fecha, mes) VALUES (?, ?, ?, ?)",
            (visitante_id, visitado_id, fecha_actual.strftime('%Y-%m-%d'), mes_actual_texto_es)
        )
        db.commit()
        nuevo_id = cursor.lastrowid

        # Devolver el registro guardado (opcionalmente con nombres)
        cursor.execute("""
            SELECT v.id, v.fecha, v.mes, h_visitante.nombre as nombre_visitante, h_visitado.nombre as nombre_visitado
            FROM visitas v
            JOIN hermanos h_visitante ON v.visitante_id = h_visitante.id
            JOIN hermanos h_visitado ON v.visitado_id = h_visitado.id
            WHERE v.id = ?
        """, (nuevo_id,))
        registro_guardado = dict(cursor.fetchone())

        return jsonify({"mensaje": "Visita registrada", "registro": registro_guardado}), 201

    except sqlite3.IntegrityError:
         return jsonify({"error": "ID de visitante o visitado no válido."}), 400
    except Exception as e:
        app.logger.error(f"Error en /api/visita: {e}")
        db.rollback()
        return jsonify({"error": str(e)}), 500

# Opcional: Endpoint para agregar hermanos (no solicitado explícitamente para base_datos.html)
@app.route('/api/hermano', methods=['POST'])
def add_hermano():
    data = request.get_json()
    nombre = data.get('nombre')
    sexo = data.get('sexo')
    otros_campos = data.get('otros_campos')

    if not nombre:
        return jsonify({"error": "El campo 'nombre' es requerido"}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO hermanos (nombre, sexo, otros_campos) VALUES (?, ?, ?)",
            (nombre, sexo, otros_campos)
        )
        db.commit()
        nuevo_id = cursor.lastrowid
        return jsonify({"mensaje": "Hermano agregado", "id": nuevo_id, "nombre": nombre, "sexo": sexo, "otros_campos": otros_campos}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    
# ... (aquí está tu función add_visita y otras rutas) ...

@app.route('/api/visita/<int:visita_id>', methods=['DELETE'])
def delete_visita(visita_id):
    try:
        db = get_db()
        cursor = db.cursor()

        # Primero, verificar si la visita existe para no dar error si no se encuentra
        cursor.execute("SELECT id FROM visitas WHERE id = ?", (visita_id,))
        visita = cursor.fetchone()

        if visita is None:
            return jsonify({"error": "Visita no encontrada"}), 404

        # Si existe, proceder a borrarla
        cursor.execute("DELETE FROM visitas WHERE id = ?", (visita_id,))
        db.commit()

        # app.logger.info(f"Visita con ID {visita_id} eliminada.") # Log opcional para el servidor
        return jsonify({"mensaje": "Visita eliminada exitosamente", "id_eliminado": visita_id}), 200 # 200 OK o 204 No Content

    except Exception as e:
        db.rollback() # Asegurarse de revertir cambios si algo sale mal
        app.logger.error(f"Error al eliminar visita {visita_id}: {e}")
        return jsonify({"error": str(e)}), 500

# ... (aquí empieza el if __name__ == '__main__':) ...

if __name__ == '__main__':
    # Crear la carpeta 'instance' si no existe, por si acaso init_db.py no se corrió
    if not os.path.exists(INSTANCE_FOLDER_PATH): # Asegúrate que INSTANCE_FOLDER_PATH esté definido arriba
        os.makedirs(INSTANCE_FOLDER_PATH)
        print(f"Directorio 'instance' creado en {INSTANCE_FOLDER_PATH}")

    print(f"Base de datos esperada en: {DB_PATH}") # Asegúrate que DB_PATH esté definido
    if not os.path.exists(DB_PATH):
        print("ADVERTENCIA: El archivo de base de datos no existe. Ejecuta `python init_db.py` primero.")

    print("DEBUG: Intentando iniciar el servidor Flask...") # Línea de DEBUG
    app.run(debug=True, host='0.0.0.0', port=5000)