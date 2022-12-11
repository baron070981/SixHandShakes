import requests
from pathlib import Path
from PIL import ImageTk, Image
import tkinter as tk


# def update_subwindow(self, file_path, text):
    # self.img_obj = ImageTk.PhotoImage(Image.open(file_path))
    # self.panel.configure(image = self.img_obj)
    # self.panel2.configure(text = text)
    # self.panel.image = self.img_obj
    # self.panel2.text = text





class CaptchaImage:
    
    def __init__(self, window_name='captcha'):
        self.image_content = None
        self.tempfilename = None
    
    
    def get_source(self, url):
        self.image_content = requests.get(url).content
        end = 'jpg'
        self.write_temp_file(end, self.image_content)
    
    
    def load_img(self, url, file_extension, *args):
        if not self.image_content:
            raise Exception("Нет данных изображеия")
    
    
    def write_temp_file(self, end, content):
        self.tempfilename = Path(f'temp.{end}')
        with open(str(self.tempfilename), 'wb') as f:
            f.write(content)

    def get_image(self):
        image = Image.open(str(self.tempfilename))
        image = ImageTk.PhotoImage(image)
        return image
    
    def show_captcha(self, url):
        root = tk.Tk()
        canvas = tk.Canvas(root)
        self.get_source(url)
        image = self.get_image()
        canvas.create_image(100, 100, anchor='nw',image=image)
        canvas.pack()
        root.mainloop()



if __name__ == "__main__":
    ...
    
    







