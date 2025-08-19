PDF Tool - Kivy Android App (all-in-one, aesthetic)

Filename: main.py

Requirements (install before building):

pip install kivy pypdf pillow pymupdf

NOTE: On Android/Kivy build some packages (pymupdf) may need special handling.

This app provides: Merge, Split, Extract Images, Encrypt (set password), Decrypt (remove password)

from kivy.app import App from kivy.lang import Builder from kivy.uix.boxlayout import BoxLayout from kivy.uix.popup import Popup from kivy.uix.label import Label from kivy.properties import ListProperty, StringProperty from kivy.core.window import Window from kivy.utils import platform import os from datetime import datetime

Try import PDF libraries

try: from pypdf import PdfReader, PdfWriter, PdfMerger PYPDF_AVAILABLE = True except Exception as e: PYPDF_AVAILABLE = False

Try PyMuPDF for robust image extraction

try: import fitz  # PyMuPDF PYMUPDF_AVAILABLE = True except Exception: PYMUPDF_AVAILABLE = False

Pillow for fallback image handling

try: from PIL import Image PIL_AVAILABLE = True except Exception: PIL_AVAILABLE = False

KV = ''' <MainLayout>: orientation: 'vertical' padding: dp(12) spacing: dp(12)

BoxLayout:
    size_hint_y: None
    height: dp(56)
    canvas.before:
        Color:
            rgba: .06,.12,.24,1
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        text: 'PDF Toolkit — Ətraflı və Pulsuz'
        color: 1,1,1,1
        bold: True
        font_size: '18sp'

BoxLayout:
    size_hint_y: None
    height: dp(56)
    spacing: dp(8)
    Button:
        text: 'Fayl seç'
        on_release: root.open_filechooser()
    Button:
        text: 'Merge (Birləşdir)'
        on_release: root.merge_selected()
    Button:
        text: 'Split (Ayır)'
        on_release: root.split_selected()

BoxLayout:
    size_hint_y: None
    height: dp(56)
    spacing: dp(8)
    Button:
        text: 'Extract Images (Şəkilləri çıxar)'
        on_release: root.extract_images()
    Button:
        text: 'Encrypt (Parol qoy)'
        on_release: root.encrypt_pdf()
    Button:
        text: 'Decrypt (Parolu sil)'
        on_release: root.decrypt_pdf()

Label:
    text: 'Seçilmiş fayllar:'
    size_hint_y: None
    height: dp(24)

BoxLayout:
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: 0.95,0.95,0.95,1
        Rectangle:
            pos: self.pos
            size: self.size
    ScrollView:
        do_scroll_x: False
        BoxLayout:
            id: files_box
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height

Label:
    text: root.log_text
    size_hint_y: None
    height: dp(120)
    text_size: self.width - dp(20), None
    valign: 'top'
    halign: 'left'
    canvas.before:
        Color:
            rgba: 0,0,0,0.03
        Rectangle:
            pos: self.pos
            size: self.size

'''

class MainLayout(BoxLayout): selected_files = ListProperty([]) log_text = StringProperty('Ready.')

def __init__(self, **kwargs):
    super().__init__(**kwargs)
    Window.bind(on_dropfile=self._on_file_drop)

def _on_file_drop(self, window, file_path):
    try:
        path = file_path.decode('utf-8')
    except Exception:
        path = str(file_path)
    if os.path.isfile(path) and path.lower().endswith('.pdf'):
        self.selected_files.append(path)
        self.update_files_box()
        self.log(f'File added: {os.path.basename(path)}')

def open_filechooser(self):
    # Simple file chooser: ask user to paste path because mobile FileChooser is flaky in some builds.
    content = BoxLayout(orientation='vertical', spacing=8)
    input_label = Label(text='Faylın tam yolunu daxil et (və ya Termux storage: /storage/emulated/0/Download/file.pdf)')
    from kivy.uix.textinput import TextInput
    ti = TextInput(multiline=False)
    btn_box = BoxLayout(size_hint_y=None, height=36, spacing=8)
    from kivy.uix.button import Button
    ok = Button(text='Əlavə et')
    cancel = Button(text='İmtina')
    btn_box.add_widget(ok)
    btn_box.add_widget(cancel)
    content.add_widget(input_label)
    content.add_widget(ti)
    content.add_widget(btn_box)
    popup = Popup(title='Fayl seç', content=content, size_hint=(.95, .4))

    def do_add(instance):
        path = ti.text.strip()
        if os.path.isfile(path) and path.lower().endswith('.pdf'):
            self.selected_files.append(path)
            self.update_files_box()
            self.log(f'Added: {path}')
            popup.dismiss()
        else:
            self.log('Fayl tapılmadı və ya PDF deyil.')

    ok.bind(on_release=do_add)
    cancel.bind(on_release=lambda *a: popup.dismiss())
    popup.open()

def update_files_box(self):
    fb = self.ids.files_box
    fb.clear_widgets()
    from kivy.uix.button import Button
    for f in self.selected_files:
        btn = Button(text=os.path.basename(f), size_hint_y=None, height=36)
        def make_rm(path):
            def rm(_):
                try:
                    self.selected_files.remove(path)
                    self.update_files_box()
                    self.log(f'Removed: {os.path.basename(path)}')
                except ValueError:
                    pass
            return rm
        btn.bind(on_release=make_rm(f))
        fb.add_widget(btn)

def log(self, msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    self.log_text = f'[{ts}] {msg}\n' + self.log_text

# --- PDF FUNCTIONS ---
def merge_selected(self):
    if not PYPDF_AVAILABLE:
        self.log('pypdf kitabxanası yoxdur. `pip install pypdf`')
        return
    if len(self.selected_files) < 2:
        self.log('Merge üçün ən azı 2 PDF seçin.')
        return
    out = self._default_output('merged')
    try:
        merger = PdfMerger()
        for p in self.selected_files:
            merger.append(p)
        merger.write(out)
        merger.close()
        self.log(f'Merge uğurlu: {out}')
    except Exception as e:
        self.log('Merge xətası: ' + str(e))

def split_selected(self):
    if not PYPDF_AVAILABLE:
        self.log('pypdf yoxdur. `pip install pypdf`')
        return
    if len(self.selected_files) != 1:
        self.log('Split üçün yalnız 1 PDF seçin (sonra bütün səhifələri ayrı-sıra çıxaracaq).')
        return
    src = self.selected_files[0]
    try:
        reader = PdfReader(src)
        base = os.path.splitext(os.path.basename(src))[0]
        out_dir = os.path.join(os.path.dirname(src), base + '_splitted')
        os.makedirs(out_dir, exist_ok=True)
        for i, page in enumerate(reader.pages, start=1):
            writer = PdfWriter()
            writer.add_page(page)
            out_path = os.path.join(out_dir, f'{base}_page_{i}.pdf')
            with open(out_path, 'wb') as f:
                writer.write(f)
        self.log(f'Split tamamlandı. Qovluq: {out_dir}')
    except Exception as e:
        self.log('Split xətası: ' + str(e))

def extract_images(self):
    if not self.selected_files:
        self.log('Şəkil çıxarmaq üçün ən azı 1 PDF seçin.')
        return
    src = self.selected_files[0]
    out_dir = os.path.join(os.path.dirname(src), os.path.splitext(os.path.basename(src))[0] + '_images')
    os.makedirs(out_dir, exist_ok=True)
    extracted = 0
    try:
        if PYMUPDF_AVAILABLE:
            doc = fitz.open(src)
            for i in range(len(doc)):
                for img_index, img in enumerate(doc.get_page_images(i), start=1):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    ext = 'png' if pix.alpha else 'jpg'
                    fn = os.path.join(out_dir, f'page{i+1}_img{img_index}.{ext}')
                    if pix.alpha:
                        pix.save(fn)
                    else:
                        pix.save(fn)
                    extracted += 1
            self.log(f'Images extracted: {extracted} -> {out_dir}')
            return
        # Fallback: try pypdf raw XObject extraction
        if PYPDF_AVAILABLE:
            reader = PdfReader(src)
            for pnum, page in enumerate(reader.pages, start=1):
                try:
                    resources = page.get('/Resources')
                    if not resources:
                        continue
                    xobj = resources.get('/XObject')
                    if not xobj:
                        continue
                    for name, obj in xobj.items():
                        data = obj.get_data()
                        filt = obj.get('/Filter')
                        # try to infer extension
                        if filt and '/DCTDecode' in str(filt):
                            ext = 'jpg'
                        else:
                            ext = 'png'
                        fn = os.path.join(out_dir, f'page{pnum}_{name[1:]}.{ext}')
                        with open(fn, 'wb') as f:
                            f.write(data)
                        extracted += 1
                except Exception:
                    continue
            self.log(f'Extract fallback done. Found: {extracted} images in {out_dir}')
            return
        self.log('Şəkil çıxarma üçün ən azı pypdf və ya pymupdf lazımdır (pypdf daha sadə, pymupdf daha güclü).')
    except Exception as e:
        self.log('Extract xətası: ' + str(e))

def encrypt_pdf(self):
    if not PYPDF_AVAILABLE:
        self.log('pypdf yoxdur. `pip install pypdf`')
        return
    if len(self.selected_files) != 1:
        self.log('Encrypt üçün 1 PDF seçin.')
        return
    src = self.selected_files[0]
    from kivy.uix.popup import Popup
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.textinput import TextInput
    from kivy.uix.button import Button
    content = BoxLayout(orientation='vertical', spacing=8)
    ti = TextInput(password=True, multiline=False)
    btn = Button(text='Set Password', size_hint_y=None, height=36)
    content.add_widget(Label(text='Yeni parolu daxil et:'))
    content.add_widget(ti)
    content.add_widget(btn)
    popup = Popup(title='Encrypt PDF', content=content, size_hint=(.9, .4))

    def do_encrypt(instance):
        pwd = ti.text.strip()
        if not pwd:
            self.log('Parol boş ola bilməz.')
            return
        try:
            reader = PdfReader(src)
            writer = PdfWriter()
            for p in reader.pages:
                writer.add_page(p)
            writer.encrypt(pwd)
            out = self._default_output('encrypted')
            with open(out, 'wb') as f:
                writer.write(f)
            self.log(f'Encrypted -> {out}')
            popup.dismiss()
        except Exception as e:
            self.log('Encrypt error: ' + str(e))
    btn.bind(on_release=do_encrypt)
    popup.open()

def decrypt_pdf(self):
    if not PYPDF_AVAILABLE:
        self.log('pypdf yoxdur. `pip install pypdf`')
        return
    if len(self.selected_files) != 1:
        self.log('Decrypt üçün 1 PDF seçin.')
        return
    src = self.selected_files[0]
    from kivy.uix.popup import Popup
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.textinput import TextInput
    from kivy.uix.button import Button
    content = BoxLayout(orientation='vertical', spacing=8)
    ti = TextInput(password=True, multiline=False)
    btn = Button(text='Unlock', size_hint_y=None, height=36)
    content.add_widget(Label(text='PDF parolunu daxil et:'))
    content.add_widget(ti)
    content.add_widget(btn)
    popup = Popup(title='Decrypt PDF', content=content, size_hint=(.9, .4))

    def do_decrypt(instance):
        pwd = ti.text.strip()
        try:
            reader = PdfReader(src)
            if reader.is_encrypted:
                success = reader.decrypt(pwd)
                if success == 0:
                    self.log('Parol səhvdir.')
                    return
            writer = PdfWriter()
            for p in reader.pages:
                writer.add_page(p)
            out = self._default_output('decrypted')
            with open(out, 'wb') as f:
                writer.write(f)
            self.log(f'Decrypted -> {out}')
            popup.dismiss()
        except Exception as e:
            self.log('Decrypt xətası: ' + str(e))
    btn.bind(on_release=do_decrypt)
    popup.open()

def _default_output(self, tag):
    base_dir = self.selected_files[0] if self.selected_files else os.getcwd()
    if os.path.isfile(base_dir):
        base_dir = os.path.dirname(base_dir)
    fn = os.path.join(base_dir, f'pdftool_{tag}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
    return fn

class PDFToolApp(App): def build(self): self.title = 'PDF Toolkit' return Builder.load_string(KV)

if name == 'main': if not PYPDF_AVAILABLE: print('Warning: pypdf not installed. Install with pip install pypdf') if not PYMUPDF_AVAILABLE: print('PyMuPDF not installed. Image extraction fallback will be used if possible.') PDFToolApp().run()

