const API_URL = 'http://127.0.0.1:5000/api'; // URL base de tu API Flask

const nombresMeses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
const diasSemana = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];

// --- Funciones Utilitarias ---
async function fetchData(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: "Error de red o respuesta no JSON" }));
            console.error(`Error ${response.status} en ${endpoint}:`, errorData);
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        if (response.status === 204) return null; // No content
        return await response.json();
    } catch (error) {
        console.error(`Fetch error en ${endpoint}:`, error);
        showGlobalMessage(`Error al contactar el servidor: ${error.message}`, 'error');
        throw error;
    }
}

function showGlobalMessage(message, type = 'success') {
    const messageContainer = document.getElementById('globalMessage') || createGlobalMessageContainer();
    messageContainer.textContent = message;
    messageContainer.className = `message ${type}`;
    messageContainer.style.display = 'block';
    setTimeout(() => {
        messageContainer.style.display = 'none';
    }, 5000);
}

function createGlobalMessageContainer() {
    const container = document.createElement('div');
    container.id = 'globalMessage';
    document.body.insertBefore(container, document.body.firstChild);
    return container;
}


// --- Funciones Específicas para Asistencia ---
function getDomingosDelMes(year, month) { // month es 0-indexado
    const domingos = [];
    const primerDiaDelMes = new Date(year, month, 1);
    let diaActual = new Date(primerDiaDelMes);

    // Encontrar el primer domingo del mes o justo antes si el mes no empieza en domingo
    // Avanzar al primer domingo: si el primer día es lunes (1), restar 1 para llegar a domingo (0). getDay() es Dom=0, Lun=1...
    // No, necesitamos el primer domingo *dentro* del mes o el último del mes anterior que es cabeza de semana.
    // Corrección: Encontrar el primer día del mes, luego avanzar hasta el primer domingo de esa semana.
    
    let d = new Date(year, month, 1);
    // Retroceder al domingo de la semana en que cae el día 1
    d.setDate(d.getDate() - d.getDay());
    
    // Iterar por semanas hasta que el domingo ya no pertenezca al mes o al inicio del siguiente
    // Esto mostrará todos los domingos que tienen al menos un día en el mes actual.
    while (d.getFullYear() < year || (d.getFullYear() === year && d.getMonth() <= month)) {
        // Solo agregar si el domingo cae dentro del mes actual o si es el domingo de la semana
        // en que empieza el mes, incluso si es del mes anterior (para mostrar la semana completa)
        // O si es un domingo del mes actual.
        const esDomingoDelMesActualOVisible = (d.getFullYear() === year && d.getMonth() === month) ||
                                              (d.getFullYear() === year && d.getMonth() === month -1 && (new Date(year, month, 1).getDay() !==0 && d.getDate() >= new Date(year,month,1).getDate() - new Date(year,month,1).getDay()));
        
        // La lógica para mostrar los domingos es:
        // todos los domingos cuyo día está EN el mes actual.
        const tempDateForSunday = new Date(d); // Copia para no modificar 'd' antes de la condición
        if (tempDateForSunday.getMonth() === month && tempDateForSunday.getFullYear() === year) {
             domingos.push(new Date(tempDateForSunday));
        } else if (domingos.length > 0 && tempDateForSunday.getMonth() > month) { 
            // Si ya hemos añadido domingos del mes y este ya es del siguiente mes, paramos.
            break;
        }


        d.setDate(d.getDate() + 7); // Siguiente domingo
         if (d.getMonth() > month && d.getFullYear() === year && domingos.length === 0){
            // Caso borde: si el primer domingo calculado ya es del mes siguiente y no hemos añadido ninguno.
            // Esto significa que el mes actual no tiene domingos (imposible) o la lógica está mal.
            // Para asegurar que al menos los domingos del mes se muestren:
            // Reajustar d al primer domingo real del mes.
            d = new Date(year, month, 1);
            d.setDate(d.getDate() + ( (7-d.getDay()) % 7 ) );
            if(d.getMonth() === month) domingos.push(new Date(d)); else continue; // Si el primer domingo real aun es del mes
            d.setDate(d.getDate() + 7);
        }
    }
    // Si el último domingo añadido no es del mes actual, pero el anterior sí, puede ser un error.
    // Nos aseguramos de que solo se incluyan domingos del mes actual.
    return domingos.filter(dom => dom.getMonth() === month && dom.getFullYear() === year);
}

function formatDateToYMD(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
}

function formatDateToDM(date) {
    const d = date.getDate();
    const m = nombresMeses[date.getMonth()].substring(0,3);
    return `${d}-${m}`;
}

async function cargarAsistencias() {
    const tablaAsistencia = document.getElementById('tablaAsistenciaBody');
    const thDomingos = document.getElementById('thDomingos');
    if (!tablaAsistencia || !thDomingos) return;

    tablaAsistencia.innerHTML = '<tr><td colspan="10">Cargando datos...</td></tr>'; // Limpiar y mensaje de carga
    thDomingos.innerHTML = ''; // Limpiar encabezados de domingos

    const hoy = new Date();
    const anioActual = hoy.getFullYear();
    const mesActualIdx = hoy.getMonth(); // 0-indexed
    const mesActualTexto = nombresMeses[mesActualIdx];

    document.getElementById('tituloMesAsistencia').textContent = `Asistencia de ${mesActualTexto.charAt(0).toUpperCase() + mesActualTexto.slice(1)} ${anioActual}`;

    const domingosDelMes = getDomingosDelMes(anioActual, mesActualIdx);

    // Crear encabezados de domingos
    domingosDelMes.forEach(domingo => {
        const th = document.createElement('th');
        th.textContent = formatDateToDM(domingo);
        thDomingos.appendChild(th);
    });

    try {
        const [hermanos, asistenciasData] = await Promise.all([
            fetchData('/hermanos'),
            fetchData(`/asistencias?mes=${mesActualTexto}&year=${anioActual}`)
        ]);

        tablaAsistencia.innerHTML = ''; // Limpiar después de cargar datos

        if (!hermanos || hermanos.length === 0) {
            tablaAsistencia.innerHTML = '<tr><td colspan="' + (domingosDelMes.length + 1) + '">No hay hermanos registrados.</td></tr>';
            return;
        }
        
        hermanos.forEach(hermano => {
            const tr = tr_hermano_asistencia_row(hermano, domingosDelMes, asistenciasData);
            tablaAsistencia.appendChild(tr);
        });

    } catch (error) {
        tablaAsistencia.innerHTML = '<tr><td colspan="' + (domingosDelMes.length + 1) + '">Error al cargar datos. Ver consola.</td></tr>';
    }
}

function tr_hermano_asistencia_row(hermano, domingosDelMes, asistenciasData){
    const tr = document.createElement('tr');
    const tdNombre = document.createElement('td');
    tdNombre.textContent = hermano.nombre;
    tr.appendChild(tdNombre);

    const asistenciasDelHermano = asistenciasData[hermano.id.toString()] || [];

    domingosDelMes.forEach(domingo => {
        const tdDomingo = document.createElement('td');
        const btnAsistencia = document.createElement('span');
        btnAsistencia.classList.add('btn-circle');
        const fechaDomingoStr = formatDateToYMD(domingo);

        if (asistenciasDelHermano.includes(fechaDomingoStr)) {
            btnAsistencia.classList.add('btn-checked');
        }

        btnAsistencia.addEventListener('click', async () => {
            if (btnAsistencia.classList.contains('btn-checked')) {
                // Aquí podrías implementar la lógica para desmarcar si fuera necesario.
                // Por ahora, la API solo registra, no borra por clic.
                console.log(`Asistencia para ${hermano.nombre} en ${fechaDomingoStr} ya está marcada.`);
                showGlobalMessage('Asistencia ya registrada para esta fecha.', 'info');
                return;
            }

            try {
                const resultado = await fetchData('/asistencia', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ hermano_id: hermano.id, fecha: fechaDomingoStr })
                });

                if (resultado.mensaje === "guardado" || resultado.mensaje === "ya registrado") {
                    btnAsistencia.classList.add('btn-checked');
                    showGlobalMessage(`Asistencia de ${hermano.nombre} para el ${formatDateToDM(domingo)} registrada.`, 'success');
                } else {
                    showGlobalMessage(resultado.error || 'Error al registrar asistencia.', 'error');
                }
            } catch (error) {
                // El error ya se maneja en fetchData y muestra mensaje global
            }
        });
        tdDomingo.appendChild(btnAsistencia);
        tr.appendChild(tdDomingo);
    });
    return tr;
}


// --- Funciones Específicas para Visitas ---

// Función auxiliar para configurar los inputs con datalist
function setupSearchableInput(inputIdText, inputIdHidden, datalistId) {
    const nombreInput = document.getElementById(inputIdText);
    const idInputHidden = document.getElementById(inputIdHidden);
    const datalist = document.getElementById(datalistId);

    if (nombreInput && idInputHidden && datalist) {
        nombreInput.addEventListener('input', function() {
            const nombreSeleccionado = this.value;
            let idEncontrado = '';
            for (let i = 0; i < datalist.options.length; i++) {
                if (datalist.options[i].value === nombreSeleccionado) {
                    idEncontrado = datalist.options[i].dataset.id;
                    break;
                }
            }
            idInputHidden.value = idEncontrado;
        });

        nombreInput.addEventListener('change', function() { // Cuando el usuario deja el campo
            if (this.value === '') { // Si lo deja vacío
                idInputHidden.value = '';
            } else { // Si escribió algo, volvemos a verificar si es una opción válida
                let idEncontrado = '';
                for (let i = 0; i < datalist.options.length; i++) {
                    if (datalist.options[i].value === this.value) {
                        idEncontrado = datalist.options[i].dataset.id;
                        break;
                    }
                }
                if (idEncontrado === '') { // Si no es una opción válida del datalist
                    // console.warn(`El nombre "${this.value}" no es una opción válida.`);
                    // showGlobalMessage(`"${this.value}" no es un hermano válido. Por favor, selecciona de la lista.`, 'error');
                    this.value = ''; // Opcional: Limpiar el campo de texto si no es válido
                    idInputHidden.value = ''; // Asegurarse que el ID oculto esté vacío
                } else {
                    idInputHidden.value = idEncontrado;
                }
            }
        });
    } else {
        console.error("Error al configurar input searchable: Faltan elementos del DOM:", inputIdText, inputIdHidden, datalistId);
    }
}


async function cargarFormularioYListaVisitas() {
    // Obtener referencias a los NUEVOS elementos del DOM para los inputs de texto y el datalist
    const visitanteNombreInput = document.getElementById('visitanteNombre');
    const visitadoNombreInput = document.getElementById('visitadoNombre');
    const datalistHermanos = document.getElementById('listaHermanosDatalist');
    
    const formVisita = document.getElementById('formRegistrarVisita');
    const listaVisitasBody = document.getElementById('listaVisitasBody');

    // Verificamos que los elementos principales del formulario y la tabla existan
    if (!formVisita || !listaVisitasBody || !visitanteNombreInput || !visitadoNombreInput || !datalistHermanos) {
        console.error("Faltan elementos esenciales en visitas.html para cargar el formulario o la lista.");
        return;
    }
    
    try {
        const hermanos = await fetchData('/hermanos');
        if (!hermanos) {
            showGlobalMessage('No se pudieron cargar los hermanos para el formulario de visitas.', 'error');
            return; // Salir si no hay hermanos
        }

        // Limpiar datalist antes de poblar
        datalistHermanos.innerHTML = ''; 

        hermanos.forEach(hermano => {
            const option = document.createElement('option');
            option.value = hermano.nombre;    // El texto que se busca y se muestra
            option.dataset.id = hermano.id; // Guardamos el ID como un atributo data-*
            datalistHermanos.appendChild(option);
        });

        // Configurar los inputs de texto para que usen el datalist y actualicen los campos ocultos
        setupSearchableInput('visitanteNombre', 'visitanteId', 'listaHermanosDatalist');
        setupSearchableInput('visitadoNombre', 'visitadoId', 'listaHermanosDatalist');

    } catch (error) {
        // El error ya se maneja en fetchData, pero podemos añadir un mensaje específico si queremos
        showGlobalMessage('Error crítico al cargar datos para el formulario de visitas.', 'error');
    }
    
    formVisita.addEventListener('submit', async (event) => {
        event.preventDefault();
        // Obtenemos los IDs de los campos OCULTOS
        const visitanteIdValue = document.getElementById('visitanteId').value;
        const visitadoIdValue = document.getElementById('visitadoId').value;

        if (!visitanteIdValue || !visitadoIdValue) {
            showGlobalMessage('Debe seleccionar ambos hermanos de la lista de sugerencias.', 'error');
            return;
        }
        if (visitanteIdValue === visitadoIdValue) {
            showGlobalMessage('El visitante y el visitado no pueden ser la misma persona.', 'error');
            return;
        }

        try {
            const resultado = await fetchData('/visita', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    visitante_id: parseInt(visitanteIdValue), 
                    visitado_id: parseInt(visitadoIdValue) 
                })
            });

            if (resultado.mensaje === "Visita registrada") {
                showGlobalMessage('Visita registrada exitosamente.', 'success');
                // Limpiar los campos de TEXTO y los campos OCULTOS
                document.getElementById('visitanteNombre').value = '';
                document.getElementById('visitadoNombre').value = '';
                document.getElementById('visitanteId').value = ''; 
                document.getElementById('visitadoId').value = '';   
                
                const nuevaVisita = resultado.registro;
                agregarFilaVisita(nuevaVisita, true); 
            } else {
                showGlobalMessage(resultado.error || 'Error al registrar la visita.', 'error');
            }
        } catch (error) {
            // El error ya se maneja en fetchData
        }
    });

    // Cargar visitas del mes actual (esta función no necesita cambios)
    await cargarTablaVisitas();
}

// El resto de tus funciones (cargarTablaVisitas, agregarFilaVisita, etc.) deberían seguir igual.
// Asegúrate también que la función setupSearchableInput esté definida ANTES de ser llamada,
// o colócala en un lugar donde esté accesible globalmente en tu app.js.

async function cargarTablaVisitas() {
    const listaVisitasBody = document.getElementById('listaVisitasBody');
    if(!listaVisitasBody) return;

    listaVisitasBody.innerHTML = '<tr><td colspan="3">Cargando visitas...</td></tr>';

    const hoy = new Date();
    const mesActualTexto = nombresMeses[hoy.getMonth()];
    const anioActual = hoy.getFullYear();

    document.getElementById('tituloMesVisitas').textContent = `Visitas de ${mesActualTexto.charAt(0).toUpperCase() + mesActualTexto.slice(1)} ${anioActual}`;

    try {
        const visitas = await fetchData(`/visitas?mes=${mesActualTexto}&year=${anioActual}`);
        listaVisitasBody.innerHTML = ''; // Limpiar antes de poblar
        if (visitas && visitas.length > 0) {
            visitas.forEach(visita => agregarFilaVisita(visita));
        } else {
            listaVisitasBody.innerHTML = '<tr><td colspan="4">No hay visitas registradas para este mes.</td></tr>';
        }
    } catch (error) {
         listaVisitasBody.innerHTML = '<tr><td colspan="3">Error al cargar visitas.</td></tr>';
    }
}

function agregarFilaVisita(visita, prepend = false) {
    const listaVisitasBody = document.getElementById('listaVisitasBody');
    if (!listaVisitasBody) return;

    const tr = document.createElement('tr');
    // Guardamos el id de la visita en la fila, para poder quitarla fácilmente
    tr.dataset.visitaId = visita.id; 

    const tdFecha = document.createElement('td');
    const fechaObj = new Date(visita.fecha + "T00:00:00"); // Asegurar que se interprete como local
    tdFecha.textContent = `${fechaObj.getDate()} de ${nombresMeses[fechaObj.getMonth()]} de ${fechaObj.getFullYear()}`;

    const tdVisitante = document.createElement('td');
    tdVisitante.textContent = visita.nombre_visitante;

    const tdVisitado = document.createElement('td');
    tdVisitado.textContent = visita.nombre_visitado;

    // --- INICIO: NUEVO CÓDIGO PARA LA CELDA DE ACCIONES Y BOTÓN BORRAR ---
    const tdAcciones = document.createElement('td');
    const btnBorrar = document.createElement('button');
    btnBorrar.textContent = 'Borrar';
    btnBorrar.classList.add('btn', 'btn-danger', 'btn-sm'); // Clases para darle estilo (puedes definir .btn-danger en styles.css)
    btnBorrar.dataset.id = visita.id; // Guardamos el ID de la visita en el botón

    btnBorrar.addEventListener('click', async function() {
        const visitaIdParaBorrar = this.dataset.id;
        // Pedimos confirmación
        if (confirm(`¿Estás seguro de que quieres eliminar esta visita (ID: ${visitaIdParaBorrar})?`)) {
            try {
                const resultado = await fetchData(`/visita/${visitaIdParaBorrar}`, {
                    method: 'DELETE'
                });

                if (resultado && (resultado.mensaje === "Visita eliminada exitosamente" || resultado.id_eliminado)) {
                    showGlobalMessage('Visita eliminada correctamente.', 'success');
                    // Eliminar la fila de la tabla HTML
                    const filaParaEliminar = document.querySelector(`tr[data-visita-id="${visitaIdParaBorrar}"]`);
                    if (filaParaEliminar) {
                        filaParaEliminar.remove();
                    }
                    // Opcional: si la tabla queda vacía después de borrar, mostrar mensaje
                    if (listaVisitasBody.children.length === 0) {
                        listaVisitasBody.innerHTML = `<tr><td colspan="4" style="text-align:center;">No hay visitas registradas para este mes.</td></tr>`;
                    }
                } else {
                    showGlobalMessage(resultado.error || 'Error al eliminar la visita.', 'error');
                }
            } catch (error) {
                // fetchData ya maneja el showGlobalMessage para errores de red/fetch
                console.error('Error en el proceso de eliminación:', error);
            }
        }
    });

    tdAcciones.appendChild(btnBorrar);
    // --- FIN: NUEVO CÓDIGO ---

    tr.appendChild(tdFecha);
    tr.appendChild(tdVisitante);
    tr.appendChild(tdVisitado);
    tr.appendChild(tdAcciones); // Añadimos la nueva celda de acciones a la fila

    const noVisitsRow = listaVisitasBody.querySelector('td[colspan="4"]'); // Asegúrate que el colspan sea 4
    if (noVisitsRow) noVisitsRow.parentElement.remove();

    if (prepend) {
        listaVisitasBody.insertBefore(tr, listaVisitasBody.firstChild);
    } else {
        listaVisitasBody.appendChild(tr);
    }
}


// --- Funciones Específicas para Base de Datos (Hermanos) ---
async function cargarHermanosEnTabla() {
    const tablaHermanosBody = document.getElementById('tablaHermanosBody');
    if (!tablaHermanosBody) return;

    tablaHermanosBody.innerHTML = '<tr><td colspan="4">Cargando hermanos...</td></tr>';
    try {
        const hermanos = await fetchData('/hermanos');
        tablaHermanosBody.innerHTML = ''; // Limpiar
        if (hermanos && hermanos.length > 0) {
            hermanos.forEach(hermano => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="text-align: right;">${hermano.id}</td>
                    <td>${hermano.nombre}</td>
                    <td style="text-align: center;">${hermano.sexo || 'N/A'}</td>
                    <td>${hermano.otros_campos || ''}</td>
                `;
                tablaHermanosBody.appendChild(tr);
            });
        } else {
            tablaHermanosBody.innerHTML = '<tr><td colspan="4">No hay hermanos registrados.</td></tr>';
        }
    } catch (error) {
        tablaHermanosBody.innerHTML = '<tr><td colspan="4">Error al cargar hermanos.</td></tr>';
    }

    // Lógica para agregar hermano (opcional)
    const formAgregarHermano = document.getElementById('formAgregarHermano');
    if (formAgregarHermano) {
        formAgregarHermano.addEventListener('submit', async (event) => {
            event.preventDefault();
            // ESTO ES LO CORRECTO
            const nombre = document.getElementById('nombreHermanoNuevo').value;
            const sexo = document.getElementById('sexoHermanoNuevo').value;
            const otros = document.getElementById('otrosCamposHermanoNuevo').value;

            if (!nombre) {
                showGlobalMessage('El nombre es requerido.', 'error');
                return;
            }

            try {
                const resultado = await fetchData('/hermano', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nombre, sexo, otros_campos: otros })
                });
                if (resultado.id) {
                    showGlobalMessage('Hermano agregado exitosamente.', 'success');
                    formAgregarHermano.reset();
                    cargarHermanosEnTabla(); // Recargar la tabla
                } else {
                    showGlobalMessage(resultado.error || 'Error al agregar hermano.', 'error');
                }
            } catch (error) {
                // Mensaje ya mostrado por fetchData
            }
        });
    }
}


// --- Inicialización General y Navegación ---
document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;
    createGlobalMessageContainer(); // Crear el contenedor de mensajes globales una vez

    if (path.endsWith('asistencia.html') || path.includes('/asistencia')) {
        cargarAsistencias();
        document.querySelector('nav a[href="asistencia.html"]').classList.add('active');
    } else if (path.endsWith('visitas.html') || path.includes('/visitas')) {
        cargarFormularioYListaVisitas();
        document.querySelector('nav a[href="visitas.html"]').classList.add('active');
    } else if (path.endsWith('base_datos.html') || path.includes('/base_datos')) {
        cargarHermanosEnTabla();
        document.querySelector('nav a[href="base_datos.html"]').classList.add('active');
    } else if (path.endsWith('index.html') || path === '/' || path.endsWith('/frontend/')) {
         if(document.querySelector('nav a[href="index.html"]')) { // Puede no existir si se sirve desde Flask /
            document.querySelector('nav a[href="index.html"]').classList.add('active');
         }
    }
});
// --- Lógica para el Modo Oscuro ---
const darkModeToggle = document.getElementById('darkModeToggle');
const cuerpoDocumento = document.body; // O document.documentElement para <html>

if (darkModeToggle) {
    // Comprobar si hay una preferencia guardada en localStorage
    if (localStorage.getItem('darkMode') === 'enabled') {
        cuerpoDocumento.classList.add('dark-mode');
        darkModeToggle.textContent = 'Modo Claro'; // Actualizar texto del botón
    }

    darkModeToggle.addEventListener('click', () => {
        cuerpoDocumento.classList.toggle('dark-mode');

        // Guardar preferencia en localStorage y actualizar texto del botón
        if (cuerpoDocumento.classList.contains('dark-mode')) {
            localStorage.setItem('darkMode', 'enabled');
            darkModeToggle.textContent = 'Modo Claro';
        } else {
            localStorage.setItem('darkMode', 'disabled');
            darkModeToggle.textContent = 'Modo Oscuro';
        }
    });
}