import Rhino
from .globals import wood_rui_globals
from .layer import ensure_layer_exists  # Import the singleton instance
from System.Drawing import Color
from typing import *


def delete_objects(guids):
    """Delete Rhino objects by their GUIDs, handling individual items, lists, and nested lists."""
    if isinstance(guids, list):
        # If the input is a list, iterate through it and call delete_objects recursively
        for item in guids:
            delete_objects(item)
    else:
        # print("delete_objects", guids)
        # If the input is not a list, assume it's a single GUID and delete it
        Rhino.RhinoDoc.ActiveDoc.Objects.Delete(guids, True)


def add_mesh(mesh, data_name):
    """Add a mesh to the specified layer and return the mesh's GUID."""

    # print("add_mesh", data_name)
    # print("start", wood_rui_globals[data_name]["mesh_guid"])

    layer_index = ensure_layer_exists("compas_wood", data_name, "mesh", Color.Black)
    if "mesh_guid" in wood_rui_globals[data_name] and wood_rui_globals[data_name]["mesh_guid"] is not None:
        delete_objects(wood_rui_globals[data_name]["mesh_guid"])
        wood_rui_globals[data_name]["mesh_guid"] = None
        wood_rui_globals[data_name]["mesh"] = None

    # if wood_rui_globals[data_name]["mesh_guid"] is not None:
    #     # Replace the mesh
    #     wood_rui_globals[data_name]["mesh"] = mesh
    #     Rhino.RhinoDoc.ActiveDoc.Objects.Replace(wood_rui_globals[data_name]["mesh_guid"], mesh)
    # else:
    # Add the mesh
    wood_rui_globals[data_name]["mesh"] = mesh
    mesh_guid = Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(mesh)
    wood_rui_globals[data_name]["mesh_guid"] = mesh_guid
    obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(mesh_guid)

    if obj:
        obj.Attributes.LayerIndex = layer_index
        obj.CommitChanges()
        # print("end", wood_rui_globals[data_name]["mesh_guid"])
        Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.Redraw()  # 0 ms
        return wood_rui_globals[data_name]["mesh_guid"]

    else:
        return None


def add_polylines(polylines: List[Rhino.Geometry.Polyline], data_name: str, group_indices: List[int] = None) -> None:
    """Add a list of polylines to the specified layer and return their GUIDs.

    Parameters
    ----------
    foldername : List[Rhino.Geometry.Polyline]
        List of polylines.
    filename_of_dataset : str
        Name of dataset.

    """

    print("add_polylines", data_name)

    layer_index = ensure_layer_exists("compas_wood", data_name, "polylines", Color.DodgerBlue)

    polyline_guids = []
    for idx, polyline in enumerate(polylines):
        if polyline:
            obj_guid = Rhino.RhinoDoc.ActiveDoc.Objects.AddCurve(polyline.ToNurbsCurve())
            if obj_guid:
                obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(obj_guid)
                if obj:
                    obj.Attributes.LayerIndex = layer_index

                    polyline_guids.append(obj_guid)
                    obj.Attributes.SetUserString("element_id", str(int(idx * 0.5)))
                    obj.Attributes.SetUserString("dataset", data_name)
                    obj.Attributes.SetUserString("type", "polylines")

                    if group_indices and len(group_indices) > idx:
                        obj.Attributes.SetUserString("group_index", str(group_indices[idx]))
                    obj.CommitChanges()
                else:
                    pass
            else:
                pass

    if "polylines_guid" in wood_rui_globals[data_name]:
        delete_objects(wood_rui_globals[data_name]["polylines_guid"])
    wood_rui_globals[data_name]["polylines_guid"] = polyline_guids
    wood_rui_globals[data_name]["polylines"] = polylines

    layer_index_dots = ensure_layer_exists("compas_wood", data_name, "joint_types", Color.MediumVioletRed)
    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.Redraw()  # 0 ms


def add_skeleton(polylines: list[Rhino.Geometry.Polyline], data_name: str, distances: list[list[float]] = [], meshes: list[Rhino.Geometry.Mesh] = [], transforms: list[Rhino.Geometry.Transform] = None) -> None:
    """Add a list of polylines to the specified layer and return their GUIDs.

    Parameters
    ----------
    foldername : list[Rhino.Geometry.Polyline]
        List of polylines.
    filename_of_dataset : str
        Name of dataset.

    """
    layer_index = ensure_layer_exists("compas_wood", data_name, "skeleton", Color.DodgerBlue)

    polyline_guids = []
    for idx, polyline in enumerate(polylines):
        if polyline:
            obj_guid = Rhino.RhinoDoc.ActiveDoc.Objects.AddCurve(polyline.ToNurbsCurve())
            if obj_guid:
                obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(obj_guid)
                if obj:
                    obj.Attributes.LayerIndex = layer_index

                    polyline_guids.append(obj_guid)
                    obj.Attributes.SetUserString("element_id", str(int(idx * 0.5)))
                    obj.Attributes.SetUserString("dataset", data_name)
                    obj.Attributes.SetUserString("type", "axes")

                    string_distances : str = ''.join(str(num) for num in distances[idx])
                    obj.Attributes.SetUserString("distances", string_distances)

                    if meshes:
                        string_vertices = ""
                        for vertex in meshes[idx].Vertices:
                            string_vertices += str(vertex.X) + "," + str(vertex.Y) + "," + str(vertex.Z) + ","

                        string_faces = ""
                        for face in meshes[idx].Faces:
                            string_faces += str(face.A) + "," + str(face.B) + "," + str(face.C) + ","

                        obj.Attributes.SetUserString("vertices", string_vertices)
                        obj.Attributes.SetUserString("faces", string_faces)

                    if transforms:
                        transformation_numbers = transforms[idx].ToDoubleArray(True)
                        string_transformation = ""
                        for number in transformation_numbers:
                            string_transformation += str(number) + ","
                        obj.Attributes.SetUserString("transform", string_transformation)

        
                    obj.CommitChanges()
                else:
                    pass
            else:
                pass

    if "polylines_guid" in wood_rui_globals[data_name]:
        delete_objects(wood_rui_globals[data_name]["polylines_guid"])
    wood_rui_globals[data_name]["polylines_guid"] = polyline_guids
    wood_rui_globals[data_name]["polylines"] = polylines

    layer_index_dots = ensure_layer_exists("compas_wood", data_name, "joint_types", Color.MediumVioletRed)
    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.Redraw()  # 0 ms

import Rhino
import System
from System.Drawing import Color
from typing import List

def add_element(mesh: Rhino.Geometry.Mesh, layer_name: str, cuts: List[Rhino.Geometry.Mesh], group_name_prefix: str) -> None:
    """Add a mesh and associated polyline to the specified layer, apply attributes, and group them uniquely.

    Parameters
    ----------
    mesh : Rhino.Geometry.Mesh
        Mesh object that represents the element shape.
    layer_name : str
        Layer name where the new object will be added.
    cuts : List[Rhino.Geometry.Mesh]
        List of cut meshes that represent fabrication cuts.
    group_name_prefix : str
        The prefix for the group name (each call creates a new unique group).

    """
    layer_index = ensure_layer_exists("compas_wood", "model", layer_name, Color.Red)

    if not mesh:
        return

    obj_guid = Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(mesh)
    if not obj_guid:
        return

    obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(obj_guid)
    if not obj:
        return

    obj.Attributes.LayerIndex = layer_index

    # Face for transformation
    result, p0, p1, p2, p3 = mesh.Faces.GetFaceVertices(0)
    if not result:
        return

    origin = p0
    x_axis = p1 - p0
    y_axis = p2 - p0
    plane = Rhino.Geometry.Plane(origin, x_axis, y_axis)
    xform = Rhino.Geometry.Transform.PlaneToPlane(plane, Rhino.Geometry.Plane.WorldXY)
    numbers = xform.ToDoubleArray(True)
    string_numbers = ','.join(str(num) for num in numbers)
    obj.Attributes.SetUserString("xform", string_numbers)

    # Axis Length
    length = mesh.GetBoundingBox(True).Max.Z
    obj.Attributes.SetUserString("length", str(length))

    # Cuts Storage
    for idx, cut_mesh in enumerate(cuts):
        opts = Rhino.FileIO.SerializationOptions()
        opts.WriteUserData = True
        json = cut_mesh.ToJSON(opts)
        obj.Attributes.SetUserString(f"cut_{idx}", json)

    obj.CommitChanges()

    # ObjectFrame
    attributes = obj.Attributes.Duplicate()
    attributes.SetObjectFrame(Rhino.Geometry.Plane.WorldXY)
    Rhino.RhinoDoc.ActiveDoc.Objects.ModifyAttributes(obj, attributes, False)

    # Create Polyline for Frame
    p0 = Rhino.Geometry.Point3d(0, 0, 0)
    p1 = p0 + Rhino.Geometry.Vector3d.XAxis*0.01
    p2 = p0 + Rhino.Geometry.Vector3d.YAxis*0.01
    groupframe = Rhino.Geometry.Polyline([p1, p0, p2])

    polyline_guid = Rhino.RhinoDoc.ActiveDoc.Objects.AddPolyline(groupframe)
    if not polyline_guid:
        return

    # Find the polyline object
    polyline_obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(polyline_guid)
    if not polyline_obj:
        return

    # Generate a unique group name using a counter
    group_index = Rhino.RhinoDoc.ActiveDoc.Groups.Add()

    # Add objects to the new group
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(group_index, obj_guid)
    Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(group_index, polyline_guid)

    # Redraw view
    Rhino.RhinoDoc.ActiveDoc.Views.Redraw()



def add_insertion_lines(lines, data_name):
    """Add a list of polylines to the specified layer and return their GUIDs."""

    print("insertion_lines", data_name)

    layer_index = ensure_layer_exists("compas_wood", data_name, "insertion", Color.Red)

    line_guids = []
    for line in lines:
        obj_guid = Rhino.RhinoDoc.ActiveDoc.Objects.AddLine(line)
        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(obj_guid)
        obj.Attributes.LayerIndex = layer_index

        line_guids.append(obj_guid)
        obj.Attributes.SetUserString("dataset", data_name)
        obj.Attributes.SetUserString("type", "insertion")
        obj.CommitChanges()

    if "insertion_guid" in wood_rui_globals[data_name]:
        delete_objects(wood_rui_globals[data_name]["insertion_guid"])
    wood_rui_globals[data_name]["insertion_guid"] = line_guids
    wood_rui_globals[data_name]["insertion"] = lines
    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.Redraw()  # 0 ms


def add_adjacency(four_indices_face_face_edge_edge, data_name):

    print("add_adjacency", data_name)
    wood_rui_globals[data_name]["adjacency"] = four_indices_face_face_edge_edge

    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.Redraw()  # 0 ms


def add_flags(flags, data_name):

    print("add_flags", data_name)
    wood_rui_globals[data_name]["flags"] = flags


def add_insertion_vectors(insertion_vectors, data_name):

    print("insertion_vectors", data_name)
    wood_rui_globals[data_name]["insertion_vectors"] = insertion_vectors

    polylines_guid = wood_rui_globals[data_name]["polylines_guid"]
    for idx, (obj_guid1, obj_guid2) in enumerate(zip(polylines_guid[0::2], polylines_guid[1::2])):
        for obj_guid in (obj_guid1, obj_guid2):
            obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(obj_guid)
            if obj:
                for idy, joints_type in enumerate(insertion_vectors[idx]):
                    obj.Attributes.SetUserString("insertion_vectors" + str(idy), str(joints_type))
                obj.CommitChanges()
            else:
                pass
    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.Redraw()  # 0 ms


def add_three_valence(three_valence, data_name):

    print("three_valence", data_name)
    wood_rui_globals[data_name]["three_valence"] = three_valence


def add_joinery(joinery: List[List[Rhino.Geometry.Polyline]], data_name: str) -> None:
    """
    Add a list of lists of polylines as groups to the specified layer in Rhino and return their GUIDs.

    :param joinery: A list of lists of polylines to add to Rhino.
    :param data_name: The name of the case to be used for layer and group management.
    """

    print("add_joinery", data_name)

    # Use wood_rui_globals.plugin_name as the top-level layer
    plugin_name = wood_rui_globals.plugin_name

    # Ensure the layer exists or create it under the plugin layer
    layer_index = ensure_layer_exists("compas_wood", data_name, "joinery", Color.Black)

    # Prepare to store all the GUIDs of added objects
    joinery_guids = []

    # Loop through the joinery list (list of lists of polylines)
    for polyline_group in joinery:
        # Store the GUIDs of the individual polylines in this group
        group_guids = []

        # Loop through individual polylines in the current group
        for polyline in polyline_group:
            # Add the polyline to the Rhino document
            obj_guid = Rhino.RhinoDoc.ActiveDoc.Objects.AddCurve(polyline.ToNurbsCurve())
            obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(obj_guid)
            if obj:
                obj.Attributes.LayerIndex = layer_index  # Assign to the specified layer

                group_guids.append(obj_guid)  # Collect the GUID for this polyline
                obj.Attributes.SetUserString("dataset", data_name)
                obj.Attributes.SetUserString("type", "joinery")
                obj.CommitChanges()  # Commit the changes to the object's attributes

        # If the group contains polylines, group them together in Rhino
        if group_guids:
            group_name = f"{data_name}_joinery_group"
            Rhino.RhinoDoc.ActiveDoc.Groups.Add(group_guids)  # Group the polyline GUIDs together
            joinery_guids.extend(group_guids)  # Add the group's GUIDs to the master list

    # If the case already has "joinery_guid", delete the previous objects
    if "joinery_guid" in wood_rui_globals[data_name]:
        delete_objects(wood_rui_globals[data_name]["joinery_guid"])

    # Store the new joinery GUIDs and the joinery data in wood_rui_globals
    wood_rui_globals[data_name]["joinery_guid"] = joinery_guids
    wood_rui_globals[data_name]["joinery"] = joinery

    # Hide all child layers except the 'joinery' layer
    # hide_non_joinery_layers(plugin_name, data_name, "joinery")
    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.Redraw()  # 0 ms


def add_joint_type(joints_per_face: List[List[int]], data_name: str) -> None:

    wood_rui_globals[data_name]["joints_per_face"] = joints_per_face

    polylines_guid = wood_rui_globals[data_name]["polylines_guid"]
    for idx, (obj_guid1, obj_guid2) in enumerate(zip(polylines_guid[0::2], polylines_guid[1::2])):
        for obj_guid in (obj_guid1, obj_guid2):
            obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(obj_guid)
            if obj:
                for idy, joints_type in enumerate(joints_per_face[idx]):
                    obj.Attributes.SetUserString("joints_per_face_" + str(idy), str(joints_type))
                obj.CommitChanges()
            else:
                pass
                print(obj_guid, obj)
    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.Redraw()  # 0 ms


def add_loft_brep(brep_lists, data_name, element_ids=None):
    """Add a list of lofted polylines with holes as breps to the specified layer and return their GUIDs."""

    print("loft", data_name)

    layer_index = ensure_layer_exists("compas_wood", data_name, "loft", Color.Black)

    brep_lists_guids = []
    for idx, brep_list in enumerate(brep_lists):
        brep_list_guids = []
        for brep in brep_list:
            obj_guid = Rhino.RhinoDoc.ActiveDoc.Objects.AddBrep(brep)
            obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(obj_guid)
            obj.Attributes.LayerIndex = layer_index
            brep_list_guids.append(obj_guid)
            obj.Attributes.SetUserString("dataset", data_name)
            if element_ids and len(element_ids) > idx:
                obj.Attributes.SetUserString("element_id", str(element_ids[idx]))
            obj.CommitChanges()

        # Group the brep_list_guids
        group_index = Rhino.RhinoDoc.ActiveDoc.Groups.Add(brep_list_guids)
        print(f"Group created with index: {group_index}")
        brep_lists_guids.append(brep_list_guids)

    if "loft_guid" in wood_rui_globals[data_name]:
        for group in wood_rui_globals[data_name]["loft_guid"]:
            delete_objects(group)

    wood_rui_globals[data_name]["loft_guid"] = brep_lists_guids
    wood_rui_globals[data_name]["loft"] = brep_lists
    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.Redraw()  # 0 ms


def add_loft_mesh(meshes, data_name):
    """Add a list of lofted polylines with holes as meshes to the specified layer and return their GUIDs."""

    print("loft", data_name)

    layer_index = ensure_layer_exists("compas_wood", data_name, "loft", Color.Black)

    mesh_guids = []
    for mesh in meshes:
        obj_guid = Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(mesh)
        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(obj_guid)
        obj.Attributes.LayerIndex = layer_index
        mesh_guids.append(obj_guid)
        obj.Attributes.SetUserString("dataset", data_name)
        obj.CommitChanges()

    if "loft_guid" in wood_rui_globals[data_name]:
        delete_objects(wood_rui_globals[data_name]["loft_guid"])
    wood_rui_globals[data_name]["loft_guid"] = mesh_guids
    wood_rui_globals[data_name]["loft"] = meshes
    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.Redraw()  # 0 ms


def add_axes(
    polylines: List[Rhino.Geometry.Polyline], data_name: str, group_indices: List[int] = None, brep_shapes=None
) -> None:
    """Add a list of polylines to the specified layer and return their GUIDs.

    Parameters
    ----------
    foldername : List[Rhino.Geometry.Polyline]
        List of polylines.
    filename_of_dataset : str
        Name of dataset.

    """

    print("add_axes", data_name)

    layer_index = ensure_layer_exists("compas_wood", data_name, "axes", Color.DodgerBlue)

    shape_guids = []
    shapes_added = []
    for idx, polyline in enumerate(polylines):
        shape = brep_shapes[idx] if brep_shapes[idx] and len(brep_shapes) else polyline

        if polyline:

            obj_guid = Rhino.RhinoDoc.ActiveDoc.Objects.Add(shape)
            shapes_added.append(shape)
            if obj_guid:
                obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(obj_guid)
                if obj:
                    obj.Attributes.LayerIndex = layer_index

                    shape_guids.append(obj_guid)
                    obj.Attributes.SetUserString("element_id", str(idx))
                    obj.Attributes.SetUserString("dataset", data_name)
                    obj.Attributes.SetUserString("type", "axes")

                    if group_indices and len(group_indices) > idx:
                        obj.Attributes.SetUserString("group_index", str(group_indices[idx]))
                    obj.CommitChanges()
                else:
                    pass

            else:
                pass

    if "axes_guid" in wood_rui_globals[data_name]:
        delete_objects(wood_rui_globals[data_name]["axes_guid"])
    wood_rui_globals[data_name]["axes_guid"] = shape_guids
    wood_rui_globals[data_name]["axes"] = shapes_added

    Rhino.RhinoDoc.ActiveDoc.Views.ActiveView.Redraw()  # 0 ms
