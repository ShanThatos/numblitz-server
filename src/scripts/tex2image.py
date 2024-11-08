import sys

from pathlib import Path
from subprocess import check_call
from typing import Optional

def tex2image(tex_file: str, density: Optional[int] = None, border: Optional[int] = None):
    tex_file = Path(tex_file).absolute()
    if not str(tex_file).endswith(".tex"):
        raise ValueError("File must be a .tex file")
    
    with open(tex_file, "r") as f:
        first_line = f.readline()
    if first_line.startswith("%tex2image"):
        config = first_line.split(maxsplit=1)[1].split(",")
        config_dict = {k.strip(): v.strip() for k, v in (x.split("=") for x in config)}
        if density is None and "density" in config_dict:
            density = int(config_dict["density"])
        if border is None and "border" in config_dict:
            border = int(config_dict["border"])

    if density is None:
        density = 500
    if border is None:
        border = 5

    output_dir = Path("./temp/tex-output/").absolute()
    output_dir.mkdir(parents=True, exist_ok=True)
    check_call(f"pdflatex -output-directory {output_dir} {tex_file}", shell=True)

    pdf_file = output_dir.joinpath(tex_file.with_suffix(".pdf").name)
    image_file = tex_file.with_suffix(".png")
    check_call(f"magick -density {density} {pdf_file} -trim {image_file}")

    check_call(f"magick {image_file} -bordercolor transparent -resize 20% -sharpen 0x10 -border {border} {image_file}")

    print(f"Converted {tex_file} [{density=}, {border=}]")

def extract_arg(args, arg_names, cls, default=None):
    arg_name = next((arg for arg in arg_names if arg in args), None)
    if arg_name is None:
        return default
    index = args.index(arg_name)
    ret = cls(args[index + 1])
    args.pop(index)
    args.pop(index)
    return ret

if __name__ == "__main__":
    density = extract_arg(sys.argv, ["-d", "--density"], int, None)
    border = extract_arg(sys.argv, ["-b", "--border"], int, None)
    tex2image(sys.argv[1], density=density, border=border)
