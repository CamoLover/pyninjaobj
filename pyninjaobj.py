# The MIT License (MIT)

# Copyright (c) 2015 Luke Gaynor

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import Text


from collections import namedtuple
import struct
import array
import os

HEADER = """# Converted with NinjaRip-2 Converter"""

DEFAULT_MAT = """Ka 0.000000 0.000000 0.000000\nKd 0.376320 0.376320 0.376320\nKs 0.000000 0.000000 0.000000"""

class Vector3():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Vector2():
    def __init__(self, u, v):
        self.u = u
        self.v = v

def read_str(filehandle):
    buf = b''
    while True:
        byte = filehandle.read(1)
        if byte != b'\0':
            buf += byte
        else:
            break
    return buf.decode("ASCII")

class RipMesh():
    def __init__(self, ripfile):
        v_idx = Vector3(0, 0, 0)
        vn_idx = Vector3(0, 0, 0)
        vt_idx = Vector2(0, 0)

        rip = open(ripfile, "rb")

        info_header = array.array("L")
        info_header.fromfile(rip, 8)

        signature = info_header[0]
        version = info_header[1]
        face_count = info_header[2]
        vertex_count = info_header[3]
        vertex_size = info_header[4]
        texture_file_count = info_header[5]
        shader_file_count = info_header[6]
        vertex_attribute_count = info_header[7]

        if signature != 0xDEADC0DE:
            raise NotImplementedError("Sorry, this file signature isn't recognized.")

        if version != 4:
            print("Warning: This tool was written for version 4 .rip files, not version", version)

        pos_idx = 0
        normal_idx = 0
        uv_idx = 0

        vertex_attrib_types = []

        for i in range(0, vertex_attribute_count):
            attrib_type = read_str(rip)

            attrib_info = array.array("L")
            attrib_info.fromfile(rip, 4)

            attrib_idx = attrib_info[0]
            attrib_offset = attrib_info[1]
            attrib_size = attrib_info[2]
            attrib_element_count = attrib_info[3]

            vertex_attrib = array.array("L")
            vertex_attrib.fromfile(rip, attrib_element_count)

            vertex_attrib_types.extend(vertex_attrib)

            if attrib_type == "POSITION" and pos_idx == 0:
                v_idx.x = attrib_offset // 4
                v_idx.y = v_idx.x + 1
                v_idx.z = v_idx.x + 2
                pos_idx += 1

            elif attrib_type == "NORMAL" and normal_idx == 0:
                vn_idx.x = attrib_offset // 4
                vn_idx.y = vn_idx.x + 1
                vn_idx.z = vn_idx.x + 2
                normal_idx += 1

            elif attrib_type == "TEXCOORD" and uv_idx == 0:
                vt_idx.u = attrib_offset // 4
                vt_idx.v = vt_idx.u + 1
                uv_idx += 1

        self.texture_files = []
        for i in range(0, texture_file_count):
            self.texture_files.append(read_str(rip))

        self.shader_files = []
        for i in range(0, shader_file_count):
            self.shader_files.append(read_str(rip))

        self.faces = []
        for x in range(0, face_count):
            face = array.array("L")
            face.fromfile(rip, 3)
            self.faces.append(face)

        self.vertices = []
        self.normals = []
        self.texcoords = []

        for i in range(0, vertex_count):
            v = Vector3(0, 0, 0)
            vn = Vector3(0, 0, 0)
            vt = Vector2(0, 0)

            for j, element_type in enumerate(vertex_attrib_types):
                pos = 0

                if element_type == 0:
                    pos, = struct.unpack("f", rip.read(struct.calcsize("f")))
                elif element_type == 1:
                    pos, = struct.unpack("L", rip.read(struct.calcsize("L")))
                elif element_type == 2:
                    pos, = struct.unpack("l", rip.read(struct.calcsize("l")))

                if j == v_idx.x:
                    v.x = pos
                elif j == v_idx.y:
                    v.y = pos
                elif j == v_idx.z:
                    v.z = pos
                elif j == vn_idx.x:
                    vn.x = pos
                elif j == vn_idx.y:
                    vn.y = pos
                elif j == vn_idx.z:
                    vn.z = pos
                elif j == vt_idx.u:
                    vt.u = pos
                elif j == vt_idx.v:
                    vt.v = 1 - pos

            self.vertices.append(v)
            self.normals.append(vn)
            self.texcoords.append(vt)

        rip.close()

def riptoobj(ripfiles, outdir, export_format, exists=False):
    meshes = []
    for ripfile in ripfiles:
        meshes.append(RipMesh(ripfile))

        if export_format == "obj":
            objname = os.path.join(outdir, os.path.splitext(ripfile)[0] + ".obj")
            mtlname = os.path.join(outdir, os.path.splitext(ripfile)[0] + ".mtl")

            texset = set()
            for mesh in meshes:
                for tex in mesh.texture_files:
                    texset.add(tex)

            objlines = []
            mtllines = []

            objlines.append(HEADER)
            if len(texset) > 0:
                objlines.append("mtllib " + mtlname)
                mtllines.append(HEADER)

                for tex in texset:
                    mtllines.append("newmtl " + tex)
                    mtllines.append(DEFAULT_MAT)
                    mtllines.append("map_Kd " + tex)
                    mtllines.append("")

                last_idx = None

                for idx, mesh in enumerate(meshes):
                    objlines.append("o Object" + str(idx))
                    for tex in mesh.texture_files:
                        objlines.append("usemtl " + tex)

                    for v in mesh.vertices:
                        objlines.append("v {} {} {}".format(v.x, v.y, v.z))

                    for vn in mesh.normals:
                        objlines.append("vn {} {} {}".format(vn.x, vn.y, vn.z))

                    for vt in mesh.texcoords:
                        objlines.append("vt {} {}".format(vt.u, vt.v))

                    if not last_idx:
                        last_idx = 1

                    highest_idx = 0
                    for face in mesh.faces:
                        line = ["f"]

                        for v in face:
                            v += last_idx
                            highest_idx = v if v > highest_idx else highest_idx
                            line.append("{}/{}/{}".format(v, v, v))
                        objlines.append(" ".join(line))

                    last_idx = highest_idx + 1
                with open(objname, "w") as obj:
                    obj.write("\n".join(objlines))

                with open(mtlname, "w") as mtl:
                    mtl.write("\n".join(mtllines))



class NinjaRipConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("NinjaRip-2 Converter")

        self.file_path = tk.StringVar()
        self.export_format = tk.StringVar()
        self.export_format.set("obj")
        self.process_option = tk.StringVar()
        self.process_option.set("file")

        self.create_widgets()

    def create_widgets(self):
        process_label = ttk.Label(self.root, text="Process:")
        process_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        file_radio = ttk.Radiobutton(self.root, text="File", variable=self.process_option, value="file")
        file_radio.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        dir_radio = ttk.Radiobutton(self.root, text="Directory", variable=self.process_option, value="dir")
        dir_radio.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        file_label = ttk.Label(self.root, text="Select .rip file or directory:")
        file_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.file_entry = ttk.Entry(self.root, textvariable=self.file_path)
        self.file_entry.grid(row=1, column=1, padx=10, pady=10, columnspan=2, sticky="we")

        browse_button = ttk.Button(self.root, text="Browse", command=self.browse_file_or_directory)
        browse_button.grid(row=1, column=3, padx=10, pady=10, sticky="w")

        export_label = ttk.Label(self.root, text="Select export format:")
        export_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        obj_radio = ttk.Radiobutton(self.root, text="OBJ", variable=self.export_format, value="obj")
        obj_radio.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        convert_button = ttk.Button(self.root, text="Convert", command=self.convert_rip)
        convert_button.grid(row=3, column=0, padx=10, pady=10, columnspan=4, sticky="we")

        self.command_output_text = Text(self.root, height=10, width=40)
        self.command_output_text.grid(row=4, column=0, padx=10, pady=10, columnspan=4, sticky="we")

    def browse_file_or_directory(self):
        if self.process_option.get() == "file":
            file_path = filedialog.askopenfilename(filetypes=[("RIP files", "*.rip")])
        else:
            file_path = filedialog.askdirectory()
        self.file_path.set(file_path)

    def convert_rip(self):
        file_path = self.file_path.get()
        export_format = self.export_format.get()
        outdir = os.path.dirname(file_path)

        if not file_path:
            self.command_output_text.delete(1.0, tk.END)
            self.command_output_text.insert(tk.END, "Please select a .rip file or directory.")
            return

        try:
            if self.process_option.get() == "file":
                riptoobj([file_path], outdir, export_format)
                self.command_output_text.delete(1.0, tk.END)
                self.command_output_text.insert(tk.END, f"Conversion successful. Output saved in {outdir}.")
            else:
                if os.path.isdir(file_path):
                    ripfiles = [os.path.join(file_path, f) for f in os.listdir(file_path) if f.endswith(".rip")]
                    if ripfiles:
                        riptoobj(ripfiles, outdir, export_format)
                        self.command_output_text.delete(1.0, tk.END)
                        self.command_output_text.insert(tk.END, f"Conversion successful. Output saved in {outdir}.")
                    else:
                        self.command_output_text.delete(1.0, tk.END)
                        self.command_output_text.insert(tk.END, "No .rip files found in the selected directory.")
                else:
                    self.command_output_text.delete(1.0, tk.END)
                    self.command_output_text.insert(tk.END, "Selected directory is not valid.")
        except Exception as e:
            self.command_output_text.delete(1.0, tk.END)
            self.command_output_text.insert(tk.END, f"Conversion failed: {str(e)}")

if __name__ == '__main__':
    root = tk.Tk()
    app = NinjaRipConverter(root)
    root.mainloop()