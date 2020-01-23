from IPython.nbformat.v4.nbbase import new_code_cell, new_notebook
import IPython.nbformat as nbf
import argparse
import codecs
import os

if not os.path.exists('files_generated'):
    os.makedirs('files_generated')
    
ap = argparse.ArgumentParser()
ap.add_argument("-nb", "--ipynb", type=str, default="files_generated/assignment.ipynb",
    help="name of exported python notebook")
ap.add_argument("-py", "--py_file", type=str, default="files_generated/extracted_python_file.py",
    help="name of python file generated")
args = vars(ap.parse_args())

python_file = args["py_file"]
python_notebook_name = args["ipynb"]

with open(python_file) as f:
    data = f.read().split('\n')

# Convert python file to python notebook
def write_to_python_notebook():
    cells = []
    for index, text in enumerate(data):
        cells.append(new_code_cell(
            source=text,
            execution_count=index,
        ))
    nb0 = new_notebook(cells=cells,
        metadata={
            'language': 'python',
        })
    f = codecs.open(python_notebook_name, encoding='utf-8', mode='w')
    nbf.write(nb0, f, 4)
    f.close()

print(f"[INFO] Writing extracted text to notebook: {python_notebook_name}")
write_to_python_notebook()
print("Done!")