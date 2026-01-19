from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from OpenGL.GL import *
from PIL import Image


@dataclass
class Texture2D:
    id: int
    width: int
    height: int

    @staticmethod
    def from_file(
        path: str | Path,
        *,
        flip_y: bool = True,
        srgb: bool = False,
        generate_mipmaps: bool = True,
        min_filter=GL_LINEAR_MIPMAP_LINEAR,
        mag_filter=GL_LINEAR,
        wrap_s=GL_REPEAT,
        wrap_t=GL_REPEAT,
    ) -> "Texture2D":
        path = Path(path)

        img = Image.open(path).convert("RGBA")
        if flip_y:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)

        w, h = img.size
        data = img.tobytes("raw", "RGBA", 0, -1)

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)

        # filtros e wrap
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, int(min_filter))
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, int(mag_filter))
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, int(wrap_s))
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, int(wrap_t))

        # upload
        internal_format = GL_SRGB8_ALPHA8 if srgb else GL_RGBA8
        glTexImage2D(
            GL_TEXTURE_2D,
            0,  # level
            internal_format,
            w, h,
            0,  # border
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            data
        )

        if generate_mipmaps:
            glGenerateMipmap(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, 0)
        return Texture2D(tex_id, w, h)

    def bind(self, unit: int = 0) -> None:
        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(GL_TEXTURE_2D, self.id)

    def destroy(self) -> None:
        glDeleteTextures([self.id])
        self.id = 0
