import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def parse_html_blocking(html_content: str, url: str) -> dict:
    """
    Esta función se ejecuta en un hilo separado para no bloquear asyncio.
    Realiza el parseo CPU-bound usando BeautifulSoup.
    """
    try:
        print(f"[Servidor A] Iniciando parseo (en thread) para {url}")
        soup = BeautifulSoup(html_content, 'lxml') 

        # 1. Título
        title = soup.title.string.strip() if soup.title else "Sin Título"

        # 2. Enlaces
        links = set()
        for a_tag in soup.find_all('a', href=True):
            full_url = urljoin(url, a_tag['href'])
            links.add(full_url)
        
        # 3. Meta tags
        meta_tags = {}
        common_names = ['description', 'keywords']
        for name in common_names:
            meta = soup.find('meta', attrs={'name': name})
            if meta and meta.get('content'):
                meta_tags[name.lower()] = meta['content']
        
        og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
        for tag in og_tags:
            meta_tags[tag.get('property')] = tag.get('content')

        # 4. Imágenes
        image_urls = []
        for img_tag in soup.find_all('img', src=True):
            img_src = urljoin(url, img_tag['src'])
            image_urls.append(img_src)
        
        images_count = len(image_urls)

        # 5. Estructura (H1-H6)
        structure = {}
        for i in range(1, 7):
            tag = f'h{i}'
            structure[tag] = len(soup.find_all(tag))

        print(f"[Servidor A] Parseo (en thread) terminado para {url}")
        return {
            "title": title,
            "links": list(links),
            "meta_tags": meta_tags,
            "images_count": images_count,
            "image_urls": image_urls, 
            "structure": structure
        }
    except Exception as e:
        print(f"[Servidor A] Error de parseo: {e}")
        raise Exception(f"Error parseando HTML: {str(e)}")


async def perform_local_scraping(url: str) -> dict:
    """
    Realiza el scraping HTML asíncrono (Parte A, Tarea 1).
    Usa aiohttp (I/O) y BeautifulSoup (en un thread).
   
    """
    print(f"[Servidor A] Iniciando scraping real para: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    try:
        # 1. Descarga (I/O Asíncrono)
        async with ClientSession(headers=headers) as session:
            async with session.get(url, timeout=30) as response:
                response.raise_for_status() 
                html_content = await response.text()
        
        print(f"[Servidor A] Descarga de {url} completa ({len(html_content)} bytes)")
        
        # 2. Parseo (CPU-Bound, movido a un thread)
        #
        parsing_results = await asyncio.to_thread(parse_html_blocking, html_content, url)
        
        print(f"[Servidor A] Parseo de {url} terminado.")
        return parsing_results

    except asyncio.TimeoutError:
        print(f"[Servidor A] Timeout scraping {url}")
        raise Exception(f"Timeout al scrapear {url} (max 30s)")
    except Exception as e:
        print(f"[Servidor A] Error en scraping real: {e}")
        raise