import Rhino
import System
from typing import *
from System.Drawing import Color  # Import Color from System.Drawing
from Rhino import RhinoMath




def add_sub_layer(
    layer_index_or_rhino_object: Union[int, Rhino.DocObjects.RhinoObject],
    sub_layer_name: str,
    geometries: list[any],
    colors: list[Color] = None,
    delete_existing: bool = False,
    use_parent = True,
) -> int:
    """Add geometry to a sub-layer of the specified layer.

    Parameters
    ----------
    layer_index_or_rhino_object : int or RhinoObject
        The index of the layer or the RhinoObject to add to the sub-layer
    sub_layer_name : str
        The name of the sub-layer.
    geometry : any
        The geometry to add to the sub-layer.
    colors : list[Color], optional
        The color of the sub-layer and objects.
    delete_existing : bool, optional
        True to delete existing objects in the sub-layer.
    user_parent : bool, optional
        True to use the parent layer as the parent of the sub-layer.

    """

    # Find current layer of object
    layer_index = -1
    if isinstance(layer_index_or_rhino_object, int):
        layer_index = layer_index_or_rhino_object
    elif isinstance(layer_index_or_rhino_object, Rhino.DocObjects.RhinoObject):
        layer_index = layer_index = layer_index_or_rhino_object.Attributes.LayerIndex

    if layer_index == -1:
        print("Layer not found. No object is added to rhino.")
        return
    
    
    # Use parent layer if specified
    if use_parent:
        parent_layer_id = Rhino.RhinoDoc.ActiveDoc.Layers[layer_index].ParentLayerId
        if parent_layer_id != System.Guid.Empty:
            parent_layer = Rhino.RhinoDoc.ActiveDoc.Layers.FindId(parent_layer_id)
            if parent_layer:
                layer_index = parent_layer.Index        

    # Now create the full path for the case (second-level) layer
    new_layer_name = (
        Rhino.RhinoDoc.ActiveDoc.Layers[layer_index].FullPath + "::" + sub_layer_name
    )
    new_layer_index = Rhino.RhinoDoc.ActiveDoc.Layers.FindByFullPath(
        new_layer_name, True
    )

    if new_layer_index < 0:
        # Create the case layer under the plugin layer
        layer = Rhino.DocObjects.Layer()
        layer.Name = sub_layer_name
        layer.ParentLayerId = Rhino.RhinoDoc.ActiveDoc.Layers[layer_index].Id
        layer.Color = colors[0] if colors else System.Drawing.Color.Black
        new_layer_index = Rhino.RhinoDoc.ActiveDoc.Layers.Add(layer)

    if delete_existing:
        delete_objects_in_layer(new_layer_index)

    obj_ids = []
    if geometries:
        for idx, geometry in enumerate(geometries):
            # Create object attributes and assign layer index
            obj_id = Rhino.RhinoDoc.ActiveDoc.Objects.Add(geometry)
            obj_ids.append(obj_id)
            obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(obj_id)

            attributes = obj.Attributes.Duplicate()
            attributes.LayerIndex = new_layer_index

            if len(colors) > 0:
                attributes.ObjectColor = colors[idx%len(colors)] if len(colors) > 1 else Color.Black
                attributes.ColorSource = (
                    Rhino.DocObjects.ObjectColorSource.ColorFromObject
                )

            Rhino.RhinoDoc.ActiveDoc.Objects.ModifyAttributes(obj, attributes, True)

            obj.CommitChanges()

        # Group all arrows
        if all(obj_ids):
            group_index = Rhino.RhinoDoc.ActiveDoc.Groups.Add()
            for id in obj_ids:
                Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(group_index, id)

    Rhino.RhinoDoc.ActiveDoc.Views.Redraw()

    return new_layer_index


def ensure_layer_exists(
    plugin_name: str,
    data_name: str,
    type_name: str,
    color: Color = None,
    delete_existing: bool = False,
) -> int:
    """Ensure that the plugin_name layer, data_name sublayer, and type_name sublayer exist, and return the type layer index.

    If delete_existing is True, delete all objects from the specified layers if they exist.

    Parameters
    ----------
    data_name : str
        The name of the data sub-layer.
    type_name : str
        The name of the type sub-sub-layer.

    """

    # Check if the parent (plugin) layer exists
    plugin_layer_index = Rhino.RhinoDoc.ActiveDoc.Layers.FindByFullPath(
        plugin_name, True
    )
    if plugin_layer_index < 0:
        # Create the parent layer if it doesn't exist
        plugin_layer_index = Rhino.RhinoDoc.ActiveDoc.Layers.Add(
            plugin_name, System.Drawing.Color.Black
        )

    # Now create the full path for the case (second-level) layer
    case_layer_name = plugin_name + "::" + data_name
    case_layer_index = Rhino.RhinoDoc.ActiveDoc.Layers.FindByFullPath(
        case_layer_name, True
    )
    if case_layer_index < 0:
        # Create the case layer under the plugin layer
        case_layer = Rhino.DocObjects.Layer()
        case_layer.Name = data_name
        case_layer.ParentLayerId = Rhino.RhinoDoc.ActiveDoc.Layers[
            plugin_layer_index
        ].Id
        case_layer.Color = System.Drawing.Color.Black
        case_layer_index = Rhino.RhinoDoc.ActiveDoc.Layers.Add(case_layer)

    # Now create the full path for the type (third-level) layer
    type_layer_name = case_layer_name + "::" + type_name
    type_layer_index = Rhino.RhinoDoc.ActiveDoc.Layers.FindByFullPath(
        type_layer_name, True
    )
    if type_layer_index < 0:
        # Create the type layer under the case layer
        type_layer = Rhino.DocObjects.Layer()
        type_layer.Name = type_name
        type_layer.ParentLayerId = Rhino.RhinoDoc.ActiveDoc.Layers[case_layer_index].Id
        type_layer.Color = color if color else System.Drawing.Color.Black
        type_layer_index = Rhino.RhinoDoc.ActiveDoc.Layers.Add(type_layer)

    if delete_existing:
        delete_objects_in_layer(type_layer_index)

    return type_layer_index


def delete_objects_in_layer(layer_index):
    """Delete all objects in the specified layer and its immediate child layers."""
    layer = Rhino.RhinoDoc.ActiveDoc.Layers[layer_index]
    objects = Rhino.RhinoDoc.ActiveDoc.Objects.FindByLayer(layer)
    for obj in objects:
        Rhino.RhinoDoc.ActiveDoc.Objects.Delete(obj, True)

    # Delete objects in immediate child layers
    child_layers = [
        l for l in Rhino.RhinoDoc.ActiveDoc.Layers if l.ParentLayerId == layer.Id
    ]
    for child_layer in child_layers:
        objects = Rhino.RhinoDoc.ActiveDoc.Objects.FindByLayer(child_layer)
        for obj in objects:
            Rhino.RhinoDoc.ActiveDoc.Objects.Delete(obj, True)


def get_objects_by_layer(layer_name, debug=False):
    """Get Rhino objects by layer name.

    Parameters
    ----------
    layer_name : str
        The name of the layer to search for objects.
    """

    # Find objects by the layer name
    layer_index = Rhino.RhinoDoc.ActiveDoc.Layers.FindByFullPath(
        layer_name, RhinoMath.UnsetIntIndex
    )
    layer = None
    if layer_index != RhinoMath.UnsetIntIndex:
        layer = Rhino.RhinoDoc.ActiveDoc.Layers[layer_index]
    else:
        layer = Rhino.RhinoDoc.ActiveDoc.Layers.FindName(layer_name)
    if layer is None:
        print(f"Layer not found: {layer_name}")
        return

    print("get_objects_by_layer: ", layer)

    rhino_objects = Rhino.RhinoDoc.ActiveDoc.Objects.FindByLayer(layer)

    # Check if objects are found
    if rhino_objects is None:
        print(f"No objects found on layer: {layer_name}")
        return

    # Iterate through the found objects and print their details
    if debug:
        for obj in rhino_objects:
            if obj:
                # Example: print object ID and type
                print(f"Object ID: {obj.Id}, Object Type: {obj.ObjectType}")

    return rhino_objects
