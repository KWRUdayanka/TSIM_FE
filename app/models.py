from typing import List, Literal
from pydantic import BaseModel, Field

# --- Request Model ---
class PluginGenerationRequest(BaseModel):
    requirement: str = Field(..., description="Natural language description of the plugin requirements.")
    plugin_name: str = Field(..., description="The desired name for the plugin (e.g., 'ForexRateFetcher').")

# --- Response Models ---
class JavaFile(BaseModel):
    filename: str = Field(..., description="The filename, e.g., 'MyPluginConfig.java'")
    code: str = Field(..., description="The complete Java source code")
    file_type: Literal["CONFIG", "PROCESSOR", "POJO", "OTHER"] = Field(..., description="Category of the file")

class PluginPackageResponse(BaseModel):
    plugin_id: str
    files: List[JavaFile]
    summary: str = Field(..., description="A brief explanation of what the agent built.")