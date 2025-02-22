import Rhino
import rhinoscriptsyntax as rs
import itertools
import System
from typing import Union
import ast


def polyline_obj_to_plane(polyline_obj):
    polyline_curve = polyline_obj.Geometry
    if polyline_curve.PointCount == 3:  # Ensure it has exactly 3 points
        polyline = polyline_curve.ToPolyline()
        origin = polyline[1]
        x_axis = polyline[0] - polyline[1]
        y_axis = polyline[2] - polyline[1]  # Corrected y-axis calculation
        return Rhino.Geometry.Plane(origin, x_axis, y_axis)
    return Rhino.Geometry.Plane.Unset


def polyline_to_plane(polyline):
    if polyline.Count == 5:  # Ensure it has exactly 3 points
        origin = polyline[1]
        x_axis = polyline[0] - polyline[1]
        y_axis = polyline[2] - polyline[1]  # Corrected y-axis calculation
        return Rhino.Geometry.Plane(origin, x_axis, y_axis)
    return Rhino.Geometry.Plane.Unset


def find_valid_groups():
    """Finds groups in Rhino that contain exactly two objects, where one is a polyline with three points.

    Returns
    -------
    List[Tuple[Rhino.DocObjects.RhinoObject, Rhino.Geometry.Plane]]
        A list of tuples, where each tuple contains:
        - The Rhino object that is NOT the polyline.
        - The computed plane from the 3-point polyline.
    """
    valid_groups = []

    # Get all objects in the document
    all_objects = Rhino.RhinoDoc.ActiveDoc.Objects

    valid_groups = []

    # Iterate through all groups
    for group_index in range(Rhino.RhinoDoc.ActiveDoc.Groups.Count):
        # Collect objects that belong to this group
        group_objects = [
            obj
            for obj in all_objects
            if obj.Attributes.GroupCount > 0
            and group_index in obj.Attributes.GetGroupList()
        ]

        # Ensure the group contains exactly 2 objects
        if len(group_objects) != 2:
            continue

        polyline_obj = None
        other_obj = None
        plane = Rhino.Geometry.Plane.Unset

        # Identify polyline and non-polyline object
        for obj in group_objects:
            if isinstance(obj.Geometry, Rhino.Geometry.PolylineCurve):
                polyline_obj = obj
            else:
                other_obj = obj

        # Ensure we found exactly one polyline and one non-polyline object
        if polyline_obj and other_obj:
            polyline_curve = polyline_obj.Geometry
            if polyline_curve.PointCount == 3:  # Ensure it has exactly 3 points
                polyline = polyline_curve.ToPolyline()
                origin = polyline[1]
                x_axis = polyline[0] - polyline[1]
                y_axis = polyline[2] - polyline[1]  # Corrected y-axis calculation
                plane = Rhino.Geometry.Plane(origin, x_axis, y_axis)

                # Store only the non-polyline object and its associated plane
                valid_groups.append((other_obj, plane))

    return valid_groups


def select_and_find_valid_groups(option_name):
    """Finds groups in Rhino that contain exactly two objects, where one is a polyline with three points.

    Returns
    -------
    List[Tuple[Rhino.DocObjects.RhinoObject, Rhino.Geometry.Plane]]
        A list of tuples, where each tuple contains:
        - The Rhino object that is NOT the polyline.
        - The computed plane from the 3-point polyline.
    """
    valid_groups = []

    # Select objects
    objs = rs.GetObjects(f"Select {option_name}")
    if not objs:
        print("No objects selected.")
        return

    group_dict, object_group_map, group_object_map = build_universal_group_dict(objs)

    # Iterate through all groups
    for key, value in group_object_map.items():
        # Collect objects that belong to this group
        group_objects = []
        for guid in value:
            polyline_obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(guid)
            group_objects.append(polyline_obj)

        # Ensure the group contains exactly 2 objects
        if len(group_objects) != 2:
            continue

        polyline_obj = None
        other_obj = None
        plane = Rhino.Geometry.Plane.Unset

        # Identify polyline and non-polyline object
        for obj in group_objects:
            if isinstance(obj.Geometry, Rhino.Geometry.PolylineCurve):
                polyline_obj = obj
            else:
                other_obj = obj

        # Ensure we found exactly one polyline and one non-polyline object
        if polyline_obj and other_obj:
            polyline_curve = polyline_obj.Geometry
            if polyline_curve.PointCount == 3:  # Ensure it has exactly 3 points
                valid_groups.append((other_obj, polyline_obj))

    return valid_groups


def build_universal_group_dict(selected_objects):
    group_dict = {}
    object_group_map = {}
    group_object_map = {}

    def update_group(full_name, simple_name, parent):
        if full_name not in group_dict:
            group_dict[full_name] = {
                "name": simple_name,
                "parent": parent,
                "children": set(),
                "objects": set(),
            }
        else:
            if parent and group_dict[full_name]["parent"] is None:
                group_dict[full_name]["parent"] = parent

    for obj in selected_objects:
        groups = rs.ObjectGroups(obj)
        object_group_map[obj] = set()
        if groups:
            for grp in groups:
                grp_name = grp if grp.strip() != "" else "(unnamed)"
                parts = [
                    p if p.strip() != "" else "(unnamed)" for p in grp_name.split("\\")
                ]
                full_chain = []
                parent = None
                for part in parts:
                    if full_chain:
                        full_chain.append(part)
                        full_name = "\\".join(full_chain)
                    else:
                        full_chain.append(part)
                        full_name = part
                    update_group(full_name, part, parent)
                    if parent:
                        group_dict[parent]["children"].add(full_name)
                    group_dict[full_name]["objects"].add(obj)
                    object_group_map[obj].add(full_name)
                    parent = full_name
        else:
            ungrouped = "Ungrouped"
            update_group(ungrouped, "Ungrouped", None)
            group_dict[ungrouped]["objects"].add(obj)
            object_group_map[obj].add(ungrouped)

    for key, value in object_group_map.items():
        group_object_map[",".join(value)] = []

    for key, value in object_group_map.items():
        group_object_map[",".join(value)].append(key)

    return group_dict, object_group_map, group_object_map


def compute_shared_elements(object_group_map):
    shared_dict = {}
    for obj, groups in object_group_map.items():
        if len(groups) > 1:
            sorted_groups = sorted(groups)
            for combo in itertools.combinations(sorted_groups, 2):
                if combo not in shared_dict:
                    shared_dict[combo] = set()
                shared_dict[combo].add(obj)
    return shared_dict


def print_universal_structure(group_dict, shared_dict):
    print("Universal Group Structure:")
    for group_full, info in sorted(group_dict.items()):
        print("--------------------------------------------------")
        print("Group: " + group_full)
        print("  Simple Name: " + info["name"])
        print("  Parent: " + (info["parent"] if info["parent"] is not None else "None"))
        if info["children"]:
            print("  Children: " + ", ".join(sorted(info["children"])))
        else:
            print("  Children: None")
        print("  Objects: " + str(list(info["objects"])))
    print("\nShared Elements Between Groups:")
    if shared_dict:
        for groups_pair, objs in sorted(shared_dict.items()):
            print(
                "Groups: "
                + " & ".join(groups_pair)
                + " share objects: "
                + str(list(objs))
            )
    else:
        print("No shared elements found among groups.")


def infer_group_hierarchy(group_dict):
    inferred_parents = {}
    groups = list(group_dict.keys())
    for group in groups:
        inferred_parents[group] = None
        objs = group_dict[group]["objects"]
        candidates = []
        for other in groups:
            if other == group:
                continue
            other_objs = group_dict[other]["objects"]
            if objs.issubset(other_objs) and objs != other_objs:
                diff = len(other_objs) - len(objs)
                candidates.append((other, diff))
        if candidates:
            parent = min(candidates, key=lambda x: x[1])[0]
            inferred_parents[group] = parent
    return inferred_parents


def build_inferred_tree(inferred_parents):
    tree = {group: {"children": []} for group in inferred_parents}
    roots = []
    for group, parent in inferred_parents.items():
        if parent:
            tree[parent]["children"].append(group)
        else:
            roots.append(group)
    return roots, tree


def print_inferred_tree(tree, node, group_dict, indent=0):
    print(" " * indent + "- " + node + " (" + group_dict[node]["name"] + ")")
    for child in sorted(tree[node]["children"]):
        print_inferred_tree(tree, child, group_dict, indent + 4)


def select_group_tree():
    objs = rs.GetObjects("Select objects")
    if not objs:
        print("No objects selected.")
        return
    group_dict, object_group_map, group_object_map = build_universal_group_dict(objs)
    shared_dict = compute_shared_elements(object_group_map)
    print_universal_structure(group_dict, shared_dict)
    inferred_parents = infer_group_hierarchy(group_dict)
    roots, tree = build_inferred_tree(inferred_parents)

    print("\nHierarchical Group Tree (inferred based on object inclusion):")
    for root in sorted(roots):
        print_inferred_tree(tree, root, group_dict)
