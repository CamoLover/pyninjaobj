# pyninjaobj (Fork)

A Python GUI Tool to Convert NinjaRip-2 .rip Files to .obj

## Introduction
This repository is a fork of the original [theFroh/pyninjaobj](https://github.com/theFroh/pyninjaobj) project by Luke Gaynor (theFroh). The pyninjaobj script is a GUI-based tool that takes NinjaRip-2 model dumps (`.rip` files) and converts them into Wavefront OBJ files (`.obj`). The forked version of pyninjaobj has made some improvements and updates to the original project.

## Features
- Converts NinjaRip-2 .rip files into .obj format through a user-friendly graphical interface.
- Supports both single `.rip` file conversion and batch conversion of `.rip` files in a directory.
- Outputs a separate .mtl (Material Template Library) file for material definitions.
- Allows the selection of the export format (currently supports .obj).

## Usage
1. Launch the application.
2. Select the processing mode - either "File" for single file conversion or "Directory" for batch conversion.
3. Click the "Browse" button to select the `.rip` file or directory containing `.rip` files.
4. Select the export format (currently supports .obj).
5. Click the "Convert" button to initiate the conversion.

The resulting `.obj` and accompanying `.mtl` files will be created in the specified output directory. You can import the `.obj` into your favorite 3D editor for inspection, editing, and export.

## Known Limitations
- NinjaRip-2 may not preserve mesh object names, resulting in generic component names.
- NinjaRip-2 may not handle certain model details correctly, especially in mods, affecting positioning and rotation.
- The script does not differentiate between multiple textures on a single mesh component.
- It imports all textures, including non-diffuse ones like emissive and specular maps, which may need manual cleanup.

## Original Author
The original pyninjaobj script was created by Luke Gaynor. This forked version aims to maintain and improve the tool's functionality. You can find the original project at [theFroh/pyninjaobj](https://github.com/theFroh/pyninjaobj).

Please report any issues or contribute to the development of this forked project. Thank you for using pyninjaobj!
