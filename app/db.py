import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "purabali")
    )

def fetch_pura_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            p.id_pura, p.nama_pura, p.deskripsi_singkat, p.tahun_berdiri,
            p.link_lokasi, p.link_gambar,
            j.nama_jenis_pura, k.nama_kabupaten
        FROM pura p
        LEFT JOIN jenis_pura j ON p.id_jenis_pura = j.id_jenis_pura
        LEFT JOIN kabupaten k ON p.id_kabupaten = k.id_kabupaten
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
