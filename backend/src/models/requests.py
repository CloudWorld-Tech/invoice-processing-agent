from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, model_validator


class RunRequest(BaseModel):
    folder_path: Optional[str] = None
    folder: Optional[str] = None
    prompt: Optional[str] = None

    @model_validator(mode="after")
    def _normalize_folder(self):
        """Accept both 'folder' and 'folder_path'."""
        if not self.folder_path and self.folder:
            self.folder_path = self.folder
        return self
