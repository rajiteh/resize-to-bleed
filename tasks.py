from invoke import task
from PIL import Image
import glob
import os

import multiprocessing
from itertools import product



@task
def process(ctx, image_glob, template, output_dir, preserve_dir=True, bleed_size=140):
  tpl = Image.open(template, 'r')
  tpl_h, tpl_w = tpl.size
  content_size = (tpl_h - bleed_size * 2, tpl_w - bleed_size * 2)

  image_paths = glob.glob(image_glob)
  with multiprocessing.Pool(processes=multiprocessing.cpu_count() * 2) as pool:
    results = pool.starmap(process_image, [(image, tpl, content_size, output_dir, preserve_dir, bleed_size)
                                          for image in image_paths])

def process_image(image_path, tpl, content_size, output_dir, preserve_dir, bleed_size):
  img = Image.open(image_path, 'r')
  print("Resizing {}".format(image_path))
  assert img.info['dpi'] == (300, 300) # sanity
  img = img.resize(content_size)
  new_img = tpl.copy()
  new_img.paste(img, (bleed_size, bleed_size))

  # change extension to png
  image_path = os.path.splitext(image_path)[0] + '.png'
  output_path = os.path.join(output_dir, image_path if preserve_dir else os.path.basename(image_path))
  os.makedirs(os.path.dirname(output_path), exist_ok=True)
  new_img.save(output_path)
  print("Saved {}".format(output_path))
