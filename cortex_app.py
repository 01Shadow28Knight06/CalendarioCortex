import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURACIÓN DE BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('cortex_v2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tareas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  actividad TEXT, 
                  prioridad TEXT, 
                  fecha DATE, 
                  estado TEXT)''')
    conn.commit()
    conn.close()

def add_task(t, p, f):
    conn = sqlite3.connect('cortex_v2.db')
    c = conn.cursor()
    c.execute("INSERT INTO tareas (actividad, prioridad, fecha, estado) VALUES (?,?,?,?)",
              (t, p, f, 'PENDIENTE'))
    conn.commit()
    conn.close()

def complete_task(id_tarea):
    conn = sqlite3.connect('cortex_v2.db')
    c = conn.cursor()
    c.execute("UPDATE tareas SET estado = 'COMPLETADO' WHERE id = ?", (id_tarea,))
    conn.commit()
    conn.close()

# --- 2. INTERFAZ DE USUARIO (STREAMLIT) ---
st.set_page_config(page_title="Córtex Exógeno v.2.0", layout="wide")
init_db()

st.title("📂 Sistema de Gestión de Realidad")
st.markdown("---")

# Barra Lateral: Entrada de Datos
with st.sidebar:
    st.header("📥 Inyectar Comando")
    nueva_tarea = st.text_input("¿Qué hay que hacer?")
    prioridad = st.selectbox("Nivel de Impacto:", ["1-CRÍTICO", "2-EVOLUTIVO", "3-MANTENIMIENTO"])
    fecha_limite = st.date_input("Fecha Objetivo:", datetime.now())
    
    if st.button("Registrar en Memoria"):
        if nueva_tarea:
            add_task(nueva_tarea, prioridad, fecha_limite)
            st.success("Dato Persistido")
        else:
            st.error("Error: Campo vacío")

# Cuerpo Principal: Visualización y Acción
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Matriz de Ejecución")
    conn = sqlite3.connect('cortex_v2.db')
    # Ordenamos por prioridad (Crítico primero) y luego fecha
    df = pd.read_sql_query("SELECT * FROM tareas WHERE estado = 'PENDIENTE' ORDER BY prioridad ASC, fecha ASC", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df.drop(columns=['id']), use_container_width=True)
    else:
        st.info("Sistema en reposo. No hay tareas pendientes.")

with col2:
    st.subheader("✅ Finalizar Tarea")
    if not df.empty:
        tarea_a_completar = st.selectbox("Seleccionar ID para colapsar:", df['id'])
        if st.button("Marcar como HECHO"):
            complete_task(tarea_a_completar)
            st.rerun()
    else:
        st.write("Nada que procesar.")

# Historial de Éxitos
with st.expander("Ver Log de Tareas Completadas"):
    conn = sqlite3.connect('cortex_v2.db')
    df_done = pd.read_sql_query("SELECT * FROM tareas WHERE estado = 'COMPLETADO'", conn)
    conn.close()
    st.table(df_done)