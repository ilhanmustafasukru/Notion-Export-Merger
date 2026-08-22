import os
import base64
import mimetypes
import zipfile
import tempfile
import urllib.parse
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from bs4 import BeautifulSoup

def image_to_base64(img_path):
    """Converts a local image file to a base64 inline data URI."""
    if not img_path.exists(): return None
    mime_type, _ = mimetypes.guess_type(str(img_path))
    if not mime_type: mime_type = "image/png"
    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"

def embed_content_recursively(file_path, visited):
    """Recursively parses HTML, embeds images, and appends subpage content to the bottom of the document."""
    if file_path in visited:
        return None
    visited.add(file_path)
    
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
    # 1. Embed Images
    for img in soup.find_all("img"):
        src = img.get("src")
        if src and not src.startswith("http") and not src.startswith("data:"):
            clean_src = urllib.parse.unquote(src)
            img_path = (file_path.parent / clean_src).resolve()
            b64_data = image_to_base64(img_path)
            if b64_data:
                img["src"] = b64_data

    # Container to hold all subpages so we can append them at the end
    subpages_to_append = []

    # 2. Hunt down links, convert to anchors, and extract subpages
    for a in soup.find_all("a", href=True):
        href = a['href']
        if href.endswith(".html") and not href.startswith("http"):
            clean_href = urllib.parse.unquote(href)
            child_path = (file_path.parent / clean_href).resolve()
            
            if child_path.exists():
                child_soup = embed_content_recursively(child_path, visited)
                if child_soup:
                    child_content = child_soup.find("article") or child_soup.find("body")
                    if child_content:
                        section_id = child_path.stem
                        # Change the link to an internal jump link
                        a['href'] = f"#{section_id}"
                        
                        # Wrap the injected content and save it to our container
                        wrapper = soup.new_tag("div", id=section_id, style="margin-top: 60px; padding-top: 20px; border-top: 3px double #ccc;")
                        wrapper.extend(child_content.contents)
                        subpages_to_append.append(wrapper)

    # 3. Append all collected subpages at the very bottom of the current page
    if subpages_to_append:
        main_content = soup.find("article") or soup.find("body")
        if main_content:
            for wrapper in subpages_to_append:
                main_content.append(wrapper)

    return soup

def extract_all_nested_zips(base_dir):
    """Recursively finds and extracts any zip files hiding within the base directory."""
    extracted_something = True
    while extracted_something:
        extracted_something = False
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith('.zip'):
                    zip_path = os.path.join(root, file)
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as inner_zip:
                            inner_zip.extractall(root)
                        os.remove(zip_path)
                        extracted_something = True
                    except Exception as e:
                        print(f"Skipping problematic zip: {zip_path} - {e}")
                    
                    if extracted_something:
                        break
            if extracted_something:
                break

def process_export():
    root = tk.Tk()
    root.withdraw()
    
    zip_path = filedialog.askopenfilename(title="1. Select Notion Export ZIP", filetypes=[("ZIP files", "*.zip")])
    if not zip_path: return

    output_path = filedialog.asksaveasfilename(title="2. Save Combined HTML As", defaultextension=".html", filetypes=[("HTML files", "*.html")])
    if not output_path: return

    status = tk.Toplevel(root)
    status.title("Processing Document")
    status.geometry("350x120")
    status.attributes('-topmost', True) 
    tk.Label(status, text="Extracting nested ZIPs and injecting pages...\nThis may take a minute. Please wait.", font=("Arial", 11), pady=30).pack()
    status.update()

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the master zip
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                
            # Drill through any inner zip files
            extract_all_nested_zips(temp_dir)
            
            temp_path = Path(temp_dir)
            
            # Smart file hunt
            all_html_files = list(temp_path.rglob("*.html"))
            if not all_html_files:
                raise ValueError("Could not find any HTML files inside the ZIP or nested ZIPs.")
            
            main_file = min(all_html_files, key=lambda p: len(p.parts))
            
            visited = set()
            master_soup = embed_content_recursively(main_file, visited)
            
            if master_soup:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(str(master_soup))
                
                status.destroy()
                messagebox.showinfo("Success", f"Process complete!\n\nDocument successfully saved to:\n{output_path}")
            else:
                raise ValueError("Parsed document returned empty.")

    except Exception as e:
        status.destroy()
        error_msg = f"The script failed to process the document.\n\nError details:\n{str(e)}"
        messagebox.showerror("Process Failed", error_msg)
    finally:
        root.destroy()

if __name__ == "__main__":
    process_export()