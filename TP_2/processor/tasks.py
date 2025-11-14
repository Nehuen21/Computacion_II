import os
import time
import base64
import io

# Importaciones para tareas reales
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image
import requests 

def run_heavy_processing(url: str, image_urls: list) -> dict:
    """
    Función que se ejecuta en un PROCESO SEPARADO.
    Implementa las tareas reales de procesamiento pesado.
   
    """
    pid = os.getpid()
    print(f"[Servidor B - PID: {pid}] Iniciando PROCESAMIENTO REAL para: {url}")

    # --- Configuración de Selenium ---
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument("--disable-gpu") 
    
    driver = None
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=chrome_options
        )
        driver.set_page_load_timeout(30) 
    except Exception as e:
        print(f"[Servidor B - PID: {pid}] ERROR: No se pudo iniciar Selenium.")
        print(f"[Servidor B - PID: {pid}] {e}")
        raise Exception(f"No se pudo iniciar Selenium/ChromeDriver: {e}")

    screenshot_base64 = None
    performance_data = {}
    thumbnails_base64 = []

    try:
        # --- 1. Screenshot y 2. Performance (Selenium) ---
        driver.get(url)

        # Performance (via JavaScript Navigation Timing API)
        try:
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            nav_timing = driver.execute_script("return window.performance.timing;")
            nav_start = nav_timing['navigationStart']
            
            if nav_timing['loadEventEnd'] > 0 and nav_start > 0:
                load_time_ms = nav_timing['loadEventEnd'] - nav_start
            else:
                load_time_ms = (time.time() * 1000) - (nav_start if nav_start > 0 else (time.time() * 1000))
                
            performance_data = {
                "load_time_ms": int(load_time_ms),
                "total_size_kb": -1, 
                "num_requests": -1   
            }
        except Exception as e:
            print(f"[Servidor B - PID: {pid}] Error midiendo performance: {e}")
            performance_data = {"error": str(e), "load_time_ms": -1}

        # Screenshot
        png_data = driver.get_screenshot_as_png()
        screenshot_base64 = base64.b64encode(png_data).decode('utf-8')
        print(f"[Servidor B - PID: {pid}] Screenshot capturado ({len(png_data)} bytes)")

    except Exception as e:
        print(f"[Servidor B - PID: {pid}] Error grave en Selenium al cargar {url}: {e}")
        if not performance_data: 
            performance_data = {"error": f"Error de Selenium: {e}", "load_time_ms": -1}
    finally:
        if driver:
            driver.quit() 

    # --- 3. Thumbnails (Pillow) ---
    print(f"[Servidor B - PID: {pid}] Iniciando procesamiento de {len(image_urls[:5])} thumbnails...")
    
    for img_url in image_urls[:5]:
        try:
            img_response = requests.get(img_url, timeout=10)
            img_response.raise_for_status()
            
            img_file = io.BytesIO(img_response.content)
            img = Image.open(img_file).convert("RGB") 
            
            img.thumbnail((100, 100))
            
            thumb_buffer = io.BytesIO()
            img.save(thumb_buffer, format="PNG") 
            
            thumb_base64 = base64.b64encode(thumb_buffer.getvalue()).decode('utf-8')
            thumbnails_base64.append(thumb_base64)
            
        except Exception as e:
            print(f"[Servidor B - PID: {pid}] No se pudo procesar imagen {img_url}: {e}")
            pass 

    print(f"[Servidor B - PID: {pid}] Procesamiento REAL terminado para: {url}")
    
    return {
        "screenshot": screenshot_base64,
        "performance": performance_data,
        "thumbnails": thumbnails_base64,
        "processed_by_pid": pid
    }