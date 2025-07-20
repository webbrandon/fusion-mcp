from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult
from typing import Annotated
from pydantic import Field
import requests
import json
import os

mcp = FastMCP(
    name="ExtendedFusionMCPServer",
    mask_error_details=True,
    on_duplicate_tools="error"
)

FUSION_HOST = os.environ.get('FUSION_HOST', '127.0.0.1')
FUSION_PORT = int(os.environ.get('FUSION_PORT', 8009))
FUSION_URL = f"http://{FUSION_HOST}:{FUSION_PORT}/"

@mcp.tool(annotations={
    "title": "Create New Sketch",
    "readOnlyHint": False,
    "destructiveHint": True,
    "openWorldHint": False
})
def create_sketch(
    plane: Annotated[str, Field(description="Construction plane (xy, xz, or yz)", default="xy")],
    name: Annotated[str, Field(description="Optional name for the sketch", default="")]
) -> ToolResult:
    """Create a new sketch on a specified plane."""
    try:
        payload = {"command": "create_sketch", "plane": plane}
        if name:
            payload["name"] = name
        response = requests.post(FUSION_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Create Circle in Sketch",
    "readOnlyHint": False,
    "destructiveHint": True,
    "openWorldHint": False
})
def create_circle(
    radius: Annotated[float, Field(description="Radius in cm", ge=0.1, le=50.0, default=5.0)],
    center_x: Annotated[float, Field(description="X-coordinate of center", default=0.0)],
    center_y: Annotated[float, Field(description="Y-coordinate of center", default=0.0)]
) -> ToolResult:
    """Create a circle in the active sketch."""
    try:
        response = requests.post(
            FUSION_URL,
            json={"command": "create_circle", "radius": radius, "center_x": center_x, "center_y": center_y}
        )
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Draw Rectangle in Sketch",
    "readOnlyHint": False,
    "destructiveHint": True,
    "openWorldHint": False
})
def draw_rectangle(
    width: Annotated[float, Field(description="Width of the rectangle in cm", ge=0.1, le=100.0, default=10.0)],
    height: Annotated[float, Field(description="Height of the rectangle in cm", ge=0.1, le=100.0, default=10.0)],
    x: Annotated[float, Field(description="X-coordinate of bottom-left corner", default=0.0)],
    y: Annotated[float, Field(description="Y-coordinate of bottom-left corner", default=0.0)]
) -> ToolResult:
    """Draw a rectangle in the active sketch."""
    try:
        response = requests.post(
            FUSION_URL,
            json={"command": "draw_rectangle", "width": width, "height": height, "x": x, "y": y}
        )
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Revolve Sketch Profile",
    "readOnlyHint": False,
    "destructiveHint": True,
    "openWorldHint": False
})
def revolve(
    angle: Annotated[float, Field(description="Revolve angle in degrees", ge=0.0, le=360.0, default=360.0)],
    operation: Annotated[str, Field(description="Operation type (new, join)", default="new")]
) -> ToolResult:
    """Revolve the last sketch profile."""
    try:
        response = requests.post(
            FUSION_URL,
            json={"command": "revolve", "angle": angle, "operation": operation}
        )
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Add Draft Angle",
    "readOnlyHint": False,
    "destructiveHint": True,
    "openWorldHint": False
})
def add_draft(
    angle: Annotated[float, Field(description="Draft angle in degrees", ge=0.0, le=10.0, default=2.0)]
) -> ToolResult:
    """Add draft angle to the last body."""
    try:
        response = requests.post(
            FUSION_URL,
            json={"command": "add_draft", "angle": angle}
        )
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Split Body",
    "readOnlyHint": False,
    "destructiveHint": True,
    "openWorldHint": False
})
def split_body() -> ToolResult:
    """Split the last body using the first construction plane."""
    try:
        response = requests.post(
            FUSION_URL,
            json={"command": "split_body"}
        )
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Sweep Feature",
    "readOnlyHint": False,
    "destructiveHint": True,
    "openWorldHint": False
})
def sweep() -> ToolResult:
    """Sweep the last profile along the previous sketch curve."""
    try:
        response = requests.post(
            FUSION_URL,
            json={"command": "sweep"}
        )
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Loft Feature",
    "readOnlyHint": False,
    "destructiveHint": True,
    "openWorldHint": False
})
def loft() -> ToolResult:
    """Loft between the last two profiles."""
    try:
        response = requests.post(
            FUSION_URL,
            json={"command": "loft"}
        )
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Fillet Feature",
    "readOnlyHint": False,
    "destructiveHint": True,
    "openWorldHint": False
})
def fillet(
    radius: Annotated[float, Field(description="Fillet radius in cm", ge=0.1, le=10.0, default=1.0)]
) -> ToolResult:
    """Add fillet to all edges of the last body."""
    try:
        response = requests.post(
            FUSION_URL,
            json={"command": "fillet", "radius": radius}
        )
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Combine Bodies",
    "readOnlyHint": False,
    "destructiveHint": True,
    "openWorldHint": False
})
def combine(
    operation: Annotated[str, Field(description="Operation type (join, cut, intersect)", default="join")]
) -> ToolResult:
    """Combine last two bodies with the specified operation."""
    try:
        response = requests.post(
            FUSION_URL,
            json={"command": "combine", "operation": operation}
        )
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Pattern Feature",
    "readOnlyHint": False,
    "destructiveHint": True,
    "openWorldHint": False
})
def pattern(
    quantity: Annotated[int, Field(description="Number of instances", ge=2, le=50, default=5)],
    distance: Annotated[float, Field(description="Distance between instances in cm", ge=1.0, le=100.0, default=10.0)]
) -> ToolResult:
    """Create rectangular pattern of the last body along X axis."""
    try:
        response = requests.post(
            FUSION_URL,
            json={"command": "pattern", "quantity": quantity, "distance": distance}
        )
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Undo Operation",
    "readOnlyHint": False,
    "destructiveHint": True,
    "openWorldHint": False
})
def undo() -> ToolResult:
    """Undo the last operation."""
    try:
        response = requests.post(
            FUSION_URL,
            json={"command": "undo"}
        )
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Delete Feature",
    "readOnlyHint": False,
    "destructiveHint": True,
    "openWorldHint": False
})
def delete_feature(
    name: Annotated[str, Field(description="Name of feature to delete (optional, deletes last if not provided)", default="")]
) -> ToolResult:
    """Delete a feature by name or the last one."""
    try:
        payload = {"command": "delete_feature"}
        if name:
            payload["name"] = name
        response = requests.post(FUSION_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Copy Body",
    "readOnlyHint": False,
    "destructiveHint": True,
    "openWorldHint": False
})
def copy_body(
    name: Annotated[str, Field(description="Name of body to copy (optional, copies last if not provided)", default="")]
) -> ToolResult:
    """Copy a body by name or the last one."""
    try:
        payload = {"command": "copy_body"}
        if name:
            payload["name"] = name
        response = requests.post(FUSION_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Create Offset Plane",
    "readOnlyHint": False,
    "destructiveHint": True,
    "openWorldHint": False
})
def create_offset_plane(
    offset: Annotated[float, Field(description="Offset distance in cm", default=10.0)],
    name: Annotated[str, Field(description="Optional name for the plane", default="")]
) -> ToolResult:
    """Create an offset construction plane from XY plane."""
    try:
        payload = {"command": "create_offset_plane", "offset": offset}
        if name:
            payload["name"] = name
        response = requests.post(FUSION_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Measure Distance",
    "readOnlyHint": True,
    "destructiveHint": False,
    "openWorldHint": False
})
def measure_distance() -> ToolResult:
    """Measure minimum distance between last two bodies."""
    try:
        response = requests.post(
            FUSION_URL,
            json={"command": "measure_distance"}
        )
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Export STL",
    "readOnlyHint": False,
    "destructiveHint": False,
    "openWorldHint": False
})
def export_stl(
    filename: Annotated[str, Field(description="Filename for STL export", default="mold.stl")]
) -> ToolResult:
    """Export the root component as STL."""
    try:
        response = requests.post(
            FUSION_URL,
            json={"command": "export_stl", "filename": filename}
        )
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

@mcp.tool(annotations={
    "title": "Extrude Sketch Profile",
    "readOnlyHint": False,
    "destructiveHint": True,
    "openWorldHint": False
})
def extrude(
    distance: Annotated[float, Field(description="Extrusion distance in cm", ge=0.1, le=50.0, default=5.0)],
    operation: Annotated[str, Field(description="Operation type (new, join, cut, intersect)", default="new")]
) -> ToolResult:
    """Extrude the last sketch profile."""
    try:
        response = requests.post(
            FUSION_URL,
            json={"command": "extrude", "distance": distance, "operation": operation}
        )
        response.raise_for_status()
        data = response.json()
        result_str = data.get("result", "Success")
        return ToolResult(
            content=[{"text": result_str}],
            structured_content={"result": result_str}
        )
    except Exception as e:
        raise ValueError(f"Error reaching Fusion: {str(e)}")

