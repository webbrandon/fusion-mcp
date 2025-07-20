import adsk.core, adsk.fusion
import traceback
import threading
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import adsk.core, adsk.fusion, adsk.cam, traceback
import threading, json, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Global variables
app = None
ui = None
handlers = []
server_thread = None
DEFAULT_PORT = 8009

def run(context):
    global app, ui, server_thread
    
    try:
        # Get the Fusion application object
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Start the HTTP server in a separate thread
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class FusionCommandHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        params = json.loads(post_data)

        app = adsk.core.Application.get()
        design = app.activeProduct
        component = design.rootComponent

        try:
            command = params.get('command')
            if command == 'create_sketch':
                plane = params.get('plane', 'xy')
                sketches = component.sketches
                if plane == 'xy':
                    plane_obj = component.xYConstructionPlane
                elif plane == 'xz':
                    plane_obj = component.xZConstructionPlane
                elif plane == 'yz':
                    plane_obj = component.yZConstructionPlane
                else:
                    raise ValueError(f"Invalid plane: {plane}")
                sketch = sketches.add(plane_obj)
                if 'name' in params:
                    sketch.name = params['name']
                result = f"Created sketch on {plane} plane"
            elif command == 'create_circle':
                radius = params.get('radius', 5.0)
                center_x = params.get('center_x', 0.0)
                center_y = params.get('center_y', 0.0)
                sketches = component.sketches
                if not sketches.count:
                    raise ValueError("No active sketch found")
                sketch = sketches[sketches.count - 1]
                center = adsk.core.Point3D.create(center_x, center_y, 0)
                sketch.sketchCurves.sketchCircles.addByCenterRadius(center, radius)
                result = f"Created circle with radius {radius} at ({center_x}, {center_y})"
            elif command == 'draw_rectangle':
                width = params.get('width', 10.0)
                height = params.get('height', 10.0)
                x = params.get('x', 0.0)
                y = params.get('y', 0.0)
                sketches = component.sketches
                if not sketches.count:
                    raise ValueError("No active sketch found")
                sketch = sketches[sketches.count - 1]
                sketch.sketchCurves.sketchLines.addTwoPointRectangle(
                    adsk.core.Point3D.create(x, y, 0),
                    adsk.core.Point3D.create(x + width, y + height, 0)
                )
                result = f"Drew rectangle at ({x}, {y}) with width {width}, height {height}"
            elif command == 'revolve':
                angle = params.get('angle', 360.0)
                operation = params.get('operation', 'new')
                sketches = component.sketches
                if not sketches.count:
                    raise ValueError("No active sketch found")
                sketch = sketches[sketches.count - 1]
                if not sketch.profiles.count:
                    raise ValueError("No profiles found in sketch")
                profile = sketch.profiles.item(0)
                revolves = component.features.revolveFeatures
                axis = component.xConstructionAxis  # Assume X axis; customize if needed
                rev_input = revolves.createInput(profile, axis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation if operation == 'new' else adsk.fusion.FeatureOperations.JoinFeatureOperation)
                rev_input.setAngleExtent(False, adsk.core.ValueInput.createByReal(angle))
                revolves.add(rev_input)
                result = f"Revolved profile by {angle} degrees"
            elif command == 'add_draft':
                angle = params.get('angle', 2.0)
                bodies = component.bRepBodies
                if not bodies.count:
                    raise ValueError("No body found")
                body = bodies.item(bodies.count - 1)
                faces = body.faces  # Assume all faces; customize
                drafts = component.features.draftFeatures
                draft_input = drafts.createInput(faces, True, adsk.core.ValueInput.createByReal(angle))
                drafts.add(draft_input)
                result = f"Added draft angle of {angle} degrees"
            elif command == 'split_body':
                bodies = component.bRepBodies
                if not bodies.count:
                    raise ValueError("No body found")
                body = bodies.item(bodies.count - 1)
                planes = component.constructionPlanes
                if not planes.count:
                    raise ValueError("No plane for splitting")
                plane = planes.item(0)  # Assume first plane; customize
                splits = component.features.splitBodyFeatures
                split_input = splits.createInput(body, plane, True)
                splits.add(split_input)
                result = "Split body into halves"
            elif command == 'sweep':
                sketches = component.sketches
                if not sketches.count:
                    raise ValueError("No active sketch found")
                sketch = sketches[sketches.count - 1]
                if not sketch.profiles.count:
                    raise ValueError("No profile for sweep")
                profile = sketch.profiles.item(0)
                path_sketch = sketches.item(sketches.count - 2) if sketches.count > 1 else sketch  # Assume previous sketch for path
                path = path_sketch.sketchCurves.item(0)  # Assume first curve as path
                sweeps = component.features.sweepFeatures
                sweep_input = sweeps.createInput(profile, path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                sweeps.add(sweep_input)
                result = "Created sweep feature"
            elif command == 'loft':
                profiles = []  # Assume last two profiles
                for i in range(max(0, component.features.count - 2), component.features.count):
                    feature = component.features.item(i)
                    if hasattr(feature, 'profiles'):
                        profiles.append(feature.profiles.item(0))
                if len(profiles) < 2:
                    raise ValueError("Need at least two profiles for loft")
                lofts = component.features.loftFeatures
                loft_input = lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                loft_input.loftSections.add(profiles[0])
                loft_input.loftSections.add(profiles[1])
                lofts.add(loft_input)
                result = "Created loft feature"
            elif command == 'fillet':
                radius = params.get('radius', 1.0)
                bodies = component.bRepBodies
                if not bodies.count:
                    raise ValueError("No body found")
                body = bodies.item(bodies.count - 1)
                edges = body.edges  # Assume all edges; customize
                fillets = component.features.filletFeatures
                fillet_input = fillets.createInput()
                fillet_input.addConstantRadiusEdgeSet(edges, adsk.core.ValueInput.createByReal(radius), True)
                fillets.add(fillet_input)
                result = f"Added fillet with radius {radius}"
            elif command == 'combine':
                operation = params.get('operation', 'join')
                bodies = component.bRepBodies
                if bodies.count < 2:
                    raise ValueError("Need at least two bodies")
                target = bodies.item(bodies.count - 1)
                tool = bodies.item(bodies.count - 2)
                combines = component.features.combineFeatures
                combine_input = combines.createInput(target, tool)
                if operation == 'join':
                    combine_input.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
                elif operation == 'cut':
                    combine_input.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
                elif operation == 'intersect':
                    combine_input.operation = adsk.fusion.FeatureOperations.IntersectFeatureOperation
                combines.add(combine_input)
                result = f"Combined bodies with {operation} operation"
            elif command == 'pattern':
                quantity = params.get('quantity', 5)
                distance = params.get('distance', 10.0)
                bodies = component.bRepBodies
                if not bodies.count:
                    raise ValueError("No body to pattern")
                body = bodies.item(bodies.count - 1)
                patterns = component.features.rectangularPatternFeatures
                input_entities = adsk.core.ObjectCollection.create()
                input_entities.add(body)
                direction = component.xConstructionAxis  # Assume X direction
                pattern_input = patterns.createInput(input_entities, direction, adsk.core.ValueInput.createByReal(quantity), adsk.core.ValueInput.createByReal(distance))
                patterns.add(pattern_input)
                result = f"Created rectangular pattern with {quantity} instances"
            elif command == 'undo':
                app.undo()
                result = "Undid last operation"
            elif command == 'delete_feature':
                name = params.get('name')
                if name:
                    for feature in component.features:
                        if feature.name == name:
                            feature.deleteMe()
                            result = f"Deleted feature {name}"
                            break
                    else:
                        raise ValueError("Feature not found")
                else:
                    if component.features.count:
                        component.features.item(component.features.count - 1).deleteMe()
                        result = "Deleted last feature"
                    else:
                        raise ValueError("No features to delete")
            elif command == 'copy_body':
                name = params.get('name')
                bodies = component.bRepBodies
                if name:
                    for body in bodies:
                        if body.name == name:
                            copied_body = body.copyToComponent(component)
                            result = f"Copied body {name}"
                            break
                    else:
                        raise ValueError("Body not found")
                else:
                    if bodies.count:
                        last_body = bodies.item(bodies.count - 1)
                        last_body.copyToComponent(component)
                        result = "Copied last body"
                    else:
                        raise ValueError("No bodies to copy")
            elif command == 'create_offset_plane':
                offset = params.get('offset', 10.0)
                base_plane = component.xYConstructionPlane  # Assume XY; customize
                planes = component.constructionPlanes
                plane_input = planes.createInput()
                plane_input.setByOffset(base_plane, adsk.core.ValueInput.createByReal(offset))
                new_plane = planes.add(plane_input)
                if 'name' in params:
                    new_plane.name = params['name']
                result = f"Created offset plane at {offset} cm"
            elif command == 'measure_distance':
                # Assume last two points or bodies; simplify to last two bodies' centers
                bodies = component.bRepBodies
                if bodies.count < 2:
                    raise ValueError("Need at least two entities to measure")
                entity1 = bodies.item(bodies.count - 1)
                entity2 = bodies.item(bodies.count - 2)
                measure_mgr = app.measureManager
                results = measure_mgr.measureMinimumDistance(entity1, entity2)
                result = f"Minimum distance: {results.value} cm"
            elif command == 'export_stl':
                filename = params.get('filename', 'mold.stl')
                export_mgr = design.exportManager
                stl_options = export_mgr.createSTLExportOptions(component)
                stl_options.filename = filename
                export_mgr.execute(stl_options)
                result = f"Exported STL to {filename}"
            elif command == 'extrude':
                distance = params.get('distance', 5.0)
                operation = params.get('operation', 'new')
                sketches = component.sketches
                if not sketches.count:
                    raise ValueError("No active sketch found")
                sketch = sketches[sketches.count - 1]
                if not sketch.profiles.count:
                    raise ValueError("No profiles found in sketch")
                prof = sketch.profiles.item(0)
                extrudes = component.features.extrudeFeatures
                op = adsk.fusion.FeatureOperations.NewBodyFeatureOperation if operation == 'new' else adsk.fusion.FeatureOperations.JoinFeatureOperation if operation == 'join' else adsk.fusion.FeatureOperations.CutFeatureOperation if operation == 'cut' else adsk.fusion.FeatureOperations.IntersectFeatureOperation
                distance_val = adsk.core.ValueInput.createByReal(distance)
                ext_input = extrudes.createInput(prof, op)
                ext_input.setDistanceExtent(False, distance_val)
                extrudes.add(ext_input)
                result = f"Extruded profile by {distance} cm"
            else:
                raise ValueError("Unknown command")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"result": result}).encode())
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

def start_server():
    """Start the HTTP server on localhost:18080"""
    try:
        host = os.environ.get('FUSION_HOST', 'localhost')
        port = int(os.environ.get('FUSION_PORT', 8009))
        server = HTTPServer((host, port), FusionCommandHandler)
        server.serve_forever()
    except Exception as e:
        if ui:
            ui.messageBox(f"Failed to start server: {str(e)}")
